section .text
global _start, syscall, printf
extern main
extern printf_impl

_start:
    xor  rbp, rbp
    pop  rdi        ; first arg = argc
    mov  rsi, rsp   ; second arg = args
    and  rsp, -16
    call main
    mov  rdi, rax   ; exit code = main return value
    mov  rax, 60    ; exit
    syscall

syscall:
    mov rax, rdi
    mov rdi, rsi
    mov rsi, rdx
    mov rdx, rcx
    mov r10, r8
    mov r8,  r9
    syscall
    ret
