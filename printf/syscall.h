#ifndef SYSCALL_H
#define SYSCALL_H
#include "types.h"

#define STDOUT 1
ssize_t write(int fd, const void *buf, size_t count);
void exit(int status);

#endif /* SYSCALL_H */
