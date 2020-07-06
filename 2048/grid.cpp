#include <cassert>
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

// draw all the cells in the grid to the terminal.
void
Grid::refresh(void) const
{
    for (unsigned row = 0; row < n_rows; ++row) {
        for (unsigned col = 0; col < n_columns; ++col) {
            move(static_cast<int>(row * cell_height) + 2,
                 static_cast<int>(col * cell_width) + 2);
            unsigned value;

            if ((value = grid[row][col]))
                printw("%4d", value);
            else
                printw("%4s", "");
        }
    }

    draw_score();
    refresh_win();
    refresh_game_over();
}

void
Grid::draw_score(void) const
{
    move(static_cast<int>(height) + 1, 0);
    clrtoeol();
    printw("score: %d", score);
}

void
Grid::refresh_win(void) const
{
    move(static_cast<int>(height) + 2, 0);

    if (has_won)
        printw("you win!");
    else
        clrtoeol();
}

void
Grid::refresh_game_over(void) const
{
    move(static_cast<int>(height) + 3, 0);

    if (!n_empty && check_game_over())
        printw("game over");
    else
        clrtoeol();
}

// move the cells and update the game as needed. returns if any cells
// actually moved.
bool
Grid::handle_key(int key)
{
    assert(key == KEY_UP || key == KEY_DOWN || key == KEY_LEFT
           || key == KEY_RIGHT);
    const auto& rows = normalize_rows(key);
    unsigned score_change = 0;
    bool did_move = false;

    for (const auto& row_ref : rows) {
        const auto& result = do_move(row_ref);
        score_change += result.score_change;
        if (result.did_move)
            did_move = true;
    }

    if (score_change) {
        score += score_change;
        draw_score();
    }

    if (did_move) {
        generate_new_cell();
        refresh_game_over();
    }

    return did_move;
}

// merge cells towards the front of the list. returns score change.
Grid::move_result
Grid::do_move(const CellReferencesT& cells)
{
    bool did_move = move_down(cells);
    // merge equal neighbors.
    unsigned score_change = 0;

    for (unsigned i = 0; i < cells.size() - 1; ++i) {
        unsigned i_val = grid[cells[i].first][cells[i].second];
        unsigned next_val = grid[cells[i + 1].first][cells[i + 1].second];
        // at the end of the row?
        if (!next_val)
            break;

        if (i_val == next_val) {
            unsigned new_val = i_val * 2;

            if (new_val == win_value) {
                has_won = true;
                refresh_win();
            }

            pop_cell(cells[i + 1].first, cells[i + 1].second);
            set_cell(cells[i].first, cells[i].second, new_val);
            score_change += new_val;
            ++n_empty;
            did_move = true;
        }
    }

    if (move_down(cells))
        did_move = true;
    return { did_move, score_change };
}

// move non-zero cells to front of list. returns if any cells were actually
// moved.
bool
Grid::move_down(const CellReferencesT& cells)
{
    unsigned end = 0;
    unsigned i = numeric_limits<unsigned>::max();
    bool did_move = false;

    while ((i = get_next_nonzero(cells, i)) < cells.size()) {
        unsigned value;

        if ((value = grid[cells[i].first][cells[i].second])) {
            if (i != end) {
                pop_cell(cells[i].first, cells[i].second);
                set_cell(cells[end].first, cells[end].second, value);
                did_move = true;
            }

            ++end;
        }
    }

    return did_move;
}

// advance i to the next non-zero cell
unsigned
Grid::get_next_nonzero(const CellReferencesT &cells, unsigned i)
{
    if (i == numeric_limits<unsigned>::max())
        i = 0;
    else
        ++i;

    for (; i < cells.size(); ++i) {
        if (grid[cells[i].first][cells[i].second])
            break;
    }

    return i;
}

vector<Grid::CellReferencesT>
Grid::normalize_rows(int key)
{
    vector<CellReferencesT> rows;
    bool forward = key == KEY_DOWN || key == KEY_RIGHT;

    // row-wise?
    if (key == KEY_UP || key == KEY_DOWN) {
        rows.reserve(n_columns);

        for (unsigned col = 0; col < n_columns; ++col) {
            CellReferencesT row_ref(n_rows);
            unsigned i = n_rows;
            unsigned row = forward ? 0 : n_rows - 1;

            while (row < n_rows) {
                row_ref[--i] = { row, col };

                if (forward)
                    ++row;
                else
                    --row;
            }

            rows.emplace_back(move(row_ref));
        }
    // column-wise?
    } else {
        rows.reserve(n_rows);

        for (unsigned row = 0; row < n_rows; ++row) {
            CellReferencesT row_ref(n_columns);
            unsigned i = n_columns;
            unsigned col = forward ? 0 : n_columns - 1;

            while (col < n_columns) {
                row_ref[--i] = { row, col };

                if (forward)
                    ++col;
                else
                    --col;
            }

            rows.emplace_back(move(row_ref));
        }
    }

    return rows;
}

// check if the game must end, when there is gridlock, where no two neighbors
// have an equal value.
// REQUIRES: n_empty == 0
bool
Grid::check_game_over(void) const
{
    // check row-wise
    for (const auto& row : grid) {
        unsigned prev = row.front();

        for (unsigned col = 1; col < n_columns; ++col) {
            if (row[col] == prev)
                return false;
            prev = row[col];
        }
    }

    // check column-wise
    for (unsigned col = 0; col < n_columns; ++col) {
        unsigned row = 0;
        unsigned prev = grid[row][col];

        while (++row < n_rows) {
            if (grid[row][col] == prev)
                return false;
            prev = grid[row][col];
        }
    }

    return true;
}

// populate an empty cell with either a 2 or a 4.
void
Grid::generate_new_cell(void)
{
    if (!n_empty)
        return;
    unsigned num = uniform_int_distribution<unsigned>(0, n_empty - 1)(mt);
    unsigned val = uniform_int_distribution<unsigned>(0, 1)(mt) ? 2 : 4;
    unsigned n_empty_tmp = 0;

    for (unsigned row = 0; row < n_rows; ++row) {
        for (unsigned col = 0; col < n_columns; ++col) {
            if (!grid[row][col]) {
                if (n_empty_tmp++ == num) {
                    set_cell(row, col, val);
                    --n_empty;
                    break;
                }
            }
        }
    }
}

void
Grid::set_cell(unsigned row, unsigned col, unsigned num)
{
    grid[row][col] = num;
    write_cell(row, col);
}

void
Grid::pop_cell(unsigned row, unsigned col)
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
