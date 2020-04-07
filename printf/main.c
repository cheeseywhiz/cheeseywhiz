#include "printf.h"
#include "syscall.h"
#include "types.h"

int
main() {
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
    write(STDOUT, "hello world\n", 12);
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
           "%h %h %h %h %h %h %h\n",
           0xdeadbeef, 0xdeadbeef & ~0x80000000, 0x123, 0, 1, 16, -1);
    printf("here's some unsigned: "
           "%u %u %u %u %u %u %u\n",
           0xdeadbeef, 0xdeadbeef & ~0x80000000, 0x123, 0, 1, 16, -1);
    printf("");
    return 0;
}
