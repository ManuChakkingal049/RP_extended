"""
Application Configuration
Centralized configuration for the Bank Liquidity Simulator
"""

import os
from pathlib import Path

# Application Info
APP_NAME = "Bank Recovery Planning & Liquidity Stress Simulator"
APP_VERSION = "1.0.0"
APP_ICON = "🏦"

# Paths
BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / "src"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Security Settings
SECURITY = {
    'MAX_FILE_SIZE_MB': 10,
    'ALLOWED_EXTENSIONS': ['.csv', '.xlsx', '.xls'],
    'SESSION_TIMEOUT_MINUTES': 60,
    'MAX_SESSIONS': 100,
    'RATE_LIMIT_ACTIONS_PER_MINUTE': 10,
}

# Logging Settings
LOGGING = {
    'LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'LOG_TO_FILE': True,
    'LOG_TO_CONSOLE': True,
    'STRUCTURED_LOGGING': True,
    'MAX_LOG_SIZE_MB': 10,
    'LOG_BACKUP_COUNT': 5,
}

# Regulatory Parameters (Basel III)
REGULATORY = {
    'LCR_MINIMUM': 100.0,  # %
    'NSFR_MINIMUM': 100.0,  # %
    'CET1_MINIMUM': 4.5,  # %
    'TIER1_MINIMUM': 6.0,  # %
    'TOTAL_CAPITAL_MINIMUM': 8.0,  # %
    'CAPITAL_CONSERVATION_BUFFER': 2.5,  # %
    'HQLA_LEVEL1_HAIRCUT': 0.0,  # %
    'HQLA_LEVEL2A_HAIRCUT': 15.0,  # %
    'HQLA_LEVEL2B_HAIRCUT': 50.0,  # %
    'LEVEL2_ASSET_CAP': 40.0,  # % of total HQLA
}

# Asset Liquidation Haircuts
HAIRCUTS = {
    'cash_reserves': 0.0,
    'hqla_level1': 0.0,
    'hqla_level2a': 5.0,
    'hqla_level2b': 15.0,
    'other_securities': 25.0,
    'performing_loans': 30.0,
    'real_estate': 40.0,
    'other_assets': 35.0,
}

# Fire-sale Parameters
FIRE_SALE = {
    'BASE_DISCOUNT': 10.0,  # %
    'INCREMENTAL_DISCOUNT': 2.0,  # % per 10% of asset sold
    'MAX_DISCOUNT': 50.0,  # %
}

# Run-off Rates (Basel III Standard)
BASEL_RUNOFF_RATES = {
    'retail_stable': 5.0,  # %
    'retail_unstable': 10.0,  # %
    'corporate_operational': 25.0,  # %
    'corporate_non_operational': 40.0,  # %
    'corporate_deposits': 40.0,  # % (blended)
    'wholesale_funding': 100.0,  # %
    'secured_funding': 25.0,  # %
}

# RWA Weights (Simplified)
RWA_WEIGHTS = {
    'cash_reserves': 0.0,
    'hqla_level1': 0.0,
    'hqla_level2a': 0.2,
    'hqla_level2b': 0.5,
    'performing_loans': 1.0,
    'npl': 1.5,
    'real_estate': 1.0,
    'other_securities': 0.5,
    'other_assets': 1.0,
}

# Simulation Defaults
SIMULATION = {
    'DEFAULT_TIME_GRANULARITY': 'Daily',
    'DEFAULT_PERIODS': 30,
    'MAX_PERIODS': 365,
    'DEFAULT_LIQUIDATION_ORDER': [
        'Cash',
        'HQLA Level 1',
        'HQLA Level 2A',
        'HQLA Level 2B',
        'Other Securities',
        'Performing Loans',
        'Real Estate'
    ],
}

# UI Settings
UI = {
    'PAGE_TITLE': APP_NAME,
    'PAGE_ICON': APP_ICON,
    'LAYOUT': 'wide',
    'INITIAL_SIDEBAR_STATE': 'expanded',
    'CHART_HEIGHT': 500,
    'CHART_TEMPLATE': 'plotly_white',
}

# Data Validation
VALIDATION = {
    'MIN_BALANCE_SHEET_SIZE': 100,  # € millions
    'MAX_BALANCE_SHEET_SIZE': 1000000,  # € millions
    'BALANCE_TOLERANCE': 1.0,  # € millions (for A = L + E check)
    'MIN_CET1_RATIO': 0.0,  # %
    'MAX_CET1_RATIO': 50.0,  # %
    'MIN_LCR': 0.0,  # %
    'MAX_LCR': 1000.0,  # %
}

# Export Settings
EXPORT = {
    'EXCEL_ENGINE': 'openpyxl',
    'CSV_ENCODING': 'utf-8',
    'DECIMAL_PLACES': 2,
    'DATE_FORMAT': '%Y-%m-%d',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}

# Recovery Actions (for future implementation)
RECOVERY_ACTIONS = [
    'Asset Sales',
    'Capital Raising',
    'Central Bank Facility',
    'Dividend Suspension',
    'AT1 Conversion',
    'Liability Management Exercise',
    'Branch Closures',
    'Staff Reductions',
]

# Predefined Scenarios
PREDEFINED_SCENARIOS = [
    {
        'name': 'Basel III LCR Standard',
        'description': 'Standard 30-day Basel III LCR stress scenario',
        'time_granularity': 'Daily',
        'num_periods': 30,
    },
    {
        'name': 'Severe Combined Stress',
        'description': 'Severe stress with deposit runs and market shocks',
        'time_granularity': 'Daily',
        'num_periods': 60,
    },
    {
        'name': 'Idiosyncratic Crisis',
        'description': 'Bank-specific crisis with major deposit flight',
        'time_granularity': 'Daily',
        'num_periods': 90,
    },
]

# Alert Thresholds
ALERTS = {
    'LCR_WARNING': 110.0,  # % - show warning
    'LCR_CRITICAL': 105.0,  # % - show critical alert
    'CET1_WARNING': 5.5,  # % - show warning
    'CET1_CRITICAL': 5.0,  # % - show critical alert
    'LIQUIDITY_WARNING': 0.1,  # Ratio - liquid assets / total assets
}

# Environment-specific overrides
ENV = os.getenv('APP_ENV', 'development')

if ENV == 'production':
    LOGGING['LEVEL'] = 'WARNING'
    SECURITY['SESSION_TIMEOUT_MINUTES'] = 30
elif ENV == 'testing':
    LOGGING['LEVEL'] = 'DEBUG'
    SECURITY['MAX_FILE_SIZE_MB'] = 5

# Feature Flags
FEATURES = {
    'ENABLE_RECOVERY_ACTIONS': False,  # Future feature
    'ENABLE_MONTE_CARLO': False,  # Future feature
    'ENABLE_SCENARIO_COMPARISON': False,  # Future feature
    'ENABLE_REVERSE_STRESS': False,  # Future feature
    'ENABLE_EXPORTS': True,
    'ENABLE_FILE_UPLOAD': True,
    'ENABLE_AUDIT_LOG': True,
}

# Help and Documentation
HELP_TEXT = {
    'balance_sheet': """
    **Balance Sheet Setup**
    
    Enter your bank's opening balance sheet. All values should be in € millions.
    The system will automatically validate that Assets = Liabilities + Equity.
    
    - **Assets**: Cash, HQLA securities, loans, and other assets
    - **Liabilities**: Deposits, funding, and other liabilities  
    - **Equity**: CET1, AT1, and Tier 2 capital
    """,
    
    'stress_scenario': """
    **Stress Scenario Configuration**
    
    Define the stress parameters for your simulation:
    
    - **Time Granularity**: How frequently to simulate (Daily, Monthly, etc.)
    - **Deposit Withdrawals**: Run-off rates by deposit type
    - **Market Stress**: Price shocks and fire-sale discounts
    - **Credit Deterioration**: Loan migrations and provisioning
    """,
    
    'simulation': """
    **Running the Simulation**
    
    Configure and execute your stress test:
    
    - **Liquidation Priority**: Order in which assets are sold
    - **Breach Thresholds**: When to stop the simulation
    - **Recovery Actions**: Optional actions to extend survival
    
    The simulation runs period-by-period until breach or completion.
    """,
}

# Tooltips
TOOLTIPS = {
    'lcr': 'Liquidity Coverage Ratio: HQLA / 30-day net outflows. Minimum 100% required.',
    'nsfr': 'Net Stable Funding Ratio: Available stable funding / Required stable funding. Minimum 100% required.',
    'cet1': 'Common Equity Tier 1 ratio: CET1 capital / Risk-weighted assets. Minimum 4.5% required.',
    'hqla_l1': 'Highest quality liquid assets with 0% haircut (e.g., central bank reserves, government bonds)',
    'hqla_l2a': 'High quality liquid assets with 15% haircut (e.g., high-rated corporate bonds)',
    'hqla_l2b': 'Lower quality liquid assets with 50% haircut (e.g., lower-rated securities)',
    'fire_sale': 'Additional discount applied when selling assets in stressed conditions',
}
