%include 'lib.asm'

section .text
global  _start

; void _start(int argc, char *argv[]);
_start:
    mov     ecx, 0      ; counter
.loop:                  ; do {
    inc     ecx         ;   ++ecx
    mov     eax, ecx    ;          ecx
    call    putint      ;   putint(|  );
    cmp     ecx, 10     ; }
    jne     .loop       ; while (ecx != 10);
    mov     eax, 0      ;      0
    call    exit        ; exit(|);
