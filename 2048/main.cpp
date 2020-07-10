#include <stack>
#include <iostream>
#include <cassert>
#include <unistd.h>
#include <getopt.h>
#include <ncurses.h>
#include "grid.hpp"
using namespace std;

static void print_help(void);
static int run_2048(void);

// args
static const char *prgm;
static int width = 4, height = 4;

int
main(int argc, char *argv[])
{
    prgm = argv[0];
    opterr = true;
    int opt, opt_i = 0;
    option opts[] = {
        { "help", no_argument, nullptr, 'h' },
        { "width", required_argument, nullptr, 'w' },
        { "height", required_argument, nullptr, 'H' },
        { nullptr, 0, nullptr, '\0' },
    };

    while ((opt = getopt_long(argc, argv, "hw:H:", opts, &opt_i)) != -1) {
        switch (opt) {
        case 'w':
            width = atoi(optarg);

            if (width < 3) {
                cout << prgm << ": invalid width -- " << width << endl;
                print_help();
                return 1;
            }

            break;
        case 'H':
            height = atoi(optarg);

            if (height < 3) {
                cout << prgm << ": invalid height -- " << height << endl;
                print_help();
                return 1;
            }

            break;
        case 'h':
            print_help();
            return 0;
        default:
            print_help();
            return 1;
        }
    }

    return run_2048();
}

static void
print_help()
{
    cout << prgm << " --help | [--width NUM] [--height NUM]" << endl << endl;
    cout << "play https://2048.io" << endl << endl;
    cout << "arrow keys to move the numbers around." << endl;
    cout << "j to move back in history." << endl;
    cout << "k to move forward in history." << endl;
    cout << "q to quit." << endl << endl;
    cout << "-h,--help" << endl;
    cout << "\t\tprint this help information" << endl;
    cout << "-w,--width NUM" << endl;
    cout << "\t\tthe width of the game grid" << endl;
    cout << "-H,--height NUM" << endl;
    cout << "\t\tthe height of the game grid" << endl;
}

static void init_ncurses(void);

static int
run_2048(void)
{
    init_ncurses();
    stack<Grid> history, backtrace;
    history.emplace(height, width);
    refresh();
    int c;

    while ((c = getch()) != ERR) {
        switch (c) {
        case 'k': {
            // forward through history
            if (backtrace.empty())
                break;
            Grid current = move(backtrace.top());
            backtrace.pop();
            history.push(move(current));
            history.top().refresh();
            refresh();
            break; }
        case 'j': {
            // backwards through history
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
