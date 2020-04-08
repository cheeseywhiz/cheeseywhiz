#include "syscall.h"
#include "printf.h"
#include "alloc.h"

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

int
main(int argc, char *argv[]) {
    /*test_printf();*/
    test_alloc();
    return 0;
}
