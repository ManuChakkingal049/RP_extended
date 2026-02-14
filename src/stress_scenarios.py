"""
Stress Scenario Module
Defines and manages stress scenarios for liquidity simulations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class StressScenario:
    """
    Represents a stress testing scenario
    """
    
    name: str
    time_granularity: str  # 'Daily', 'Monthly', 'Quarterly', 'Yearly'
    num_periods: int
    
    # Deposit run-off parameters
    runoff_rates: Dict[str, float] = field(default_factory=dict)
    custom_runoff: Optional[pd.DataFrame] = None
    
    # Market stress parameters
    security_shocks: Dict[str, float] = field(default_factory=dict)
    fire_sale_discount: float = 10.0
    fire_sale_increment: float = 2.0
    
    # Funding stress
    funding_spread_increase: int = 100  # basis points
    collateral_haircut_increase: float = 10.0  # percentage points
    
    # Credit deterioration
    loan_migration_rate: float = 2.0  # percentage
    provisioning_rate: float = 50.0  # percentage
    rwa_increase: float = 10.0  # percentage
    
    # Metadata
    description: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize scenario"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        
        # Set default runoff rates if not provided
        if not self.runoff_rates:
            self.runoff_rates = self._default_runoff_rates()
        
        # Validate
        self._validate()
    
    def _default_runoff_rates(self) -> Dict[str, float]:
        """
        Return Basel III standard runoff rates
        
        Returns:
            Dict: Default runoff rates by deposit type
        """
        return {
            'retail_stable': 5.0,
            'retail_unstable': 10.0,
            'corporate_deposits': 40.0,
            'wholesale_funding': 100.0,
            'secured_funding': 25.0
        }
    
    def _validate(self):
        """Validate scenario parameters"""
        # Validate time granularity
        valid_granularities = ['Daily', 'Monthly', 'Quarterly', 'Yearly']
        if self.time_granularity not in valid_granularities:
            raise ValueError(f"Invalid time granularity: {self.time_granularity}")
        
        # Validate number of periods
        if self.num_periods <= 0:
            raise ValueError(f"Number of periods must be positive: {self.num_periods}")
        
        # Validate runoff rates
        for deposit_type, rate in self.runoff_rates.items():
            if not 0 <= rate <= 100:
                raise ValueError(f"Invalid runoff rate for {deposit_type}: {rate}")
        
        # Validate shocks
        for asset_type, shock in self.security_shocks.items():
            if not -100 <= shock <= 100:
                raise ValueError(f"Invalid shock for {asset_type}: {shock}")
        
        logger.info(f"Scenario '{self.name}' validated successfully")
    
    def get_period_duration_days(self) -> int:
        """
        Get the duration of one period in days
        
        Returns:
            int: Number of days per period
        """
        durations = {
            'Daily': 1,
            'Monthly': 30,
            'Quarterly': 90,
            'Yearly': 365
        }
        return durations.get(self.time_granularity, 30)
    
    def get_runoff_for_period(
        self,
        period: int,
        deposit_type: str,
        opening_balance: float
    ) -> float:
        """
        Calculate deposit runoff for a specific period
        
        Args:
            period: Period number (0-indexed)
            deposit_type: Type of deposit
            opening_balance: Opening balance for the period
            
        Returns:
            float: Runoff amount
        """
        # Check if custom runoff is defined
        if self.custom_runoff is not None and period < len(self.custom_runoff):
            col_name = f"{deposit_type}_withdrawal"
            if col_name in self.custom_runoff.columns:
                return self.custom_runoff.iloc[period][col_name]
        
        # Use standard runoff rate
        rate = self.runoff_rates.get(deposit_type, 0) / 100
        runoff = opening_balance * rate
        
        return runoff
    
    def get_security_shock(self, asset_type: str) -> float:
        """
        Get the price shock for a security type
        
        Args:
            asset_type: Type of security
            
        Returns:
            float: Price shock as decimal (e.g., -0.15 for -15%)
        """
        shock_pct = self.security_shocks.get(asset_type, 0)
        return shock_pct / 100
    
    def calculate_fire_sale_discount(self, amount_sold: float, total_available: float) -> float:
        """
        Calculate fire-sale discount based on volume sold
        
        Args:
            amount_sold: Amount being sold
            total_available: Total amount available
            
        Returns:
            float: Discount percentage
        """
        base_discount = self.fire_sale_discount
        
        # Calculate percentage of available assets being sold
        if total_available > 0:
            volume_pct = (amount_sold / total_available) * 100
            # Add incremental discount
            additional_discount = (volume_pct / 10) * self.fire_sale_increment
        else:
            additional_discount = 0
        
        total_discount = base_discount + additional_discount
        
        # Cap at reasonable maximum
        return min(total_discount, 50.0)
    
    def apply_credit_deterioration(self, balance_sheet) -> Dict:
        """
        Apply credit deterioration to balance sheet
        
        Args:
            balance_sheet: BalanceSheet object
            
        Returns:
            Dict: Impact of credit deterioration
        """
        performing_loans = balance_sheet.data['assets'].get('performing_loans', 0)
        
        # Calculate loan migration
        migration_amount = performing_loans * (self.loan_migration_rate / 100)
        
        # Move to NPL
        balance_sheet.data['assets']['performing_loans'] -= migration_amount
        balance_sheet.data['assets']['npl'] += migration_amount
        
        # Apply provisioning
        provision = migration_amount * (self.provisioning_rate / 100)
        balance_sheet.data['equity']['cet1'] -= provision
        
        logger.debug(
            f"Credit deterioration: Migrated {migration_amount:.2f}M to NPL, "
            f"Provision {provision:.2f}M"
        )
        
        return {
            'migration_amount': migration_amount,
            'provision': provision,
            'rwa_increase_pct': self.rwa_increase
        }
    
    def to_dict(self) -> Dict:
        """
        Convert scenario to dictionary
        
        Returns:
            Dict: Scenario as dictionary
        """
        data = {
            'name': self.name,
            'time_granularity': self.time_granularity,
            'num_periods': self.num_periods,
            'runoff_rates': self.runoff_rates,
            'security_shocks': self.security_shocks,
            'fire_sale_discount': self.fire_sale_discount,
            'fire_sale_increment': self.fire_sale_increment,
            'funding_spread_increase': self.funding_spread_increase,
            'collateral_haircut_increase': self.collateral_haircut_increase,
            'loan_migration_rate': self.loan_migration_rate,
            'provisioning_rate': self.provisioning_rate,
            'rwa_increase': self.rwa_increase,
            'description': self.description,
            'created_at': self.created_at
        }
        
        if self.custom_runoff is not None:
            data['custom_runoff'] = self.custom_runoff.to_dict()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """
        Create scenario from dictionary
        
        Args:
            data: Dictionary with scenario parameters
            
        Returns:
            StressScenario: Scenario object
        """
        # Handle custom runoff
        custom_runoff = None
        if 'custom_runoff' in data:
            custom_runoff = pd.DataFrame.from_dict(data.pop('custom_runoff'))
        
        scenario = cls(**data)
        scenario.custom_runoff = custom_runoff
        
        return scenario
    
    def __repr__(self):
        return (f"StressScenario(name='{self.name}', "
                f"granularity={self.time_granularity}, "
                f"periods={self.num_periods})")


class ScenarioLibrary:
    """
    Library of predefined stress scenarios
    """
    
    @staticmethod
    def basel_lcr_standard() -> StressScenario:
        """
        Basel III LCR standard stress scenario
        
        Returns:
            StressScenario: Basel LCR scenario
        """
        return StressScenario(
            name="Basel III LCR Standard",
            time_granularity="Daily",
            num_periods=30,
            runoff_rates={
                'retail_stable': 5.0,
                'retail_unstable': 10.0,
                'corporate_deposits': 40.0,
                'wholesale_funding': 100.0,
                'secured_funding': 25.0
            },
            security_shocks={},
            fire_sale_discount=0.0,
            description="Standard Basel III LCR stress scenario over 30 days"
        )
    
    @staticmethod
    def severe_stress() -> StressScenario:
        """
        Severe combined stress scenario
        
        Returns:
            StressScenario: Severe stress scenario
        """
        return StressScenario(
            name="Severe Combined Stress",
            time_granularity="Daily",
            num_periods=60,
            runoff_rates={
                'retail_stable': 15.0,
                'retail_unstable': 30.0,
                'corporate_deposits': 60.0,
                'wholesale_funding': 100.0,
                'secured_funding': 50.0
            },
            security_shocks={
                'hqla_level1': 0.0,
                'hqla_level2a': -10.0,
                'hqla_level2b': -25.0,
                'other_securities': -40.0
            },
            fire_sale_discount=15.0,
            fire_sale_increment=3.0,
            funding_spread_increase=250,
            collateral_haircut_increase=20.0,
            loan_migration_rate=5.0,
            provisioning_rate=60.0,
            rwa_increase=15.0,
            description="Severe stress combining deposit runs, market shocks, and credit deterioration"
        )
    
    @staticmethod
    def idiosyncratic_crisis() -> StressScenario:
        """
        Bank-specific idiosyncratic crisis
        
        Returns:
            StressScenario: Idiosyncratic crisis scenario
        """
        return StressScenario(
            name="Idiosyncratic Bank Crisis",
            time_granularity="Daily",
            num_periods=90,
            runoff_rates={
                'retail_stable': 20.0,
                'retail_unstable': 50.0,
                'corporate_deposits': 80.0,
                'wholesale_funding': 100.0,
                'secured_funding': 75.0
            },
            security_shocks={
                'hqla_level1': 0.0,
                'hqla_level2a': -15.0,
                'hqla_level2b': -35.0,
                'other_securities': -50.0
            },
            fire_sale_discount=20.0,
            fire_sale_increment=5.0,
            funding_spread_increase=500,
            collateral_haircut_increase=30.0,
            loan_migration_rate=8.0,
            provisioning_rate=70.0,
            rwa_increase=25.0,
            description="Severe idiosyncratic crisis with major deposit flight"
        )
    
    @staticmethod
    def get_all_predefined() -> List[StressScenario]:
        """
        Get all predefined scenarios
        
        Returns:
            List[StressScenario]: List of scenarios
        """
        return [
            ScenarioLibrary.basel_lcr_standard(),
            ScenarioLibrary.severe_stress(),
            ScenarioLibrary.idiosyncratic_crisis()
        ]
