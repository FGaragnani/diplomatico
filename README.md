
# Diplomatico

A solver for the *Diplomatico* puzzle, using Neo4J and Python.

---

## Structure
- `src/` - Main application code
- `doc/` - LaTeX essay


## Setup
1. Install Python dependencies (see requirements.txt):
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure Neo4J is running locally or remotely. **Tested with Neo4J 5.x and APOC 5.x** (see [Neo4J Download](https://neo4j.com/download/) and [APOC Docs](https://neo4j.com/labs/apoc/)).
3. Configure connection settings in `src/config.py` (do not commit real passwords!):
   ```python
   # Configuration for Neo4J connection
   NEO4J_URI = "bolt://localhost:7687"
   NEO4J_USER = "neo4j"
   NEO4J_PASSWORD = "password"  # Change to your actual password
   ```
   You may copy `src/config.py` to `src/config.example.py` for sharing safe defaults.

---

## The Game

*Diplomatico* is a strategic board game played on a grid. The objective is to fill the board with numbers from 1 to N (where N is the total number of squares) such that each number is placed in a square that is a valid move away from the previous number, following specific movement rules - specifically, each move must skip either two squares horizontally or vertically, or one square diagonally.

An example of a filled $5 \times 5$ grid:
|17| 9 | 2 | 16 | 8 |
|---|---|---|---|---|
| 4 | 14 | 19 | 5 | 13 |
| 1 | 22 | 25 | 10 | 21 |
| 18 | 6 | 3 | 15 | 7 |
| 24 | 11 | 20 | 23 | 12 |

---

## Testing & Batch Usage

To run a suite of experiments and log results, use the provided batch script:

```powershell
test.bat
```

This will execute multiple runs of `main.py` with various parameters and append results to `test_output.txt`.

To verify your installation, try:

```powershell
python main.py --r 5 --c 5 --query_type PYTHON --n 1
```

---

## main.py — Solution Finder CLI

`main.py` is the main command-line interface for generating and analyzing solution spaces for the game Diplomatico using Neo4J and Python. It supports multiple query strategies, board sizes, and optional start/end node anchoring.

### Features

- **Board Graph Creation:** Automatically builds a Neo4J graph representing the game board, with nodes for squares and edges for valid moves.
- **Multiple Query Strategies:** Supports four solution search methods:
   - `RAW`: Expands all possible paths of the required length, then filters for Hamiltonian paths.
   - `CONSTRUCTIVE`: Builds paths step-by-step, pruning non-Hamiltonian candidates early.
   - `APOC`: Uses Neo4J's APOC library for efficient path expansion.
   - `PYTHON`: Uses a pure Python backtracking solver.
- **Customizable Parameters:** Specify board size, query type, number of solutions, starting/ending nodes, and number of timing repetitions.
- **Performance Measurement:** Optionally runs multiple trials and reports average solution time.
- **Result Display:** Prints each solution path as a board visualization.

### Usage

Run from the command line:

```powershell
python main.py --r <rows> --c <cols> --query_type <RAW|CONSTRUCTIVE|APOC|PYTHON> [--n <num_paths>] [--starting_node <row,col>] [--ending_node <row,col>] [--t <trials>]
```

#### Arguments

- `--r`: Number of rows (default: 5)
- `--c`: Number of columns (default: 5)
- `--query_type`: Solution search strategy (`RAW`, `CONSTRUCTIVE`, `APOC`, `PYTHON`)
- `--n` *(optional)*: Number of solution paths to return
- `--starting_node` *(optional)*: Starting node as `row,col`
- `--ending_node` *(optional)*: Ending node as `row,col`
- `--t` *(optional)*: Number of times to repeat and average timing

#### Example

```powershell
python main.py --r 7 --c 7 --query_type APOC --n 1 --starting_node 0,0 --ending_node 6,6 --t 5
```


### Notes

- For large boards, `RAW` queries may be slow or infeasible.
- Start/end node anchoring is supported for all query types.
- Even for the `PYTHON` method, a Neo4J connection is required to build the board graph.

---

## Contributing

Contributions, bug reports, and feature requests are welcome! Please open an issue or submit a pull request. For major changes, please discuss them in an issue first.

---

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

---


## Essay

For a detailed analysis of the game and of the implementations, refer to the [essay](./doc/essay.pdf) in the `doc/` directory.