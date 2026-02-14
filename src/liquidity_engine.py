"""
Liquidity Engine Module
Executes liquidity stress simulations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)


class LiquidityEngine:
    """
    Core engine for running liquidity stress simulations
    """
    
    def __init__(
        self,
        balance_sheet,
        scenario,
        liquidation_order: List[str],
        recovery_actions: Optional[List[str]] = None
    ):
        """
        Initialize the liquidity engine
        
        Args:
            balance_sheet: Initial balance sheet
            scenario: Stress scenario
            liquidation_order: Order of asset liquidation
            recovery_actions: Available recovery actions
        """
        self.initial_balance_sheet = balance_sheet
        self.scenario = scenario
        self.liquidation_order = liquidation_order
        self.recovery_actions = recovery_actions or []
        
        # Results storage
        self.period_results = []
        self.current_period = 0
    
    def run_simulation(
        self,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Run the full simulation
        
        Args:
            progress_callback: Callback for progress updates
            
        Returns:
            Dict: Simulation results
        """
        logger.info(f"Starting simulation: {self.scenario.name}")
        
        # Initialize
        bs = self.initial_balance_sheet.copy()
        breached = False
        breach_info = None
        
        # Run period by period
        for period in range(self.scenario.num_periods):
            self.current_period = period
            
            # Update progress
            if progress_callback:
                progress = int((period / self.scenario.num_periods) * 100)
                progress_callback(progress, f"Processing period {period + 1}/{self.scenario.num_periods}")
            
            # Execute period
            period_result = self._execute_period(bs, period)
            self.period_results.append(period_result)
            
            # Check for breach
            breach = self._check_breach(bs, period_result)
            if breach:
                breached = True
                breach_info = breach
                logger.info(f"Breach detected at period {period}: {breach['type']}")
                break
        
        # Compile results
        results = self._compile_results(breached, breach_info)
        
        logger.info(f"Simulation completed: Survival horizon = {results['survival_horizon']} periods")
        
        return results
    
    def _execute_period(self, balance_sheet, period: int) -> Dict:
        """Execute a single period"""
        period_data = {
            'period': period,
            'opening_bs': balance_sheet.to_dict() if hasattr(balance_sheet, 'to_dict') else {},
            'outflows': {},
            'liquidations': [],
            'losses': 0,
            'metrics': {}
        }
        
        # Step 1: Apply deposit withdrawals
        total_outflow = self._apply_withdrawals(balance_sheet, period, period_data)
        
        # Step 2: Meet outflows through asset liquidation
        self._meet_outflows(balance_sheet, total_outflow, period_data)
        
        # Step 3: Apply credit deterioration (every 10 periods)
        if period % 10 == 0 and period > 0:
            credit_impact = self.scenario.apply_credit_deterioration(balance_sheet)
            period_data['credit_impact'] = credit_impact
        
        # Step 4: Calculate metrics
        period_data['metrics'] = self._calculate_metrics(balance_sheet)
        period_data['closing_bs'] = balance_sheet.to_dict() if hasattr(balance_sheet, 'to_dict') else {}
        
        return period_data
    
    def _apply_withdrawals(self, balance_sheet, period: int, period_data: Dict) -> float:
        """Apply deposit withdrawals"""
        total_outflow = 0
        
        deposit_types = [
            'retail_stable', 'retail_unstable', 'corporate_deposits',
            'wholesale_funding', 'secured_funding'
        ]
        
        for deposit_type in deposit_types:
            opening_balance = balance_sheet.data['liabilities'].get(deposit_type, 0)
            if opening_balance > 0:
                runoff = self.scenario.get_runoff_for_period(period, deposit_type, opening_balance)
                withdrawn = balance_sheet.apply_withdrawal(deposit_type, runoff)
                total_outflow += withdrawn
                period_data['outflows'][deposit_type] = withdrawn
        
        return total_outflow
    
    def _meet_outflows(self, balance_sheet, outflow: float, period_data: Dict):
        """Meet outflows through asset liquidation"""
        remaining_outflow = outflow
        
        # Map liquidation order to asset types
        asset_mapping = {
            'Cash': 'cash_reserves',
            'HQLA Level 1': 'hqla_level1',
            'HQLA Level 2A': 'hqla_level2a',
            'HQLA Level 2B': 'hqla_level2b',
            'Other Securities': 'other_securities',
            'Performing Loans': 'performing_loans',
            'Real Estate': 'real_estate'
        }
        
        for asset_name in self.liquidation_order:
            if remaining_outflow <= 0:
                break
            
            asset_type = asset_mapping.get(asset_name)
            if not asset_type:
                continue
            
            available = balance_sheet.data['assets'].get(asset_type, 0)
            if available <= 0:
                continue
            
            # Calculate haircut
            haircut = self._get_liquidation_haircut(asset_type, available)
            
            # Liquidate
            amount_to_liquidate = min(remaining_outflow / (1 - haircut / 100), available)
            
            if amount_to_liquidate > 0:
                result = balance_sheet.liquidate_asset(asset_type, amount_to_liquidate, haircut)
                period_data['liquidations'].append(result)
                period_data['losses'] += result['loss']
                remaining_outflow -= result['proceeds']
        
        # Use cash to meet remaining
        if remaining_outflow > 0:
            cash_available = balance_sheet.data['assets'].get('cash_reserves', 0)
            cash_used = min(remaining_outflow, cash_available)
            balance_sheet.data['assets']['cash_reserves'] -= cash_used
    
    def _get_liquidation_haircut(self, asset_type: str, available: float) -> float:
        """Calculate haircut including fire-sale premium"""
        base_haircuts = {
            'cash_reserves': 0,
            'hqla_level1': 0,
            'hqla_level2a': 5,
            'hqla_level2b': 15,
            'other_securities': 25,
            'performing_loans': 30,
            'real_estate': 40
        }
        
        base_haircut = base_haircuts.get(asset_type, 20)
        
        # Don't apply fire-sale to cash or Level 1 HQLA
        if asset_type in ['cash_reserves', 'hqla_level1']:
            return base_haircut
        
        # Add fire-sale discount for other assets
        fire_sale = self.scenario.fire_sale_discount
        
        return base_haircut + fire_sale
    
    def _calculate_metrics(self, balance_sheet) -> Dict:
        """Calculate liquidity and capital metrics"""
        return {
            'lcr': self._calculate_lcr(balance_sheet),
            'nsfr': self._calculate_nsfr(balance_sheet),
            'cet1_ratio': balance_sheet.cet1_ratio(),
            'total_capital_ratio': balance_sheet.total_capital_ratio(),
            'liquid_assets': balance_sheet.total_liquid_assets(),
            'total_deposits': balance_sheet.total_deposits()
        }
    
    def _calculate_lcr(self, balance_sheet) -> float:
        """Calculate Liquidity Coverage Ratio (simplified)"""
        hqla = balance_sheet.total_hqla(apply_haircuts=True)
        
        # 30-day net outflows (simplified)
        deposits = balance_sheet.total_deposits()
        net_outflows = deposits * 0.25  # Simplified assumption
        
        if net_outflows <= 0:
            return 999.9
        
        return (hqla / net_outflows) * 100
    
    def _calculate_nsfr(self, balance_sheet) -> float:
        """Calculate Net Stable Funding Ratio (simplified)"""
        # Available stable funding
        equity = balance_sheet.total_equity()
        retail_stable = balance_sheet.data['liabilities'].get('retail_stable', 0)
        asf = equity + (retail_stable * 0.95)
        
        # Required stable funding
        loans = balance_sheet.data['assets'].get('performing_loans', 0)
        rsf = loans * 0.85
        
        if rsf <= 0:
            return 999.9
        
        return (asf / rsf) * 100
    
    def _check_breach(self, balance_sheet, period_result: Dict) -> Optional[Dict]:
        """Check for threshold breaches"""
        metrics = period_result['metrics']
        
        # Check LCR
        if metrics['lcr'] < 100:
            return {
                'type': 'LCR',
                'value': metrics['lcr'],
                'threshold': 100,
                'period': period_result['period']
            }
        
        # Check CET1
        if metrics['cet1_ratio'] < 4.5:
            return {
                'type': 'CET1',
                'value': metrics['cet1_ratio'],
                'threshold': 4.5,
                'period': period_result['period']
            }
        
        # Check cash
        if balance_sheet.data['assets'].get('cash_reserves', 0) <= 0:
            if balance_sheet.total_liquid_assets() <= 0:
                return {
                    'type': 'Liquidity',
                    'value': 0,
                    'threshold': 0,
                    'period': period_result['period']
                }
        
        return None
    
    def _compile_results(self, breached: bool, breach_info: Optional[Dict]) -> Dict:
        """Compile final results"""
        if breached and breach_info:
            survival_horizon = breach_info['period']
            breach_type = breach_info['type']
        else:
            survival_horizon = self.scenario.num_periods
            breach_type = 'None'
        
        # Calculate cumulative metrics
        total_asset_depletion = sum(
            sum(liq['amount_liquidated'] for liq in p['liquidations'])
            for p in self.period_results
        )
        
        total_losses = sum(p.get('losses', 0) for p in self.period_results)
        
        # Get final metrics
        final_metrics = self.period_results[-1]['metrics'] if self.period_results else {}
        
        return {
            'survival_horizon': survival_horizon,
            'breach_type': breach_type,
            'breach_info': breach_info,
            'asset_depletion': total_asset_depletion,
            'total_losses': total_losses,
            'capital_erosion': (total_losses / self.initial_balance_sheet.total_equity() * 100
                              if self.initial_balance_sheet.total_equity() > 0 else 0),
            'final_lcr': final_metrics.get('lcr', 0),
            'final_cet1': final_metrics.get('cet1_ratio', 0),
            'period_results': self.period_results,
            'scenario_name': self.scenario.name
        }
