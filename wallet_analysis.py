#!/usr/bin/env python3
"""
Wallet Analysis - Complete wallet and transaction tracker
Analyzes all wallet addresses, e-wallets, deposits, and withdrawals
Usage: python3 wallet_analysis.py [user_id]
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

def analyze_wallet_addresses(user_id, db, report_file):
    """Analyze cryptocurrency wallet addresses"""
    print_and_log("\n" + "="*80, report_file)
    print_and_log("SECTION 1: CRYPTOCURRENCY WALLET ADDRESSES", report_file)
    print_and_log("="*80, report_file)

    try:
        query = f"SELECT * FROM user_addresses WHERE user_id = {user_id}"
        df = db.execute_query(query, db.raw_db)

        if not df.empty:
            row = df.iloc[0]

            print_and_log("\n--- DEPOSIT ADDRESS ---", report_file)
            if pd.notna(row['daddress']) and str(row['daddress']) not in ['0', 'None', '']:
                print_and_log(f"Address: {row['daddress']}", report_file)
                print_and_log("Type: Bitcoin Deposit Address", report_file)
                print_and_log("Purpose: This is where the user deposits funds INTO the platform", report_file)
                print_and_log(f"First Added: {row['firstadd']}", report_file)
                print_and_log(f"Timestamp: {row['ts']}", report_file)
            else:
                print_and_log("No deposit address found", report_file)

            print_and_log("\n--- WITHDRAWAL ADDRESS 1 ---", report_file)
            if pd.notna(row['waddress1']) and str(row['waddress1']) not in ['0', 'None', '']:
                print_and_log(f"Label: {row['waddress1Label']}", report_file)
                print_and_log(f"Address: {row['waddress1']}", report_file)
                print_and_log("Purpose: Primary withdrawal address - where funds are sent when user withdraws", report_file)
            else:
                print_and_log("No withdrawal address 1 set", report_file)

            print_and_log("\n--- WITHDRAWAL ADDRESS 2 ---", report_file)
            if pd.notna(row['waddress2']) and str(row['waddress2']) not in ['0', 'None', '']:
                print_and_log(f"Label: {row['waddress2Label']}", report_file)
                print_and_log(f"Address: {row['waddress2']}", report_file)
                print_and_log("Purpose: Secondary withdrawal address (backup)", report_file)
            else:
                print_and_log("No withdrawal address 2 set", report_file)

            print_and_log(f"\nMissing Payment Flag: {row['missing_payment']}", report_file)

        else:
            print_and_log("\nNo wallet address records found", report_file)

    except Exception as e:
        print_and_log(f"\nError analyzing wallet addresses: {str(e)}", report_file)

def analyze_ewallets(user_id, db, report_file):
    """Analyze internal e-wallet balances"""
    print_and_log("\n" + "="*80, report_file)
    print_and_log("SECTION 2: INTERNAL E-WALLET BALANCES", report_file)
    print_and_log("="*80, report_file)

    wallet_tables = {
        'working_e_wallet': {
            'name': 'Working Wallet',
            'description': 'Holds referral bonuses, commissions, and active earnings'
        },
        'roi_e_wallet': {
            'name': 'ROI Wallet',
            'description': 'Holds daily ROI (Return on Investment) income'
        },
        'final_e_wallet': {
            'name': 'Final E-Wallet',
            'description': 'Purpose unclear - appears mostly unused'
        }
    }

    total_balance = 0

    for table, info in wallet_tables.items():
        try:
            query = f"SELECT * FROM {table} WHERE user_id = {user_id}"
            df = db.execute_query(query, db.raw_db)

            if not df.empty:
                row = df.iloc[0]
                balance = float(row['amount'])
                total_balance += balance

                print_and_log(f"\n--- {info['name'].upper()} ---", report_file)
                print_and_log(f"Description: {info['description']}", report_file)
                print_and_log(f"Balance: {balance:.10f} BTC", report_file)
                print_and_log(f"Status: {row['status']}", report_file)
                print_and_log(f"Record ID: {row['id']}", report_file)

        except Exception as e:
            print_and_log(f"\nError reading {table}: {str(e)}", report_file)

    print_and_log(f"\n{'='*80}", report_file)
    print_and_log(f"TOTAL E-WALLET BALANCE: {total_balance:.10f} BTC", report_file)
    print_and_log(f"{'='*80}", report_file)

def analyze_ewallet_usage(user_id, db, report_file):
    """Analyze e-wallet usage from credit_debit transactions"""
    print_and_log("\n" + "="*80, report_file)
    print_and_log("SECTION 3: E-WALLET USAGE ANALYSIS", report_file)
    print_and_log("="*80, report_file)
    print_and_log("Analyzing which e-wallets were used in transactions...", report_file)

    try:
        query = f"SELECT ewallet_used_by, COUNT(*) as count, SUM(credit_amt) as total_credits, SUM(debit_amt) as total_debits FROM credit_debit WHERE user_id = {user_id} GROUP BY ewallet_used_by ORDER BY count DESC"
        df = db.execute_query(query, db.raw_db)

        if not df.empty:
            print_and_log(f"\nFound {len(df)} different e-wallet types used:\n", report_file)
            print_and_log(f"{'E-Wallet Type':<30} | {'Transactions':<15} | {'Total Credits':<20} | {'Total Debits':<20}", report_file)
            print_and_log("-" * 90, report_file)

            for idx, row in df.iterrows():
                ewallet = row['ewallet_used_by'] if pd.notna(row['ewallet_used_by']) else 'Unknown'
                count = int(row['count'])
                try:
                    credits = float(row['total_credits']) if pd.notna(row['total_credits']) else 0.0
                except (ValueError, TypeError):
                    credits = 0.0
                try:
                    debits = float(row['total_debits']) if pd.notna(row['total_debits']) else 0.0
                except (ValueError, TypeError):
                    debits = 0.0

                print_and_log(f"{ewallet:<30} | {count:<15} | {credits:<20.10f} | {debits:<20.10f}", report_file)

            # Detailed breakdown by e-wallet type
            print_and_log("\n" + "="*80, report_file)
            print_and_log("DETAILED E-WALLET TRANSACTION BREAKDOWN", report_file)
            print_and_log("="*80, report_file)

            for idx, row in df.iterrows():
                ewallet = row['ewallet_used_by'] if pd.notna(row['ewallet_used_by']) else 'Unknown'

                print_and_log(f"\n--- {ewallet.upper()} ---", report_file)

                # Get detailed transactions for this e-wallet
                detail_query = f"SELECT * FROM credit_debit WHERE user_id = {user_id} AND ewallet_used_by = '{ewallet}' ORDER BY ts"
                detail_df = db.execute_query(detail_query, db.raw_db)

                if not detail_df.empty:
                    print_and_log(f"Total Transactions: {len(detail_df)}\n", report_file)

                    for i, trans in detail_df.iterrows():
                        print_and_log(f"Transaction #{i+1}:", report_file)
                        print_and_log(f"  ID: {trans['id']}", report_file)
                        print_and_log(f"  Transaction No: {trans['transaction_no']}", report_file)
                        print_and_log(f"  Invoice/Reference: {trans['invoice_no']}", report_file)
                        print_and_log(f"  Type: {trans['ttype']}", report_file)
                        print_and_log(f"  Description: {trans['TranDescription']}", report_file)

                        # Handle amount conversions safely
                        try:
                            credit = float(trans['credit_amt']) if pd.notna(trans['credit_amt']) else 0.0
                        except (ValueError, TypeError):
                            credit = 0.0
                        try:
                            debit = float(trans['debit_amt']) if pd.notna(trans['debit_amt']) else 0.0
                        except (ValueError, TypeError):
                            debit = 0.0
                        try:
                            admin_charge = float(trans['admin_charge']) if pd.notna(trans['admin_charge']) else 0.0
                        except (ValueError, TypeError):
                            admin_charge = 0.0

                        print_and_log(f"  Credit Amount: {credit:.10f} BTC", report_file)
                        print_and_log(f"  Debit Amount: {debit:.10f} BTC", report_file)
                        print_and_log(f"  Admin Charge: {admin_charge:.10f} BTC", report_file)
                        print_and_log(f"  Receiver ID: {trans['receiver_id']}", report_file)
                        print_and_log(f"  Sender ID: {trans['sender_id']}", report_file)
                        print_and_log(f"  Product Name: {trans['product_name']}", report_file)
                        print_and_log(f"  Status: {trans['status']}", report_file)
                        print_and_log(f"  Date: {trans['receive_date']}", report_file)
                        print_and_log(f"  Timestamp: {trans['ts']}", report_file)
                        print_and_log(f"  Cause: {trans['Cause']}", report_file)
                        print_and_log(f"  Remark: {trans['Remark']}", report_file)
                        print_and_log("", report_file)

        else:
            print_and_log("\nNo e-wallet usage data found", report_file)

    except Exception as e:
        print_and_log(f"\nError analyzing e-wallet usage: {str(e)}", report_file)

def analyze_deposits(user_id, db, report_file):
    """Analyze all deposit transactions"""
    print_and_log("\n" + "="*80, report_file)
    print_and_log("SECTION 4: DEPOSIT ANALYSIS", report_file)
    print_and_log("="*80, report_file)

    # First, get the user's deposit address
    deposit_address = None
    try:
        addr_query = f"SELECT daddress FROM user_addresses WHERE user_id = {user_id}"
        addr_df = db.execute_query(addr_query, db.raw_db)
        if not addr_df.empty and pd.notna(addr_df.iloc[0]['daddress']):
            deposit_address = addr_df.iloc[0]['daddress']
            print_and_log(f"\nUser's Deposit Address (daddress): {deposit_address}", report_file)
            print_and_log("This is the Bitcoin address where funds should be deposited.\n", report_file)
    except Exception as e:
        print_and_log(f"\nCould not retrieve deposit address: {str(e)}", report_file)

    try:
        # Look for deposit-related transactions in credit_debit
        deposit_keywords = ['deposit', 'payment approved', 'payment received', 'fund received']
        conditions = " OR ".join([f"LOWER(ttype) LIKE '%{keyword}%' OR LOWER(TranDescription) LIKE '%{keyword}%'" for keyword in deposit_keywords])

        query = f"""
            SELECT * FROM credit_debit
            WHERE user_id = {user_id}
            AND ({conditions})
            ORDER BY ts
        """
        df = db.execute_query(query, db.raw_db)

        if not df.empty:
            print_and_log(f"\nFound {len(df)} deposit-related transaction(s)\n", report_file)

            total_deposits = 0

            for idx, row in df.iterrows():
                print_and_log(f"\n{'='*80}", report_file)
                print_and_log(f"DEPOSIT #{idx + 1}", report_file)
                print_and_log(f"{'='*80}", report_file)

                if deposit_address:
                    print_and_log(f"Deposit Address: {deposit_address}", report_file)

                print_and_log(f"Transaction ID: {row['id']}", report_file)
                print_and_log(f"Transaction No: {row['transaction_no']}", report_file)
                print_and_log(f"Type: {row['ttype']}", report_file)
                print_and_log(f"Description: {row['TranDescription']}", report_file)

                # Handle amounts safely
                try:
                    credit_amt = float(row['credit_amt']) if pd.notna(row['credit_amt']) else 0.0
                except (ValueError, TypeError):
                    credit_amt = 0.0
                try:
                    admin_charge = float(row['admin_charge']) if pd.notna(row['admin_charge']) else 0.0
                except (ValueError, TypeError):
                    admin_charge = 0.0

                print_and_log(f"Amount: {credit_amt:.10f} BTC", report_file)
                print_and_log(f"Admin Charge: {admin_charge:.10f} BTC", report_file)
                print_and_log(f"Receiver ID: {row['receiver_id']}", report_file)
                print_and_log(f"Sender ID: {row['sender_id']}", report_file)
                print_and_log(f"Invoice/Hash: {row['invoice_no']}", report_file)
                print_and_log(f"Product Name: {row['product_name']}", report_file)
                print_and_log(f"E-Wallet Used: {row['ewallet_used_by']}", report_file)
                print_and_log(f"Status: {row['status']}", report_file)
                print_and_log(f"Date: {row['receive_date']}", report_file)
                print_and_log(f"Timestamp: {row['ts']}", report_file)
                print_and_log(f"Cause: {row['Cause']}", report_file)
                print_and_log(f"Remark: {row['Remark']}", report_file)

                total_deposits += credit_amt

            print_and_log(f"\n{'='*80}", report_file)
            print_and_log(f"TOTAL DEPOSITS: {total_deposits:.10f} BTC", report_file)
            print_and_log(f"{'='*80}", report_file)

        else:
            print_and_log("\nNo deposit transactions found", report_file)

    except Exception as e:
        print_and_log(f"\nError analyzing deposits: {str(e)}", report_file)

def analyze_withdrawals(user_id, db, report_file):
    """Analyze all withdrawal requests and confirmations"""
    print_and_log("\n" + "="*80, report_file)
    print_and_log("SECTION 5: WITHDRAWAL ANALYSIS", report_file)
    print_and_log("="*80, report_file)

    # Part 1: Withdrawal Requests
    print_and_log("\n" + "-"*80, report_file)
    print_and_log("PART A: WITHDRAWAL REQUESTS (withdraw_request table)", report_file)
    print_and_log("-"*80, report_file)

    try:
        query = f"SELECT * FROM withdraw_request WHERE user_id = {user_id} ORDER BY id"
        df = db.execute_query(query, db.raw_db)

        if not df.empty:
            print_and_log(f"\nFound {len(df)} withdrawal request(s)\n", report_file)

            total_requested = 0

            for idx, row in df.iterrows():
                print_and_log(f"\n{'='*80}", report_file)
                print_and_log(f"WITHDRAWAL REQUEST #{idx + 1}", report_file)
                print_and_log(f"{'='*80}", report_file)

                for col in df.columns:
                    val = row[col]
                    # Format amounts if numeric
                    if col.lower() in ['amount', 'amt', 'charge', 'fee'] and pd.notna(val):
                        try:
                            val_float = float(val)
                            print_and_log(f"{col}: {val_float:.10f} BTC", report_file)
                        except (ValueError, TypeError):
                            print_and_log(f"{col}: {val}", report_file)
                    else:
                        print_and_log(f"{col}: {val}", report_file)

                if 'amount' in df.columns:
                    try:
                        total_requested += float(row['amount']) if pd.notna(row['amount']) else 0.0
                    except (ValueError, TypeError):
                        pass

            print_and_log(f"\n{'='*80}", report_file)
            print_and_log(f"TOTAL REQUESTED: {total_requested:.10f} BTC", report_file)
            print_and_log(f"{'='*80}", report_file)

        else:
            print_and_log("\nNo withdrawal requests found", report_file)

    except Exception as e:
        print_and_log(f"\nError analyzing withdrawal requests: {str(e)}", report_file)

    # Part 2: Withdrawal Confirmations
    print_and_log("\n" + "-"*80, report_file)
    print_and_log("PART B: WITHDRAWAL CONFIRMATIONS (withdraw_confirm table)", report_file)
    print_and_log("-"*80, report_file)

    try:
        # Check which column exists
        structure = db.get_table_structure('withdraw_confirm', db.raw_db)
        columns = structure['Field'].str.lower().tolist()

        user_column = 'userid' if 'userid' in columns else 'user_id'

        query = f"SELECT * FROM withdraw_confirm WHERE {user_column} = {user_id} ORDER BY id"
        df = db.execute_query(query, db.raw_db)

        if not df.empty:
            print_and_log(f"\nFound {len(df)} withdrawal confirmation(s)\n", report_file)

            total_confirmed = 0

            for idx, row in df.iterrows():
                print_and_log(f"\n{'='*80}", report_file)
                print_and_log(f"WITHDRAWAL CONFIRMATION #{idx + 1}", report_file)
                print_and_log(f"{'='*80}", report_file)

                for col in df.columns:
                    val = row[col]
                    # Format amounts if numeric
                    if col.lower() in ['amount', 'amt', 'charge', 'fee'] and pd.notna(val):
                        try:
                            val_float = float(val)
                            print_and_log(f"{col}: {val_float:.10f} BTC", report_file)
                        except (ValueError, TypeError):
                            print_and_log(f"{col}: {val}", report_file)
                    else:
                        print_and_log(f"{col}: {val}", report_file)

                if 'amount' in df.columns:
                    try:
                        total_confirmed += float(row['amount']) if pd.notna(row['amount']) else 0.0
                    except (ValueError, TypeError):
                        pass

            print_and_log(f"\n{'='*80}", report_file)
            print_and_log(f"TOTAL CONFIRMED: {total_confirmed:.10f} BTC", report_file)
            print_and_log(f"{'='*80}", report_file)

        else:
            print_and_log("\nNo withdrawal confirmations found", report_file)

    except Exception as e:
        print_and_log(f"\nError analyzing withdrawal confirmations: {str(e)}", report_file)

    # Part 3: Withdrawal-related transactions from credit_debit
    print_and_log("\n" + "-"*80, report_file)
    print_and_log("PART C: WITHDRAWAL TRANSACTIONS (credit_debit table)", report_file)
    print_and_log("-"*80, report_file)

    try:
        query = f"""
            SELECT * FROM credit_debit
            WHERE user_id = {user_id}
            AND (LOWER(ttype) LIKE '%withdraw%' OR LOWER(TranDescription) LIKE '%withdraw%')
            ORDER BY ts
        """
        df = db.execute_query(query, db.raw_db)

        if not df.empty:
            print_and_log(f"\nFound {len(df)} withdrawal transaction(s)\n", report_file)

            for idx, row in df.iterrows():
                print_and_log(f"\n{'='*80}", report_file)
                print_and_log(f"WITHDRAWAL TRANSACTION #{idx + 1}", report_file)
                print_and_log(f"{'='*80}", report_file)

                for col in df.columns:
                    print_and_log(f"{col}: {row[col]}", report_file)

        else:
            print_and_log("\nNo withdrawal transactions found in credit_debit table", report_file)

    except Exception as e:
        print_and_log(f"\nError analyzing withdrawal transactions: {str(e)}", report_file)

def main():
    """Main entry point"""

    # Get user ID from command line or use default
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
        except ValueError:
            print("Error: User ID must be a valid integer")
            print("Usage: python3 wallet_analysis.py [user_id]")
            return
    else:
        user_id = TARGET_ACCOUNT
        print(f"No user ID provided, using default: {user_id}")

    print(f"\n{'='*80}")
    print(f"WALLET ANALYSIS")
    print(f"User ID: {user_id}")
    print(f"{'='*80}\n")

    db = DatabaseConnection()

    # Test connection
    if not db.test_connections():
        print("Database connection failed!")
        return

    # Create reports directory
    reports_dir = "forensic_reports"
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file_path = os.path.join(reports_dir, f"wallet_analysis_{user_id}_{timestamp}.txt")

    with open(report_file_path, 'w') as report_file:
        # Write header
        report_file.write(f"WALLET ANALYSIS REPORT\n")
        report_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_file.write(f"User ID: {user_id}\n")
        report_file.write(f"{'='*80}\n")

        # Run all analysis sections
        analyze_wallet_addresses(user_id, db, report_file)
        analyze_ewallets(user_id, db, report_file)
        analyze_ewallet_usage(user_id, db, report_file)
        analyze_deposits(user_id, db, report_file)
        analyze_withdrawals(user_id, db, report_file)

        # Footer
        print_and_log(f"\n{'='*80}", report_file)
        print_and_log(f"ANALYSIS COMPLETE", report_file)
        print_and_log(f"{'='*80}", report_file)
        print_and_log(f"\nReport saved to: {report_file_path}", report_file)

if __name__ == "__main__":
    main()
