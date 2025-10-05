"""
Enhanced Configuration for Forensic Audit System
Focused on Account 88295329 Analysis
"""

# MySQL Database Configuration - Updated for WSL to Windows connection
MYSQL_CONFIG = {
    'host': '172.18.176.1',  # Windows host IP for WSL connection
    'port': 3306,
    'user': 'wsl_user',
    'password': 'Neezbeez20',
    'charset': 'utf8mb4',
    'autocommit': True,
    'connect_timeout': 30,
    'sql_mode': 'TRADITIONAL'
}

# Database Names
RAW_DATABASE = 'crypto_transactions_raw'
CLEANED_DATABASE = 'crypto_transactions_cleaned'

# Primary Target Account for Forensic Analysis
TARGET_ACCOUNT = 88295329

# Priority Accounts for Comparative Analysis (if needed)
PRIORITY_ACCOUNTS = [
    88295329, 25907866, 8868196, 44737950, 94828779,
    7757674, 9574673, 46334234, 39401335, 3326780
]

# Forensic Analysis Configuration
FORENSIC_CONFIG = {
    'target_account': TARGET_ACCOUNT,
    'large_transaction_threshold': 10000,
    'suspicious_time_window_hours': 24,
    'outlier_std_threshold': 2.5,
    'round_amount_threshold': 100,  # Detect round numbers (multiples of this)
    'balance_tolerance': 0.01,  # Tolerance for balance discrepancies
    'hash_algorithm': 'sha256'
}

# Anomaly Detection Thresholds
ANOMALY_THRESHOLDS = {
    'amount_percentile_high': 99.5,
    'amount_percentile_low': 0.5,
    'frequency_threshold': 10,  # Transactions per hour
    'duplicate_time_window': 300,  # 5 minutes in seconds
    'business_hours_start': 9,
    'business_hours_end': 17,
    'weekend_transaction_flag': True
}

# Data Quality Thresholds
DATA_QUALITY_THRESHOLDS = {
    'completeness_threshold': 0.95,  # 95% completeness required
    'consistency_threshold': 0.98,   # 98% consistency required
    'accuracy_threshold': 0.99,      # 99% accuracy required
    'integrity_threshold': 0.99      # 99% integrity required
}

# Reporting Configuration
REPORTING_CONFIG = {
    'output_directory': './forensic_reports/',
    'report_formats': ['json', 'csv', 'excel', 'pdf'],
    'chart_format': 'png',
    'chart_dpi': 300,
    'include_visualizations': True,
    'executive_summary': True,
    'technical_details': True
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': './forensic_reports/forensic_audit.log',
    'max_bytes': 10485760,  # 10MB
    'backup_count': 5
}

# Visualization Settings
VISUALIZATION_CONFIG = {
    'figure_size': (12, 8),
    'color_palette': 'viridis',
    'style': 'whitegrid',
    'font_size': 12,
    'title_size': 16,
    'chart_dpi': 300,
    'save_plots': True,
    'show_plots': False  # Set to True for interactive mode
}

# Database Query Timeouts and Limits
QUERY_CONFIG = {
    'timeout_seconds': 300,  # 5 minutes
    'parallel_processing': True,
    'cache_results': True
}