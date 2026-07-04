# Neo4j Driver Injection Update

This update replaces custom session-factory injection with direct `neo4j.Driver` injection.

## Preferred constructor

```python
from neo4j import GraphDatabase
from diagnostic_pipeline_production.graph_repository import Neo4jGraphRepository


driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "password"),
)
repo = Neo4jGraphRepository(driver=driver, database="neo4j")
```

## Why this is preferred

- It follows the official Neo4j Python driver object model.
- It keeps connection-pool management inside the shared driver object.
- It simplifies application wiring because repositories open sessions directly from the injected driver.
- It avoids extra indirection for code that already owns the driver lifecycle.

## Files included

- `graph_repository.py`: updated repository implementation using direct driver injection.
- `neo4j_driver_integration_example.py`: example of wiring `DiagnosticPipeline` with a real `neo4j.Driver`.
