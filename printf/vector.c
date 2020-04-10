#include "vector.h"
#include "alloc.h"

static void vector_grow(struct Vector *);

void
init_vector(struct Vector *vector, size_t item_size, vector_type_move move,
            vector_default_init default_init) {
    vector->begin = NULL;
    vector->end = NULL;
    vector->capacity = NULL;
    vector->item_size = item_size;
    vector->move = move;
    vector->default_init = default_init;
}

void*
vector_at(const struct Vector *vector, size_t i) {
    return vector->begin + (vector->item_size * i);
}

void*
vector_push_back(struct Vector *vector) {
    void *ptr;
    if (vector->end == vector->capacity)
        vector_grow(vector);
    ptr = vector->end;
    vector->end += vector->item_size;;
    return ptr;
}

void
vector_resize(struct Vector *vector, size_t length) {
    size_t n_new_items = length - vector_length(vector);
    size_t i;
    vector_reserve(vector, length);
    for (i = 0; i < n_new_items; ++i)
        vector->default_init(vector_push_back(vector));
}

void
vector_reserve(struct Vector *vector, size_t length) {
    size_t old_length = vector_length(vector);
    size_t capacity = length * vector->item_size;
    size_t i;
    void *new = ALLOC(capacity);
    void *dest = new, *src = vector->begin;

    for (i = 0; i < old_length; ++i) {
        vector->move(dest, src);
        dest += vector->item_size;
        src += vector->item_size;
    }

    FREE(vector->begin);
    vector->begin = new;
    vector->end = dest;
    vector->capacity = new + capacity;
}

size_t
vector_length(const struct Vector *vector) {
    return (vector->end - vector->begin) / vector->item_size;
}

void
vector_clear(struct Vector *vector) {
    FREE(vector->begin);
    vector->begin = NULL;
    vector->end = NULL;
    vector->capacity = NULL;
}

void
vector_map(const struct Vector *vector, vector_visit_item visitor) {
    void *ptr;
    for (ptr = vector->begin; ptr != vector->end; ptr += vector->item_size)
        visitor(ptr);
}

static void
vector_grow(struct Vector *vector) {
    vector_reserve(vector, 2 * vector_length(vector) + 1);
}
