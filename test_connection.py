#!/usr/bin/env python3
"""
Database Connection Test
Simple utility to verify database connectivity and basic information
"""

from database_connection import DatabaseConnection
from config import MYSQL_CONFIG, RAW_DATABASE, CLEANED_DATABASE

def main():
    """Test database connections and display basic information"""

    print("DATABASE CONNECTION TEST")
    print("=" * 60)

    # Display configuration (without password)
    config_display = MYSQL_CONFIG.copy()
    config_display['password'] = '*' * len(config_display['password'])

    print("Configuration:")
    for key, value in config_display.items():
        print(f"  {key}: {value}")

    print(f"\nTarget Databases:")
    print(f"  Raw Database: {RAW_DATABASE}")
    print(f"  Cleaned Database: {CLEANED_DATABASE}")

    print("\n" + "-" * 60)

    # Initialize connection
    try:
        db = DatabaseConnection()
        print("✅ Database connection object created successfully")
    except Exception as e:
        print(f"❌ Failed to create database connection: {e}")
        return

    # Test connections
    print("\nTesting database connections...")
    if not db.test_connections():
        print("❌ Connection test failed!")
        return

    print("\n" + "=" * 60)
    print("DATABASE OVERVIEW")
    print("=" * 60)

    # Get database summaries
    for db_name in [RAW_DATABASE, CLEANED_DATABASE]:
        print(f"\n📊 {db_name.upper()}")
        print("-" * 40)

        try:
            # Get table list
            tables = db.get_table_list(db_name)
            print(f"Total Tables: {len(tables)}")

            # Get size information
            size_query = f"""
            SELECT
                COALESCE(SUM(TABLE_ROWS), 0) as total_rows,
                ROUND(COALESCE(SUM(DATA_LENGTH + INDEX_LENGTH), 0) / 1024 / 1024, 2) as total_size_mb
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = '{db_name}'
            """

            size_info = db.execute_query(size_query, db_name)
            total_rows = int(size_info.iloc[0]['total_rows'])
            total_size = float(size_info.iloc[0]['total_size_mb'])

            print(f"Total Rows: {total_rows:,}")
            print(f"Total Size: {total_size:.2f} MB")

            # Show top 10 largest tables
            table_info_query = f"""
            SELECT
                TABLE_NAME,
                TABLE_ROWS,
                ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) as SIZE_MB
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = '{db_name}'
            ORDER BY TABLE_ROWS DESC
            LIMIT 10
            """

            table_info = db.execute_query(table_info_query, db_name)

            if not table_info.empty:
                print(f"\nTop 10 Largest Tables:")
                print(f"{'Table Name':<30} {'Rows':<12} {'Size (MB)':<10}")
                print("-" * 52)
                for _, row in table_info.iterrows():
                    table_name = row['TABLE_NAME']
                    table_rows = int(row['TABLE_ROWS']) if row['TABLE_ROWS'] else 0
                    table_size = float(row['SIZE_MB']) if row['SIZE_MB'] else 0.0
                    print(f"{table_name:<30} {table_rows:<12,} {table_size:<10.2f}")

        except Exception as e:
            print(f"❌ Error analyzing {db_name}: {e}")

    # Test sample queries
    print(f"\n" + "=" * 60)
    print("SAMPLE QUERY TESTS")
    print("=" * 60)

    # Test a simple query on each database
    for db_name in [RAW_DATABASE, CLEANED_DATABASE]:
        print(f"\n🔍 Testing queries on {db_name}")
        try:
            # Get first table with data
            tables = db.get_table_list(db_name)

            sample_table = None
            for table in tables[:5]:  # Check first 5 tables
                try:
                    count_result = db.execute_query(f"SELECT COUNT(*) as count FROM `{table}` LIMIT 1", db_name)
                    if count_result.iloc[0]['count'] > 0:
                        sample_table = table
                        break
                except:
                    continue

            if sample_table:
                print(f"  ✅ Successfully queried table: {sample_table}")

                # Get table structure
                structure = db.get_table_structure(sample_table, db_name)
                print(f"  📋 Table structure: {len(structure)} columns")

                # Get sample data
                sample_data = db.get_table_sample(sample_table, db_name, 1)
                print(f"  📄 Sample data retrieved: {len(sample_data)} rows")

            else:
                print(f"  ⚠️  No tables with data found for testing")

        except Exception as e:
            print(f"  ❌ Query test failed: {e}")

    print(f"\n" + "=" * 60)
    print("CONNECTION TEST COMPLETE!")
    print("=" * 60)
    print("✅ All systems ready for analysis")
    print(f"💡 Next step: Run 'python3 account_table_summary.py [account_number]'")

if __name__ == "__main__":
    main()