# OpenAPI Client Generator

A Python-based OpenAPI client generator that can generate client code from OpenAPI specifications.

## Features

- Parse OpenAPI 3.x specifications
- Generate Python client code
- Support for various authentication methods
- Request/response validation
- Type hints and documentation generation
- Fast dependency management with `uv`

## Installation

1. Clone the repository
2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

1. Start the service:
```bash
uvicorn src.openapi_consumer.main:app --reload
```

2. Use the API endpoints:
- POST `/generate`: Generate client code from OpenAPI specification
- GET `/validate`: Validate OpenAPI specification

## API Documentation

Once the service is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
.
├── src/
│   └── openapi_consumer/
│       ├── __init__.py
│       ├── main.py
│       ├── generator/
│       │   ├── __init__.py
│       │   └── client_generator.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py
│       └── templates/
│           └── client.py.jinja2
├── scripts/
│   ├── README.md
│   └── update_dependencies.py
└── tests/
    └── test_generator.py
```

## Development

### Managing Dependencies

The project includes a dependency management script that uses `uv` for fast package operations. To update dependencies:

1. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Run the dependency update script:
```bash
./scripts/update_dependencies.py
```

The script will:
- Show current vs latest versions of all packages
- Optionally update requirements.txt with latest versions
- Use `uv` for fast dependency resolution

For more details about the dependency management script, see [scripts/README.md](scripts/README.md).
