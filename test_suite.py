"""
Test Suite for Bank Liquidity Simulator
Validates core functionality of all modules
"""

import sys
import traceback
from datetime import datetime

# Test results tracking
tests_passed = 0
tests_failed = 0
test_results = []


def test_result(test_name, passed, error_msg=None):
    """Record test result"""
    global tests_passed, tests_failed
    if passed:
        tests_passed += 1
        test_results.append(f"✓ {test_name}")
        print(f"✓ {test_name}")
    else:
        tests_failed += 1
        test_results.append(f"✗ {test_name}: {error_msg}")
        print(f"✗ {test_name}")
        if error_msg:
            print(f"  Error: {error_msg}")


def test_imports():
    """Test that all modules can be imported"""
    test_name = "Module Imports"
    try:
        from src.balance_sheet import BalanceSheet
        from src.stress_scenarios import StressScenario, ScenarioLibrary
        from src.liquidity_engine import LiquidityEngine
        from src.metrics_calculator import MetricsCalculator
        from src.survival_analyzer import SurvivalAnalyzer
        from src.visualization import Visualizer
        from src.security import SecurityManager
        from src.logger import AppLogger, AuditLogger
        test_result(test_name, True)
        return True
    except Exception as e:
        test_result(test_name, False, str(e))
        return False


def test_balance_sheet():
    """Test BalanceSheet class"""
    test_name = "BalanceSheet Creation and Validation"
    try:
        from src.balance_sheet import BalanceSheet
        
        # Create a test balance sheet
        bs_data = {
            'assets': {
                'cash_reserves': 1000.0,
                'hqla_level1': 2000.0,
                'hqla_level2a': 500.0,
                'hqla_level2b': 300.0,
                'performing_loans': 15000.0,
                'npl': 500.0,
                'real_estate': 1000.0,
                'other_securities': 800.0,
                'other_assets': 200.0
            },
            'liabilities': {
                'retail_stable': 8000.0,
                'retail_unstable': 4000.0,
                'corporate_deposits': 3000.0,
                'wholesale_funding': 2000.0,
                'secured_funding': 1500.0,
                'other_liabilities': 500.0
            },
            'equity': {
                'cet1': 1500.0,
                'at1': 200.0,
                'tier2': 300.0
            }
        }
        
        bs = BalanceSheet(bs_data)
        
        # Validate
        if not bs.validate():
            raise Exception("Balance sheet validation failed")
        
        # Check calculations
        total_assets = bs.total_assets()
        total_liabilities = bs.total_liabilities()
        total_equity = bs.total_equity()
        
        if abs(total_assets - (total_liabilities + total_equity)) > 0.01:
            raise Exception("Balance equation not satisfied")
        
        # Check metrics
        cet1_ratio = bs.cet1_ratio()
        if cet1_ratio <= 0:
            raise Exception("Invalid CET1 ratio")
        
        test_result(test_name, True)
        return True
    except Exception as e:
        test_result(test_name, False, str(e))
        traceback.print_exc()
        return False


def test_stress_scenario():
    """Test StressScenario class"""
    test_name = "Stress Scenario Creation"
    try:
        from src.stress_scenarios import StressScenario, ScenarioLibrary
        
        # Create a simple scenario
        scenario = StressScenario(
            name="Test Scenario",
            time_granularity="Daily",
            num_periods=30
        )
        
        # Test predefined scenarios
        basel_scenario = ScenarioLibrary.basel_lcr_standard()
        if basel_scenario.name != "Basel III LCR Standard":
            raise Exception("Predefined scenario not loaded correctly")
        
        test_result(test_name, True)
        return True
    except Exception as e:
        test_result(test_name, False, str(e))
        traceback.print_exc()
        return False


def test_metrics_calculator():
    """Test MetricsCalculator"""
    test_name = "Metrics Calculator"
    try:
        from src.balance_sheet import BalanceSheet
        from src.metrics_calculator import MetricsCalculator
        
        # Create balance sheet
        bs_data = {
            'assets': {
                'cash_reserves': 1000.0,
                'hqla_level1': 2000.0,
                'hqla_level2a': 500.0,
                'hqla_level2b': 300.0,
                'performing_loans': 15000.0,
                'npl': 500.0,
                'real_estate': 1000.0,
                'other_securities': 800.0,
                'other_assets': 200.0
            },
            'liabilities': {
                'retail_stable': 8000.0,
                'retail_unstable': 4000.0,
                'corporate_deposits': 3000.0,
                'wholesale_funding': 2000.0,
                'secured_funding': 1500.0,
                'other_liabilities': 500.0
            },
            'equity': {
                'cet1': 1500.0,
                'at1': 200.0,
                'tier2': 300.0
            }
        }
        
        bs = BalanceSheet(bs_data)
        
        # Calculate LCR
        lcr_metrics = MetricsCalculator.calculate_lcr(bs)
        if 'lcr' not in lcr_metrics:
            raise Exception("LCR not calculated")
        
        # Calculate NSFR
        nsfr_metrics = MetricsCalculator.calculate_nsfr(bs)
        if 'nsfr' not in nsfr_metrics:
            raise Exception("NSFR not calculated")
        
        # Calculate all metrics
        all_metrics = MetricsCalculator.calculate_all_metrics(bs)
        if len(all_metrics) < 5:
            raise Exception("Not all metrics calculated")
        
        test_result(test_name, True)
        return True
    except Exception as e:
        test_result(test_name, False, str(e))
        traceback.print_exc()
        return False


def test_security_manager():
    """Test SecurityManager"""
    test_name = "Security Manager"
    try:
        from src.security import SecurityManager
        
        security = SecurityManager()
        
        # Test session generation
        session_id = security.generate_session_id()
        if not session_id or len(session_id) < 16:
            raise Exception("Invalid session ID generated")
        
        # Test session validation
        if not security.validate_session(session_id):
            raise Exception("Valid session marked as invalid")
        
        # Test input sanitization
        sanitized = security.sanitize_input("<script>alert('xss')</script>")
        if '<script>' in sanitized:
            raise Exception("XSS not sanitized")
        
        # Test numeric validation
        if not security.validate_numeric_input(100.0, min_value=0, max_value=200):
            raise Exception("Valid number marked as invalid")
        
        if security.validate_numeric_input(-10, min_value=0, allow_negative=False):
            raise Exception("Negative number not caught")
        
        test_result(test_name, True)
        return True
    except Exception as e:
        test_result(test_name, False, str(e))
        traceback.print_exc()
        return False


def test_logger():
    """Test logging system"""
    test_name = "Logging System"
    try:
        from src.logger import AppLogger, AuditLogger
        
        # Setup logging
        AppLogger.setup_logging(log_level="INFO", log_to_file=False, log_to_console=False)
        
        # Get logger
        logger = AppLogger.get_logger(__name__)
        
        # Test logging
        logger.info("Test log message")
        logger.debug("Test debug message")
        
        # Test audit logger
        audit = AuditLogger()
        audit.log_action(
            action="test_action",
            session_id="test_session",
            details={'test': 'data'}
        )
        
        test_result(test_name, True)
        return True
    except Exception as e:
        test_result(test_name, False, str(e))
        traceback.print_exc()
        return False


def test_simulation_engine():
    """Test LiquidityEngine (basic simulation)"""
    test_name = "Simulation Engine"
    try:
        from src.balance_sheet import BalanceSheet
        from src.stress_scenarios import ScenarioLibrary
        from src.liquidity_engine import LiquidityEngine
        
        # Create balance sheet
        bs_data = {
            'assets': {
                'cash_reserves': 1000.0,
                'hqla_level1': 2000.0,
                'hqla_level2a': 500.0,
                'hqla_level2b': 300.0,
                'performing_loans': 15000.0,
                'npl': 500.0,
                'real_estate': 1000.0,
                'other_securities': 800.0,
                'other_assets': 200.0
            },
            'liabilities': {
                'retail_stable': 8000.0,
                'retail_unstable': 4000.0,
                'corporate_deposits': 3000.0,
                'wholesale_funding': 2000.0,
                'secured_funding': 1500.0,
                'other_liabilities': 500.0
            },
            'equity': {
                'cet1': 1500.0,
                'at1': 200.0,
                'tier2': 300.0
            }
        }
        
        bs = BalanceSheet(bs_data)
        scenario = ScenarioLibrary.basel_lcr_standard()
        
        liquidation_order = ['Cash', 'HQLA Level 1', 'HQLA Level 2A', 'HQLA Level 2B']
        
        # Create engine
        engine = LiquidityEngine(
            balance_sheet=bs,
            scenario=scenario,
            liquidation_order=liquidation_order
        )
        
        # Run short simulation (5 periods for speed)
        scenario.num_periods = 5
        results = engine.run_simulation()
        
        if 'survival_horizon' not in results:
            raise Exception("Simulation results incomplete")
        
        if len(results['period_results']) == 0:
            raise Exception("No period results generated")
        
        test_result(test_name, True)
        return True
    except Exception as e:
        test_result(test_name, False, str(e))
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Bank Liquidity Simulator - Test Suite")
    print("="*60 + "\n")
    
    print(f"Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run tests
    tests = [
        test_imports,
        test_balance_sheet,
        test_stress_scenario,
        test_metrics_calculator,
        test_security_manager,
        test_logger,
        test_simulation_engine,
    ]
    
    for test_func in tests:
        print(f"\nRunning: {test_func.__name__}...")
        test_func()
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"\nTotal Tests: {tests_passed + tests_failed}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {tests_failed} test(s) failed")
        print("\nFailed tests:")
        for result in test_results:
            if result.startswith("✗"):
                print(f"  {result}")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
