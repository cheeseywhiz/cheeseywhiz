section .text
global _start, syscall, printf
extern main, printf_impl

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

printf:
    pop  rax         ; caller's rip
    ; now we're in the caller's stack frame
    ; these are now contiguous with the rest of the stack varargs
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
