#include <unistd.h>
#include <ncurses.h>
#include <stack>
#include <cassert>
#include "grid.hpp"
using namespace std;

static void init_ncurses(void);

int
main()
{
    init_ncurses();
    stack<Grid> history, backtrace;
    Grid first(4, 4);
    first.draw_lines();
    first.draw_score();
    first.generate_new_cell();
    first.generate_new_cell();
    history.push(move(first));
    refresh();
    int c;

    while ((c = getch()) != ERR) {
        switch (c) {
        case 'k': {
            // ascend history
            if (backtrace.empty())
                break;
            Grid current = move(backtrace.top());
            backtrace.pop();
            history.push(move(current));
            history.top().refresh();
            refresh();
            break; }
        case 'j': {
            // descend history
            if (history.size() <= 1)
                break;
            Grid current = move(history.top());
            history.pop();
            backtrace.push(move(current));
            history.top().refresh();
            refresh();
            break; }
        case KEY_LEFT:
        case KEY_RIGHT:
        case KEY_UP:
        case KEY_DOWN: {
            assert(history.size());
            Grid new_grid(history.top());

            if (new_grid.handle_key(c)) {
                history.push(move(new_grid));
                while (backtrace.size())
                    backtrace.pop();
            }

            refresh();
            break; }
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
    // print the PID so that we can connect in another terminal with gdb
    printw(" %d", getpid());
    getch();
#endif
}
