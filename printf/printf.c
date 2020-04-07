#include "printf.h"
#include "syscall.h"

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
