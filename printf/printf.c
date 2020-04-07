#include "printf.h"
#include "syscall.h"
#include "types.h"

static void put_int(int);
static void put_unsigned(unsigned);
static void put_hex(unsigned);

union PrintfArg {
    char c;
    const char *s;
    int i;
    unsigned u;
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
            case 'h':
                put_hex(args[i++].u);
                break;
            case 'u':
                put_unsigned(args[i++].u);
                break;
        }

        if (!first)
            first = last + 1;
    }

    write(STDOUT, first, last - first);
}

static void
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

static void
put_unsigned(unsigned n) {
    char mem[12], *stack = mem + LENGTH(mem) - 1;
    *stack = 0;

    do {
        *--stack = (n % 10) + '0';
    } while (n /= 10);

    put_string(stack);
}

static void
put_hex(unsigned n) {
    char mem[] = "0x00000000";
    char *stack = mem + LENGTH(mem) - 1;

    do {
        char c = n % 16;

        if (c < 10)
            c += '0';
        else
            c += 'a' - 10;

        *--stack = c;
    } while (n /= 16);

    put_string(mem);
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
