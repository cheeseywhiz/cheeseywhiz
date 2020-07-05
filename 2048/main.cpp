#include <unistd.h>
#include <ncurses.h>
#include "grid.hpp"
using namespace std;

static void init_ncurses(void);

int
main()
{
    init_ncurses();
    Grid grid(4, 4), alt_grid;
    grid.draw_lines();
    grid.draw_score();
    grid.generate_new_cell();
    grid.generate_new_cell();
    refresh();
    int c;

    while ((c = getch()) != ERR) {
        switch (c) {
        case ' ':
            swap(alt_grid, grid);
            grid.refresh();
            refresh();
            break;
        case KEY_LEFT:
        case KEY_RIGHT:
        case KEY_UP:
        case KEY_DOWN:
            alt_grid = grid;
            grid.handle_key(c);
            refresh();
            break;
        case 'q':
            endwin();
            return 0;
        }
    }

    return 1;
}

static void
init_ncurses(void)
{
    initscr();
    cbreak();
    noecho();
    curs_set(0);
    keypad(stdscr, true);

#ifdef DEBUG
    // print the PID so that we can connect in another window with gdb
    printw(" %d", getpid());
    getch();
#endif
}
