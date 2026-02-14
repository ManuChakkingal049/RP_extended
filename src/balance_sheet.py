"""
Balance Sheet Module
Handles balance sheet creation, validation, and calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class BalanceSheet:
    """
    Balance Sheet representation with validation and calculation methods
    """
    
    data: Dict
    period: int = 0
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Initialize calculated fields"""
        self._assets_df = None
        self._liabilities_df = None
        self._validate_structure()
    
    def _validate_structure(self):
        """Validate that required fields exist"""
        required_keys = ['assets', 'liabilities', 'equity']
        for key in required_keys:
            if key not in self.data:
                raise ValueError(f"Missing required key: {key}")
    
    def validate(self) -> bool:
        """
        Validate balance sheet integrity
        
        Returns:
            bool: True if valid, raises exception otherwise
        """
        try:
            # Check all values are non-negative
            for category in ['assets', 'liabilities', 'equity']:
                for key, value in self.data[category].items():
                    if value < 0:
                        raise ValueError(f"Negative value not allowed: {category}.{key} = {value}")
            
            # Check balance equation (with tolerance for floating point)
            total_assets = self.total_assets()
            total_liabilities = self.total_liabilities()
            total_equity = self.total_equity()
            
            balance_diff = abs(total_assets - (total_liabilities + total_equity))
            tolerance = 0.01  # €10,000 tolerance
            
            if balance_diff > tolerance:
                logger.warning(
                    f"Balance sheet imbalance: Assets={total_assets:.2f}, "
                    f"Liabilities={total_liabilities:.2f}, Equity={total_equity:.2f}, "
                    f"Difference={balance_diff:.2f}"
                )
                # Allow slight imbalance but log it
                if balance_diff > 1.0:  # €1M threshold
                    raise ValueError(f"Balance sheet significantly out of balance: {balance_diff:.2f}M")
            
            logger.info("Balance sheet validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Balance sheet validation failed: {str(e)}")
            raise
    
    def total_assets(self) -> float:
        """Calculate total assets"""
        return sum(self.data['assets'].values())
    
    def total_liabilities(self) -> float:
        """Calculate total liabilities"""
        return sum(self.data['liabilities'].values())
    
    def total_equity(self) -> float:
        """Calculate total equity"""
        return sum(self.data['equity'].values())
    
    def total_hqla(self, apply_haircuts: bool = False) -> float:
        """
        Calculate total High Quality Liquid Assets
        
        Args:
            apply_haircuts: Whether to apply regulatory haircuts
            
        Returns:
            float: Total HQLA value
        """
        hqla_level1 = self.data['assets'].get('hqla_level1', 0)
        hqla_level2a = self.data['assets'].get('hqla_level2a', 0)
        hqla_level2b = self.data['assets'].get('hqla_level2b', 0)
        
        if apply_haircuts:
            # Basel III LCR haircuts
            hqla_level1 *= 1.00  # No haircut
            hqla_level2a *= 0.85  # 15% haircut
            hqla_level2b *= 0.50  # 50% haircut
        
        return hqla_level1 + hqla_level2a + hqla_level2b
    
    def total_deposits(self) -> float:
        """Calculate total deposits"""
        deposits = 0
        deposits += self.data['liabilities'].get('retail_stable', 0)
        deposits += self.data['liabilities'].get('retail_unstable', 0)
        deposits += self.data['liabilities'].get('corporate_deposits', 0)
        return deposits
    
    def total_retail_deposits(self) -> float:
        """Calculate total retail deposits"""
        return (self.data['liabilities'].get('retail_stable', 0) + 
                self.data['liabilities'].get('retail_unstable', 0))
    
    def total_liquid_assets(self) -> float:
        """Calculate total liquid assets (cash + HQLA)"""
        liquid = self.data['assets'].get('cash_reserves', 0)
        liquid += self.total_hqla()
        return liquid
    
    def tier1_capital(self) -> float:
        """Calculate Tier 1 capital (CET1 + AT1)"""
        return (self.data['equity'].get('cet1', 0) + 
                self.data['equity'].get('at1', 0))
    
    def total_capital(self) -> float:
        """Calculate total regulatory capital"""
        return self.total_equity()
    
    def rwa_estimate(self) -> float:
        """
        Estimate Risk-Weighted Assets (simplified)
        
        Uses simple weights:
        - Cash & HQLA: 0%
        - Performing loans: 100%
        - NPL: 150%
        - Real estate: 100%
        - Other securities: 50%
        """
        rwa = 0
        
        # Cash and HQLA - 0% weight
        # Performing loans - 100% weight
        rwa += self.data['assets'].get('performing_loans', 0) * 1.0
        
        # NPL - 150% weight
        rwa += self.data['assets'].get('npl', 0) * 1.5
        
        # Real estate - 100% weight
        rwa += self.data['assets'].get('real_estate', 0) * 1.0
        
        # Other securities - 50% weight
        rwa += self.data['assets'].get('other_securities', 0) * 0.5
        
        # Other assets - 100% weight
        rwa += self.data['assets'].get('other_assets', 0) * 1.0
        
        return rwa
    
    def cet1_ratio(self) -> float:
        """Calculate CET1 ratio as percentage"""
        rwa = self.rwa_estimate()
        if rwa == 0:
            return 0
        cet1 = self.data['equity'].get('cet1', 0)
        return (cet1 / rwa) * 100
    
    def tier1_ratio(self) -> float:
        """Calculate Tier 1 ratio as percentage"""
        rwa = self.rwa_estimate()
        if rwa == 0:
            return 0
        return (self.tier1_capital() / rwa) * 100
    
    def total_capital_ratio(self) -> float:
        """Calculate total capital ratio as percentage"""
        rwa = self.rwa_estimate()
        if rwa == 0:
            return 0
        return (self.total_capital() / rwa) * 100
    
    def leverage_ratio(self) -> float:
        """Calculate simple leverage ratio (Equity / Assets)"""
        assets = self.total_assets()
        if assets == 0:
            return 0
        return (self.total_equity() / assets) * 100
    
    def apply_withdrawal(self, deposit_type: str, amount: float):
        """
        Apply a deposit withdrawal
        
        Args:
            deposit_type: Type of deposit (e.g., 'retail_stable')
            amount: Amount to withdraw
        """
        if deposit_type not in self.data['liabilities']:
            raise ValueError(f"Unknown deposit type: {deposit_type}")
        
        current_amount = self.data['liabilities'][deposit_type]
        withdrawal = min(amount, current_amount)  # Can't withdraw more than available
        
        self.data['liabilities'][deposit_type] -= withdrawal
        
        logger.debug(f"Withdrawal applied: {deposit_type} = {withdrawal:.2f}M")
        
        return withdrawal
    
    def liquidate_asset(self, asset_type: str, amount: float, haircut: float = 0) -> Dict:
        """
        Liquidate an asset with optional haircut
        
        Args:
            asset_type: Type of asset to liquidate
            amount: Amount to liquidate (pre-haircut)
            haircut: Haircut percentage (0-100)
            
        Returns:
            Dict with liquidation details
        """
        if asset_type not in self.data['assets']:
            raise ValueError(f"Unknown asset type: {asset_type}")
        
        available = self.data['assets'][asset_type]
        liquidated = min(amount, available)
        
        # Apply haircut
        proceeds = liquidated * (1 - haircut / 100)
        loss = liquidated - proceeds
        
        # Update balance sheet
        self.data['assets'][asset_type] -= liquidated
        self.data['assets']['cash_reserves'] += proceeds
        
        # Record loss in equity
        self.data['equity']['cet1'] -= loss
        
        logger.debug(
            f"Asset liquidated: {asset_type} = {liquidated:.2f}M, "
            f"Haircut={haircut:.1f}%, Proceeds={proceeds:.2f}M, Loss={loss:.2f}M"
        )
        
        return {
            'asset_type': asset_type,
            'amount_liquidated': liquidated,
            'haircut_pct': haircut,
            'proceeds': proceeds,
            'loss': loss
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert balance sheet to DataFrame format
        
        Returns:
            pd.DataFrame: Balance sheet in tabular format
        """
        data = []
        
        # Assets
        for key, value in self.data['assets'].items():
            data.append({
                'Category': 'Assets',
                'Item': key.replace('_', ' ').title(),
                'Amount_M_EUR': value,
                'Percentage': (value / self.total_assets() * 100) if self.total_assets() > 0 else 0
            })
        
        # Add total assets
        data.append({
            'Category': 'Assets',
            'Item': 'TOTAL ASSETS',
            'Amount_M_EUR': self.total_assets(),
            'Percentage': 100.0
        })
        
        # Liabilities
        for key, value in self.data['liabilities'].items():
            data.append({
                'Category': 'Liabilities',
                'Item': key.replace('_', ' ').title(),
                'Amount_M_EUR': value,
                'Percentage': (value / self.total_assets() * 100) if self.total_assets() > 0 else 0
            })
        
        # Equity
        for key, value in self.data['equity'].items():
            data.append({
                'Category': 'Equity',
                'Item': key.upper(),
                'Amount_M_EUR': value,
                'Percentage': (value / self.total_assets() * 100) if self.total_assets() > 0 else 0
            })
        
        # Add total liabilities + equity
        data.append({
            'Category': 'Liabilities + Equity',
            'Item': 'TOTAL LIABILITIES + EQUITY',
            'Amount_M_EUR': self.total_liabilities() + self.total_equity(),
            'Percentage': 100.0
        })
        
        return pd.DataFrame(data)
    
    def copy(self):
        """Create a deep copy of the balance sheet"""
        import copy
        return BalanceSheet(
            data=copy.deepcopy(self.data),
            period=self.period,
            timestamp=self.timestamp
        )
    
    def __repr__(self):
        return (f"BalanceSheet(Assets={self.total_assets():.2f}M, "
                f"Liabilities={self.total_liabilities():.2f}M, "
                f"Equity={self.total_equity():.2f}M, "
                f"Period={self.period})")
