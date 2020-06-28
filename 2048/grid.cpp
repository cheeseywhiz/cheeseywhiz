#include <random>
#include <ncurses.h>
#include "grid.hpp"
using namespace std;

void
Grid::draw_lines(void) const
{
    /* example cell, with number
     * +------+
     * |      |
     * | 2048 |
     * |      |
     * +------+
     */
    for (unsigned row = 0; row <= height; ++row) {
        for (unsigned col = 0; col <= width; ++col) {
            move(static_cast<int>(row), static_cast<int>(col));
            const bool is_horiz_line = !(row % cell_height);
            const bool is_vertical_line = !(col % cell_width);

            // intersection?
            if (is_vertical_line && is_horiz_line) {
                // top row?
                if (!row) {
                    // left col?, right col?, middle col?, etc
                    if (!col)
                        addch(ACS_ULCORNER);
                    else if (col == width)
                        addch(ACS_URCORNER);
                    else
                        addch(ACS_TTEE);
                // bottom row?
                } else if (row == height) {
                    if (!col)
                        addch(ACS_LLCORNER);
                    else if (col == width)
                        addch(ACS_LRCORNER);
                    else
                        addch(ACS_BTEE);
                // middle row?
                } else {
                    if (!col) {
                        addch(ACS_LTEE);
                    } else if (col == width) {
                        addch(ACS_RTEE);
                    } else {
                        addch(ACS_PLUS);
                    }
                }
            } else if (is_vertical_line) {
                addch(ACS_VLINE);
            } else if (is_horiz_line) {
                addch(ACS_HLINE);
            }
        }
    }
}

void
Grid::generate_new_cell(void)
{
    unsigned num = uniform_int_distribution<unsigned>(0, get_n_empty() - 1)(mt);
    unsigned val = uniform_int_distribution<unsigned>(0, 1)(mt) ? 2 : 4;
    unsigned n_empty = 0;

    for (unsigned row = 0; row < n_rows; ++row) {
        for (unsigned col = 0; col < n_columns; ++col) {
            if (!grid[row][col]) {
                if (n_empty++ == num) {
                    set_cell(row, col, val);
                    break;
                }
            }
        }
    }
}

/* get the number of empty cells */
unsigned
Grid::get_n_empty(void) const
{
    unsigned n_empty = 0;

    for (unsigned row = 0; row < n_rows; ++row) {
        for (unsigned col = 0; col < n_columns; ++col) {
            if (!grid[row][col])
                ++n_empty;
        }
    }

    return n_empty;
}

void
Grid::set_cell(unsigned row, unsigned col, unsigned num)
{
    grid[row][col] = num;
    write_cell(row, col);
}

void
Grid::erase_cell(unsigned row, unsigned col)
{
    set_cell(row, col, 0);
    move(static_cast<int>(row * cell_height + 2),
         static_cast<int>(col * cell_width + 2));
    printw("%4s", "");
}

void
Grid::write_cell(unsigned row, unsigned col) const
{
    move(static_cast<int>(row * cell_height + 2),
         static_cast<int>(col * cell_width + 2));
    printw("%4d", grid[row][col]);
}
