#include <unistd.h>
#include <ncurses.h>
#include "grid.hpp"
using namespace std;

static void init_ncurses(void);

int
main()
{
    init_ncurses();

#ifdef DEBUG
    // print the PID so that we can connect in another window with gdb
    printw(" %d", getpid());
    getch();
#endif

    Grid grid(4, 5);
    grid.draw_lines();

    // start game
    grid.generate_new_cell();
    grid.generate_new_cell();
    refresh();

    int c;

    while ((c = getch()) != ERR) {
        switch (c) {
        case KEY_LEFT:
            break;
        case KEY_RIGHT:
            break;
        case KEY_UP:
            break;
        case KEY_DOWN:
            break;
        case 'q':
            endwin();
            return 0;
        default:
            break;
        }

        refresh();
    }
}

static void
init_ncurses(void)
{
    initscr();
    cbreak();
    noecho();
    curs_set(0);
    keypad(stdscr, true);
}
