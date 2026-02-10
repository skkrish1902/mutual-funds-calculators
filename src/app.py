import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
from calculator import (
    calculate_sip,
    calculate_lumpsum,
    compare_investments,
    calculate_required_return,
    calculate_sip_with_hold_period,
    calculate_lumpsum_with_hold_period
)

# Page configuration
st.set_page_config(
    page_title="Mutual Funds Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .result-container {
        background-color: #d4edda;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .amount-label {
        font-size: 0.75em;
        vertical-align: super;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)


def format_amount_with_label(amount: float) -> str:
    """
    Format amount with Indian numbering system explanation.
    
    Args:
        amount: The amount to format
    
    Returns:
        Formatted string like "1,00,000 (1 lakh)"
    """
    if amount < 0:
        return format_amount_with_label(-amount)
    
    # Get Indian numbering label
    amount_int = int(amount)
    
    if amount_int >= 10000000:  # Crore
        crore = amount_int / 10000000
        if crore == int(crore):
            label = f"{int(crore)} Cr"
        else:
            label = f"{crore:.1f} Cr"
    elif amount_int >= 100000:  # Lakh
        lakh = amount_int / 100000
        if lakh == int(lakh):
            label = f"{int(lakh)} L"
        else:
            label = f"{lakh:.1f} L"
    elif amount_int >= 1000:  # Thousand
        thousand = amount_int / 1000
        if thousand == int(thousand):
            label = f"{int(thousand)}K"
        else:
            label = f"{thousand:.1f}K"
    else:
        label = str(amount_int)
    
    # Format amount with commas
    decimal_part = amount - amount_int
    if decimal_part > 0:
        amount_str = f"{amount:,.2f}"
    else:
        amount_str = f"{amount_int:,}"
    
    return f"₹{amount_str}<sup style='font-size:0.65em;color:#666;'> ({label})</sup>"


def display_metric(col, label: str, amount: float, suffix: str = ""):
    """Display a metric with Indian numbering label"""
    if isinstance(amount, (int, float)):
        formatted = format_amount_with_label(amount)
        col.markdown(f"**{label}**  \n{formatted} {suffix}", unsafe_allow_html=True)
    else:
        col.metric(label, amount)

def display_sip_calculator():
    """Display SIP Calculator Section"""
    st.subheader("💰 SIP (Systematic Investment Plan) Calculator")
    
    # Fund Type Selection
    col_type, col_tax = st.columns(2)
    with col_type:
        fund_type = st.radio(
            "Fund Type",
            ["Equity", "Debt"],
            horizontal=True,
            key="sip_fund_type"
        )
    
    with col_tax:
        calculate_tax = st.checkbox(
            "Calculate Tax Impact",
            value=True,
            key="sip_calc_tax"
        )
    
    # Tax slab selector for debt funds
    if fund_type == "Debt" and calculate_tax:
        investor_slab = st.select_slider(
            "Your Income Tax Slab",
            options=["0%", "5%", "10%", "15%", "20%", "30%"],
            value="30%",
            key="sip_debt_slab"
        )
    else:
        investor_slab = "30%"
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_investment = st.number_input(
            "Monthly Investment Amount (₹)",
            min_value=500,
            value=5000,
            step=100,
            help="Minimum ₹500"
        )
    
    with col2:
        annual_return = st.slider(
            "Expected Annual Return (%)",
            min_value=0.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            help="Typical equity funds: 8-15%, Debt funds: 4-8%"
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        years = st.slider(
            "Investment Period (Years)",
            min_value=1,
            max_value=40,
            value=10,
            step=1
        )
    
    with col4:
        start_date = st.date_input(
            "Investment Start Date",
            value=datetime.now()
        )
    
    if st.button("Calculate SIP", key="sip_calc"):
        result = calculate_sip(
            monthly_investment, 
            annual_return, 
            years,
            fund_type=fund_type.lower(),
            investor_tax_slab=investor_slab,
            calculate_tax=calculate_tax
        )
        
        if "error" not in result:
            st.divider()
            
            # Display results with and without tax
            if calculate_tax and "tax_info" in result:
                col1, col2, col3, col4, col5 = st.columns(5)
                
                display_metric(col1, "Total Invested", result['total_invested'])
                display_metric(col2, "Maturity\n(Before Tax)", result['maturity_amount'])
                display_metric(col3, "Tax", result['tax_info']['tax_amount'])
                display_metric(col4, "Maturity\n(After Tax)", result['maturity_after_tax'])
                col5.metric("Effective Tax Rate", f"{result['tax_info']['effective_tax_rate']:.2f}%")
                
                # Tax Info Box
                st.info(f"""
                **Tax Information:**
                - Fund Type: {fund_type} Mutual Fund
                - Holding Period: {result['months']} months
                - Tax Type: {result['tax_info']['tax_type']}
                - Gain Before Tax: ₹{result['gain']:,.0f}
                - Gain After Tax: ₹{result['tax_info']['gain_after_tax']:,.0f}
                {f"- Tax Slab: {investor_slab}" if fund_type == "Debt" else ""}
                """)
            else:
                col1, col2, col3, col4 = st.columns(4)
                
                display_metric(col1, "Maturity Amount", result['maturity_amount'])
                display_metric(col2, "Total Invested", result['total_invested'])
                display_metric(col3, "Total Gain", result['gain'])
                col4.metric("Return %", f"{result['gain_percentage']:.2f}%")
            
            # Breakdown visualization
            st.divider()
            
            # Pie chart
            col1, col2 = st.columns(2)
            
            with col1:
                if calculate_tax and "tax_info" in result:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Invested Amount', 'Gain After Tax', 'Tax Paid'],
                            values=[
                                result['total_invested'],
                                result['tax_info']['gain_after_tax'],
                                result['tax_info']['tax_amount']
                            ],
                            marker=dict(colors=['#1f77b4', '#2ca02c', '#d62728']),
                            hole=0.3
                        )
                    ])
                else:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Invested Amount', 'Gain'],
                            values=[result['total_invested'], result['gain']],
                            marker=dict(colors=['#1f77b4', '#2ca02c']),
                            hole=0.3
                        )
                    ])
                fig.update_layout(
                    title="Investment Breakdown",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Growth over time visualization
                months_array = []
                maturity_array = []
                invested_array = []
                
                monthly_rate = annual_return / 12 / 100
                
                for month in range(0, result['months'] + 1, 12):
                    months_array.append(month / 12)
                    
                    invested = monthly_investment * month
                    invested_array.append(invested)
                    
                    if monthly_rate == 0:
                        maturity = invested
                    else:
                        if month == 0:
                            maturity = 0
                        else:
                            maturity = monthly_investment * (
                                (((1 + monthly_rate) ** month - 1) / monthly_rate) * (1 + monthly_rate)
                            )
                    maturity_array.append(maturity)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=months_array,
                    y=invested_array,
                    mode='lines',
                    name='Invested Amount',
                    fill='tozeroy',
                    line=dict(color='#1f77b4')
                ))
                fig.add_trace(go.Scatter(
                    x=months_array,
                    y=maturity_array,
                    mode='lines',
                    name='Maturity Amount',
                    fill='tonexty',
                    line=dict(color='#2ca02c')
                ))
                
                fig.update_layout(
                    title="Growth Over Time",
                    xaxis_title="Years",
                    yaxis_title="Amount (₹)",
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)


def display_lumpsum_calculator():
    """Display Lumpsum Calculator Section"""
    st.subheader("🎯 Lumpsum Investment Calculator")
    
    # Fund Type Selection
    col_type, col_tax = st.columns(2)
    with col_type:
        fund_type = st.radio(
            "Fund Type",
            ["Equity", "Debt"],
            horizontal=True,
            key="lumpsum_fund_type"
        )
    
    with col_tax:
        calculate_tax = st.checkbox(
            "Calculate Tax Impact",
            value=True,
            key="lumpsum_calc_tax"
        )
    
    # Tax slab selector for debt funds
    if fund_type == "Debt" and calculate_tax:
        investor_slab = st.select_slider(
            "Your Income Tax Slab",
            options=["0%", "5%", "10%", "15%", "20%", "30%"],
            value="30%",
            key="lumpsum_debt_slab"
        )
    else:
        investor_slab = "30%"
    
    col1, col2 = st.columns(2)
    
    with col1:
        principal = st.number_input(
            "Investment Amount (₹)",
            min_value=1000,
            value=100000,
            step=1000,
            key="lumpsum_principal",
            help="Minimum ₹1000"
        )
    
    with col2:
        annual_return = st.slider(
            "Expected Annual Return (%)",
            min_value=0.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            key="lumpsum_return"
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        years = st.slider(
            "Investment Period (Years)",
            min_value=1,
            max_value=40,
            value=10,
            step=1,
            key="lumpsum_years"
        )
    
    with col4:
        start_date = st.date_input(
            "Investment Start Date",
            value=datetime.now(),
            key="lumpsum_start"
        )
    
    if st.button("Calculate Lumpsum", key="lumpsum_calc"):
        result = calculate_lumpsum(
            principal, 
            annual_return, 
            years,
            fund_type=fund_type.lower(),
            investor_tax_slab=investor_slab,
            calculate_tax=calculate_tax
        )
        
        if "error" not in result:
            st.divider()
            
            # Display results with and without tax
            if calculate_tax and "tax_info" in result:
                col1, col2, col3, col4, col5 = st.columns(5)
                
                display_metric(col1, "Principal", result['principal'])
                display_metric(col2, "Maturity\n(Before Tax)", result['maturity_amount'])
                display_metric(col3, "Tax", result['tax_info']['tax_amount'])
                display_metric(col4, "Maturity\n(After Tax)", result['maturity_after_tax'])
                col5.metric("Effective Tax Rate", f"{result['tax_info']['effective_tax_rate']:.2f}%")
                
                # Tax Info Box
                st.info(f"""
                **Tax Information:**
                - Fund Type: {fund_type} Mutual Fund
                - Holding Period: {result['years']} years
                - Tax Type: {result['tax_info']['tax_type']}
                - Gain Before Tax: ₹{result['gain']:,.0f}
                - Gain After Tax: ₹{result['tax_info']['gain_after_tax']:,.0f}
                {f"- Tax Slab: {investor_slab}" if fund_type == "Debt" else ""}
                """)
            else:
                col1, col2, col3, col4 = st.columns(4)
                
                display_metric(col1, "Principal", result['principal'])
                display_metric(col2, "Maturity Amount", result['maturity_amount'])
                display_metric(col3, "Total Gain", result['gain'])
                col4.metric("Return %", f"{result['gain_percentage']:.2f}%")
            
            # Breakdown visualization
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if calculate_tax and "tax_info" in result:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Principal', 'Gain After Tax', 'Tax Paid'],
                            values=[
                                result['principal'],
                                result['tax_info']['gain_after_tax'],
                                result['tax_info']['tax_amount']
                            ],
                            marker=dict(colors=['#ff7f0e', '#2ca02c', '#d62728']),
                            hole=0.3
                        )
                    ])
                else:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Principal', 'Gain'],
                            values=[result['principal'], result['gain']],
                            marker=dict(colors=['#ff7f0e', '#d62728']),
                            hole=0.3
                        )
                    ])
                fig.update_layout(
                    title="Investment Breakdown",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Growth over time visualization
                years_array = []
                maturity_array = []
                
                annual_rate = annual_return / 100
                
                for year in range(years + 1):
                    years_array.append(year)
                    maturity = principal * ((1 + annual_rate) ** year)
                    maturity_array.append(maturity)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=years_array,
                    y=maturity_array,
                    mode='lines+markers',
                    name='Maturity Amount',
                    fill='tozeroy',
                    line=dict(color='#ff7f0e')
                ))
                
                fig.update_layout(
                    title="Growth Over Time",
                    xaxis_title="Years",
                    yaxis_title="Amount (₹)",
                    height=400,
                    hovermode='x'
                )
                st.plotly_chart(fig, use_container_width=True)


def display_comparison():
    """Display SIP vs Lumpsum Comparison"""
    st.subheader("⚖️ Compare SIP vs Lumpsum")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        monthly_sip = st.number_input(
            "Monthly SIP Amount (₹)",
            min_value=500,
            value=5000,
            step=100,
            key="compare_sip"
        )
    
    with col2:
        lumpsum = st.number_input(
            "Lumpsum Amount (₹)",
            min_value=1000,
            value=60000,
            step=1000,
            key="compare_lumpsum",
            help=f"Suggested: ₹{monthly_sip * 12}"
        )
    
    with col3:
        annual_return_compare = st.slider(
            "Expected Return (%)",
            min_value=0.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            key="compare_return"
        )
    
    with col4:
        years_compare = st.slider(
            "Investment Period (Years)",
            min_value=1,
            max_value=40,
            value=10,
            step=1,
            key="compare_years"
        )
    
    if st.button("Compare Investments"):
        result = compare_investments(monthly_sip, lumpsum, annual_return_compare, years_compare)
        
        if "error" not in result:
            st.divider()
            
            # Comparison metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "SIP Maturity",
                    f"₹{result['sip']['maturity_amount']:,.0f}",
                    f"₹{result['sip']['gain']:,.0f} gain"
                )
            
            with col2:
                st.metric(
                    "Lumpsum Maturity",
                    f"₹{result['lumpsum']['maturity_amount']:,.0f}",
                    f"₹{result['lumpsum']['gain']:,.0f} gain"
                )
            
            with col3:
                better = result['better_option']
                difference = abs(result['difference'])
                st.metric(
                    "Better Option",
                    better,
                    f"More by ₹{difference:,.0f}"
                )
            
            # Comparison chart
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                comparison_data = {
                    'Strategy': ['SIP', 'Lumpsum'],
                    'Maturity Amount': [
                        result['sip']['maturity_amount'],
                        result['lumpsum']['maturity_amount']
                    ],
                    'Total Invested': [
                        result['sip']['total_invested'],
                        result['lumpsum']['principal']
                    ]
                }
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=comparison_data['Strategy'],
                    y=comparison_data['Maturity Amount'],
                    name='Maturity Amount',
                    marker_color=['#1f77b4', '#ff7f0e']
                ))
                fig.update_layout(
                    title="Maturity Amount Comparison",
                    yaxis_title="Amount (₹)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=comparison_data['Strategy'],
                    y=comparison_data['Total Invested'],
                    name='Total Invested',
                    marker_color=['#2ca02c', '#d62728']
                ))
                fig.update_layout(
                    title="Total Invested Amount",
                    yaxis_title="Amount (₹)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def display_growth_holding_period():
    """Display Investment with Growth Holding Period Calculator"""
    st.subheader("📈 Investment with Growth Holding Period")
    st.markdown("""
    Calculate returns for both **SIP** and **Lumpsum** with:
    - Active investment period
    - Hold period (no new investments, just compound growth)
    - **Before and After Tax Analysis**
    """)
    
    # Fund Type and Tax Settings
    col_type, col_tax = st.columns(2)
    
    with col_type:
        fund_type = st.radio(
            "Fund Type",
            ["Equity", "Debt"],
            horizontal=True,
            key="ghp_fund_type"
        )
    
    with col_tax:
        calculate_tax = st.checkbox(
            "Calculate Tax Impact",
            value=True,
            key="ghp_calc_tax"
        )
    
    # Tax slab selector for debt funds
    if fund_type == "Debt" and calculate_tax:
        investor_slab = st.select_slider(
            "Your Income Tax Slab",
            options=["0%", "5%", "10%", "15%", "20%", "30%"],
            value="30%",
            key="ghp_debt_slab"
        )
    else:
        investor_slab = "30%"
    
    # Input section
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        investment_type = st.radio(
            "Investment Type",
            ["SIP", "Lumpsum"],
            horizontal=True,
            key="ghp_type"
        )
    
    with col2:
        if investment_type == "SIP":
            monthly_investment = st.number_input(
                "Monthly Investment (₹)",
                min_value=500,
                value=5000,
                step=100,
                key="ghp_sip_amount"
            )
        else:
            lumpsum_amount = st.number_input(
                "Lumpsum Amount (₹)",
                min_value=1000,
                value=100000,
                step=1000,
                key="ghp_lumpsum_amount"
            )
    
    with col3:
        investment_years = st.slider(
            "Investment Period (Years)",
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            key="ghp_invest_years"
        )
    
    with col4:
        hold_years = st.slider(
            "Hold Period (Years)",
            min_value=0,
            max_value=30,
            value=3,
            step=1,
            key="ghp_hold_years",
            help="Years to hold without new investments"
        )
    
    col5, col6 = st.columns(2)
    
    with col5:
        annual_return = st.slider(
            "Expected Annual Return (%)",
            min_value=0.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            key="ghp_return"
        )
    
    with col6:
        st.empty()  # Spacing
    
    if st.button("Calculate Growth with Hold Period", key="ghp_calc"):
        st.divider()
        
        if investment_type == "SIP":
            result = calculate_sip_with_hold_period(
                monthly_investment, 
                investment_years, 
                hold_years, 
                annual_return,
                fund_type=fund_type.lower(),
                investor_tax_slab=investor_slab,
                calculate_tax=calculate_tax
            )
        else:
            result = calculate_lumpsum_with_hold_period(
                lumpsum_amount, 
                investment_years, 
                hold_years, 
                annual_return,
                fund_type=fund_type.lower(),
                investor_tax_slab=investor_slab,
                calculate_tax=calculate_tax
            )
        
        if "error" not in result:
            # Summary metrics with tax info
            if calculate_tax and "tax_info" in result:
                col1, col2, col3, col4, col5 = st.columns(5)
                
                display_metric(col1, "Total Invested", result['total_invested'])
                display_metric(col2, "Final Maturity\n(Before Tax)", result['final_maturity'])
                display_metric(col3, "Tax Amount", result['tax_info']['tax_amount'])
                display_metric(col4, "Final Maturity\n(After Tax)", result['final_maturity_after_tax'])
                col5.metric("Effective Tax Rate", f"{result['tax_info']['effective_tax_rate']:.2f}%")
                
                # Tax Information Box
                st.warning(f"""
                **Tax Analysis (FY 2026-27):**
                - Fund Type: {fund_type} Mutual Fund
                - Tax Type: {result['tax_info']['tax_type']}
                - Total Gain (Before Tax): ₹{result['total_gain']:,.0f}
                - Tax Payable: ₹{result['tax_info']['tax_amount']:,.0f}
                - Net Gain (After Tax): ₹{result['tax_info']['gain_after_tax']:,.0f}
                {f"- Investor Tax Slab: {investor_slab}" if fund_type == "Debt" else f"- Threshold for LTCG Tax: ₹1.25 Lakh"}
                """)
            else:
                col1, col2, col3, col4, col5 = st.columns(5)
                
                display_metric(col1, "Total Invested", result['total_invested'])
                display_metric(col2, "After Investment Period", result['maturity_after_investment'])
                display_metric(col3, "Gain (Investment)", result['gain_during_investment'])
                display_metric(col4, "Final Maturity", result['final_maturity'])
                col5.metric("Total Gain %", f"{result['total_gain_percentage']:.2f}%")
            
            st.divider()
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Phase breakdown pie chart
                if calculate_tax and "tax_info" in result:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Invested Amount', 'Gain After Tax', 'Tax'],
                            values=[
                                result['total_invested'],
                                result['tax_info']['gain_after_tax'],
                                result['tax_info']['tax_amount']
                            ],
                            marker=dict(colors=['#1f77b4', '#2ca02c', '#d62728']),
                            hole=0.3
                        )
                    ])
                else:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Invested Amount', 'Gain During Investment', 'Growth During Hold'],
                            values=[
                                result['total_invested'],
                                result['gain_during_investment'],
                                result['total_gain'] - result['gain_during_investment']
                            ],
                            marker=dict(colors=['#1f77b4', '#2ca02c', '#ff7f0e']),
                            hole=0.3
                        )
                    ])
                fig.update_layout(
                    title="Investment Breakdown",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Growth trajectory
                years_array = [item['year'] for item in result['year_wise_data']]
                amount_array = [item['amount'] for item in result['year_wise_data']]
                phase_array = [item['phase'] for item in result['year_wise_data']]
                
                # Create color list based on phase
                colors = ['#1f77b4' if phase == 'Investment' else '#2ca02c' for phase in phase_array]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=years_array,
                    y=amount_array,
                    mode='lines+markers',
                    name='Amount',
                    fill='tozeroy',
                    line=dict(color='#1f77b4', width=2),
                    marker=dict(size=8, color=colors)
                ))
                
                # Add vertical line between investment and hold period
                fig.add_vline(
                    x=investment_years + 0.5,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Investment End",
                    annotation_position="top right"
                )
                
                fig.update_layout(
                    title="Growth Over Time",
                    xaxis_title="Years",
                    yaxis_title="Amount (₹)",
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Year-wise breakdown table
            st.divider()
            st.subheader("📊 Year-wise Breakdown")
            
            df_data = []
            for item in result['year_wise_data']:
                df_data.append({
                    'Year': item['year'],
                    'Phase': item['phase'],
                    'Invested (₹)': f"₹{item['invested']:,.0f}",
                    'Amount (₹)': f"₹{item['amount']:,.0f}",
                    'Gain (₹)': f"₹{item['gain']:,.0f}"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary info
            st.divider()
            st.markdown(f"""
            ### 📋 Summary
            
            **Investment Phase:** Years 1-{investment_years}
            - You invest: ₹{result['total_invested']:,.0f}
            - Amount grows to: ₹{result['maturity_after_investment']:,.0f}
            - Gain during investment: ₹{result['gain_during_investment']:,.0f}
            
            **Hold Phase:** Years {investment_years + 1}-{investment_years + hold_years}
            - No new investments
            - Compound growth on ₹{result['maturity_after_investment']:,.0f}
            - Final amount (before tax): ₹{result['final_maturity']:,.0f}
            
            **Tax Impact:**
            {f"- Tax Amount: ₹{result['tax_info']['tax_amount']:,.0f}" if calculate_tax else "- No tax calculated"}
            {f"- Final Amount (after tax): ₹{result['final_maturity_after_tax']:,.0f}" if calculate_tax else ""}
            
            **Total Outcome:**
            - Total invested: ₹{result['total_invested']:,.0f}
            - Final maturity (before tax): ₹{result['final_maturity']:,.0f}
            - Total gain (before tax): ₹{result['total_gain']:,.0f} ({result['total_gain_percentage']:.2f}%)
            {f"- Total gain (after tax): ₹{result['tax_info']['gain_after_tax']:,.0f}" if calculate_tax and "tax_info" in result else ""}
            """)



def main():
    """Main application"""
    # Header
    st.title("📊 Mutual Funds Calculator")
    st.markdown("""
    Calculate and compare **SIP** and **Lumpsum** investments in Indian mutual funds.
    
    **Data Sources:**
    - [AMFI (Association of Mutual Funds in India)](https://www.amfiindia.com/)
    - [NSE (National Stock Exchange)](https://www.nseindia.com/)
    """)
    
    st.divider()
    
    # Sidebar navigation
    st.sidebar.title("📱 Navigation")
    page = st.sidebar.radio(
        "Select Calculator",
        ["SIP Calculator", "Lumpsum Calculator", "Compare SIP vs Lumpsum", "Growth Holding Period", "About"]
    )
    
    if page == "SIP Calculator":
        display_sip_calculator()
    
    elif page == "Lumpsum Calculator":
        display_lumpsum_calculator()
    
    elif page == "Compare SIP vs Lumpsum":
        display_comparison()
    
    elif page == "Growth Holding Period":
        display_growth_holding_period()
    
    elif page == "About":
        st.header("About This Calculator")
        
        st.subheader("Features")
        st.write("""
        - **SIP Calculator**: Calculate maturity of monthly systematic investments (with tax impact)
        - **Lumpsum Calculator**: Calculate returns on one-time investments (with tax impact)
        - **Comparison Tool**: Compare SIP vs Lumpsum strategies side-by-side
        - **Growth Holding Period**: Calculate returns with investment and hold periods
        - **Tax Analysis**: Before and after-tax calculations for both equity and debt funds
        - **Visual Charts**: Interactive graphs showing investment growth
        """)
        
        st.subheader("Tax Features (FY 2026-27)")
        st.write("""
        **Equity Mutual Funds:**
        - LTCG (Long-term, >12 months): 12.5% tax on gains exceeding ₹1.25 lakh
        - STCG (Short-term, ≤12 months): 20% tax on all gains
        
        **Debt Mutual Funds:**
        - Taxed as per your income tax slab (0%, 5%, 10%, 15%, 20%, 30%)
        
        **Features:**
        - Select fund type (Equity/Debt)
        - Toggle tax calculations on/off
        - Choose your income tax slab (for debt funds)
        - View maturity amounts before and after tax
        - See effective tax rate and tax amount payable
        """)
        
        st.subheader("How to Use")
        st.write("""
        1. Select a calculator from the sidebar
        2. Enter your investment details
        3. View calculated results with visualizations
        4. Use the comparison tool to decide between SIP and Lumpsum
        """)
        
        st.subheader("Key Terms")
        st.write("""
        **SIP (Systematic Investment Plan)**: Regular monthly investments in mutual funds
        
        **Lumpsum**: One-time investment of a large amount
        
        **NAV (Net Asset Value)**: Per-unit market value of a mutual fund
        
        **Return Rate**: Expected annual percentage return on investment
        """)
        
        st.subheader("Important Links")
        st.write("""
        - [AMFI - Mutual Fund Data](https://www.amfiindia.com/)
        - [NSE - Market Data](https://www.nseindia.com/)
        - [SEBI - Investor Protection](https://www.sebi.gov.in/)
        """)
        
        st.subheader("Disclaimer")
        st.warning("""
        This calculator provides estimates based on expected returns. 
        Actual returns may vary based on market conditions and fund performance. 
        Please consult with a financial advisor before making investment decisions.
        """)


if __name__ == "__main__":
    main()
