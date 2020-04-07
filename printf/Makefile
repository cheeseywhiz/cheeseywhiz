CFLAGS += -ansi -Wall -Werror -pedantic -nostdlib -fno-builtin
LD := ld
AS := nasm
ASFLAGS += -f elf64

%.o: %.asm
	$(AS) $(ASFLAGS) -o $@ $<

printf: main.o printf.o syscall.o write.o
	$(LD) $(LDFLAGS) -o $@ $^

.PHONY: all release debug clean

all: printf

release: CFLAGS += -O3
release: all

debug: CFLAGS += -g -Og
debug: ASFLAGS += -gdwarf
debug: all

clean:
	rm -rfv vgcore.* .clangd *.o *.plist \
		printf
