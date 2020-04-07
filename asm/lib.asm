; void exit(int eax);
exit:
    mov     ebx, eax    ;      eax
    mov     eax, 0x01   ; exit |
    int     0x80        ; |   (|  );

; void putint(int eax);
putint:
    push    eax             ; preserve
    push    ecx
    push    edx
    push    esi
    mov     ecx, 0          ; count string size
.div_loop:                  ; do {
    inc     ecx             ;   ++ecx;
    xor     edx, edx        ;   edx = 0;
    mov     esi, 10         ;          10              10
    idiv    esi             ;   eax /= | ; edx = eax % | ;
    add     edx, '0'        ;   edx += '0';
    push    edx             ;   build stack string
    cmp     eax, 0          ; }
    jnz     .div_loop       ; while (eax);
.print_loop:                ; do {
    dec     ecx             ;   --ecx;
    pop     eax             ;           eax
    call    putchar         ;   putchar(|  );
    cmp     ecx, 0          ; }
    jnz     .print_loop     ; while (ecx);
    mov     eax, 0x0a       ;         '\n'
    call    putchar         ; putchar(|   );
    pop     esi             ; preserve
    pop     edx
    pop     ecx
    pop     eax
    ret

; void puts(char *const eax);
puts:
    push    eax             ; preserve
    call    print           ; print(eax);
    mov     eax, 0x0a       ;         '\n'
    call    putchar         ; putchar(|   );
    pop     eax             ; preserve
    ret

; void putchar(char eax);
putchar:
    push    edx         ; preserve
    push    ecx
    push    ebx
    push    eax
    mov     edx, 1      ;                     1
    mov     ecx, esp    ;               &eax  |
    mov     ebx, 1      ;       stdout  |     |
    mov     eax, 0x04   ; write |       |     |
    int     0x80        ; |    (|     , |   , |);
    pop     eax         ; preserve
    pop     ebx
    pop     ecx
    pop     edx
    ret

; void print(char *const eax);
print:
    push    edx         ; preserve
    push    ecx
    push    ebx
    push    eax
    push    eax         ; save
    call    strlen      ;                    strlen(eax)
    mov     edx, eax    ;                    |
    pop     eax         ; restore       eax  |
    mov     ecx, eax    ;               |    |
    mov     ebx, 1      ;       stdout  |    |
    mov     eax, 0x04   ; write |       |    |
    int     0x80        ; |    (      , |  , |          );
    pop     eax         ; preserve
    pop     ebx
    pop     ecx
    pop     edx
    ret

; size_t (*)(char *const eax);
strlen:
    push    ebx             ; preserve
    mov     ebx, eax        ; ebx = eax;
    jmp     .while
.loop:                      ; do {
    inc eax                 ;   ++eax;
.while:
    cmp     byte [eax], 0   ; }
    jnz     .loop           ; while (eax);
    sub     eax, ebx        ; return eax - ebx;
    pop     ebx             ; preserve
    ret
