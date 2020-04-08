#include "printf.h"
#include "syscall.h"

union PrintfArg {
    char c;
    const char *s;
    int i;
    unsigned u;
    void *ptr;
};

void fprintf_impl(int, const char*, union PrintfArg[]);
static void fput_int(int, int);
static void fput_unsigned(int, unsigned);
static void fput_hex(int, unsigned);
static void fput_ul_hex(int, size_t);

void
printf_impl(const char *format, union PrintfArg args[]) {
    fprintf_impl(STDOUT_FILENO, format, args);
}

void
put_string(const char *s) {
    fputs(STDOUT_FILENO, s);
}

void
put_char(char c) {
    fputc(STDOUT_FILENO, c);
}

void
fprintf_impl(int fd, const char *format, union PrintfArg args[]) {
    const char *first, *last;
    int type_mode = 0, i = 0;

    for (first = last = format; *last; ++last) {
        if (*last == '%') {
            if (type_mode)
                first = last;
            else
                write(STDOUT_FILENO, first, last - first);

            type_mode = !type_mode;
            continue;
        } else if (!type_mode) {
            continue;
        }

        first = last + 1;
        type_mode = 0;

        switch (*last) {
            case 's':
                fputs(fd, args[i++].s);
                break;
            case 'c':
                fputc(fd, args[i++].c);
                break;
            case 'd':
                fput_int(fd, args[i++].i);
                break;
            case 'x':
                fput_hex(fd, args[i++].u);
                break;
            case 'u':
                fput_unsigned(fd, args[i++].u);
                break;
            case 'p':
                fput_ul_hex(fd, (size_t)args[i++].ptr);
                break;
        }
    }

    write(fd, first, last - first);
}

static void
fput_int(int fd, int n) {
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

    fputs(fd, stack);
}

static void
fput_unsigned(int fd, unsigned n) {
    char mem[12], *stack = mem + LENGTH(mem) - 1;
    *stack = 0;

    do {
        *--stack = (n % 10) + '0';
    } while (n /= 10);

    fputs(fd, stack);
}

static void
fput_hex(int fd, unsigned n) {
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

    fputs(fd, mem);
}

static void
fput_ul_hex(int fd, size_t n) {
    char mem[] = "0x0000000000000000";
    char *stack = mem + LENGTH(mem) - 1;

    do {
        char c = n % 16;

        if (c < 10)
            c += '0';
        else
            c += 'a' - 10;

        *--stack = c;
    } while (n /= 16);

    fputs(fd, mem);
}

void
fputs(int fd, const char *s) {
    write(fd, s, strlen(s));
}

void
fputc(int fd, char c) {
    write(fd, &c, 1);
}

size_t
strlen(const char *s) {
    const char *end = s;
    while (*end)
        ++end;
    return end - s;
}
