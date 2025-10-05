# database_connection.py - Simple database connection utility
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from config import MYSQL_CONFIG, RAW_DATABASE, CLEANED_DATABASE

class DatabaseConnection:
    def __init__(self):
        self.config = MYSQL_CONFIG
        self.raw_db = RAW_DATABASE
        self.cleaned_db = CLEANED_DATABASE

        # Create SQLAlchemy engines
        self.engines = {}
        for db_name in [self.raw_db, self.cleaned_db]:
            connection_string = (
                f"mysql+mysqlconnector://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{db_name}"
            )
            self.engines[db_name] = create_engine(connection_string)

    def execute_query(self, query, database_name):
        """Execute query using SQLAlchemy"""
        engine = self.engines[database_name]
        return pd.read_sql(query, engine)

    def test_connections(self):
        """Test connections to both databases"""
        print("Testing Database Connections...")
        print("=" * 50)

        try:
            # Test server connection
            conn = mysql.connector.connect(**self.config)
            print("✅ MySQL Server: Connected successfully")
            conn.close()

            # Test both databases
            for db_name in [self.raw_db, self.cleaned_db]:
                config = self.config.copy()
                config['database'] = db_name
                conn = mysql.connector.connect(**config)
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"✅ {db_name}: {len(tables)} tables found")
                cursor.close()
                conn.close()

            print("🚀 All connections successful! Ready for analysis.")
            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def get_table_list(self, database_name):
        """Get list of all tables"""
        query = "SHOW TABLES"
        df = self.execute_query(query, database_name)
        return df.iloc[:, 0].tolist()

    def get_table_structure(self, table_name, database_name):
        """Get table structure"""
        query = f"DESCRIBE `{table_name}`"
        return self.execute_query(query, database_name)

    def get_table_sample(self, table_name, database_name, limit=10):
        """Get sample data"""
        query = f"SELECT * FROM `{table_name}` LIMIT {limit}"
        return self.execute_query(query, database_name)

    def get_table_count(self, table_name, database_name):
        """Get row count"""
        query = f"SELECT COUNT(*) as row_count FROM `{table_name}`"
        result = self.execute_query(query, database_name)
        return result.iloc[0]['row_count']