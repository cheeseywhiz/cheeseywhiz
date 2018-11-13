#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "immunization.h"

#define LOG_ERRNO(function) fprintf(stderr, "%s: %s\n", function, strerror(errno))

struct ll_node* ll_new(void *data) {
        struct ll_node *node = malloc(sizeof(struct ll_node));

        if (node == NULL) {
                LOG_ERRNO("malloc");
                return NULL;
        }

        node->next = NULL;
        node->data = data;
        return node;
}

struct ll_node* ll_end(struct ll_node **head) {
        if (*head == NULL) {
                return NULL;
        }

        struct ll_node *end;
        for (end = *head; end->next != NULL; end = end->next);
        return end;
}

struct ll_node* ll_append(struct ll_node **head, void *data) {
        struct ll_node *new = ll_new(data);

        if (!new) {
                return NULL;
        } else if (*head == NULL) {
                *head = new;
        } else {
                struct ll_node *end = ll_end(head);
                end->next = new;
        }

        return new;
}

size_t ll_length(struct ll_node **head) {
        if (*head == NULL) {
                return 0;
        }

        size_t length = 0;
        for (struct ll_node *ptr = *head; ptr != NULL; ptr = ptr->next) length++;
        return length;
}

struct ll_node* ll_get_index(struct ll_node **head, size_t index) {
        if (*head == NULL) {
                return NULL;
        } else if (index >= ll_length(head)) {
                return NULL;
        }

        struct ll_node *item = *head;

        for (size_t i = 0; i < index; i++) {
                if (item == NULL) {
                        return NULL;
                }

                item = item->next;
        }

        return item;
}

void* ll_pop_index(struct ll_node **head, size_t index) {
        struct ll_node *item;
        size_t length = ll_length(head);

        if (length == 0 || index >= length) {
                item = NULL;
        } else if (length == 1 || index == 0) {
                item = *head;
                *head = item->next;
        } else {
                struct ll_node *before = ll_get_index(head, index - 1);
                if (before == NULL) return NULL;
                item = before->next;
                if (item == NULL) return NULL;
                before->next = item->next;
        }

        void *data;

        if (item == NULL) {
                data = NULL;
        } else {
                data = item->data;
                free(item);
        }

        return data;
}

void ll_deep_free(struct ll_node **head, ll_free_func free_data) {
        struct ll_node *item, *item_alias;

        for (item = *head; item != NULL; ) {
                item_alias = item;
                item = item->next;
                free_data(item_alias->data);
                free(item_alias);
        }
}

void ll_2d_deep_free(struct ll_node **head, ll_free_func free_data) {
        struct ll_node *row_ptr, *row_alias;

        for (row_ptr = *head; row_ptr != NULL; ) {
                row_alias = row_ptr;
                row_ptr = row_ptr->next;
                struct ll_node *cell_ptr, *cell_alias;

                for (cell_ptr = row_alias->data; cell_ptr != NULL; ) {
                        cell_alias = cell_ptr;
                        cell_ptr = cell_ptr->next;
                        free_data(cell_alias->data);
                        free(cell_alias);
                }

                free(row_alias);
        }
}

char* read_file(char *path) {
        struct stat st;

        if (stat(path, &st)) {
                LOG_ERRNO("stat");
                return NULL;
        }

        size_t buffer_size = st.st_size + 1;
        char *buffer = calloc(buffer_size, 1);
        int fd = open(path, O_RDONLY);

        if (fd == -1) {
                LOG_ERRNO("open");
                free(buffer);
                return NULL;
        }

        if (read(fd, buffer, buffer_size) < 0) {
                LOG_ERRNO("read");
                free(buffer);
                close(fd);
                return NULL;
        }

        close(fd);
        return buffer;
}

void csv_free(struct ll_node *csv_data) {
        ll_2d_deep_free(&csv_data, free);
}

static struct ll_node* ll_csv_append(struct ll_node **head, char *contents, int current_word) {
        char *word = contents + current_word;
        char *word_copy = malloc(strlen(word) + 1);

        if (word_copy == NULL) {
                LOG_ERRNO("malloc");
                return NULL;
        }

        strcpy(word_copy, word);
        return ll_append(head, word_copy);
}

#define HANDLE_SEP() \
        contents[ptr] = '\0'; \
        if (ll_csv_append(&row, contents, current_word) == NULL) { \
                free(contents); \
                ll_deep_free(&row, free); \
                csv_free(csv_data); \
                return NULL; \
        } \
        current_word = ptr + 1

struct ll_node* read_csv(char *path) {
        char *contents = read_file(path);

        if (!contents) {
                return NULL;
        }

        struct ll_node *csv_data = NULL;
        int ptr;
        int current_word = 0;

        for (ptr = 0; contents[ptr] != '\0'; ptr++) {
                struct ll_node *row = NULL;

                for (;; ptr++) {
                        if (contents[ptr] == '\n') {
                                HANDLE_SEP();
                                break;
                        } else if (contents[ptr] == ',') {
                                HANDLE_SEP();
                        }
                }

                if (ll_append(&csv_data, row) == NULL) {
                        free(contents);
                        ll_deep_free(&row, free);
                        csv_free(csv_data);
                        return NULL;
                }
        }

        free(contents);
        return csv_data;
}

void print_csv(struct ll_node **csv_data) {
        struct ll_node *row_ptr;
        struct ll_node *cell_ptr;

        for (row_ptr = *csv_data; row_ptr != NULL; row_ptr = row_ptr->next) {
                for (cell_ptr = row_ptr->data; cell_ptr != NULL; cell_ptr = cell_ptr->next) {
                        int *data = cell_ptr->data;
                        printf("%d", *data);
                        if (cell_ptr->next) putchar(',');
                }

                putchar('\n');
        }
}

int init_immunization_data(struct immunization_data *data) {
        data->matrix = read_csv("immunization.csv");

        if (data->matrix == NULL) {
                return 1;
        }

        data->years = ll_pop_index(&data->matrix, 0);

        if (data->years == NULL) {
                csv_free(data->matrix);
                return 2;
        }

        data->year_label = ll_pop_index(&data->years, 0);

        if (data->year_label == NULL) {
                csv_free(data->matrix);
                return 3;
        }

        data->population = ll_pop_index(&data->matrix, 0);

        if (data->population == NULL) {
                csv_free(data->matrix);
                return 4;
        }

        data->population_label = ll_pop_index(&data->population, 0);

        if (data->population_label == NULL) {
                csv_free(data->matrix);
                return 5;
        }

        struct ll_node *ptr;

        for (ptr = data->population; ptr != NULL; ptr = ptr->next) {
                char *pop_str = ptr->data;
                ptr->data = malloc(sizeof(unsigned long long));
                if (ptr->data == NULL) return 6;
                *((unsigned long long*) ptr->data) = strtoull(pop_str, NULL, 0);
                free(pop_str);
        }

        data->disease_names = NULL;
        struct ll_node *row_ptr, *row;

        for (row_ptr = data->matrix; row_ptr != NULL; row_ptr = row_ptr->next) {
                row = row_ptr->data;
                struct ll_node *next = row->next;
                char *disease_name = ll_pop_index(&row, 0);
                ll_append(&data->disease_names, disease_name);
                row_ptr->data = next;

                for (; row != NULL; row = row->next) {
                        char *value_str = row->data;
                        row->data = malloc(sizeof(int));
                        if (row->data == NULL) return 7;
                        *((int*)row->data) = atoi(value_str);
                        free(value_str);
                }
        }

        return 0;
}

void immunization_free(struct immunization_data *data) {
        free(data->year_label);
        ll_deep_free(&data->years, free);
        free(data->population_label);
        ll_deep_free(&data->population, free);
        ll_deep_free(&data->disease_names, free);
        ll_2d_deep_free(&data->matrix, free);
}

void print_repeat_char(char c, size_t n) {
        for (size_t i = 0; i < n; i++) putchar(c);
}

void print_align(char *string, print_alignment alignment, size_t field_width) {
        if (string == NULL) {
                string = "";
        }

        size_t string_length = strlen(string);
        size_t padding = field_width >= string_length ? field_width - string_length : 0;

        switch (alignment) {
                case PA_LEFT: {
                        printf("%s", string);
                        print_repeat_char(' ', padding);
                        break;
                };
                case PA_RIGHT: {
                        print_repeat_char(' ', padding);
                        printf("%s", string);
                        break;
                };
        }
}

char* input(char *prompt) {
        printf("%s ", prompt);
        char *buffer = NULL;
        size_t n = 0;
        ssize_t buffer_length = getline(&buffer, &n, stdin);

        if (buffer_length < 0) {
                LOG_ERRNO("getline");
        } else if (buffer[buffer_length - 1] == '\n') {
                buffer[buffer_length - 1] = '\0';
        }

        return buffer;
}

char* disease_input(struct immunization_data *data) {
        struct ll_node *name_node;
        size_t i = 1;
        size_t diseases_length = ll_length(&data->disease_names);

        for (name_node = data->disease_names; name_node != NULL; name_node = name_node->next) {
                char *name = name_node->data;
                print_align(name, PA_LEFT, 21);
                putchar('\t');

                if (i % 3 == 0 || i == diseases_length) {
                        putchar('\n');
                }

                i++;
        }

        putchar('\n');
        return input("Enter the name or part of a name of the disease:");
}

int main(int argc, char *argv[]) {
        struct immunization_data data;
        if (init_immunization_data(&data)) return 1;
        char *disease_answer = disease_input(&data);
        printf("%s\n", disease_answer);
        free(disease_answer);
        immunization_free(&data);
        return 0;
}
