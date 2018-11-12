#include <errno.h>
#include <fcntl.h>
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
        strcpy(word_copy, word);

        if (word_copy == NULL) {
                LOG_ERRNO("malloc");
                return NULL;
        }

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
                        char *data = cell_ptr->data;
                        fputs(data, stdout);
                        if (cell_ptr->next) putchar(',');
                }

                putchar('\n');
        }
}

int main(int argc, char *argv[]) {
        struct ll_node *csv_data = read_csv("immunization.csv");
        if (csv_data == NULL) return 1;
        print_csv(&csv_data);
        csv_free(csv_data);
        return 0;
}
