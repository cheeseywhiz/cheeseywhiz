CFLAGS += -ansi -Wall -Werror -pedantic -nostdlib -fno-builtin
LD := ld
AS := nasm
ASFLAGS += -f elf64

%.o: %.asm
	$(AS) $(ASFLAGS) -o $@ $<

printf: main.o printf.o syscall.o
	$(LD) $(LDFLAGS) -o $@ $^

sys-syscall.asm: /usr/include/asm/unistd_64.h
	grep "^#define __NR_"  $< \
		| sed -e "s/__NR/SYS/" -e "s/^#/%/" \
		> $@

.PHONY: all release debug clean deps

all: printf

release: CFLAGS += -O3
release: all

debug: CFLAGS += -g -Og
debug: ASFLAGS += -gdwarf
debug: all

clean:
	rm -rfv vgcore.* .clangd *.o *.plist \
		printf sys-syscall.asm

deps:
	touch sys-syscall.asm
	nasm -MG syscall.asm -o syscall.o | tee -a Makefile
	rm sys-syscall.asm
	gcc -MM *.c | tee -a Makefile

syscall.o : syscall.asm sys-syscall.asm

main.o: main.c printf.h types.h syscall.h
printf.o: printf.c printf.h types.h syscall.h
