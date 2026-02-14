"""
Visualization Module
Creates charts and visualizations for simulation results
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class Visualizer:
    """
    Creates visualizations for simulation results
    """
    
    @staticmethod
    def create_balance_sheet_waterfall(
        initial_bs,
        final_bs,
        title: str = "Balance Sheet Evolution"
    ) -> go.Figure:
        """
        Create waterfall chart showing balance sheet changes
        
        Args:
            initial_bs: Initial balance sheet
            final_bs: Final balance sheet
            title: Chart title
            
        Returns:
            plotly Figure
        """
        # Calculate changes
        changes = {
            'Cash & Reserves': (
                final_bs.data['assets'].get('cash_reserves', 0) -
                initial_bs.data['assets'].get('cash_reserves', 0)
            ),
            'HQLA': (
                final_bs.total_hqla() - initial_bs.total_hqla()
            ),
            'Loans': (
                final_bs.data['assets'].get('performing_loans', 0) -
                initial_bs.data['assets'].get('performing_loans', 0)
            ),
            'Other Assets': (
                (final_bs.data['assets'].get('real_estate', 0) +
                 final_bs.data['assets'].get('other_securities', 0)) -
                (initial_bs.data['assets'].get('real_estate', 0) +
                 initial_bs.data['assets'].get('other_securities', 0))
            )
        }
        
        # Create waterfall
        fig = go.Figure(go.Waterfall(
            name="Balance Sheet",
            orientation="v",
            measure=["absolute"] + ["relative"] * len(changes) + ["total"],
            x=["Opening"] + list(changes.keys()) + ["Closing"],
            y=[initial_bs.total_assets()] + list(changes.values()) + [final_bs.total_assets()],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title=title,
            showlegend=False,
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_metrics_evolution(
        period_results: List[Dict],
        title: str = "Key Metrics Evolution"
    ) -> go.Figure:
        """
        Create line chart showing metric evolution over time
        
        Args:
            period_results: List of period results
            title: Chart title
            
        Returns:
            plotly Figure
        """
        # Extract data
        periods = [r['period'] for r in period_results]
        lcr = [r['metrics'].get('lcr', 0) for r in period_results]
        cet1 = [r['metrics'].get('cet1_ratio', 0) for r in period_results]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Liquidity Coverage Ratio (%)', 'CET1 Capital Ratio (%)'),
            vertical_spacing=0.15
        )
        
        # LCR
        fig.add_trace(
            go.Scatter(x=periods, y=lcr, name='LCR', line=dict(color='#1f77b4', width=2)),
            row=1, col=1
        )
        fig.add_hline(y=100, line_dash="dash", line_color="red", 
                     annotation_text="Minimum 100%", row=1, col=1)
        
        # CET1
        fig.add_trace(
            go.Scatter(x=periods, y=cet1, name='CET1', line=dict(color='#2ca02c', width=2)),
            row=2, col=1
        )
        fig.add_hline(y=4.5, line_dash="dash", line_color="red",
                     annotation_text="Minimum 4.5%", row=2, col=1)
        
        fig.update_xaxes(title_text="Period", row=2, col=1)
        fig.update_yaxes(title_text="%", row=1, col=1)
        fig.update_yaxes(title_text="%", row=2, col=1)
        
        fig.update_layout(
            title=title,
            height=700,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_liquidity_buffer_chart(
        period_results: List[Dict],
        title: str = "Liquidity Buffer Depletion"
    ) -> go.Figure:
        """
        Create stacked area chart showing liquidity buffer over time
        
        Args:
            period_results: List of period results
            title: Chart title
            
        Returns:
            plotly Figure
        """
        periods = [r['period'] for r in period_results]
        liquid_assets = [r['metrics'].get('liquid_assets', 0) for r in period_results]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=periods,
            y=liquid_assets,
            fill='tozeroy',
            name='Liquid Assets',
            line=dict(color='#17becf')
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Period",
            yaxis_title="€ Millions",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_deposit_outflow_chart(
        period_results: List[Dict],
        title: str = "Cumulative Deposit Outflows"
    ) -> go.Figure:
        """
        Create chart showing deposit outflows by type
        
        Args:
            period_results: List of period results
            title: Chart title
            
        Returns:
            plotly Figure
        """
        # Aggregate outflows by type
        deposit_types = ['retail_stable', 'retail_unstable', 'corporate_deposits', 
                        'wholesale_funding', 'secured_funding']
        
        cumulative = {dt: [] for dt in deposit_types}
        periods = []
        
        for result in period_results:
            periods.append(result['period'])
            outflows = result.get('outflows', {})
            
            for dt in deposit_types:
                if not cumulative[dt]:
                    cumulative[dt].append(outflows.get(dt, 0))
                else:
                    cumulative[dt].append(cumulative[dt][-1] + outflows.get(dt, 0))
        
        # Create figure
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        labels = {
            'retail_stable': 'Stable Retail',
            'retail_unstable': 'Unstable Retail',
            'corporate_deposits': 'Corporate',
            'wholesale_funding': 'Wholesale',
            'secured_funding': 'Secured'
        }
        
        for i, dt in enumerate(deposit_types):
            fig.add_trace(go.Scatter(
                x=periods,
                y=cumulative[dt],
                name=labels[dt],
                stackgroup='one',
                line=dict(color=colors[i])
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Period",
            yaxis_title="Cumulative Outflow (€M)",
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_asset_liquidation_chart(
        period_results: List[Dict],
        title: str = "Asset Liquidation by Type"
    ) -> go.Figure:
        """
        Create bar chart showing asset liquidations
        
        Args:
            period_results: List of period results
            title: Chart title
            
        Returns:
            plotly Figure
        """
        # Aggregate liquidations
        asset_totals = {}
        
        for result in period_results:
            for liq in result.get('liquidations', []):
                asset_type = liq['asset_type']
                amount = liq['amount_liquidated']
                
                if asset_type not in asset_totals:
                    asset_totals[asset_type] = 0
                asset_totals[asset_type] += amount
        
        if not asset_totals:
            # No liquidations
            fig = go.Figure()
            fig.add_annotation(
                text="No asset liquidations occurred",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Create bar chart
        assets = list(asset_totals.keys())
        amounts = list(asset_totals.values())
        
        # Prettier labels
        label_map = {
            'cash_reserves': 'Cash',
            'hqla_level1': 'HQLA L1',
            'hqla_level2a': 'HQLA L2A',
            'hqla_level2b': 'HQLA L2B',
            'other_securities': 'Other Securities',
            'performing_loans': 'Loans',
            'real_estate': 'Real Estate'
        }
        
        assets = [label_map.get(a, a) for a in assets]
        
        fig = go.Figure(data=[
            go.Bar(
                x=assets,
                y=amounts,
                marker_color='#d62728'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title="Asset Type",
            yaxis_title="Amount Liquidated (€M)",
            height=400
        )
        
        return fig
