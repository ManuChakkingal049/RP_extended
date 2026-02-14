"""
Survival Analyzer Module
Analyzes survival horizon and breach conditions
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SurvivalAnalyzer:
    """
    Analyzes simulation results for survival metrics
    """
    
    def __init__(self, simulation_results: Dict):
        """
        Initialize analyzer with simulation results
        
        Args:
            simulation_results: Results from LiquidityEngine
        """
        self.results = simulation_results
        self.period_results = simulation_results.get('period_results', [])
    
    def get_survival_horizon(self) -> int:
        """
        Get the survival horizon in periods
        
        Returns:
            int: Number of periods survived
        """
        return self.results.get('survival_horizon', 0)
    
    def get_breach_analysis(self) -> Dict:
        """
        Analyze the breach conditions
        
        Returns:
            Dict: Detailed breach analysis
        """
        breach_info = self.results.get('breach_info')
        
        if not breach_info:
            return {
                'breached': False,
                'message': 'No breach detected - bank survives full scenario'
            }
        
        breach_type = breach_info['type']
        breach_period = breach_info['period']
        
        analysis = {
            'breached': True,
            'type': breach_type,
            'period': breach_period,
            'value': breach_info.get('value', 0),
            'threshold': breach_info.get('threshold', 0)
        }
        
        # Add contextual analysis
        if breach_type == 'LCR':
            analysis['message'] = (
                f"Liquidity Coverage Ratio fell below 100% at period {breach_period}. "
                f"The bank exhausted its high-quality liquid assets and could no longer "
                f"meet stressed 30-day outflows."
            )
            analysis['severity'] = 'Critical'
        
        elif breach_type == 'CET1':
            analysis['message'] = (
                f"CET1 capital ratio fell below 4.5% at period {breach_period}. "
                f"Realized losses from asset liquidations eroded capital below minimum "
                f"regulatory requirements."
            )
            analysis['severity'] = 'Critical'
        
        elif breach_type == 'Liquidity':
            analysis['message'] = (
                f"Complete liquidity depletion at period {breach_period}. "
                f"The bank ran out of all liquid assets including cash."
            )
            analysis['severity'] = 'Fatal'
        
        else:
            analysis['message'] = f"Breach of {breach_type} at period {breach_period}"
            analysis['severity'] = 'High'
        
        return analysis
    
    def get_critical_periods(self) -> List[int]:
        """
        Identify periods where metrics came close to breaching
        
        Returns:
            List[int]: List of critical period numbers
        """
        critical_periods = []
        
        for result in self.period_results:
            period = result['period']
            metrics = result.get('metrics', {})
            
            # Check if near breach
            if metrics.get('lcr', 999) < 110:  # Within 10% of breach
                critical_periods.append(period)
            elif metrics.get('cet1_ratio', 999) < 5.5:  # Within 1% of breach
                critical_periods.append(period)
        
        return sorted(set(critical_periods))
    
    def get_primary_driver(self) -> str:
        """
        Identify primary driver of failure
        
        Returns:
            str: Description of primary driver
        """
        breach_info = self.results.get('breach_info')
        
        if not breach_info:
            return "No failure - scenario survived"
        
        breach_type = breach_info['type']
        
        # Analyze patterns leading to breach
        period_results = self.period_results[:breach_info['period'] + 1]
        
        total_outflows = sum(
            sum(result['outflows'].values())
            for result in period_results
        )
        
        total_losses = sum(
            result.get('losses', 0)
            for result in period_results
        )
        
        # Determine primary driver
        if breach_type == 'Liquidity' or breach_type == 'LCR':
            if total_outflows > total_losses * 5:
                return "Severe deposit withdrawals exceeded liquidity buffers"
            else:
                return "Asset fire-sale losses depleted liquidity"
        
        elif breach_type == 'CET1':
            return "Realized losses from asset liquidations eroded capital"
        
        else:
            return f"Breach of {breach_type}"
    
    def get_asset_depletion_analysis(self) -> Dict:
        """
        Analyze asset depletion patterns
        
        Returns:
            Dict: Asset depletion analysis
        """
        asset_sales = {}
        
        for result in self.period_results:
            for liquidation in result.get('liquidations', []):
                asset_type = liquidation['asset_type']
                amount = liquidation['amount_liquidated']
                
                if asset_type not in asset_sales:
                    asset_sales[asset_type] = {
                        'total_sold': 0,
                        'total_loss': 0,
                        'count': 0
                    }
                
                asset_sales[asset_type]['total_sold'] += amount
                asset_sales[asset_type]['total_loss'] += liquidation['loss']
                asset_sales[asset_type]['count'] += 1
        
        # Calculate averages
        for asset_type in asset_sales:
            total_sold = asset_sales[asset_type]['total_sold']
            total_loss = asset_sales[asset_type]['total_loss']
            
            if total_sold > 0:
                asset_sales[asset_type]['avg_haircut'] = (total_loss / total_sold) * 100
            else:
                asset_sales[asset_type]['avg_haircut'] = 0
        
        return asset_sales
    
    def get_metrics_trajectory(self) -> Dict[str, List[float]]:
        """
        Get time series of key metrics
        
        Returns:
            Dict: Time series data
        """
        trajectory = {
            'period': [],
            'lcr': [],
            'cet1_ratio': [],
            'liquid_assets': [],
            'total_deposits': []
        }
        
        for result in self.period_results:
            metrics = result.get('metrics', {})
            
            trajectory['period'].append(result['period'])
            trajectory['lcr'].append(metrics.get('lcr', 0))
            trajectory['cet1_ratio'].append(metrics.get('cet1_ratio', 0))
            trajectory['liquid_assets'].append(metrics.get('liquid_assets', 0))
            trajectory['total_deposits'].append(metrics.get('total_deposits', 0))
        
        return trajectory
    
    def generate_summary_report(self) -> Dict:
        """
        Generate comprehensive summary report
        
        Returns:
            Dict: Summary report
        """
        return {
            'survival_horizon': self.get_survival_horizon(),
            'breach_analysis': self.get_breach_analysis(),
            'primary_driver': self.get_primary_driver(),
            'critical_periods': self.get_critical_periods(),
            'asset_depletion': self.get_asset_depletion_analysis(),
            'total_asset_depletion': self.results.get('asset_depletion', 0),
            'total_losses': self.results.get('total_losses', 0),
            'capital_erosion_pct': self.results.get('capital_erosion', 0),
            'final_lcr': self.results.get('final_lcr', 0),
            'final_cet1': self.results.get('final_cet1', 0)
        }
