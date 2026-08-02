### Acceptance Criteria Checklist
- [x] `KnowledgeGraph` uses `networkx.DiGraph`.
- [x] `KnowledgeGraph` is instantiated by `ExecutionEngine`.
- [x] `validate_methodology` returns violations for unsupported claims.
- [x] `validation_rules/rules.jsonld` conditions are parsed and evaluated.
- [x] `ontologies/methodology.jsonld` is loaded in `populate_knowledge_graph.py`.
- [x] `ExecutionEngine` accepts `knowledge_graph` parameter.

### Verification Output
- Automated tests pass.
- `ExecutionEngine` uses `KnowledgeGraph` during execution to emit `KNOWLEDGE_VIOLATION` events.
