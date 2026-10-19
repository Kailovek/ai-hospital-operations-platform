# Third-party dependencies

This project uses packages through Python dependency management. The following table credits their upstream projects and licenses.

| Dependency | Primary purpose | License |
| --- | --- | --- |
| FastAPI | REST API framework | MIT |
| Uvicorn | ASGI server | BSD-3-Clause |
| Pydantic / pydantic-settings | Validation and settings | MIT |
| SQLAlchemy | Persistence layer | MIT |
| python-multipart | Multipart uploads | Apache-2.0 |
| HTTPX | Provider HTTP client | BSD-3-Clause |
| Faker | Data generation | MIT |
| openpyxl | XLSX import | MIT |
| python-docx | DOCX parsing | MIT |
| pypdf | PDF text extraction | BSD-3-Clause |
| pytest / pytest-cov / Ruff | Tests, coverage and static checks | MIT |

The optional `full` dependency group contains the following client libraries:

| Optional dependency | Declared role | License reference |
| --- | --- | --- |
| PyMySQL | SQLAlchemy MySQL driver | [MIT](https://pypi.org/project/PyMySQL/) |
| redis | Cache client library | [MIT](https://pypi.org/project/redis/) |
| pymilvus | Vector-store client library | [Apache-2.0](https://pypi.org/project/pymilvus/) |
| openai | Optional compatible API SDK | [Apache-2.0](https://pypi.org/project/openai/) |

Package names, versions, and upstream metadata are declared in `pyproject.toml`. Redistribution must comply with each dependency's upstream license.
