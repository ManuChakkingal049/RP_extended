# Bank Recovery Planning & Liquidity Stress Simulator

A regulatory-grade stress testing and recovery planning tool for banks, aligned with Basel III standards and ICAAP/ILAAP frameworks.

## 🎯 Overview

This simulator models balance sheet evolution under stress scenarios and estimates the survival horizon of a bank under liquidity and funding pressure. It supports:

- **Recovery Planning**: Model recovery actions and their impact
- **Contingency Funding Planning**: Test liquidity buffers under stress
- **ICAAP Stress Testing**: Calculate survival horizons and breach points
- **Basel III Compliance**: LCR, NSFR, and capital ratio calculations

## 🚀 Features

### Core Capabilities

1. **Balance Sheet Framework**
   - Full asset and liability structure
   - Dynamic equity calculation
   - Support for multiple security types and deposit classes
   - Real-time validation and balance checks

2. **Stress Scenarios**
   - Multiple time granularities (Daily, Monthly, Quarterly, Yearly)
   - Deposit withdrawal/run-off modeling
   - Market stress parameters (price shocks, fire-sale discounts)
   - Credit deterioration (NPL migration, provisioning)
   - Upload custom scenarios via CSV

3. **Liquidity Management**
   - User-defined asset liquidation priority
   - Asset-specific haircuts and fire-sale penalties
   - Automatic cash management
   - Emergency funding options

4. **Basel III Metrics**
   - Liquidity Coverage Ratio (LCR) with regulatory haircuts
   - Net Stable Funding Ratio (NSFR)
   - CET1, Tier 1, and Total Capital ratios
   - Counterbalancing capacity

5. **Survival Analysis**
   - Period-by-period simulation
   - Configurable breach thresholds
   - Primary driver identification
   - Critical period detection

6. **Security Features**
   - Session management with timeout
   - File upload validation
   - Input sanitization
   - Comprehensive audit logging
   - Rate limiting

## 📋 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the repository**
   ```bash
   cd bank-liquidity-simulator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - The app will open in your default browser
   - Default URL: `http://localhost:8501`

## 📖 User Guide

### 1. Balance Sheet Setup

Create your opening balance sheet using one of three methods:

**Manual Entry:**
- Enter values for each asset and liability category
- System validates balance equation automatically
- View summary metrics instantly

**Upload Data:**
- Upload CSV or Excel file with balance sheet data
- File validation ensures security
- Automatic parsing and validation

**Template:**
- Download pre-formatted template
- Fill in your data
- Upload completed template

### 2. Configure Stress Scenarios

**Time Configuration:**
- Select granularity: Daily, Monthly, Quarterly, or Yearly
- Set number of periods to simulate

**Deposit Withdrawals:**
- Uniform run-off rates by deposit type
- Custom period-by-period withdrawals
- Basel III regulatory standard rates
- Upload CSV with custom scenario data

**Market Stress:**
- Security price shocks by asset class
- Fire-sale discounts (base + incremental)
- Funding spread increases
- Collateral haircut increases

**Credit Deterioration:**
- Loan migration to NPL rate
- Provisioning rate on new NPLs
- RWA increase percentage

### 3. Run Simulation

**Configuration:**
- Select saved scenario
- Define asset liquidation priority (drag to reorder)
- Set breach thresholds (LCR, CET1, Cash minimum)
- Enable/disable recovery actions

**Execution:**
- Click "Run Simulation"
- Monitor progress in real-time
- View quick summary upon completion

### 4. Analyze Results

**Key Metrics:**
- Survival horizon (number of periods)
- Breach type and timing
- Cumulative asset depletion
- Capital erosion percentage

**Visualizations:**
- Balance sheet evolution waterfall
- LCR and NSFR trends over time
- Liquidity buffer depletion
- Capital ratio trajectories
- Deposit outflow analysis
- Asset liquidation breakdown

**Export Options:**
- Excel workbook with detailed results
- PDF report with charts and analysis
- CSV data for further analysis

### 5. Configuration

**Regulatory Parameters:**
- Basel III LCR parameters
- HQLA haircuts and caps
- Capital requirements (CET1, Tier 1, Total)
- Capital conservation buffer

**Haircuts & Discounts:**
- Base haircuts by asset class
- Fire-sale penalties
- Maximum daily sale limits
- Edit in interactive table

**System Settings:**
- Logging level and audit trail
- Data retention policies
- File upload limits
- Session timeout
- Rate limiting

### 6. Audit Log

View complete audit trail:
- All user actions with timestamps
- Session information
- Data access events
- Configuration changes
- Export capability for compliance

## 🔒 Security Features

### File Upload Security
- Extension validation (CSV, XLSX only)
- Size limits (10MB default)
- Content scanning for malicious patterns
- Automatic virus signature checking

### Session Management
- Cryptographically secure session IDs
- Automatic timeout after inactivity
- Session limit enforcement
- Activity tracking

### Input Validation
- Numeric range checking
- String sanitization
- SQL injection prevention
- XSS protection

### Audit Trail
- Structured JSON logging
- Separate error and audit logs
- Log rotation (10MB files, 5 backups)
- Security event tracking

## 🏗️ Architecture

### Project Structure

```
bank-liquidity-simulator/
│
├── app.py                          # Main Streamlit application
│
├── src/
│   ├── balance_sheet.py           # Balance sheet model and calculations
│   ├── stress_scenarios.py        # Scenario definitions and management
│   ├── liquidity_engine.py        # Core simulation engine
│   ├── metrics_calculator.py      # Basel III metrics calculations
│   ├── survival_analyzer.py       # Survival analysis and reporting
│   ├── visualization.py           # Plotly charts and visualizations
│   ├── security.py                # Security features and validation
│   └── logger.py                  # Structured logging system
│
├── logs/                          # Log files (auto-created)
│   ├── app.log                    # Application logs
│   ├── error.log                  # Error logs only
│   └── audit.log                  # Audit trail
│
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### Data Flow

1. **Input**: User creates balance sheet and defines scenarios
2. **Validation**: Security checks and data validation
3. **Simulation**: Period-by-period execution by LiquidityEngine
4. **Analysis**: Metrics calculation and survival analysis
5. **Output**: Results display and export options

### Key Classes

- **BalanceSheet**: Represents and validates balance sheet, calculates ratios
- **StressScenario**: Defines stress parameters and run-off rates
- **LiquidityEngine**: Executes simulation period-by-period
- **MetricsCalculator**: Computes Basel III metrics (LCR, NSFR)
- **SurvivalAnalyzer**: Analyzes breach conditions and survival
- **SecurityManager**: Handles security features
- **AppLogger**: Structured logging system

## 📊 Example Use Cases

### 1. Basel III LCR Compliance Test
- Use "Basel III LCR Standard" predefined scenario
- 30-day horizon with regulatory run-off rates
- Verify LCR remains above 100%

### 2. Severe Stress Test
- Model combined market and funding stress
- 60-90 day horizon
- Identify survival horizon and breach point
- Test recovery action effectiveness

### 3. Idiosyncratic Bank Run
- High deposit withdrawal rates
- Rapid liquidity depletion
- Capital erosion from fire sales
- Recovery planning

### 4. Recovery Planning
- Test various asset liquidation strategies
- Enable/disable recovery actions
- Compare scenarios side-by-side
- Optimize recovery playbook

## 🔧 Configuration Options

### Breach Thresholds (Configurable)
- **LCR Minimum**: Default 100%
- **CET1 Minimum**: Default 4.5%
- **Minimum Cash**: Default €0M
- **Tier 1 Minimum**: Default 6.0%

### Liquidation Haircuts (Customizable)
- Cash: 0%
- HQLA Level 1: 0%
- HQLA Level 2A: 5%
- HQLA Level 2B: 15%
- Other Securities: 25%
- Performing Loans: 30%
- Real Estate: 40%

### Time Granularities
- **Daily**: 1 day per period
- **Monthly**: 30 days per period
- **Quarterly**: 90 days per period
- **Yearly**: 365 days per period

## 📈 Metrics Calculated

### Liquidity Metrics
- **LCR**: Liquidity Coverage Ratio (HQLA / 30-day net outflows)
- **NSFR**: Net Stable Funding Ratio (ASF / RSF)
- **Counterbalancing Capacity**: Unencumbered liquid assets

### Capital Metrics
- **CET1 Ratio**: Common Equity Tier 1 / RWA
- **Tier 1 Ratio**: (CET1 + AT1) / RWA
- **Total Capital Ratio**: (Tier 1 + Tier 2) / RWA
- **Leverage Ratio**: Equity / Total Assets

### Balance Sheet Metrics
- Total Assets, Liabilities, Equity
- Liquid Assets vs Total Assets
- Loan-to-Deposit Ratio
- Asset Depletion (cumulative)

## ⚠️ Limitations & Disclaimers

### Model Limitations
- Simplified RWA calculation (no detailed risk weights)
- Stylized NSFR calculation
- No intra-day liquidity modeling
- No contagion or systemic effects
- Fire-sale impacts are simplified

### Regulatory Compliance
- This tool is for **internal analysis only**
- Not a substitute for official regulatory submissions
- Results should be validated by qualified professionals
- Consult your regulator for official requirements

### Data Privacy
- All data remains local to your session
- No data is transmitted externally
- Sessions timeout after inactivity
- Clear session data regularly

## 🐛 Troubleshooting

### Common Issues

**"Balance sheet validation failed"**
- Check that Assets = Liabilities + Equity
- Ensure all values are non-negative
- Verify numeric inputs are valid

**"File upload failed"**
- Check file size is under 10MB
- Ensure file extension is .csv, .xlsx, or .xls
- Verify file is not corrupted

**"Simulation timeout"**
- Reduce number of periods
- Simplify scenario complexity
- Check system resources

**"No results to display"**
- Ensure simulation completed successfully
- Check for breach in early periods
- Review logs for errors

### Debug Mode

Enable debug logging in Configuration → System Settings:
1. Set Log Level to "DEBUG"
2. Check logs/ directory for detailed logs
3. Review audit.log for action history

## 📝 Best Practices

### Balance Sheet Setup
- Start with validated, audited balance sheet data
- Ensure regulatory capital ratios are realistic
- Include sufficient liquidity buffers
- Document assumptions

### Scenario Design
- Start with Basel standard scenario
- Gradually increase severity
- Test multiple time horizons
- Consider tail risks

### Interpretation
- Survival horizon is indicative, not definitive
- Test sensitivity to assumptions
- Compare multiple scenarios
- Validate with historical stress periods

### Documentation
- Export audit logs regularly
- Save scenarios with descriptive names
- Document configuration changes
- Maintain version history

## 🤝 Support & Contribution

### Getting Help
- Review this README thoroughly
- Check logs for error messages
- Examine audit trail for action history

### Feature Requests
Consider future enhancements:
- Multi-scenario comparison dashboard
- Monte Carlo simulation
- Reverse stress testing
- Management action optimization
- API integration

## 📄 License

This software is provided "as is" for internal analysis and planning purposes.

## 🔄 Version History

**v1.0.0** (Current)
- Initial release
- Core simulation engine
- Basel III metrics
- Security features
- Audit logging
- Interactive UI

---

**Built with**: Python, Streamlit, Pandas, NumPy, Plotly

**Compatible with**: Basel III, ICAAP, ILAAP frameworks

**Last Updated**: February 2026
