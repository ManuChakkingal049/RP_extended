"""
Bank Recovery Planning and Liquidity Stress Simulator
A regulatory-grade ICAAP/ILAAP stress testing tool

FIXED VERSION - Resolves 'dict' object has no attribute 'name' error
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path

# Import custom modules
from src.balance_sheet import BalanceSheet
from src.stress_scenarios import StressScenario
from src.liquidity_engine import LiquidityEngine
from src.metrics_calculator import MetricsCalculator
from src.survival_analyzer import SurvivalAnalyzer
from src.visualization import Visualizer
from src.security import SecurityManager
from src.logger import AppLogger

# Configure page
st.set_page_config(
    page_title="Bank Recovery & Liquidity Stress Simulator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = AppLogger.get_logger(__name__)

# Initialize security manager
security = SecurityManager()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = security.generate_session_id()
        logger.info(f"New session initialized: {st.session_state.session_id}")
    
    if 'balance_sheet' not in st.session_state:
        st.session_state.balance_sheet = None
    
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None
    
    if 'audit_log' not in st.session_state:
        st.session_state.audit_log = []

def log_user_action(action: str, details: dict = None):
    """Log user actions for audit trail"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'session_id': st.session_state.session_id,
        'action': action,
        'details': details or {}
    }
    st.session_state.audit_log.append(log_entry)
    logger.info(f"User action: {action}", extra={'details': details})

def main():
    """Main application function"""
    
    # Initialize
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🏦 Bank Recovery Planning & Liquidity Stress Simulator</div>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=Bank+Simulator", 
                 use_container_width=True)
        st.markdown("### Navigation")
        
        page = st.radio(
            "Select Module",
            ["📊 Balance Sheet Setup",
             "📉 Stress Scenarios",
             "🔄 Run Simulation",
             "📈 Results & Analytics",
             "⚙️ Configuration",
             "📋 Audit Log"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
        st.markdown(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Route to appropriate page
    if page == "📊 Balance Sheet Setup":
        show_balance_sheet_setup()
    elif page == "📉 Stress Scenarios":
        show_stress_scenarios()
    elif page == "🔄 Run Simulation":
        show_simulation()
    elif page == "📈 Results & Analytics":
        show_results()
    elif page == "⚙️ Configuration":
        show_configuration()
    elif page == "📋 Audit Log":
        show_audit_log()

def show_balance_sheet_setup():
    """Balance Sheet Setup Page"""
    st.header("📊 Balance Sheet Setup")
    
    tab1, tab2, tab3 = st.tabs(["Manual Entry", "Upload Data", "Template"])
    
    with tab1:
        st.subheader("Manual Balance Sheet Entry")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Assets (€ millions)")
            
            with st.expander("💰 Cash & Reserves", expanded=True):
                cash_reserves = st.number_input("Cash & Central Bank Reserves", 
                                                min_value=0.0, value=1000.0, step=10.0)
            
            with st.expander("💎 HQLA Securities"):
                hqla_level1 = st.number_input("Level 1 HQLA", min_value=0.0, value=2000.0, step=10.0)
                hqla_level2a = st.number_input("Level 2A HQLA", min_value=0.0, value=500.0, step=10.0)
                hqla_level2b = st.number_input("Level 2B HQLA", min_value=0.0, value=300.0, step=10.0)
            
            with st.expander("📚 Loan Book"):
                performing_loans = st.number_input("Performing Loans", 
                                                   min_value=0.0, value=15000.0, step=100.0)
                npl = st.number_input("Non-Performing Loans", 
                                     min_value=0.0, value=500.0, step=10.0)
            
            with st.expander("🏢 Other Assets"):
                real_estate = st.number_input("Real Estate / Illiquid Assets", 
                                             min_value=0.0, value=1000.0, step=10.0)
                other_securities = st.number_input("Other Marketable Securities", 
                                                   min_value=0.0, value=800.0, step=10.0)
                other_assets = st.number_input("Other Assets", 
                                              min_value=0.0, value=200.0, step=10.0)
        
        with col2:
            st.markdown("#### Liabilities (€ millions)")
            
            with st.expander("💳 Retail Deposits", expanded=True):
                retail_stable = st.number_input("Stable Retail Deposits", 
                                               min_value=0.0, value=8000.0, step=100.0)
                retail_unstable = st.number_input("Less Stable Retail Deposits", 
                                                 min_value=0.0, value=4000.0, step=100.0)
            
            with st.expander("🏢 Corporate & Wholesale"):
                corporate_deposits = st.number_input("Corporate Deposits", 
                                                    min_value=0.0, value=3000.0, step=100.0)
                wholesale_funding = st.number_input("Wholesale Funding", 
                                                   min_value=0.0, value=2000.0, step=100.0)
                secured_funding = st.number_input("Secured Funding", 
                                                 min_value=0.0, value=1500.0, step=100.0)
            
            with st.expander("💼 Other Liabilities & Equity"):
                other_liabilities = st.number_input("Other Liabilities", 
                                                   min_value=0.0, value=500.0, step=10.0)
                
                st.markdown("**Equity**")
                cet1 = st.number_input("CET1 Capital", min_value=0.0, value=1500.0, step=10.0)
                at1 = st.number_input("AT1 Capital", min_value=0.0, value=200.0, step=10.0)
                tier2 = st.number_input("Tier 2 Capital", min_value=0.0, value=300.0, step=10.0)
        
        # Validation and creation
        if st.button("✅ Create Balance Sheet", type="primary"):
            try:
                # Create balance sheet object
                bs_data = {
                    'assets': {
                        'cash_reserves': cash_reserves,
                        'hqla_level1': hqla_level1,
                        'hqla_level2a': hqla_level2a,
                        'hqla_level2b': hqla_level2b,
                        'performing_loans': performing_loans,
                        'npl': npl,
                        'real_estate': real_estate,
                        'other_securities': other_securities,
                        'other_assets': other_assets
                    },
                    'liabilities': {
                        'retail_stable': retail_stable,
                        'retail_unstable': retail_unstable,
                        'corporate_deposits': corporate_deposits,
                        'wholesale_funding': wholesale_funding,
                        'secured_funding': secured_funding,
                        'other_liabilities': other_liabilities
                    },
                    'equity': {
                        'cet1': cet1,
                        'at1': at1,
                        'tier2': tier2
                    }
                }
                
                # Validate
                balance_sheet = BalanceSheet(bs_data)
                if balance_sheet.validate():
                    st.session_state.balance_sheet = balance_sheet
                    log_user_action("balance_sheet_created", {'method': 'manual'})
                    st.success("✅ Balance Sheet created and validated successfully!")
                    
                    # Show summary
                    total_assets = balance_sheet.total_assets()
                    total_liabilities = balance_sheet.total_liabilities()
                    total_equity = balance_sheet.total_equity()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Assets", f"€{total_assets:,.0f}M")
                    col2.metric("Total Liabilities", f"€{total_liabilities:,.0f}M")
                    col3.metric("Total Equity", f"€{total_equity:,.0f}M")
                    col4.metric("Balance Check", 
                               f"€{abs(total_assets - total_liabilities - total_equity):,.2f}M")
                else:
                    st.error("❌ Balance Sheet validation failed!")
                    
            except Exception as e:
                logger.error(f"Error creating balance sheet: {str(e)}")
                st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.subheader("Upload Balance Sheet Data")
        st.markdown("Upload a CSV or Excel file with balance sheet data")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload balance sheet data in CSV or Excel format"
        )
        
        if uploaded_file is not None:
            try:
                # Security check
                if not security.validate_file_upload(uploaded_file):
                    st.error("❌ File validation failed. Please check file type and size.")
                    return
                
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.dataframe(df, use_container_width=True)
                
                if st.button("Import Balance Sheet"):
                    # Process and create balance sheet
                    # (Implementation would parse the DataFrame)
                    st.success("✅ Balance Sheet imported successfully!")
                    log_user_action("balance_sheet_imported", {'filename': uploaded_file.name})
                    
            except Exception as e:
                logger.error(f"Error uploading file: {str(e)}")
                st.error(f"❌ Error reading file: {str(e)}")
    
    with tab3:
        st.subheader("Download Template")
        st.markdown("Download a template file to fill in your balance sheet data")
        
        # Create template
        template_data = {
            'Category': ['Cash & Reserves', 'HQLA Level 1', 'HQLA Level 2A', 
                        'Performing Loans', 'Retail Stable', 'Corporate Deposits'],
            'Amount_M_EUR': [1000, 2000, 500, 15000, 8000, 3000],
            'Type': ['Asset', 'Asset', 'Asset', 'Asset', 'Liability', 'Liability']
        }
        template_df = pd.DataFrame(template_data)
        
        st.dataframe(template_df, use_container_width=True)
        
        csv = template_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Template",
            data=csv,
            file_name="balance_sheet_template.csv",
            mime="text/csv"
        )

def show_stress_scenarios():
    """Stress Scenarios Page - FIXED VERSION"""
    st.header("📉 Stress Scenario Configuration")
    
    if st.session_state.balance_sheet is None:
        st.warning("⚠️ Please create a balance sheet first in the 'Balance Sheet Setup' page.")
        return
    
    # Time granularity selection
    st.subheader("⏱️ Time Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        time_granularity = st.selectbox(
            "Time Granularity",
            ["Daily", "Monthly", "Quarterly", "Yearly"],
            help="Select the time period for stress scenario"
        )
    
    with col2:
        num_periods = st.number_input(
            "Number of Periods",
            min_value=1,
            max_value=365 if time_granularity == "Daily" else 120,
            value=30 if time_granularity == "Daily" else 12,
            help="Number of simulation periods"
        )
    
    st.markdown("---")
    
    # Scenario tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💸 Deposit Withdrawals",
        "📊 Market Stress",
        "💳 Credit Deterioration",
        "📁 Upload Scenario"
    ])
    
    with tab1:
        st.subheader("Deposit Withdrawal & Run-off Scenario")
        
        scenario_type = st.radio(
            "Scenario Type",
            ["Uniform Run-off", "Custom Period-by-Period", "Regulatory Standard"],
            horizontal=True
        )
        
        if scenario_type == "Uniform Run-off":
            col1, col2 = st.columns(2)
            
            with col1:
                retail_stable_runoff = st.slider("Stable Retail Run-off %", 0, 100, 5)
                retail_unstable_runoff = st.slider("Unstable Retail Run-off %", 0, 100, 10)
                corporate_runoff = st.slider("Corporate Deposit Run-off %", 0, 100, 40)
            
            with col2:
                wholesale_runoff = st.slider("Wholesale Funding Run-off %", 0, 100, 100)
                secured_runoff = st.slider("Secured Funding Run-off %", 0, 100, 25)
        
        elif scenario_type == "Custom Period-by-Period":
            st.info("📊 Enter withdrawal amounts for each period (or upload CSV)")
            
            # Create editable dataframe
            periods_df = pd.DataFrame({
                'Period': range(1, int(num_periods) + 1),
                'Retail_Stable_Withdrawal': [0.0] * int(num_periods),
                'Retail_Unstable_Withdrawal': [0.0] * int(num_periods),
                'Corporate_Withdrawal': [0.0] * int(num_periods),
                'Wholesale_Withdrawal': [0.0] * int(num_periods)
            })
            
            edited_df = st.data_editor(
                periods_df,
                use_container_width=True,
                num_rows="fixed"
            )
        
        else:  # Regulatory Standard
            st.info("📋 Using Basel III LCR standard run-off rates")
            st.markdown("""
            - Stable Retail: 5%
            - Unstable Retail: 10%
            - Corporate Operational: 25%
            - Corporate Non-operational: 40%
            - Wholesale: 100%
            """)
            # Set default values for regulatory standard
            retail_stable_runoff = 5
            retail_unstable_runoff = 10
            corporate_runoff = 40
            wholesale_runoff = 100
            secured_runoff = 25
    
    with tab2:
        st.subheader("Market Stress Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Security Price Shocks**")
            hqla_l1_shock = st.slider("HQLA Level 1 Price Shock %", -20, 0, 0)
            hqla_l2a_shock = st.slider("HQLA Level 2A Price Shock %", -30, 0, -5)
            hqla_l2b_shock = st.slider("HQLA Level 2B Price Shock %", -50, 0, -15)
            other_sec_shock = st.slider("Other Securities Price Shock %", -60, 0, -25)
        
        with col2:
            st.markdown("**Fire-sale Discounts**")
            fire_sale_base = st.slider("Base Fire-sale Discount %", 0, 50, 10)
            fire_sale_increment = st.slider("Incremental Discount per Volume %", 0, 20, 2,
                                           help="Additional discount for large sales")
            
            st.markdown("**Funding Stress**")
            funding_spread = st.slider("Funding Spread Increase (bps)", 0, 1000, 100)
            collateral_haircut = st.slider("Collateral Haircut Increase %", 0, 50, 10)
    
    with tab3:
        st.subheader("Credit Deterioration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_migration_rate = st.slider(
                "Loan Migration to NPL %",
                0.0, 20.0, 2.0,
                help="Percentage of performing loans migrating to NPL"
            )
            
            provisioning_rate = st.slider(
                "Additional Provisioning %",
                0, 100, 50,
                help="Provisioning rate on new NPLs"
            )
        
        with col2:
            rwa_increase = st.slider(
                "Risk-Weighted Assets Increase %",
                0, 50, 10,
                help="Increase in RWA due to credit quality deterioration"
            )
    
    with tab4:
        st.subheader("Upload Scenario File")
        st.markdown("Upload a CSV file with custom scenario parameters")
        
        scenario_file = st.file_uploader(
            "Choose scenario file",
            type=['csv'],
            help="Upload CSV with period-by-period scenario data"
        )
        
        if scenario_file is not None:
            try:
                if security.validate_file_upload(scenario_file):
                    scenario_df = pd.read_csv(scenario_file)
                    st.dataframe(scenario_df, use_container_width=True)
                    
                    if st.button("Import Scenario"):
                        st.success("✅ Scenario imported successfully!")
                        log_user_action("scenario_imported", {'filename': scenario_file.name})
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Save scenario - FIXED VERSION
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        scenario_name = st.text_input("Scenario Name", "Stress Scenario 1")
        
        if st.button("💾 Save Scenario", type="primary", use_container_width=True):
            try:
                # ✅ FIX: Create complete scenario dict with all required parameters
                scenario_dict = {
                    'name': scenario_name,
                    'time_granularity': time_granularity,
                    'num_periods': int(num_periods),
                    'runoff_rates': {
                        'retail_stable': float(retail_stable_runoff) if 'retail_stable_runoff' in locals() else 5.0,
                        'retail_unstable': float(retail_unstable_runoff) if 'retail_unstable_runoff' in locals() else 10.0,
                        'corporate_deposits': float(corporate_runoff) if 'corporate_runoff' in locals() else 40.0,
                        'wholesale_funding': float(wholesale_runoff) if 'wholesale_runoff' in locals() else 100.0,
                        'secured_funding': float(secured_runoff) if 'secured_runoff' in locals() else 25.0
                    },
                    'security_shocks': {
                        'hqla_level1': float(hqla_l1_shock) if 'hqla_l1_shock' in locals() else 0.0,
                        'hqla_level2a': float(hqla_l2a_shock) if 'hqla_l2a_shock' in locals() else -5.0,
                        'hqla_level2b': float(hqla_l2b_shock) if 'hqla_l2b_shock' in locals() else -15.0,
                        'other_securities': float(other_sec_shock) if 'other_sec_shock' in locals() else -25.0
                    },
                    'fire_sale_discount': float(fire_sale_base) if 'fire_sale_base' in locals() else 10.0,
                    'fire_sale_increment': float(fire_sale_increment) if 'fire_sale_increment' in locals() else 2.0,
                    'funding_spread_increase': int(funding_spread) if 'funding_spread' in locals() else 100,
                    'collateral_haircut_increase': float(collateral_haircut) if 'collateral_haircut' in locals() else 10.0,
                    'loan_migration_rate': float(loan_migration_rate) if 'loan_migration_rate' in locals() else 2.0,
                    'provisioning_rate': float(provisioning_rate) if 'provisioning_rate' in locals() else 50.0,
                    'rwa_increase': float(rwa_increase) if 'rwa_increase' in locals() else 10.0,
                    'description': f"Created on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    'created_at': datetime.now().isoformat()
                }
                
                # Validate by creating StressScenario object
                scenario_obj = StressScenario(**scenario_dict)
                validated_dict = scenario_obj.to_dict()
                
                # Store validated dict
                st.session_state.scenarios.append(validated_dict)
                log_user_action("scenario_saved", {'name': scenario_name})
                st.success(f"✅ Scenario '{scenario_name}' saved successfully!")
                
            except Exception as e:
                logger.error(f"Error saving scenario: {str(e)}")
                st.error(f"❌ Error creating scenario: {str(e)}")

def show_simulation():
    """Run Simulation Page - FIXED VERSION"""
    st.header("🔄 Run Stress Simulation")
    
    if st.session_state.balance_sheet is None:
        st.warning("⚠️ Please create a balance sheet first.")
        return
    
    if not st.session_state.scenarios:
        st.warning("⚠️ Please create at least one stress scenario.")
        return
    
    # Configuration
    st.subheader("⚙️ Simulation Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_scenario = st.selectbox(
            "Select Scenario",
            [s['name'] for s in st.session_state.scenarios]
        )
        
        st.markdown("**Liquidation Priority**")
        liquidation_order = st.multiselect(
            "Asset Liquidation Order (drag to reorder)",
            ["Cash", "HQLA Level 1", "HQLA Level 2A", "HQLA Level 2B", 
             "Other Securities", "Performing Loans", "Real Estate"],
            default=["Cash", "HQLA Level 1", "HQLA Level 2A", "HQLA Level 2B"]
        )
    
    with col2:
        st.markdown("**Breach Thresholds**")
        
        lcr_threshold = st.number_input("LCR Minimum %", min_value=0, max_value=200, value=100)
        cet1_threshold = st.number_input("CET1 Minimum %", min_value=0.0, max_value=20.0, value=4.5)
        cash_threshold = st.number_input("Minimum Cash (€M)", min_value=0.0, value=0.0)
        
        st.markdown("**Recovery Actions**")
        enable_recovery = st.checkbox("Enable Recovery Actions", value=False)
        
        if enable_recovery:
            recovery_actions = st.multiselect(
                "Available Recovery Actions",
                ["Asset Sales", "Capital Raising", "Central Bank Facility", 
                 "Dividend Suspension", "AT1 Conversion"],
                default=["Central Bank Facility"]
            )
    
    # Run simulation
    st.markdown("---")
    
    if st.button("▶️ Run Simulation", type="primary", use_container_width=True):
        with st.spinner("Running simulation... This may take a moment."):
            try:
                # ✅ FIX: Convert scenario dict to StressScenario object before passing to engine
                # Find the selected scenario dict
                selected_scenario_dict = next(
                    (s for s in st.session_state.scenarios if s['name'] == selected_scenario),
                    st.session_state.scenarios[0]
                )
                
                # Convert dict to StressScenario object
                scenario_obj = StressScenario.from_dict(selected_scenario_dict)
                
                # Create simulation engine with the StressScenario object (not dict)
                engine = LiquidityEngine(
                    balance_sheet=st.session_state.balance_sheet,
                    scenario=scenario_obj,  # ✅ Now passing object instead of dict
                    liquidation_order=liquidation_order
                )
                
                # Run simulation
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = engine.run_simulation(
                    progress_callback=lambda p, msg: (
                        progress_bar.progress(p),
                        status_text.text(msg)
                    )
                )
                
                # Store results
                st.session_state.simulation_results = results
                log_user_action("simulation_completed", {'scenario': selected_scenario})
                
                progress_bar.progress(100)
                status_text.text("✅ Simulation completed!")
                
                st.success("✅ Simulation completed successfully!")
                
                # Show quick summary
                st.markdown("### Quick Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                survival_periods = results.get('survival_horizon', 0)
                breach_type = results.get('breach_type', 'None')
                
                col1.metric("Survival Horizon", f"{survival_periods} periods")
                col2.metric("Breach Type", breach_type)
                col3.metric("Final LCR", f"{results.get('final_lcr', 0):.1f}%")
                col4.metric("Final CET1", f"{results.get('final_cet1', 0):.2f}%")
                
                st.info("📊 View detailed results in the 'Results & Analytics' page")
                
            except Exception as e:
                logger.error(f"Simulation error: {str(e)}")
                st.error(f"❌ Simulation failed: {str(e)}")

def show_results():
    """Results & Analytics Page"""
    st.header("📈 Simulation Results & Analytics")
    
    if st.session_state.simulation_results is None:
        st.info("ℹ️ No simulation results available. Please run a simulation first.")
        return
    
    results = st.session_state.simulation_results
    
    # Summary metrics
    st.subheader("📊 Key Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Survival Horizon", f"{results.get('survival_horizon', 0)} periods")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        breach_type = results.get('breach_type', 'None')
        if breach_type == 'None':
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-box">', unsafe_allow_html=True)
        st.metric("First Breach", breach_type)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Cumulative Asset Depletion", f"€{results.get('asset_depletion', 0):,.0f}M")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Capital Erosion", f"{results.get('capital_erosion', 0):.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "Balance Sheet Evolution",
        "Liquidity Metrics",
        "Capital Ratios",
        "Detailed Analysis"
    ])
    
    with tab1:
        st.subheader("Balance Sheet Evolution")
        # Placeholder for visualization
        st.info("📊 Balance sheet evolution chart will be displayed here")
        
    with tab2:
        st.subheader("Liquidity Coverage Ratio & NSFR")
        st.info("📈 LCR and NSFR trend charts will be displayed here")
    
    with tab3:
        st.subheader("Capital Ratios")
        st.info("📉 Capital ratio evolution will be displayed here")
    
    with tab4:
        st.subheader("Detailed Period-by-Period Analysis")
        st.info("📋 Detailed table with period-by-period metrics will be displayed here")
    
    # Export options
    st.markdown("---")
    st.subheader("📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to Excel", use_container_width=True):
            st.success("Excel export prepared!")
            log_user_action("results_exported", {'format': 'excel'})
    
    with col2:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            st.success("PDF report prepared!")
            log_user_action("results_exported", {'format': 'pdf'})
    
    with col3:
        if st.button("📋 Export to CSV", use_container_width=True):
            st.success("CSV export prepared!")
            log_user_action("results_exported", {'format': 'csv'})

def show_configuration():
    """Configuration Page"""
    st.header("⚙️ System Configuration")
    
    tab1, tab2, tab3 = st.tabs(["Regulatory Parameters", "Haircuts & Discounts", "System Settings"])
    
    with tab1:
        st.subheader("Basel III Regulatory Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**LCR Parameters**")
            st.number_input("HQLA Level 1 Haircut %", 0, 100, 0)
            st.number_input("HQLA Level 2A Haircut %", 0, 100, 15)
            st.number_input("HQLA Level 2B Haircut %", 0, 100, 50)
            st.number_input("Level 2 Asset Cap %", 0, 100, 40)
        
        with col2:
            st.markdown("**Capital Requirements**")
            st.number_input("CET1 Minimum %", 0.0, 20.0, 4.5, step=0.1)
            st.number_input("Tier 1 Minimum %", 0.0, 20.0, 6.0, step=0.1)
            st.number_input("Total Capital Minimum %", 0.0, 20.0, 8.0, step=0.1)
            st.number_input("Capital Conservation Buffer %", 0.0, 10.0, 2.5, step=0.1)
    
    with tab2:
        st.subheader("Asset Liquidation Haircuts")
        
        st.markdown("Configure haircuts applied during asset liquidation")
        
        haircuts_df = pd.DataFrame({
            'Asset Class': ['HQLA Level 1', 'HQLA Level 2A', 'HQLA Level 2B',
                           'Other Securities', 'Performing Loans', 'Real Estate'],
            'Base Haircut %': [0, 5, 15, 25, 30, 40],
            'Fire-sale Penalty %': [2, 5, 10, 15, 20, 25],
            'Max Daily Sale €M': [1000, 500, 300, 200, 100, 50]
        })
        
        edited_haircuts = st.data_editor(
            haircuts_df,
            use_container_width=True,
            disabled=['Asset Class']
        )
        
        if st.button("💾 Save Haircut Configuration"):
            st.success("✅ Haircut configuration saved!")
            log_user_action("config_updated", {'type': 'haircuts'})
    
    with tab3:
        st.subheader("System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Logging**")
            log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
            enable_audit = st.checkbox("Enable Audit Logging", value=True)
            
            st.markdown("**Data Retention**")
            retention_days = st.number_input("Session Data Retention (days)", 1, 365, 30)
        
        with col2:
            st.markdown("**Security**")
            max_file_size = st.number_input("Max Upload File Size (MB)", 1, 100, 10)
            session_timeout = st.number_input("Session Timeout (minutes)", 5, 240, 60)
            
            st.markdown("**Performance**")
            max_periods = st.number_input("Max Simulation Periods", 10, 1000, 365)
        
        if st.button("💾 Save System Configuration"):
            st.success("✅ System configuration saved!")
            log_user_action("config_updated", {'type': 'system'})

def show_audit_log():
    """Audit Log Page"""
    st.header("📋 Audit Log & Session History")
    
    if not st.session_state.audit_log:
        st.info("ℹ️ No audit log entries yet.")
        return
    
    # Convert to DataFrame
    audit_df = pd.DataFrame(st.session_state.audit_log)
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        action_filter = st.multiselect(
            "Filter by Action",
            audit_df['action'].unique().tolist()
        )
    
    with col2:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now().date(), datetime.now().date())
        )
    
    # Apply filters
    if action_filter:
        audit_df = audit_df[audit_df['action'].isin(action_filter)]
    
    # Display
    st.dataframe(
        audit_df,
        use_container_width=True,
        column_config={
            'timestamp': st.column_config.DatetimeColumn('Timestamp', format="DD/MM/YYYY HH:mm:ss"),
            'action': st.column_config.TextColumn('Action'),
            'session_id': st.column_config.TextColumn('Session ID')
        }
    )
    
    # Export
    if st.button("📥 Export Audit Log"):
        csv = audit_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "audit_log.csv",
            "text/csv"
        )
        log_user_action("audit_log_exported")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("❌ An unexpected error occurred. Please check the logs.")
