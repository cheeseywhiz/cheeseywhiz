#include "syscall.h"
#include "printf.h"
#include "alloc.h"
#include "list.h"
#include "vector.h"
#include "hashtable.h"

extern void *_GLOBAL_OFFSET_TABLE_;
int main(int argc, char *argv[]);

void
test_printf() {
    const struct {
        const char *name;
        char grade;
        int percent;
    } tests[] = {
        { "physics", 'A', 93 },
        { "english", 'C', 72 },
        { "social studies", 'B', 89 },
    };
    int i;
    write(STDOUT_FILENO, "hello world\n", 12);
    put_string("goodbye world");
    put_char('\n');
    for (i = 0; i < LENGTH(tests); ++i)
        printf("On the %s test I got a %c grade of %d%%!\n",
               tests[i].name, tests[i].grade, tests[i].percent);
    printf("here's ten ints: "
           "%d %d %d %d %d %d %d %d %d %d\n",
           123, -123, 0, 1, 0xdeadbeef, 0xdeadbeef & ~0x80000000,
           7, 8, 9, 10);
    printf("here's some hexes: "
           "%x %x %x %x %x %x %x\n",
           0xdeadbeef, 0xdeadbeef & ~0x80000000, 0x123, 0, 1, 16, -1);
    printf("here's some unsigned: "
           "%u %u %u %u %u %u %u\n",
           0xdeadbeef, 0xdeadbeef & ~0x80000000, 0x123, 0, 1, 16, -1);
    printf("");
    printf("%p %p %p %p\n", main, _GLOBAL_OFFSET_TABLE_, NULL, (void*)-1);
}

void
test_alloc() {
    int i, len = 10;
    int *arr = ALLOC(len * sizeof(int));
    for (i = 0; i < len; ++i)
        arr[i] = i;
    for (i = 0; i < len; ++i)
        printf("%d ", arr[i]);
    printf("\n");
    FREE(arr);
}

void
print_int_node(struct IntNode *node) {
    printf("%d ", node->datum);
}

void
test_list() {
    int i, len = 10;
    struct List int_list;
    init_list(&int_list, sizeof(struct IntNode));

    for (i = 0; i < len; ++i) {
        struct IntNode *new = (struct IntNode*)list_push_back(&int_list);
        new->datum = i;
    }

    check_alloc(0);
    list_map(&int_list, (list_node_visitor)print_int_node);
    printf("\n%d\n", (int)int_list.size);

    list_erase(&int_list, list_at(&int_list, len / 2));
    list_pop_front(&int_list);
    list_pop_back(&int_list);
    check_alloc(0);

    /* TODO: remove cast once %lu is implemented */
    list_map(&int_list, (list_node_visitor)print_int_node);
    printf("\n%d\n", (int)int_list.size);

    list_clear(&int_list);
    printf("%d\n", (int)int_list.size);
}

static void
move_int(int *dest, int *src) {
    *dest = *src;
}

static void
default_init_int(int *n) {
    *n = 0;
}

static void
print_int(const int *n) {
    printf("%d ", *n);
}

static void
vector_check(struct Vector *vector) {
    check_alloc(0);
    vector_map(vector, (vector_visit_item)print_int);
    printf("\n%d\n", (int)vector_length(vector));
}

void
test_vector() {
    size_t i, len = 5;
    struct Vector vector;
    init_vector(&vector, sizeof(int), (vector_type_move)move_int,
                (vector_default_init)default_init_int);
    vector_resize(&vector, len);
    vector_check(&vector);
    for (i = 0; i < len; ++i)
        *(int*)vector_at(&vector, i) = i;
    vector_check(&vector);
    len += 5;
    for (; i < len; ++i)
        *(int*)vector_push_back(&vector) = i;
    vector_check(&vector);
    vector_clear(&vector);
}

static void hashtable_check(const struct Hashtable *hashtable);
static void print_bucket(const struct Bucket *bucket);
static void print_item(const char*, const int*);
static int string_equal(const char*, const char*);
static int strcmp(const char*, const char*);
static size_t lu_hash(size_t);
static size_t string_hash(const char*);

static void
hashtable_check(const struct Hashtable *hashtable) {
    check_alloc(0);
    vector_map(&hashtable->buckets, (vector_visit_item)print_bucket);
    put_string("{ ");
    hashtable_map(hashtable, (hashtable_item_visitor)print_item);
    printf("}\n%d\n\n", (int)hashtable->size);
}

static void
print_bucket(const struct Bucket *bucket) {
    printf("Bucket{ %d, \"%s\", \"%s\" }\n", bucket->status, bucket->key,
           bucket->value);
}

static void
print_item(const char *object, const int *color) {
    printf("\"%s\": \"%s\", ", object, color);
}

static int
string_equal(const char *s1, const char *s2) {
    return !strcmp(s1, s2);
}

static int
strcmp(const char *s1, const char *s2) {
    /* http://www.cplusplus.com/reference/algorithm/lexicographical_compare/ */
    while (*s1) {
        if (!*s2 || *s2 < *s1)
            return 1;
        if (*s1 < *s2)
            return -1;
        ++s1;
        ++s2;
    }

    return *s2;
}

static size_t
string_hash(const char *s) {
    size_t hash = 0, new_hash;
    while ((new_hash = lu_hash(*s++)))
        hash = lu_hash(hash + new_hash);
    return hash;
}

static size_t lu_hash(size_t x) {
    /* https://stackoverflow.com/a/12996028 */
    x = ((x >> 16) ^ x) * 0x45d9f3b;
    x = ((x >> 16) ^ x) * 0x45d9f3b;
    x = (x >> 16) ^ x;
    return x;
}

struct Item {
    char *object;
    char *color;
};

void
test_hashtable() {
    struct Hashtable ht;
    struct Bucket *bucket;
    const struct Item items[] = {
        { "apple", "red" },
        { "orange", "orange" },
        { "banana", "yellow" },
    };
    size_t i;
    init_hashtable(&ht, (hashtable_hash_key)string_hash, (hashtable_key_equal)string_equal);
    hashtable_check(&ht);
    printf("%d %d\n",
           strcmp(items[1].object, items[2].object),
           string_equal(items[1].object, items[2].object));

    for (i = 0; i < LENGTH(items); ++i) {
        const struct Item *item = &items[i];
        bucket = hashtable_insert(&ht, item->object);
        printf("insert bucket:\n");
        print_bucket(bucket);
        bucket->key = item->object;
        bucket->value = item->color;
        hashtable_check(&ht);
    }

    print_bucket(hashtable_insert(&ht, items[0].object));
    printf("%s %s %s\n", hashtable_find(&ht, "orange"),
                      hashtable_find(&ht, "grape"),
                      hashtable_find(&ht, "apple")
    );
    hashtable_check(&ht);

    bucket = hashtable_erase(&ht, items[0].object);
    print_bucket(bucket);
    bucket->key = NULL;
    bucket->value = NULL;
    hashtable_check(&ht);

    bucket = hashtable_erase(&ht, "not found");
    print_bucket(bucket);
    hashtable_check(&ht);

    bucket = hashtable_erase(&ht, "abc");
    print_bucket(bucket);
    hashtable_check(&ht);

    bucket = hashtable_insert(&ht, items[0].object);
    print_bucket(bucket);
    bucket->key = items[0].object;
    bucket->value = items[0].object;
    hashtable_check(&ht);

    hashtable_free(&ht);
}

int
main(int argc, char *argv[]) {
    test_printf();
    test_alloc();
    test_list();
    test_vector();
    test_hashtable();
    return 0;
}
