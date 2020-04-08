; https://the-linux-channel.the-toffee-project.org/index.php?page=5-tutorials-a-linux-system-call-in-c-without-a-standard-library
%include "sys-syscall.asm"

section .text
global _start, fprintf, printf, write, exit, mmap, munmap
extern main, fprintf_impl, printf_impl, check_alloc

_start:
    xor  rbp, rbp
    pop  rdi        ; first arg = argc
    mov  rsi, rsp   ; second arg = args
    and  rsp, -16
    call main
    mov  rdi, rax
    call exit

write:
    mov rax, SYS_write
    syscall
    ret

exit:
    call check_alloc
    mov rdi, rax
    mov rax, SYS_exit
    syscall

mmap:
    mov rax, SYS_mmap
    mov r10, rcx
    syscall
    ret

munmap:
    mov rax, SYS_munmap
    syscall
    ret

fprintf:
    pop  rax        ; caller's rip
    ; now we're in the caller's stack frame
    ; now these are contiguous with the rest of the varargs on the stack
    push r9
    push r8
    push rcx
    push rdx
    ; pass rdi and rsi to impl
    mov  rdx, rsp   ; third arg = varargs
    push rax        ; save
    call fprintf_impl
    pop  rax        ; restore
    add  rsp, 32    ; dealloc printf_impl stack args
    push rax        ; stack frame back to normal
    ret

printf:
    pop  rax        ; caller's rip
    ; now we're in the caller's stack frame
    ; now these are contiguous with the rest of the varargs on the stack
    push r9
    push r8
    push rcx
    push rdx
    push rsi
    ; pass rdi to impl
    mov  rsi, rsp   ; second arg = varargs
    push rax        ; save
    call printf_impl
    pop  rax        ; restore
    add  rsp, 40    ; dealloc printf_impl stack args
    push rax        ; stack frame back to normal
    ret
