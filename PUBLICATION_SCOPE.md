# Publication Scope

## Included

- Independently implemented FastAPI service and SQLAlchemy data model.
- Synthetic-data generator and generic import/cleaning pipeline.
- Platform-neutral document parsing, local deterministic hybrid retrieval, heuristic reranking, and citations.
- Mock LLM provider and OpenAI-compatible provider interfaces.
- Operations report aggregation, Markdown export, tests, and Windows scripts.

## Excluded

- Employer or customer source code, data, documents, prompts, endpoints, and business rules.
- Patient data or any personally identifiable medical information.
- API keys, database credentials, model weights, adapters, checkpoints, and training outputs.
- Claims that the Demo implementation is a certified clinical decision system.

Demo data and the committed examples are synthetic. User-supplied knowledge documents remain local and are never part of this repository. Redis, Milvus, Function Calling, and LoRA training are not implemented here; the HTTP provider adapters exist but real provider calls have not been locally verified.
