# Diplomatico Neo4J Python Project

This project integrates Python with Neo4J for graph database operations. 

## Structure
- `src/` - Python logic and main application code
- `neo4j/` - Neo4J scripts and utility functions
- `doc/` - LaTeX essay and documentation

## Setup
1. Install Python dependencies (see requirements.txt)
2. Ensure Neo4J is running locally or remotely
3. Configure connection settings in `src/config.py`:
   ```
   # Configuration for Neo4J connection
   NEO4J_URI = "bolt://localhost:7687"
   NEO4J_USER = "neo4j"
   NEO4J_PASSWORD = "password"  # Change to your actual password
   ```

## Usage
- Run Python scripts in `src/` to interact with Neo4J
- Use scripts in `neo4j/` for database setup and utilities
- Write documentation in `doc/`

---