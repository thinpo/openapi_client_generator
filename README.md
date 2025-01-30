# OpenAPI Client Generator

A Python-based OpenAPI client generator that creates type-safe, async Python clients from OpenAPI specifications.

## Features

- ✨ Generate fully typed Python clients from OpenAPI 3.x specifications
- 🔄 Async/await support with aiohttp
- 🛡️ Type safety with Pydantic models
- 🧩 Smart handling of circular dependencies
- 📝 Proper model inheritance and composition
- 🔍 Comprehensive query parameter handling
- 🚨 Built-in error handling with custom exceptions
- 🔐 Support for various authentication methods
- 📦 Automatic dependency management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/thinpo/openapi_client_generator.git
cd openapi_client_generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the service:
```bash
uvicorn src.openapi_consumer.main:app --reload
```

2. Generate a client from your OpenAPI spec:
```bash
curl -X POST http://localhost:8000/generate \
  -F "spec_file=@your_api.yaml" \
  -F "package_name=your_client"
```

3. Use the generated client:
```python
from your_client import YourAPIClient

async with YourAPIClient("https://api.example.com", api_key="your-key") as client:
    # List resources with query parameters
    items = await client.listItems(
        category=["electronics"],
        price_range={"min": 0, "max": 1000},
        sort="price_asc",
        page=1
    )
    
    # Create a resource
    new_item = await client.createItem(
        ItemCreate(name="Test Item", price=99.99)
    )
```

## Project Structure

```
.
├── src/
│   └── openapi_consumer/
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       ├── generator/
│       │   ├── __init__.py
│       │   └── client_generator.py  # Client generation logic
│       └── models/
│           ├── __init__.py
│           └── schemas.py       # Request/Response models
├── scripts/
│   ├── README.md
│   └── update_dependencies.py   # Dependency management script
└── tests/
    └── test_generator.py
```

## Generated Client Features

The generated client includes:

- **Type-Safe Models**: All models are generated as Pydantic classes
- **Smart Query Parameters**: Handles complex query parameters (arrays, objects) correctly
- **Error Handling**: Custom ApiError class with status code and error details
- **Resource Management**: Proper cleanup with async context manager
- **Authentication**: Support for API key, Bearer token, and OAuth2
- **Forward References**: Handles circular dependencies between models
- **Model Inheritance**: Proper handling of allOf, oneOf, anyOf schemas

## Development

### Managing Dependencies

Use the provided dependency management script to check and update package versions:

```bash
./scripts/update_dependencies.py
```

The script will:
- Show current vs latest versions of all packages
- Update requirements.txt with latest versions if desired
- Handle version conflicts and dependencies

### API Documentation

When the service is running, access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
