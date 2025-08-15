# Database Manager

Intelligent database management tool for the FastAPI backend.

## Features

- **Auto-discovery**: Automatically detects SQLAlchemy models from `models/database.py`
- **Table Management**: Create, drop, and reset tables with proper relationships
- **Safety Features**: Confirmation prompts for destructive operations
- **Comprehensive Logging**: Detailed output of all operations
- **Command-line Interface**: Easy-to-use commands for common tasks

## Installation

No installation required. The script is included in the `scripts` directory.

## Usage

```bash
# Create all tables from models
python db_manager.py create

# Drop all tables (with confirmation)
python db_manager.py drop

# Reset tables (drop and recreate)
python db_manager.py reset

# Show current table status
python db_manager.py status

# Validate database connection
python db_manager.py validate
```

## Advanced Usage

### Specific Tables

You can target specific tables by name:

```bash
# Create only the 'conversations' table
python db_manager.py create --tables conversations

# Drop only the 'conversation_turns' table
python db_manager.py drop --tables conversation_turns --force
```

### Force Operations

Add `--force` to skip confirmation prompts:

```bash
# Drop all tables without confirmation
python db_manager.py drop --force
```

## Safety Features

- **Table Dropping**: Requires confirmation unless `--force` is used
- **Cascade Deletion**: Properly handles foreign key constraints
- **Connection Validation**: Checks database connectivity before operations

## Development Workflow

For a clean development environment:

1. Reset tables before starting work:
   ```bash
   python db_manager.py reset
   ```

2. Check table status after making model changes:
   ```bash
   python db_manager.py status
   ```

3. Create tables when deploying to a new environment:
   ```bash
   python db_manager.py create
   ```

## Troubleshooting

- Ensure your database connection settings in `config/__init__.py` are correct
- Check the database service is running
- Review logs for detailed error information

## License

This script is part of the FastAPI backend and follows the same license terms.