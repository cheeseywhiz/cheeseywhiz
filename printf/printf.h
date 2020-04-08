#ifndef PRINTF_H
#define PRINTF_H
#include <unistd.h>

void printf(const char *format, ...);
void put_string(const char *s);
void put_char(char c);

void fprintf(int fd, const char *format, ...);
void fputs(int fd, const char *s);
void fputc(int fd, char c);

size_t strlen(const char *s);

#endif /* PRINTF_H */
