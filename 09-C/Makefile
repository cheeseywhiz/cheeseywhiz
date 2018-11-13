CFLAGS+=-Wall -Wextra -std=gnu11 -fPIC
CFLAGS+=-Og -g3 -Wno-unused-parameter
CFLAGS+=-D_GNU_SOURCE

all: immunization

clean:
	rm -rf immunization

test:
	echo mum | valgrind -v --leak-check=full --track-origins=yes --show-leak-kinds=all ./immunization

.PHONY: all clean test

immunization: immunization.c immunization.h
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)
