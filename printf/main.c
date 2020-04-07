#include "printf.h"
#include "syscall.h"

int main() {
    write(STDOUT, "hello world\n", 12);
    put_string("goodbye world");
    put_char('\n');
    return 0;
}
