# Third-party dependencies

This project uses packages from their official distributions. No third-party project source tree is copied into this repository.

| Dependency | Primary purpose | License |
| --- | --- | --- |
| FastAPI | REST API framework | MIT |
| Uvicorn | ASGI server | BSD-3-Clause |
| Pydantic / pydantic-settings | Validation and settings | MIT |
| SQLAlchemy | Persistence layer | MIT |
| python-multipart | Multipart uploads | Apache-2.0 |
| HTTPX | Provider HTTP client | BSD-3-Clause |
| Faker | Synthetic data generation | MIT |
| openpyxl | XLSX import | MIT |
| python-docx | DOCX parsing | MIT |
| pypdf | PDF text extraction | BSD-3-Clause |
| pytest / pytest-cov / Ruff | Tests, coverage and static checks | MIT |

The optional `full` extra declares packages for future integration work. Installing them does not enable a Redis or Milvus runtime adapter:

| Optional dependency | Declared role | License reference |
| --- | --- | --- |
| PyMySQL | SQLAlchemy MySQL driver | [MIT](https://pypi.org/project/PyMySQL/) |
| redis | Reserved cache integration | [MIT](https://pypi.org/project/redis/) |
| pymilvus | Reserved vector-store integration | [Apache-2.0](https://pypi.org/project/pymilvus/) |
| openai | Optional compatible API SDK | [Apache-2.0](https://pypi.org/project/openai/) |

Package names, versions, and upstream metadata are declared in `pyproject.toml`. Redistribution must comply with each dependency's upstream license.
