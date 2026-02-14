# Bank Liquidity Simulator - Quick Reference Guide

## 🚀 Getting Started (5 Minutes)

### Installation
```bash
# Install dependencies
pip install streamlit pandas numpy plotly openpyxl --break-system-packages

# Run the application
streamlit run app.py

# Open browser to: http://localhost:8501
```

### First Simulation (Step-by-Step)

#### 1. Create Balance Sheet (2 minutes)
```
Navigate to: Balance Sheet Setup → Manual Entry

Enter these values (in € millions):

Assets:
- Cash & Reserves: 1000
- HQLA Level 1: 2000
- HQLA Level 2A: 500
- HQLA Level 2B: 300
- Performing Loans: 15000
- NPL: 500
- Real Estate: 1000
- Other Securities: 800
- Other Assets: 200
TOTAL ASSETS: 21,300

Liabilities:
- Stable Retail: 8000
- Unstable Retail: 4000
- Corporate: 3000
- Wholesale: 2000
- Secured: 1500
- Other: 800
TOTAL LIABILITIES: 19,300

Equity:
- CET1: 1200
- AT1: 200
- Tier 2: 100
TOTAL EQUITY: 1,500

Click: "Create Balance Sheet" ✓
```

#### 2. Create Scenario (1 minute)
```
Navigate to: Stress Scenarios

Time Configuration:
- Time Granularity: Daily
- Number of Periods: 30

Deposit Withdrawals:
- Select: "Regulatory Standard"
  (Uses Basel III standard rates)

Click: "Save Scenario" ✓
```

#### 3. Run Simulation (1 minute)
```
Navigate to: Run Simulation

Configuration:
- Select Scenario: "Stress Scenario 1"
- Liquidation Priority: 
  ✓ Cash
  ✓ HQLA Level 1
  ✓ HQLA Level 2A
  ✓ HQLA Level 2B
  
- Breach Thresholds:
  LCR Minimum: 100%
  CET1 Minimum: 4.5%
  
Click: "Run Simulation" ▶️

Wait for completion (~10 seconds)
```

#### 4. View Results (1 minute)
```
Navigate to: Results & Analytics

View:
- Survival Horizon: X periods
- Breach Type: None / LCR / CET1
- Asset Depletion: €X million
- Capital Erosion: X%

Export:
- Click "Export to Excel" for detailed results
```

---

## 📊 Common Scenarios

### Scenario A: Basel III Compliance Test
**Purpose**: Verify 100% LCR requirement

```
Scenario Settings:
- Name: "Basel LCR Test"
- Time: Daily, 30 periods
- Run-off Rates: Regulatory Standard
  • Stable Retail: 5%
  • Unstable Retail: 10%
  • Corporate: 40%
  • Wholesale: 100%
- Market Shocks: None
- Fire-sale: 0%

Expected Result: 
✓ Survives 30 days
✓ LCR > 100% throughout
```

### Scenario B: Moderate Stress
**Purpose**: Test resilience under adverse conditions

```
Scenario Settings:
- Name: "Moderate Stress"
- Time: Daily, 60 periods
- Run-off Rates:
  • Stable Retail: 10%
  • Unstable Retail: 20%
  • Corporate: 50%
  • Wholesale: 100%
- Market Shocks:
  • HQLA L2A: -5%
  • HQLA L2B: -15%
  • Other Securities: -25%
- Fire-sale: 10% base

Expected Result:
? Survives 40-60 days
? LCR may breach
```

### Scenario C: Severe Crisis
**Purpose**: Extreme stress test

```
Scenario Settings:
- Name: "Severe Crisis"
- Time: Daily, 90 periods
- Run-off Rates:
  • Stable Retail: 20%
  • Unstable Retail: 40%
  • Corporate: 70%
  • Wholesale: 100%
- Market Shocks:
  • HQLA L2A: -15%
  • HQLA L2B: -35%
  • Other Securities: -50%
- Fire-sale: 20% base + 5% incremental

Expected Result:
✗ Breaches in 15-30 days
✗ Significant losses
```

---

## 🎯 Key Metrics Cheat Sheet

### LCR (Liquidity Coverage Ratio)
```
Formula: HQLA / 30-day Net Outflows
Minimum: 100%
Meaning: Can survive 30-day stress?

Good: >120%
Warning: 100-110%
Critical: <100%
```

### NSFR (Net Stable Funding Ratio)
```
Formula: Available Stable Funding / Required Stable Funding
Minimum: 100%
Meaning: Structural funding stability

Good: >110%
Warning: 100-105%
Critical: <100%
```

### CET1 Ratio
```
Formula: CET1 Capital / Risk-Weighted Assets
Minimum: 4.5% (+ buffers)
Meaning: Core capital adequacy

Good: >8%
Warning: 5-7%
Critical: <5%
```

### Survival Horizon
```
Definition: Periods until first breach
Measurement: Number of periods

Resilient: >30 periods
Moderate: 15-30 periods
Vulnerable: <15 periods
```

---

## ⚙️ Configuration Quick Reference

### Haircuts (Asset Liquidation)
```
Cash & Reserves:        0%   (no loss)
HQLA Level 1:           0%   (sovereign bonds)
HQLA Level 2A:          5%   (high-grade corporate)
HQLA Level 2B:         15%   (lower-grade securities)
Other Securities:      25%   (illiquid securities)
Performing Loans:      30%   (loan portfolios)
Real Estate:           40%   (illiquid assets)
```

### Run-off Rates (Basel III Standard)
```
Retail Stable:          5%   (insured, relationship)
Retail Unstable:       10%   (non-operational)
Corporate Operational: 25%   (operational accounts)
Corporate Non-op:      40%   (investment accounts)
Wholesale:            100%   (unsecured wholesale)
Secured Funding:       25%   (repo, covered bonds)
```

### Breach Thresholds (Adjustable)
```
LCR Minimum:         100%   (regulatory)
NSFR Minimum:        100%   (regulatory)
CET1 Minimum:        4.5%   (regulatory)
Tier 1 Minimum:      6.0%   (regulatory)
Total Capital:       8.0%   (regulatory)

Management Triggers (suggested):
LCR Warning:         110%
CET1 Warning:        5.5%
```

---

## 🔧 Troubleshooting

### Problem: "Balance sheet validation failed"
```
Check:
1. Assets = Liabilities + Equity?
2. All values ≥ 0?
3. Realistic proportions?

Fix: Adjust equity to balance
Example: If A=21,300 and L=19,300, then E should = 2,000
```

### Problem: "Simulation completes immediately"
```
Check:
1. Balance sheet created? ✓
2. Scenario saved? ✓
3. Periods > 0? ✓

Fix: Create balance sheet and scenario first
```

### Problem: "LCR shows 999.9%"
```
Meaning: Net outflows are zero or negative
Cause: Very small deposits or strong inflows
Action: This is technically valid (infinite LCR)
```

### Problem: "CET1 ratio is negative"
```
Meaning: Capital has been depleted
Cause: Realized losses exceed capital
Action: This triggers immediate breach
```

---

## 📁 File Formats

### Balance Sheet CSV Format
```csv
Category,Item,Amount_M_EUR
Assets,Cash & Central Bank Reserves,1000
Assets,HQLA Level 1,2000
Assets,Performing Loans,15000
Liabilities,Stable Retail Deposits,8000
Liabilities,Corporate Deposits,3000
Equity,CET1 Capital,1500
```

### Scenario CSV Format
```csv
Period,Retail_Stable_Withdrawal,Retail_Unstable_Withdrawal,Corporate_Withdrawal
1,100,200,300
2,150,250,350
3,200,300,400
...
```

---

## 🎓 Interpretation Guide

### When LCR Breaches First
```
Meaning: Liquidity exhaustion
Root Cause: Insufficient HQLA buffer
Actions:
- Increase HQLA holdings
- Diversify funding sources
- Reduce reliance on wholesale
```

### When CET1 Breaches First
```
Meaning: Capital depletion from losses
Root Cause: High fire-sale haircuts
Actions:
- Reduce need for liquidation
- Improve asset quality
- Consider capital raising
```

### When Both Breach Together
```
Meaning: Severe combined stress
Root Cause: Rapid deterioration
Actions:
- Comprehensive recovery plan
- Pre-positioned facilities
- Accelerate capital plan
```

### Primary Driver Analysis
```
If "Deposit flight exceeded liquidity buffers":
→ Focus on deposit stability
→ Strengthen franchise
→ Diversify funding

If "Asset fire-sale losses depleted capital":
→ Reduce liquidation needs
→ Better asset quality
→ Negotiate secured funding

If "Combined deposit and market stress":
→ Comprehensive approach
→ Both liquidity and capital
→ Review business model
```

---

## 💡 Best Practices

### Balance Sheet Setup
✓ Use audited, current data
✓ Include all material items
✓ Document assumptions
✓ Validate regulatory ratios
✗ Don't use outdated data
✗ Don't omit material items

### Scenario Design
✓ Start with Basel standard
✓ Gradually increase severity
✓ Test multiple time horizons
✓ Consider tail risks
✗ Don't jump to extreme scenarios
✗ Don't ignore historical precedents

### Running Simulations
✓ Run multiple scenarios
✓ Test sensitivity
✓ Compare results
✓ Document findings
✗ Don't rely on single scenario
✗ Don't ignore warnings

### Interpreting Results
✓ Consider context
✓ Validate with judgment
✓ Compare to peers
✓ Update assumptions
✗ Don't take results as gospel
✗ Don't ignore limitations

---

## 📞 Support

**Check First:**
1. README.md - Comprehensive documentation
2. INSTALL.md - Installation guide
3. PROJECT_SUMMARY.md - Technical details
4. logs/app.log - Error messages

**Common Questions:**

Q: Can I use this for regulatory reporting?
A: No, this is for internal analysis only.

Q: How accurate are the results?
A: Directionally useful, but simplified. Validate with experts.

Q: Can I modify the code?
A: Yes, it's designed to be extensible.

Q: What if network is required?
A: Plotly requires installation. Work in offline environment.

---

## 🏁 Quick Commands

```bash
# Install
pip install -r requirements.txt

# Run
streamlit run app.py

# Run on different port
streamlit run app.py --server.port 8502

# Stop
Ctrl+C

# Check logs
tail -f logs/app.log

# Export audit log
# (Use the Audit Log page in the app)
```

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**For**: Internal Risk Management Use

---

## 📚 Additional Reading

- Basel III LCR: https://www.bis.org/publ/bcbs238.htm
- Basel III NSFR: https://www.bis.org/publ/bcbs295.htm
- ICAAP Guidance: Consult your regulator
- Recovery Planning: FSB Key Attributes
