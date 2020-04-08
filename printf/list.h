#ifndef LIST_H
#define LIST_H
#include <unistd.h>

/* make a Node struct the first entry in your struct so that your struct
 * is cast-able to struct Node */

struct Node {
    struct Node *next, *prev;
};

/* some helper nodes */
struct IntNode {
    struct Node node;
    int datum;
};

struct List {
    struct Node *first, *last;
    size_t node_size;
    size_t size;
};

void init_list(struct List *list, size_t node_size);

/* allocates and returns a new node */
struct Node* list_push_back(struct List *list);
/* frees the node */
void list_pop_front(struct List *list);
/* frees the node */
void list_pop_back(struct List *list);
/* frees the node */
void list_erase(struct List *list, struct Node *node);
/* frees all nodes */
void list_clear(struct List *list);

typedef void (*list_node_visitor)(struct Node *node);
void list_map(struct List *list, list_node_visitor visitor);

struct Node* list_at(struct List *list, size_t i);

#endif /* LIST_H */
