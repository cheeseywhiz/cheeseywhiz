#include "syscall.h"
#include "types.h"
#include <sys/syscall.h>

ssize_t
write(int fd, const void *buf, size_t count) {
    return (size_t)syscall(
        (void*)SYS_write,
        (void*)(size_t)fd,
        (void*)buf,
        (void*)count,
        0,
        0
    );
}
