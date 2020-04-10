#ifndef VECTOR_H
#define VECTOR_H
#include "alloc.h"

typedef void (*vector_type_move)(void *dest, void *src);
typedef void (*vector_default_init)(void *ptr);

struct VectorType {
    size_t size;
    vector_type_move move;
    vector_default_init default_init;
};

struct Vector {
    void *begin;
    void *end;
    void *capacity;
    const struct VectorType *type;
};

void init_vector(struct Vector *vector, const struct VectorType *type);
void* vector_at(struct Vector *vector, size_t i);
void vector_resize(struct Vector *vector, size_t length);
void vector_reserve(struct Vector *vector, size_t length);
size_t vector_length(struct Vector *vector);
void* vector_push_back(struct Vector *vector);
void vector_clear(struct Vector *vector);

typedef void (*vector_visit_item)(void *item);
void vector_map(struct Vector *vector, vector_visit_item visitor);

#endif /* VECTOR_H */
