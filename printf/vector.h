#ifndef VECTOR_H
#define VECTOR_H
#include "alloc.h"

/* the vector owns its data */

typedef void (*vector_type_move)(void *dest, void *src);
typedef void (*vector_default_init)(void *ptr);

struct Vector {
    void *begin;
    void *end;
    void *capacity;
    size_t item_size;
    vector_type_move move;
    vector_default_init default_init;
};

void init_vector(struct Vector *vector, size_t item_size,
                 vector_type_move move, vector_default_init default_init);
void* vector_at(const struct Vector *vector, size_t i);
void vector_resize(struct Vector *vector, size_t length);
void vector_reserve(struct Vector *vector, size_t length);
size_t vector_length(const struct Vector *vector);
void* vector_push_back(struct Vector *vector);
void vector_clear(struct Vector *vector);

typedef void (*vector_visit_item)(const void *item);
void vector_map(const struct Vector *vector, vector_visit_item visitor);

#endif /* VECTOR_H */
