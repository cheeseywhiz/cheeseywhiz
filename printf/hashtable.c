#include "hashtable.h"

static void grow(struct Hashtable*);
static struct Bucket* find(struct Hashtable*, const void*);
static void init_buckets(struct Vector*);
static void move_bucket(struct Bucket*, struct Bucket*);
static void default_init_bucket(struct Bucket*);

void
init_hashtable(struct Hashtable *hashtable, hashtable_hash_key hash_key,
               hashtable_key_equal key_equal) {
    init_buckets(&hashtable->buckets);
    vector_resize(&hashtable->buckets, 3);
    hashtable->size = 0;
    hashtable->hash_key = hash_key;
    hashtable->key_equal = key_equal;
}

void
hashtable_free(struct Hashtable *hashtable) {
    vector_clear(&hashtable->buckets);
}

struct Bucket*
hashtable_insert(struct Hashtable *hashtable, const void *key) {
    struct Bucket *bucket;
    grow(hashtable);
    bucket = find(hashtable, key);
    if (bucket->status == BS_OCCUPIED)
        return bucket;
    bucket->status = BS_OCCUPIED;
    ++hashtable->size;
    return bucket;
}

void*
hashtable_find(struct Hashtable *hashtable, const void *key) {
    struct Bucket *bucket = find(hashtable, key);
    return bucket->value;
}

struct Bucket*
hashtable_erase(struct Hashtable *hashtable, const void *key) {
    struct Bucket *bucket = find(hashtable, key);
    if (bucket->status != BS_OCCUPIED)
        return bucket;
    bucket->status = BS_DELETED;
    --hashtable->size;
    return bucket;
}

void
hashtable_map(const struct Hashtable *hashtable,
              hashtable_item_visitor visitor) {
    size_t i, length = vector_length(&hashtable->buckets);

    for (i = 0; i < length; ++i) {
        struct Bucket *bucket = vector_at(&hashtable->buckets, i);
        if (bucket->status == BS_OCCUPIED)
            visitor(bucket->key, bucket->value);
    }
}

static void
grow(struct Hashtable *hashtable) {
    struct Vector old_buckets = hashtable->buckets;
    size_t old_bucket_size = vector_length(&hashtable->buckets);
    size_t i;
    if (2 * hashtable->size < old_bucket_size)
        return;
    init_buckets(&hashtable->buckets);
    vector_resize(&hashtable->buckets, 2 * old_bucket_size);

    for (i = 0; i < old_bucket_size; ++i) {
        const struct Bucket *bucket = vector_at(&old_buckets, i);

        if (bucket->status == BS_OCCUPIED) {
            struct Bucket *insert_bucket = find(hashtable, bucket->key);
            insert_bucket->status = BS_OCCUPIED;
            insert_bucket->key = bucket->key;
            insert_bucket->value = bucket->value;
        }
    }

    vector_clear(&old_buckets);
}

static struct Bucket*
find(struct Hashtable *hashtable, const void *key) {
    struct Bucket *deleted = NULL;
    size_t buckets_length = vector_length(&hashtable->buckets);
    size_t i, first_i = hashtable->hash_key(key) % buckets_length;
    int checked_first_i = 0;

    for (i = first_i; ; i = (i + 1) % buckets_length) {
        struct Bucket *bucket = vector_at(&hashtable->buckets, i);

        switch (bucket->status) {
        case BS_EMPTY:
            return deleted ? deleted : bucket;
        case BS_DELETED:
            /* all unoccupied buckets are deleted */
            if (checked_first_i && i == first_i)
                return bucket;
            if (!deleted)
                deleted = bucket;
            break;
        case BS_OCCUPIED:
            /* all unoccupied buckets are deleted */
            if (checked_first_i && i == first_i)
                return deleted;
            if (hashtable->key_equal(bucket->key, key))
                return bucket;
            break;
        }

        checked_first_i = 1;
    }
}

static void
init_buckets(struct Vector *buckets) {
    init_vector(
        buckets, sizeof(struct Bucket),
        (vector_type_move)move_bucket,
        (vector_default_init)default_init_bucket);
}

static void
move_bucket(struct Bucket *dest, struct Bucket *src) {
    dest->status = src->status;
    dest->key = src->key;
    dest->value = src->value;
}

static void
default_init_bucket(struct Bucket *bucket) {
    bucket->status = BS_EMPTY;
    bucket->key = NULL;
    bucket->value = NULL;
}
