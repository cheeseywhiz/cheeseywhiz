#ifndef IMMUNIZATION_H
#define IMMUNIZATION_H

struct ll_node {
        struct ll_node *next;
        void *data;
};

typedef void (*ll_free_func)(void *ptr);

struct ll_node* ll_new(void *data);
struct ll_node* ll_end(struct ll_node **head);
struct ll_node* ll_append(struct ll_node **head, void *data);
void ll_deep_free(struct ll_node **head, ll_free_func free_data);
void ll_2d_deep_free(struct ll_node **head, ll_free_func free_data);

struct immunization_data {
        char *year_label;
        char **years;

        char *population_label;
        unsigned long long *population;

        char **disease_names;
        int **matrix;
        int n_years;  /* rows */
        int n_diseases;  /* cols */
};

char* read_file(char *path);
void csv_free(struct ll_node *csv_data);
struct ll_node* read_csv(char *path);
void print_csv(struct ll_node **csv_data);

#endif
