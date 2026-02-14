# SPECIFIC FIX FOR YOUR APP
# Replace the problematic section in show_simulation() function

# ==========================================
# PROBLEM LOCATION: show_simulation() function
# Line: scenario=st.session_state.scenarios[0]
# ==========================================

# BEFORE (CAUSES ERROR):
"""
engine = LiquidityEngine(
    balance_sheet=st.session_state.balance_sheet,
    scenario=st.session_state.scenarios[0],  # ❌ This is a dict!
    liquidation_order=liquidation_order
)
"""

# AFTER (FIXED):
"""
from src.stress_scenarios import StressScenario

# Find the selected scenario
selected_scenario_dict = next(
    (s for s in st.session_state.scenarios if s['name'] == selected_scenario),
    st.session_state.scenarios[0]
)

# Convert dict to StressScenario object
scenario_obj = StressScenario.from_dict(selected_scenario_dict)

# Now create engine with object
engine = LiquidityEngine(
    balance_sheet=st.session_state.balance_sheet,
    scenario=scenario_obj,  # ✅ Now it's an object!
    liquidation_order=liquidation_order
)
"""

# ==========================================
# COMPLETE FIXED show_simulation() FUNCTION
# Copy and paste this to replace your current function
# ==========================================

def show_simulation():
    """Run Simulation Page"""
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
                # ✅ FIX STARTS HERE
                from src.stress_scenarios import StressScenario
                
                # Find the selected scenario (it's a dict)
                selected_scenario_dict = next(
                    (s for s in st.session_state.scenarios if s['name'] == selected_scenario),
                    st.session_state.scenarios[0]
                )
                
                # Convert dict to StressScenario object
                scenario_obj = StressScenario.from_dict(selected_scenario_dict)
                # ✅ FIX ENDS HERE
                
                # Create simulation engine
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


# ==========================================
# ALSO FIX: show_stress_scenarios() function
# The scenario is being saved as a dict - this is OK,
# but we need to make it a proper StressScenario dict
# ==========================================

def show_stress_scenarios_FIXED():
    """Stress Scenarios Page - FIXED VERSION"""
    # ... (keep all the existing code until the save button)
    
    # At the "Save Scenario" button section, replace with:
    if st.button("💾 Save Scenario", type="primary", use_container_width=True):
        # Create scenario object with proper structure
        from src.stress_scenarios import StressScenario
        
        # Build the complete scenario dict
        scenario_dict = {
            'name': scenario_name,
            'time_granularity': time_granularity,
            'num_periods': num_periods,
            'runoff_rates': {
                'retail_stable': retail_stable_runoff / 100,
                'retail_unstable': retail_unstable_runoff / 100,
                'corporate_deposits': corporate_runoff / 100,
                'wholesale_funding': wholesale_runoff / 100,
                'secured_funding': secured_runoff / 100
            } if scenario_type == "Uniform Run-off" else {},
            'security_shocks': {
                'hqla_level1': hqla_l1_shock,
                'hqla_level2a': hqla_l2a_shock,
                'hqla_level2b': hqla_l2b_shock,
                'other_securities': other_sec_shock
            },
            'fire_sale_discount': fire_sale_base,
            'fire_sale_increment': fire_sale_increment,
            'funding_spread_increase': funding_spread,
            'collateral_haircut_increase': collateral_haircut,
            'loan_migration_rate': loan_migration_rate,
            'provisioning_rate': provisioning_rate,
            'rwa_increase': rwa_increase,
            'description': f"Created on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'created_at': datetime.now().isoformat()
        }
        
        # Validate by creating object and converting back to dict
        try:
            scenario_obj = StressScenario(**scenario_dict)
            validated_dict = scenario_obj.to_dict()
            
            st.session_state.scenarios.append(validated_dict)
            log_user_action("scenario_saved", {'name': scenario_name})
            st.success(f"✅ Scenario '{scenario_name}' saved successfully!")
        except Exception as e:
            st.error(f"❌ Error creating scenario: {str(e)}")
