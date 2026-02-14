"""
Metrics Calculator Module
Calculates Basel III and other regulatory metrics
"""

import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """
    Calculator for liquidity and capital metrics
    """
    
    @staticmethod
    def calculate_lcr(
        balance_sheet,
        stress_scenario: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate Liquidity Coverage Ratio per Basel III
        
        Returns:
            Dict: LCR components and ratio
        """
        # HQLA with haircuts
        level1 = balance_sheet.data['assets'].get('hqla_level1', 0)
        level2a = balance_sheet.data['assets'].get('hqla_level2a', 0) * 0.85
        level2b = balance_sheet.data['assets'].get('hqla_level2b', 0) * 0.50
        
        # Level 2 cap: max 40% of HQLA after haircuts
        level2_total = level2a + level2b
        level2_cap = (level1 + level2_total) * 0.40
        
        if level2_total > level2_cap:
            level2_adjusted = level2_cap
        else:
            level2_adjusted = level2_total
        
        total_hqla = level1 + level2_adjusted
        
        # Net cash outflows (30-day)
        outflows = MetricsCalculator._calculate_30day_outflows(balance_sheet)
        inflows = MetricsCalculator._calculate_30day_inflows(balance_sheet)
        
        net_outflows = max(outflows - inflows * 0.75, outflows * 0.25)  # Inflow cap at 75%
        
        lcr = (total_hqla / net_outflows * 100) if net_outflows > 0 else 999.9
        
        return {
            'lcr': lcr,
            'total_hqla': total_hqla,
            'level1_hqla': level1,
            'level2_hqla': level2_adjusted,
            'net_outflows': net_outflows,
            'gross_outflows': outflows,
            'gross_inflows': inflows
        }
    
    @staticmethod
    def _calculate_30day_outflows(balance_sheet) -> float:
        """Calculate 30-day stressed outflows"""
        outflows = 0
        
        # Retail deposits
        retail_stable = balance_sheet.data['liabilities'].get('retail_stable', 0)
        retail_unstable = balance_sheet.data['liabilities'].get('retail_unstable', 0)
        
        outflows += retail_stable * 0.05  # 5% runoff
        outflows += retail_unstable * 0.10  # 10% runoff
        
        # Corporate deposits
        corporate = balance_sheet.data['liabilities'].get('corporate_deposits', 0)
        outflows += corporate * 0.40  # 40% runoff
        
        # Wholesale funding
        wholesale = balance_sheet.data['liabilities'].get('wholesale_funding', 0)
        outflows += wholesale * 1.00  # 100% runoff
        
        # Secured funding
        secured = balance_sheet.data['liabilities'].get('secured_funding', 0)
        outflows += secured * 0.25  # 25% rollover risk
        
        return outflows
    
    @staticmethod
    def _calculate_30day_inflows(balance_sheet) -> float:
        """Calculate 30-day inflows (simplified)"""
        # Simplified: assume some portion of loans mature
        performing_loans = balance_sheet.data['assets'].get('performing_loans', 0)
        return performing_loans * 0.05  # 5% mature in 30 days
    
    @staticmethod
    def calculate_nsfr(balance_sheet) -> Dict:
        """
        Calculate Net Stable Funding Ratio per Basel III
        
        Returns:
            Dict: NSFR components and ratio
        """
        # Available Stable Funding
        asf = MetricsCalculator._calculate_asf(balance_sheet)
        
        # Required Stable Funding
        rsf = MetricsCalculator._calculate_rsf(balance_sheet)
        
        nsfr = (asf / rsf * 100) if rsf > 0 else 999.9
        
        return {
            'nsfr': nsfr,
            'available_stable_funding': asf,
            'required_stable_funding': rsf
        }
    
    @staticmethod
    def _calculate_asf(balance_sheet) -> float:
        """Calculate Available Stable Funding"""
        asf = 0
        
        # Capital (100% ASF factor)
        equity = balance_sheet.total_equity()
        asf += equity * 1.00
        
        # Stable retail deposits (95% ASF factor)
        retail_stable = balance_sheet.data['liabilities'].get('retail_stable', 0)
        asf += retail_stable * 0.95
        
        # Less stable retail deposits (90% ASF factor)
        retail_unstable = balance_sheet.data['liabilities'].get('retail_unstable', 0)
        asf += retail_unstable * 0.90
        
        # Corporate deposits (50% ASF factor)
        corporate = balance_sheet.data['liabilities'].get('corporate_deposits', 0)
        asf += corporate * 0.50
        
        return asf
    
    @staticmethod
    def _calculate_rsf(balance_sheet) -> float:
        """Calculate Required Stable Funding"""
        rsf = 0
        
        # Cash (0% RSF factor)
        # HQLA (5-15% RSF factor)
        level1 = balance_sheet.data['assets'].get('hqla_level1', 0)
        level2a = balance_sheet.data['assets'].get('hqla_level2a', 0)
        level2b = balance_sheet.data['assets'].get('hqla_level2b', 0)
        
        rsf += level1 * 0.05
        rsf += level2a * 0.15
        rsf += level2b * 0.50
        
        # Performing loans (85% RSF factor)
        loans = balance_sheet.data['assets'].get('performing_loans', 0)
        rsf += loans * 0.85
        
        # NPL (100% RSF factor)
        npl = balance_sheet.data['assets'].get('npl', 0)
        rsf += npl * 1.00
        
        # Real estate (100% RSF factor)
        real_estate = balance_sheet.data['assets'].get('real_estate', 0)
        rsf += real_estate * 1.00
        
        # Other assets (85% RSF factor)
        other_securities = balance_sheet.data['assets'].get('other_securities', 0)
        other_assets = balance_sheet.data['assets'].get('other_assets', 0)
        rsf += other_securities * 0.85
        rsf += other_assets * 0.85
        
        return rsf
    
    @staticmethod
    def calculate_all_metrics(balance_sheet) -> Dict:
        """
        Calculate all key metrics
        
        Returns:
            Dict: All metrics
        """
        lcr_metrics = MetricsCalculator.calculate_lcr(balance_sheet)
        nsfr_metrics = MetricsCalculator.calculate_nsfr(balance_sheet)
        
        return {
            **lcr_metrics,
            **nsfr_metrics,
            'cet1_ratio': balance_sheet.cet1_ratio(),
            'tier1_ratio': balance_sheet.tier1_ratio(),
            'total_capital_ratio': balance_sheet.total_capital_ratio(),
            'leverage_ratio': balance_sheet.leverage_ratio(),
            'liquid_assets': balance_sheet.total_liquid_assets(),
            'total_assets': balance_sheet.total_assets(),
            'total_deposits': balance_sheet.total_deposits(),
            'loan_to_deposit_ratio': (
                balance_sheet.data['assets'].get('performing_loans', 0) /
                balance_sheet.total_deposits() * 100
                if balance_sheet.total_deposits() > 0 else 0
            )
        }
