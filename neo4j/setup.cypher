# Example Neo4J setup script
# Run this in Neo4J Browser or via Python utilities

CREATE CONSTRAINT ON (n:Person) ASSERT n.name IS UNIQUE;

CREATE (a:Person {name: 'Alice'})
CREATE (b:Person {name: 'Bob'})
CREATE (a)-[:KNOWS]->(b);
