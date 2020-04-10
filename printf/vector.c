#include "vector.h"
#include "alloc.h"

void
init_vector(struct Vector *vector, const struct VectorType *type) {
    vector->begin = NULL;
    vector->end = NULL;
    vector->capacity = NULL;
    vector->type = type;
}

void*
vector_at(struct Vector *vector, size_t i) {
    return vector->begin + (vector->type->size * i);
}

static void vector_grow(struct Vector *);

void*
vector_push_back(struct Vector *vector) {
    void *ptr;
    if (vector->end == vector->capacity)
        vector_grow(vector);
    ptr = vector->end;
    vector->end += vector->type->size;;
    return ptr;
}

void
vector_resize(struct Vector *vector, size_t length) {
    size_t n_new_items = length - vector_length(vector);
    size_t i;
    vector_reserve(vector, length);
    for (i = 0; i < n_new_items; ++i)
        vector->type->default_init(vector_push_back(vector));
}

static void
vector_grow(struct Vector *vector) {
    vector_reserve(vector, 2 * vector_length(vector) + 1);
}

void
vector_reserve(struct Vector *vector, size_t length) {
    size_t old_length = vector_length(vector);
    size_t capacity = length * vector->type->size;
    size_t i;
    void *new = ALLOC(capacity);
    void *dest = new, *src = vector->begin;

    for (i = 0; i < old_length; ++i) {
        vector->type->move(dest, src);
        dest += vector->type->size;
        src += vector->type->size;
    }

    FREE(vector->begin);
    vector->begin = new;
    vector->end = dest;
    vector->capacity = new + capacity;
}

size_t
vector_length(struct Vector *vector) {
    return (vector->end - vector->begin) / vector->type->size;
}

void vector_clear(struct Vector *vector) {
    FREE(vector->begin);
    vector->begin = NULL;
    vector->end = NULL;
    vector->capacity = NULL;
}

void
vector_map(struct Vector *vector, vector_visit_item visitor) {
    void *ptr;
    for (ptr = vector->begin; ptr != vector->end; ptr += vector->type->size)
        visitor(ptr);
}
