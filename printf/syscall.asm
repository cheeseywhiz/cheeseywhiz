; https://the-linux-channel.the-toffee-project.org/index.php?page=5-tutorials-a-linux-system-call-in-c-without-a-standard-library
%include "sys-syscall.asm"

section .text
global _start, write, printf
extern main, printf_impl

_start:
    xor  rbp, rbp
    pop  rdi        ; first arg = argc
    mov  rsi, rsp   ; second arg = args
    and  rsp, -16
    call main
    mov  rdi, rax   ; exit code = main return value
    call exit

write:
    mov rax, SYS_write
    syscall
    ret

exit:
    mov rax, SYS_exit
    syscall

printf:
    pop  rax         ; caller's rip
    ; now we're in the caller's stack frame
    ; now these are contiguous with the rest of the varargs on the stack
    push r9
    push r8
    push rcx
    push rdx
    push rsi
    mov  rsi, rsp   ; second arg = varargs
    push rax        ; save
    call printf_impl
    pop  rax        ; restore
    add  rsp, 40    ; dealloc printf_impl stack args
    push rax        ; stack frame back to normal
    ret
