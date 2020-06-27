%include 'lib.asm'

section .text
global  _start

; void _start(int argc, char *argv[]);
_start:
    mov     eax, 90
    mov     ebx, 9
    mul     ebx         ; eax = 90 * 9;
    call    putint
    mov     eax, 0      ;      0
    call    exit        ; exit(|);
