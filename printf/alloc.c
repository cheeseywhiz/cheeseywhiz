#include <sys/mman.h>
#include <unistd.h>
#include "alloc.h"
#include "syscall.h"
#include "printf.h"

struct Allocation {
    size_t size;
    void *ptr;
    struct Allocation *next, *prev;
};

struct AllocList {
    struct Allocation *head, *tail;
};

struct AllocList alloc_list = { NULL, NULL };

static void alloc_list_push(struct AllocList*, struct Allocation*);
static void alloc_list_remove(struct AllocList*, struct Allocation*);

#define VOID_PTR_ADD(ptr, arg) ((void*)(((size_t)(ptr)) + arg))
#define VOID_PTR_SUB(ptr, arg) ((void*)(((size_t)(ptr)) - arg))

static void
init_alloc(struct Allocation *alloc, size_t size, void *map) {
    alloc->size = size;
    alloc->ptr = VOID_PTR_ADD(map, sizeof(struct Allocation));
    alloc->next = NULL;
    alloc->prev = NULL;
}

void*
alloc_impl(size_t size, const char *file, int line) {
    struct Allocation *alloc;
    void *map;
    /* allocate enough memory for the caller's needs and for our bookkeeping structure */
    size += sizeof(struct Allocation);
    map = mmap(NULL, size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

    if (DID_SYSCALL_FAIL(map)) {
        fprintf(STDERR_FILENO, "mmap failed with %d at %s:%d\n", SYSCALL_ERRNO_CAST(map), file, line);
        exit(1);
    }

    alloc = map;
    init_alloc(alloc, size, map);
    alloc_list_push(&alloc_list, alloc);
    fprintf(STDERR_FILENO, "allocated %d at %s:%d\n", (int)size, file, line);
    return alloc->ptr;
}

void
free_impl(void *ptr, const char *file, int line) {
    size_t ret, size;
    struct Allocation *alloc = VOID_PTR_SUB(ptr, sizeof(struct Allocation));
    if (!ptr)
        return;
    alloc_list_remove(&alloc_list, alloc);
    size = alloc->size;

    if (DID_SYSCALL_FAIL(ret = munmap(alloc, size))) {
        fprintf(STDERR_FILENO, "munmap failed with %d at %s:%d\n", SYSCALL_ERRNO_CAST(ret), file, line);
        exit(1);
    }

    size -= sizeof(struct Allocation);
    fprintf(STDERR_FILENO, "freed %d at %s:%d\n", (int)size, file, line);
}

static void
alloc_list_push(struct AllocList *list, struct Allocation *alloc) {
    if (list->tail)
        list->tail->next = alloc;
    else
        list->head = alloc;

    alloc->prev = list->tail;
    list->tail = alloc;
}

static void
alloc_list_remove(struct AllocList *list, struct Allocation *alloc) {
    /* https://gitlab.eecs.umich.edu/sctodd/eecs-280/blob/master/p4-web/List.h#L233 */
    if (alloc == list->head) {
        if ((list->head = alloc->next))
            list->head->prev = NULL;
        else
            list->tail = NULL;
    } else if (alloc == list->tail) {
        if ((list->tail = alloc->prev))
            list->tail->next = NULL;
        else
            list->head = NULL;
    } else {
        alloc->prev->next = alloc->next;
        alloc->next->prev = alloc->prev;
    }
}
