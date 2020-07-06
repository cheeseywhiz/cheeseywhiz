/* The grid is composed of numbers and empty cells. Arrow keys cause the numbers
 * to fall and merge. */
#pragma once
#include <vector>
#include <utility>
#include <limits>
#include <random>
using std::vector;
using std::pair;
using std::numeric_limits;

class Grid {
public:
    Grid()
        : n_rows(0), n_columns(0), height(0), width(0), n_empty(0), score(0),
          has_won(false)
    {
    }

    // create a new 2048 game grid and render it to the terminal.
    Grid(unsigned n_rows_in, unsigned n_columns_in)
        : n_rows(n_rows_in), n_columns(n_columns_in),
          height(n_rows * cell_height), width(n_columns * cell_width),
          n_empty(n_rows_in * n_columns_in), score(0), has_won(false),
          grid(n_rows_in, vector<unsigned>(n_columns_in, 0))
    {
        mt.seed(1);
        draw_lines();
        draw_score();
        generate_new_cell();
        generate_new_cell();
    }


    // draw all the cells in the grid to the terminal.
    void refresh(void) const;

    // move the cells and update the game as needed. returns if any cells
    // actually moved.
    bool handle_key(int key);

private:
    void draw_lines(void) const;
    void draw_score(void) const;
    void refresh_win(void) const;
    void refresh_game_over(void) const;

    using CellReferencesT = vector<pair<unsigned, unsigned>>;

    struct move_result {
        bool did_move;
        unsigned score_change;
    };

    move_result do_move(const CellReferencesT&);
    bool move_down(const CellReferencesT&);
    unsigned get_next_nonzero(const CellReferencesT&,
                              unsigned=numeric_limits<unsigned>::max());
    vector<CellReferencesT> normalize_rows(int);
    bool check_game_over(void) const;

    void generate_new_cell(void);

    void set_cell(unsigned row, unsigned col, unsigned num);
    void pop_cell(unsigned row, unsigned col);
    void write_cell(unsigned row, unsigned col) const;

    unsigned n_rows;
    unsigned n_columns;
    unsigned height;
    unsigned width;
    unsigned n_empty;
    unsigned score;
    bool has_won;
    vector<vector<unsigned>> grid;
    std::mt19937 mt;

    static const unsigned cell_width = 7;
    static const unsigned cell_height = 4;
    static const unsigned win_value = 2048;
};
