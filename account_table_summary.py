#!/usr/bin/env python3
"""
Account Table Summary - Simple focused analysis
Get all tables and record counts for any target account
Usage: python3 account_table_summary.py [account_number]
"""

import pandas as pd
import sys
import os
from datetime import datetime
from database_connection import DatabaseConnection
from config import TARGET_ACCOUNT

def print_and_log(message, file_handle=None):
    """Print to console and optionally write to file"""
    print(message)
    if file_handle:
        file_handle.write(message + '\n')

def main():
    """Generate focused table summary for target account"""

    # Get account number from command line or use default
    if len(sys.argv) > 1:
        try:
            account_number = int(sys.argv[1])
        except ValueError:
            print("Error: Account number must be a valid integer")
            print("Usage: python3 account_table_summary.py [account_number]")
            return
    else:
        account_number = TARGET_ACCOUNT
        print(f"No account number provided, using default: {account_number}")

    # Create reports directory
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    # Create report file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"account_summary_{account_number}_{timestamp}.txt"
    report_path = os.path.join(reports_dir, report_filename)

    # Open report file
    with open(report_path, 'w') as report_file:
        # Write header with metadata
        report_file.write(f"Account Table Summary Report\n")
        report_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_file.write(f"Account Number: {account_number}\n")
        report_file.write("=" * 80 + "\n\n")

        print_and_log(f"ACCOUNT TABLE SUMMARY - Account: {account_number}", report_file)
        print_and_log("=" * 80, report_file)
        print_and_log(f"Report will be saved to: {report_path}", report_file)

        db = DatabaseConnection()

        # Check connections first
        if not db.test_connections():
            print_and_log("Database connection failed!", report_file)
            return

        print_and_log("\nScanning all tables for account data...", report_file)
        print_and_log("-" * 80, report_file)

        # Results storage
        results = {
            'raw_database': [],
            'cleaned_database': []
        }

        # Scan raw database
        print_and_log(f"\nScanning RAW DATABASE: {db.raw_db}", report_file)
        print_and_log("-" * 50, report_file)

        raw_tables = db.get_table_list(db.raw_db)
        print_and_log(f"Total tables in raw database: {len(raw_tables)}", report_file)

        for table_name in raw_tables:
            try:
                # Check common column names for user/account ID
                structure = db.get_table_structure(table_name, db.raw_db)
                columns = structure['Field'].str.lower().tolist()

                account_columns = ['userid', 'user_id', 'account_id', 'id', 'accountid']
                found_column = None

                for col in account_columns:
                    if col in columns:
                        found_column = structure[structure['Field'].str.lower() == col]['Field'].iloc[0]
                        break

                if found_column:
                    # Count records for target account
                    count_query = f"SELECT COUNT(*) as count FROM `{table_name}` WHERE `{found_column}` = {account_number}"
                    result = db.execute_query(count_query, db.raw_db)
                    count = result['count'].iloc[0]

                    if count > 0:
                        results['raw_database'].append({
                            'table': table_name,
                            'column': found_column,
                            'records': count
                        })
                        print_and_log(f"{table_name:<30} | {found_column:<15} | {count:>6} records", report_file)

            except Exception as e:
                # Skip tables that cause errors (permissions, etc.)
                continue

        # Scan cleaned database
        print_and_log(f"\n Scanning CLEANED DATABASE: {db.cleaned_db}", report_file)
        print_and_log("-" * 50, report_file)

        cleaned_tables = db.get_table_list(db.cleaned_db)
        print_and_log(f"Total tables in cleaned database: {len(cleaned_tables)}", report_file)

        for table_name in cleaned_tables:
            try:
                # Check common column names for user/account ID
                structure = db.get_table_structure(table_name, db.cleaned_db)
                columns = structure['Field'].str.lower().tolist()

                account_columns = ['userid', 'user_id', 'account_id', 'id', 'accountid']
                found_column = None

                for col in account_columns:
                    if col in columns:
                        found_column = structure[structure['Field'].str.lower() == col]['Field'].iloc[0]
                        break

                if found_column:
                    # Count records for target account
                    count_query = f"SELECT COUNT(*) as count FROM `{table_name}` WHERE `{found_column}` = {account_number}"
                    result = db.execute_query(count_query, db.cleaned_db)
                    count = result['count'].iloc[0]

                    if count > 0:
                        results['cleaned_database'].append({
                            'table': table_name,
                            'column': found_column,
                            'records': count
                        })
                        print_and_log(f"{table_name:<30} | {found_column:<15} | {count:>6} records", report_file)

            except Exception as e:
                # Skip tables that cause errors (permissions, etc.)
                continue

        # Summary
        print_and_log("\n" + "="*80, report_file)
        print_and_log("SUMMARY REPORT", report_file)
        print_and_log("="*80, report_file)

        raw_total = sum(item['records'] for item in results['raw_database'])
        cleaned_total = sum(item['records'] for item in results['cleaned_database'])

        print_and_log(f"Target Account: {account_number}", report_file)
        print_and_log(f"Raw Database Tables: {len(results['raw_database'])} tables, {raw_total} total records", report_file)
        print_and_log(f"Cleaned Database Tables: {len(results['cleaned_database'])} tables, {cleaned_total} total records", report_file)

        print_and_log(f"\nRAW DATABASE BREAKDOWN:", report_file)
        for item in sorted(results['raw_database'], key=lambda x: x['records'], reverse=True):
            print_and_log(f"  {item['table']:<30} | {item['column']:<15} | {item['records']:>6} records", report_file)

        print_and_log(f"\nCLEANED DATABASE BREAKDOWN:", report_file)
        for item in sorted(results['cleaned_database'], key=lambda x: x['records'], reverse=True):
            print_and_log(f"  {item['table']:<30} | {item['column']:<15} | {item['records']:>6} records", report_file)

        # Identify tables only in one database
        raw_table_names = {item['table'] for item in results['raw_database']}
        cleaned_table_names = {item['table'] for item in results['cleaned_database']}

        only_in_raw = raw_table_names - cleaned_table_names
        only_in_cleaned = cleaned_table_names - raw_table_names

        if only_in_raw:
            print_and_log(f"\nTables ONLY in RAW database:", report_file)
            for table in sorted(only_in_raw):
                records = next(item['records'] for item in results['raw_database'] if item['table'] == table)
                print_and_log(f"  {table} ({records} records)", report_file)

        if only_in_cleaned:
            print_and_log(f"\nTables ONLY in CLEANED database:", report_file)
            for table in sorted(only_in_cleaned):
                records = next(item['records'] for item in results['cleaned_database'] if item['table'] == table)
                print_and_log(f"  {table} ({records} records)", report_file)

        # Final message
        print_and_log(f"\n Report saved to: {report_path}", report_file)
        print_and_log("Analysis complete!", report_file)

if __name__ == "__main__":
    main()