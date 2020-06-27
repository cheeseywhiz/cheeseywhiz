#include <ncurses.h>

int main()
{
    initscr();
    printw("hello world");
    refresh();
    getch();
    endwin();
}
