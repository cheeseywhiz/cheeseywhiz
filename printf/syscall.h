#ifndef SYSCALL_H
#define SYSCALL_H
#include "types.h"

void* syscall(void *syscall_number,
              void *param1,
              void *param2,
              void *param3,
              void *param4,
              void *param5
);

#define STDOUT 1
ssize_t write(int fd, const void *buf, size_t count);

#endif /* SYSCALL_H */
