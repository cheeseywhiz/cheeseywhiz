#include <ncurses.h>

static int n_columns = 4;
static int n_rows = 5;

static void init_ncurses(void);
static void print_grid(void);

int
main()
{
    init_ncurses();
    print_grid();
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
            goto end;
        default:
            break;
        }

        refresh();
    }

end:
    endwin();
}

static void
init_ncurses(void)
{
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, true);
}

static void
print_grid(void)
{
    /* example cell, with number
     * +------+
     * |      |
     * | 2048 |
     * |      |
     * +------+
     */
    int cell_width = 8;
    int cell_height = 5;
    int grid_width = n_rows * cell_width;
    int grid_height = n_columns * cell_height;

    // draw horizontal lines
    for (int row = 0; row <= grid_height; row += cell_height) {
        for (int col = 0; col < grid_width; ++col)
            mvaddch(row, col, ACS_HLINE);
    }

    // draw vertical lines
    for (int col = 0; col <= grid_width; col += cell_width) {
        for (int row = 0; row < grid_height; ++row)
            mvaddch(row, col, ACS_VLINE);
    }

    // draw intersections
    for (int row = 0; row <= grid_height; row += cell_height) {
        for (int col = 0; col <= grid_width; col += cell_width) {
            move(row, col);

            if (!row) {
                // top row
                if (!col)
                    addch(ACS_ULCORNER);
                else if (col == grid_width)
                    addch(ACS_URCORNER);
                else
                    addch(ACS_TTEE);
            } else if (row == grid_height) {
                // bottom row
                if (!col)
                    addch(ACS_LLCORNER);
                else if (col == grid_width)
                    addch(ACS_LRCORNER);
                else
                    addch(ACS_BTEE);
            // middle row
            } else if (!col) {
                addch(ACS_LTEE);
            } else if (col == grid_width) {
                addch(ACS_RTEE);
            } else {
                addch(ACS_PLUS);
            }
        }
    }
}
