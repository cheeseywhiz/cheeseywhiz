#ifndef IMMUNIZATION_H
#define IMMUNIZATION_H

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
int read_csv(char *path);

#endif
