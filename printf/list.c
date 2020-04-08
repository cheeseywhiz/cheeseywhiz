#include "list.h"
#include "alloc.h"

void
init_list(struct List *list, size_t node_size) {
    list->first = NULL;
    list->last = NULL;
    list->node_size = node_size;
    list->size = 0;
}

/* allocates and returns a new node */
struct Node*
list_push_back(struct List *list) {
    struct Node *new = ALLOC(list->node_size);
    new->next = NULL;
    new->prev = list->last;

    if (list->last)
        list->last->next = new;
    else
        list->first = new;

    list->last = new;
    ++list->size;
    return new;
}

void
list_pop_front(struct List *list) {
    struct Node *copy = list->first;

    if ((list->first = list->first->next))
        list->first->prev = NULL;
    else
        list->last = NULL;

    --list->size;
    FREE(copy);
}

void
list_pop_back(struct List *list) {
    struct Node *copy = list->last;

    if ((list->last = list->last->prev))
        list->last->next = NULL;
    else
        list->first = NULL;

    --list->size;
    FREE(copy);
}

void
list_erase(struct List *list, struct Node *node) {
    if (node == list->first) {
        list_pop_front(list);
        return;
    }

    if (node == list->last) {
        list_pop_back(list);
        return;
    }
    
    /* node is a middle element */
    node->prev->next = node->next;
    node->next->prev = node->prev;
    --list->size;
    FREE(node);
}

void
list_clear(struct List *list) {
    struct Node *node, *next;

    for (node = list->first; node; node = next) {
        next = node->next;
        FREE(node);
    }

    list->first = NULL;
    list->last = NULL;
    list->size = 0;
}

void
list_map(struct List *list, list_node_visitor visitor) {
    struct Node *node;
    for (node = list->first; node; node = node->next)
        visitor(node);
}

struct Node*
list_at(struct List *list, size_t i) {
    size_t n;
    struct Node *node = list->first;
    for (n = 0; n < i; ++n)
        node = node->next;
    return node;
}
