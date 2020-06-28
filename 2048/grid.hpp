/* The grid is composed of numbers and empty cells. Arrow keys cause the numbers
 * to fall and merge. */
#pragma once
#include <vector>
#include <random>
using std::vector;

class Grid {
public:
    Grid(unsigned n_rows_in, unsigned n_columns_in)
        : n_rows(n_rows_in), n_columns(n_columns_in),
          height(n_rows * cell_height), width(n_columns * cell_width),
          grid(n_rows_in, vector<unsigned>(n_columns_in, 0))
    {
        mt.seed(0);
    }

    void draw_lines(void) const;
    void generate_new_cell(void);

private:
    unsigned get_n_empty(void) const;
    void set_cell(unsigned row, unsigned col, unsigned num);
    void erase_cell(unsigned row, unsigned col);
    void write_cell(unsigned row, unsigned col) const;

    unsigned n_rows;
    unsigned n_columns;
    unsigned height;
    unsigned width;
    static const unsigned cell_width = 7;
    static const unsigned cell_height = 4;
    vector<vector<unsigned>> grid;

    std::mt19937 mt;
};
