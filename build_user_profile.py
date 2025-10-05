#!/usr/bin/env python3
"""
User Profile Builder
Extracts and consolidates user information from multiple tables
Usage: python3 build_user_profile.py [user_id]
"""

import pandas as pd
import sys
import os
from datetime import datetime
from database_connection import DatabaseConnection
from config import TARGET_ACCOUNT

def main():
    """Build comprehensive user profile"""

    # Get user ID from command line or use default
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
        except ValueError:
            print("Error: User ID must be a valid integer")
            print("Usage: python3 build_user_profile.py [user_id]")
            return
    else:
        user_id = TARGET_ACCOUNT
        print(f"No user ID provided, using default: {user_id}")

    print(f"\n{'='*80}")
    print(f"USER PROFILE BUILDER")
    print(f"User ID: {user_id}")
    print(f"{'='*80}\n")

    db = DatabaseConnection()

    # Test connection
    if not db.test_connections():
        print("Database connection failed!")
        return

    # Storage for profile data
    profile = {
        'user_id': user_id,
        'username': None,
        'first_name': None,
        'last_name': None,
        'email': None,
        'country': None,
        'city': None,
        'ip_addresses': [],
        'wallet_addresses': []
    }

    # Track all raw data from tables
    raw_data = {}

    # Tables to check for user information
    profile_tables = [
        'user_registration',
        'visitor',
        'manage_messages',
        'previous_record',
        'updated_record',
        'support_log',
        'user_addresses',
        'withdraw_confirm'
    ]

    print("Extracting data from tables...")
    print("-" * 80)

    for table in profile_tables:
        try:
            # Check which column exists in this table
            structure = db.get_table_structure(table, db.raw_db)
            columns = structure['Field'].str.lower().tolist()

            # Determine the correct column name
            user_column = None
            if 'user_id' in columns:
                user_column = 'user_id'
            elif 'userid' in columns:
                user_column = 'userid'
            else:
                # Skip this table if no user column found
                continue

            query = f"SELECT * FROM `{table}` WHERE `{user_column}` = {user_id}"
            df = db.execute_query(query, db.raw_db)

            if not df.empty:
                print(f"\n✓ Found data in {table} ({len(df)} record(s))")
                raw_data[table] = df

                # Extract relevant fields from each table
                for idx, row in df.iterrows():
                    # Username
                    if profile['username'] is None:
                        for col in ['username', 'user_name', 'login', 'account_name']:
                            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                                profile['username'] = str(row[col]).strip()
                                print(f"  → username: {profile['username']}")
                                break

                    # First name
                    if profile['first_name'] is None:
                        for col in ['first_name', 'fname', 'firstname', 'name']:
                            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                                profile['first_name'] = str(row[col]).strip()
                                print(f"  → first_name: {profile['first_name']}")
                                break

                    # Last name
                    if profile['last_name'] is None:
                        for col in ['last_name', 'lname', 'lastname', 'surname']:
                            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                                profile['last_name'] = str(row[col]).strip()
                                print(f"  → last_name: {profile['last_name']}")
                                break

                    # Email
                    if profile['email'] is None:
                        for col in ['email', 'email_address', 'mail']:
                            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                                profile['email'] = str(row[col]).strip()
                                print(f"  → email: {profile['email']}")
                                break

                    # Country
                    if profile['country'] is None:
                        for col in ['country', 'country_name']:
                            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                                profile['country'] = str(row[col]).strip()
                                print(f"  → country: {profile['country']}")
                                break

                    # City
                    if profile['city'] is None:
                        for col in ['city', 'city_name']:
                            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                                profile['city'] = str(row[col]).strip()
                                print(f"  → city: {profile['city']}")
                                break

                    # IP addresses (can be multiple)
                    for col in ['ip', 'ip_address', 'ip_addr', 'ipaddress', 'ipadd']:
                        if col in row and pd.notna(row[col]) and str(row[col]).strip():
                            ip = str(row[col]).strip()
                            if ip not in profile['ip_addresses']:
                                profile['ip_addresses'].append(ip)
                                print(f"  → ip_address: {ip}")

                    # Wallet addresses (can be multiple)
                    for col in ['daddress', 'waddress1', 'waddress2', 'wallet_address', 'wallet',
                               'address', 'btc_address', 'eth_address', 'crypto_address', 'payment_address']:
                        if col in row and pd.notna(row[col]) and str(row[col]).strip():
                            wallet = str(row[col]).strip()
                            # Skip placeholder values
                            if wallet in ['0', 'None', 'NULL', '']:
                                continue
                            if wallet not in profile['wallet_addresses']:
                                profile['wallet_addresses'].append(f"{col}: {wallet}")
                                print(f"  → {col}: {wallet}")

        except Exception as e:
            print(f"✗ Error reading {table}: {str(e)}")

    # Display unified profile
    print("\n" + "="*80)
    print("UNIFIED USER PROFILE")
    print("="*80 + "\n")

    print(f"User ID:        {profile['user_id']}")
    print(f"Username:       {profile['username'] or 'Not found'}")
    print(f"First Name:     {profile['first_name'] or 'Not found'}")
    print(f"Last Name:      {profile['last_name'] or 'Not found'}")
    print(f"Email:          {profile['email'] or 'Not found'}")
    print(f"Country:        {profile['country'] or 'Not found'}")
    print(f"City:           {profile['city'] or 'Not found'}")

    print(f"\nIP Addresses:   ", end="")
    if profile['ip_addresses']:
        print(f"{len(profile['ip_addresses'])} found")
        for i, ip in enumerate(profile['ip_addresses'], 1):
            print(f"  {i}. {ip}")
    else:
        print("None found")

    print(f"\nWallet Addresses: ", end="")
    if profile['wallet_addresses']:
        print(f"{len(profile['wallet_addresses'])} found")
        for i, wallet in enumerate(profile['wallet_addresses'], 1):
            print(f"  {i}. {wallet}")
    else:
        print("None found")

    # Save to file
    reports_dir = "forensic_reports"
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    profile_file = os.path.join(reports_dir, f"user_profile_{user_id}_{timestamp}.txt")

    with open(profile_file, 'w') as f:
        f.write(f"USER PROFILE REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*80}\n\n")

        f.write(f"User ID:        {profile['user_id']}\n")
        f.write(f"Username:       {profile['username'] or 'Not found'}\n")
        f.write(f"First Name:     {profile['first_name'] or 'Not found'}\n")
        f.write(f"Last Name:      {profile['last_name'] or 'Not found'}\n")
        f.write(f"Email:          {profile['email'] or 'Not found'}\n")
        f.write(f"Country:        {profile['country'] or 'Not found'}\n")
        f.write(f"City:           {profile['city'] or 'Not found'}\n")

        f.write(f"\nIP Addresses:   ")
        if profile['ip_addresses']:
            f.write(f"{len(profile['ip_addresses'])} found\n")
            for i, ip in enumerate(profile['ip_addresses'], 1):
                f.write(f"  {i}. {ip}\n")
        else:
            f.write("None found\n")

        f.write(f"\nWallet Addresses: ")
        if profile['wallet_addresses']:
            f.write(f"{len(profile['wallet_addresses'])} found\n")
            for i, wallet in enumerate(profile['wallet_addresses'], 1):
                f.write(f"  {i}. {wallet}\n")
        else:
            f.write("None found\n")

        # Add raw data section
        f.write(f"\n{'='*80}\n")
        f.write(f"RAW DATA FROM TABLES\n")
        f.write(f"{'='*80}\n\n")

        for table, df in raw_data.items():
            f.write(f"\n--- {table} ---\n")
            for idx, row in df.iterrows():
                f.write(f"\nRecord #{idx + 1}:\n")
                for col, val in row.items():
                    if pd.notna(val):
                        f.write(f"  {col}: {val}\n")

    print(f"\n{'='*80}")
    print(f"Profile saved to: {profile_file}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
