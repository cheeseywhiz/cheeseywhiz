#include "syscall.h"
#include "printf.h"
#include "alloc.h"
#include "list.h"
#include "vector.h"

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

static const struct VectorType int_type = {
    sizeof(int),
    (vector_type_move)move_int,
    (vector_default_init)default_init_int,
};

static void
print_int(int *n) {
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
    init_vector(&vector, &int_type);
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

int
main(int argc, char *argv[]) {
    test_printf();
    test_alloc();
    test_list();
    test_vector();
    return 0;
}
