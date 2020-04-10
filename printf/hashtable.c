#include "hashtable.h"

enum BucketStatus {
    BS_EMPTY,
    BS_OCCUPIED,
    BS_DELETED
};

struct Bucket {
    struct Item item;
    enum BucketStatus status;
};

static void grow(struct Hashtable*);
static struct Bucket* find(const struct Hashtable*, const void*);
static void init_buckets(struct Vector*);
static void move_bucket(struct Bucket*, const struct Bucket*);
static void default_init_bucket(struct Bucket*);
static void set_bucket(struct Bucket*, void*, void*, enum BucketStatus);

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

struct Item*
hashtable_insert(struct Hashtable *hashtable, const void *key) {
    struct Bucket *bucket;
    grow(hashtable);
    bucket = find(hashtable, key);

    if (bucket->status != BS_OCCUPIED) {
        bucket->status = BS_OCCUPIED;
        ++hashtable->size;
    }

    return (struct Item*)bucket;
}

struct Item*
hashtable_find(const struct Hashtable *hashtable, const void *key) {
    struct Bucket *bucket = find(hashtable, key);
    if (bucket->status != BS_OCCUPIED)
        return NULL;
    return (struct Item*)bucket;
}

struct Item*
hashtable_erase(struct Hashtable *hashtable, const void *key) {
    struct Bucket *bucket = find(hashtable, key);

    if (bucket->status == BS_OCCUPIED) {
        bucket->status = BS_DELETED;
        --hashtable->size;
    }

    return (struct Item*)bucket;
}

void
hashtable_map(const struct Hashtable *hashtable,
              hashtable_item_visitor visitor) {
    size_t i, length = vector_length(&hashtable->buckets);

    for (i = 0; i < length; ++i) {
        struct Bucket *bucket = vector_at(&hashtable->buckets, i);
        if (bucket->status == BS_OCCUPIED)
            visitor(bucket->item.key, bucket->item.value);
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
            struct Bucket *insert_bucket = find(hashtable, bucket->item.key);
            set_bucket(insert_bucket, bucket->item.key, bucket->item.value,
                       BS_OCCUPIED);
        }
    }

    vector_clear(&old_buckets);
}

static struct Bucket*
find(const struct Hashtable *hashtable, const void *key) {
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
                return deleted;
            if (!deleted)
                deleted = bucket;
            break;
        case BS_OCCUPIED:
            /* all unoccupied buckets are deleted */
            if (checked_first_i && i == first_i)
                return deleted;
            if (hashtable->key_equal(bucket->item.key, key))
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
move_bucket(struct Bucket *dest, const struct Bucket *src) {
    set_bucket(dest, src->item.key, src->item.value, src->status);
}

static void
default_init_bucket(struct Bucket *bucket) {
    set_bucket(bucket, NULL, NULL, BS_EMPTY);
}

static void
set_bucket(struct Bucket *bucket, void *key, void *value,
           enum BucketStatus status) {
    bucket->item.key = key;
    bucket->item.value = value;
    bucket->status = status;
}
