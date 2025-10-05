# Database Analysis Tools

A clean, focused toolkit for analyzing cryptocurrency transaction databases.

## Overview

This project provides simple tools to analyze account data across two MySQL databases:
- **Raw Database** (`crypto_transactions_raw`) - Original unprocessed data
- **Cleaned Database** (`crypto_transactions_cleaned`) - Processed/cleaned data

## Quick Start

### 1. Setup

1. **Clone/Navigate to project directory:**
   ```bash
   cd /home/nihal/DB_005
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Test database connection:**
   ```bash
   python3 test_connection.py
   ```

### 2. Analyze Account Data

**Quick Analysis:**
```bash
# Use default account (88295329)
python3 account_table_summary.py

# Analyze specific account
python3 account_table_summary.py 12345678
```

## Configuration

Database settings are configured in `config.py`:

```python
# MySQL Database Configuration
MYSQL_CONFIG = {
    'host': '172.18.176.1',    # Windows host IP for WSL connection
    'port': 3306,
    'user': 'wsl_user',
    'password': 'your_password',
    'charset': 'utf8mb4',
    'autocommit': True,
    'connect_timeout': 30,
    'sql_mode': 'TRADITIONAL'
}

# Database Names
RAW_DATABASE = 'crypto_transactions_raw'
CLEANED_DATABASE = 'crypto_transactions_cleaned'

# Default Target Account
TARGET_ACCOUNT = 88295329
```

## Requirements

- Python 3.x
- MySQL server with configured databases
- Required packages (see `venv/` for installed packages):
  - `pandas`
  - `mysql-connector-python`
  - `sqlalchemy`

## Troubleshooting

### Connection Issues
1. **Check database connection:**
   ```bash
   python3 test_connection.py
   ```

2. **Verify configuration:**
   - Check host IP in `config.py`
   - Verify username/password
   - Ensure databases exist

3. **Common fixes:**
   - For WSL: Use Windows host IP (usually `172.x.x.1`)
   - Check MySQL service is running
   - Verify user has database permissions

### No Results Found
If no tables are found for an account:
- Verify the account number exists in the databases
- Check if account uses different column names (script checks: `user_id`, `account_id`, `id`, `userid`, `accountid`)
- Some tables may have permissions issues and are skipped automatically
