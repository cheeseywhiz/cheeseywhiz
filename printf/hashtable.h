#ifndef HASHTABLE_H
#define HASHTABLE_H
#include "vector.h"

/* the hashtable does not own its data */

struct Item {
    void *key, *value;
};

typedef size_t (*hashtable_hash_key)(const void *key);
typedef int (*hashtable_key_equal)(const void *key1, const void *key2);

struct Hashtable {
    struct Vector buckets;
    size_t size;
    hashtable_hash_key hash_key;
    hashtable_key_equal key_equal;
};

void init_hashtable(struct Hashtable *hashtable, hashtable_hash_key hash_key,
                    hashtable_key_equal key_equal);

void hashtable_free(struct Hashtable *hashtable);

/* if key is not NULL:
 *   key is in already in the container
 * else:
 *   key is not in the container */
struct Item* hashtable_insert(struct Hashtable *hashtable, const void *key);

/* if item is not NULL:
 *   key is not in the container
 * else:
 *   key is in the container */
struct Item* hashtable_find(const struct Hashtable *hashtable, const void *key);

/* if key is not NULL:
 *   key was removed from the container
 *   set key+value to NULL
 * else:
 *   key was not in the container */
struct Item* hashtable_erase(struct Hashtable *hashtable, const void *key);

typedef void (*hashtable_item_visitor)(const void *key, void *value);
void hashtable_map(const struct Hashtable *hashtable,
                   hashtable_item_visitor visitor);

#endif /* HASHTABLE_H */
