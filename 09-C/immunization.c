#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "immunization.h"

#define LOG_ERRNO(function) fprintf(stderr, "%s: %s\n", function, strerror(errno))

char* read_file(char *path) {
        struct stat st;

        if (stat(path, &st)) {
                LOG_ERRNO("stat");
                return NULL;
        }

        size_t buffer_size = st.st_size + 1;
        char *buffer = calloc(buffer_size, 1);
        int fd = open(path, O_RDONLY);

        if (fd == -1) {
                LOG_ERRNO("open");
                free(buffer);
                return NULL;
        }

        if (read(fd, buffer, buffer_size) < 0) {
                LOG_ERRNO("read");
                free(buffer);
                close(fd);
                return NULL;
        }

        close(fd);
        return buffer;
}

#define HANDLE_SEP() \
        contents[ptr] = '\0'; \
        printf("%d %d %d %s\n", row_n, col_n, ptr, contents + current_word); \
        current_word = ptr + 1; \
        col_n++

int read_csv(char *path) {
        char *contents = read_file(path);

        if (!contents) {
                return 1;
        }

        int rows = 1;
        int cols = 0;
        int ptr;
        for (ptr = 0; contents[ptr] != '\n'; ptr++) if (contents[ptr] == ',') rows++;
        for (ptr = 0; contents[ptr] != '\0'; ptr++) if (contents[ptr] == '\n') cols++;

        int current_word = 0;
        int row_n = 0;
        int col_n;

        for (ptr = 0; contents[ptr] != '\0'; ptr++) {
                printf("before\n");
                col_n = 0;

                for (;; ptr++) {
                        if (contents[ptr] == '\n') {
                                HANDLE_SEP();
                                break;
                        } else if (contents[ptr] == ',') {
                                HANDLE_SEP();
                        }
                }

                row_n++;
                printf("after\n");
        }

        free(contents);
        return 0;
}

int main(int argc, char *argv[]) {
        read_csv("immunization.csv");
        return 0;
}
