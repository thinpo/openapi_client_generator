# Python Dependency Manager

A fast and efficient Python dependency management script that uses `uv` to check and update package versions.

## Features

- 🚀 Uses `uv` for fast dependency resolution
- 📊 Shows comparison between current and latest package versions
- 🔄 Automatically updates requirements.txt with latest versions
- ✅ Case-insensitive package name matching
- 🛡️ Error handling for missing packages and network issues
- 💡 Interactive prompts for safe updates

## Prerequisites

- Python 3.x
- `uv` package manager

If you don't have `uv` installed, you can install it with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Usage

1. Make sure you're in the project directory that contains your `requirements.txt`

2. Run the script:
```bash
./update_dependencies.py
```

3. The script will:
   - Check if `uv` is installed
   - Display current and latest versions of all packages
   - Ask if you want to update requirements.txt
   - If yes, update all dependencies to their latest versions

Example output:
```
Checking current dependencies...

Current vs Latest versions:
------------------------------------------------------------
Package                         Current         Latest         
------------------------------------------------------------
fastapi                        0.104.0         0.109.2       
uvicorn                        0.24.0          0.27.1        
pydantic                       2.4.2           2.6.1         
...

Would you like to update requirements.txt with latest versions? (y/n):
```

## How It Works

1. **Version Detection**:
   - Uses `uv pip list` to get currently installed versions
   - Uses `uv pip search` to find latest versions on PyPI

2. **Requirements Parsing**:
   - Supports various version specifiers (>=, ==, ~=)
   - Handles packages with and without version specifications

3. **Update Process**:
   - Updates all packages to use >= with their latest versions
   - Preserves all packages from original requirements.txt
   - Provides warning for packages where latest version couldn't be determined

## Error Handling

The script handles various error cases:
- Missing `uv` installation
- Missing requirements.txt
- Network connectivity issues
- Invalid package names
- JSON parsing errors

## Best Practices

1. Always review the changes before accepting the update
2. Keep a backup of your original requirements.txt
3. Test your application after updating dependencies
4. Use a virtual environment to isolate dependencies

## Contributing

Feel free to submit issues and enhancement requests! 