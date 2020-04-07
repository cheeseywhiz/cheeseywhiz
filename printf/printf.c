#include "printf.h"
#include "syscall.h"
#include "types.h"

union PrintfArg {
    char c;
    const char *s;
    int i;
};

void
printf_impl(const char *format, union PrintfArg args[]) {
    const char *first, *last;
    int type_mode = 0, i = 0;

    for (first = last = format; *last; ++last) {
        if (!type_mode) {
            if (*last == '%') {
                type_mode = 1;
                write(STDOUT, first, last - first);
            }

            continue;
        }

        type_mode = 0;
        first = NULL;

        switch (*last) {
            case '%':
                first = last;
                break;
            case 's':
                put_string(args[i++].s);
                break;
            case 'c':
                put_char(args[i++].c);
                break;
            case 'd':
                put_int(args[i++].i);
                break;
        }

        if (!first)
            first = last + 1;
    }

    write(STDOUT, first, last - first);
}

void
put_int(int n) {
    char mem[12], *stack = mem + LENGTH(mem) - 1;
    int copy = n;
    *stack = 0;

    do {
        char c = n % 10;

        if (n > 0)
            c += '0';
        else
            c = '0' - c;

        *--stack = c;
    } while (n /= 10);

    if (copy < 0)
        *--stack = '-';

    put_string(stack);
}

void
put_string(const char *s) {
    write(STDOUT, s, strlen(s));
}

void
put_char(char c) {
    write(STDOUT, &c, 1);
}

size_t
strlen(const char *s) {
    const char *end = s;
    while (*end)
        ++end;
    return end - s;
}
