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

**Comprehensive Phase 1 Forensic Audit:**
```bash
# Run complete Phase 1 analysis suite
python3 phase1_forensic_audit.py 88295329

# Individual Phase 1 tools
python3 transaction_timeline_builder.py 88295329
python3 data_completeness_checker.py 88295329
python3 cross_table_validator.py 88295329
```

## Files

| File | Purpose |
|------|---------|
| **Core Tools** | |
| `account_table_summary.py` | Initial analysis - shows all tables and record counts for any account |
| `database_connection.py` | Database connection utilities and helper functions |
| `config.py` | Database configuration (host, credentials, database names) |
| `test_connection.py` | Database connection verification |
| **Phase 1: Data Extraction & Timeline Analysis** | |
| `transaction_timeline_builder.py` | Extract and analyze chronological data across all tables |
| `data_completeness_checker.py` | Identify missing records, gaps, and data quality issues |
| `cross_table_validator.py` | Verify data consistency and relationships across tables |
| `phase1_forensic_audit.py` | Run complete Phase 1 audit suite |
| **Documentation** | |
| `README.md` | This documentation |

## Sample Output

```
ACCOUNT TABLE SUMMARY - Account: 88295329
================================================================================
Report will be saved to: reports/account_summary_88295329_20240915_143052.txt

Scanning RAW DATABASE: crypto_transactions_raw
--------------------------------------------------
Total tables in raw database: 157
  ✅ credit_debit                    | user_id        |     51 records
  ✅ visitor                         | user_id        |     35 records
  ✅ support_log                     | user_id        |      4 records
  ✅ withdraw_request                | user_id        |      2 records
  ...

Scanning CLEANED DATABASE: crypto_transactions_cleaned
----------------------------------------------------------
Total tables in cleaned database: 1
  ✅ mtiusers                        | id             |      1 records

================================================================================
SUMMARY REPORT
================================================================================
Target Account: 88295329
Raw Database Tables: 13 tables, 102 total records
Cleaned Database Tables: 1 tables, 1 total records

RAW DATABASE BREAKDOWN:
  credit_debit                   | user_id        |     51 records
  visitor                        | user_id        |     35 records
  support_log                    | user_id        |      4 records
  ...

Report saved to: reports/account_summary_88295329_20240915_143052.txt
Analysis complete!
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

## Features

### Account Table Summary (Core Tool)
- **Auto-discovery**: Automatically finds tables containing account data
- **Record counts**: Shows exact number of records per table
- **Cross-database**: Compares data between raw and cleaned databases
- **Summary report**: Provides clear breakdown and totals
- **Flexible**: Works with any account number
- **Report generation**: Automatically saves detailed reports to `reports/` folder
- **Timestamped**: Each report includes timestamp for tracking

### Phase 1 Forensic Analysis Suite
- **🕒 Timeline Builder**: Extract and analyze all account data chronologically
  - Combines data from all tables with timestamps
  - Identifies activity patterns and temporal trends
  - Exports timeline data for further analysis

- **📊 Completeness Checker**: Comprehensive data quality analysis
  - Identifies missing data and gaps in records
  - Calculates completeness scores per table
  - Detects data quality issues and anomalies

- **🔗 Cross-table Validator**: Data consistency verification
  - Compares raw vs cleaned database consistency
  - Validates referential integrity across tables
  - Checks business logic and constraints

- **🚀 Phase 1 Runner**: Execute complete audit suite
  - Runs all Phase 1 tools in sequence
  - Provides comprehensive status reporting
  - Generates consolidated analysis results

### Database Connection
- **Connection testing**: Verifies database connectivity
- **Helper functions**: Table listing, structure analysis, sample data
- **Error handling**: Graceful handling of connection issues
- **SQLAlchemy**: Efficient database queries with pandas integration

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

## Development

To extend functionality:
1. Add new analysis functions to `database_connection.py`
2. Create new scripts following the pattern of `account_table_summary.py`
3. Update configuration in `config.py` as needed

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify database connectivity with `test_connection.py`
3. Review configuration in `config.py`