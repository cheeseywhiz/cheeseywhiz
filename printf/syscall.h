#ifndef SYSCALL_H
#define SYSCALL_H
#include <unistd.h>

#define LENGTH(arr) (sizeof(arr)/sizeof(arr[0]))
void exit(int status);
void* mmap(void *addr, size_t length, int prot, int flags,
           int fd, off_t offset);
int munmap(void *addr, size_t length);

#define DID_SYSCALL_FAIL(ret) ((size_t)(ret) > -4096UL)
#define SYSCALL_ERRNO_CAST(ret) ((int)(-(size_t)(ret)))

#endif /* SYSCALL_H */
