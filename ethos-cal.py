import streamlit as st
import pandas as pd
import numpy as np

# Set page config at the very beginning
st.set_page_config(
    page_title="Ethos Lending Revenue Share Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state if not exists
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.total_rev_share = 0
    st.session_state.total_volume = 0

def calculate_level_rev_share(lo_count, units, volume, bonus_percent, generation_bonus):
    """Calculate revenue share for a specific level"""
    try:
        base_rev_share = float(volume) * float(bonus_percent)
        generation_bonus_amount = float(volume) * float(generation_bonus)
        return base_rev_share + generation_bonus_amount
    except Exception as e:
        st.error(f"Calculation error: {str(e)}")
        return 0

def calculate_profit_sharing_bonus(company_lo_count, annual_units_per_lo, avg_loan_size, profit_sharing_percent, share_max):
    """Calculate profit sharing bonus"""
    try:
        company_volume = float(company_lo_count) * float(annual_units_per_lo) * float(avg_loan_size)
        total_bonus = company_volume * float(profit_sharing_percent)
        return total_bonus * (float(share_max) / 100)
    except Exception as e:
        st.error(f"Calculation error: {str(e)}")
        return 0

def main():
    try:
        st.title("Ethos Lending Revenue Share Calculator")
        
        # Sidebar with company branding
        with st.sidebar:
            st.header("Basic Information")
            ambassador_name = st.text_input("Ambassador Name", key='ambassador_name')
            paid_as_title = st.text_input("Paid-As Title", value="DIR3", key='paid_as_title')
            frontline_legs = st.number_input("Frontline Legs", value=10, min_value=0, key='frontline_legs')
            team_loans = st.number_input("Team Loans", value=1190, min_value=0, key='team_loans')
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        # Level 1 Calculations
        with col1:
            st.subheader("Level 1 Revenue Share")
            l1_lo_count = st.number_input("Level 1 LO Count", value=10, min_value=0, key="l1_lo")
            l1_units = st.number_input("Level 1 Units", value=200, min_value=0, key="l1_units")
            l1_volume = st.number_input("Level 1 Revenue Share Volume", value=61200000, min_value=0, key="l1_volume")
            l1_bonus = st.number_input("Level 1 Bonus %", value=0.001, format="%.3f", key="l1_bonus")
            l1_gen_bonus = st.number_input("Level 1 Generation Bonus %", value=0.0001, format="%.4f", key="l1_gen")
            
            l1_rev_share = calculate_level_rev_share(l1_lo_count, l1_units, l1_volume, l1_bonus, l1_gen_bonus)
            st.metric("Level 1 Revenue Share", f"${l1_rev_share:,.2f}")
        
        # Level 2 Calculations
        with col2:
            st.subheader("Level 2 Revenue Share")
            l2_lo_count = st.number_input("Level 2 LO Count", value=20, min_value=0, key="l2_lo")
            l2_units = st.number_input("Level 2 Units", value=480, min_value=0, key="l2_units")
            l2_volume = st.number_input("Level 2 Revenue Share Volume", value=121200000, min_value=0, key="l2_volume")
            l2_bonus = st.number_input("Level 2 Bonus %", value=0.001, format="%.3f", key="l2_bonus")
            l2_gen_bonus = st.number_input("Level 2 Generation Bonus %", value=0.0001, format="%.4f", key="l2_gen")
            
            l2_rev_share = calculate_level_rev_share(l2_lo_count, l2_units, l2_volume, l2_bonus, l2_gen_bonus)
            st.metric("Level 2 Revenue Share", f"${l2_rev_share:,.2f}")
        
        # Level 3 and Profit Sharing
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Level 3 Revenue Share")
            l3_lo_count = st.number_input("Level 3 LO Count", value=30, min_value=0, key="l3_lo")
            l3_units = st.number_input("Level 3 Units", value=510, min_value=0, key="l3_units")
            l3_volume = st.number_input("Level 3 Revenue Share Volume", value=181050000, min_value=0, key="l3_volume")
            l3_bonus = st.number_input("Level 3 Bonus %", value=0.0007, format="%.4f", key="l3_bonus")
            l3_gen_bonus = st.number_input("Level 3 Generation Bonus %", value=0.0001, format="%.4f", key="l3_gen")
            
            l3_rev_share = calculate_level_rev_share(l3_lo_count, l3_units, l3_volume, l3_bonus, l3_gen_bonus)
            st.metric("Level 3 Revenue Share", f"${l3_rev_share:,.2f}")
        
        with col4:
            st.subheader("Profit Sharing Bonus")
            company_lo_count = st.number_input("Company LO Count", value=200, min_value=0)
            annual_units_per_lo = st.number_input("Annual Units per LO", value=24, min_value=0)
            avg_loan_size = st.number_input("Average Loan Size", value=400000, min_value=0)
            profit_sharing_percent = st.number_input("Profit Sharing %", value=0.0001, format="%.4f")
            share_max = st.number_input("Share Max %", value=25.0, min_value=0.0, max_value=100.0)
            
            profit_sharing_bonus = calculate_profit_sharing_bonus(
                company_lo_count, 
                annual_units_per_lo, 
                avg_loan_size, 
                profit_sharing_percent, 
                share_max
            )
            st.metric("Profit Sharing Bonus", f"${profit_sharing_bonus:,.2f}")
        
        # Summary section
        st.divider()
        st.header("Summary")
        total_rev_share = l1_rev_share + l2_rev_share + l3_rev_share + profit_sharing_bonus
        total_volume = l1_volume + l2_volume + l3_volume
        
        col5, col6 = st.columns(2)
        with col5:
            st.metric("Total Revenue Share", f"${total_rev_share:,.2f}")
        with col6:
            st.metric("Total Revenue Share Volume", f"${total_volume:,.2f}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")