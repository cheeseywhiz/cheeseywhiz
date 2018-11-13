#ifndef IMMUNIZATION_H
#define IMMUNIZATION_H

#include <stddef.h>

struct ll_node {
        struct ll_node *next;
        void *data;
};

typedef void (*ll_free_func)(void *ptr);

struct ll_node* ll_new(void *data);
struct ll_node* ll_end(struct ll_node **head);
struct ll_node* ll_append(struct ll_node **head, void *data);
size_t ll_length(struct ll_node **head);
struct ll_node* ll_get_index(struct ll_node **head, size_t index);
void* ll_pop_index(struct ll_node **head, size_t index);
void ll_deep_free(struct ll_node **head, ll_free_func free_data);
void ll_2d_deep_free(struct ll_node **head, ll_free_func free_data);

struct immunization_data {
        char *year_label;
        struct ll_node *years;

        char *population_label;
        struct ll_node *population;

        struct ll_node *disease_names;
        struct ll_node *matrix;
};

char* read_file(char *path);
void csv_free(struct ll_node *csv_data);
struct ll_node* read_csv(char *path);
void print_csv(struct ll_node **csv_data);
int init_immunization_data(struct immunization_data *data);
void immunization_free(struct immunization_data *data);

typedef enum {
        PA_LEFT, PA_RIGHT
} print_alignment;

void print_repeat_char(char c, size_t n);
void print_align(char *string, print_alignment alignment, size_t field_width);
char* input(char *prompt);
char* disease_input(struct immunization_data *data);

#endif
