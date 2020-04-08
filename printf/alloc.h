#ifndef ALLOC_H
#define ALLOC_H
#include <unistd.h>

#define ALLOC(size) alloc_impl(size, __FILE__, __LINE__)
void* alloc_impl(size_t size, const char *file, int line);
#define FREE(ptr) free_impl(ptr, __FILE__, __LINE__)
void free_impl(void *ptr, const char *file, int line);
int check_alloc(int status);

#endif /* ALLOC_H */
