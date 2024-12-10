import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Revenue Share Calculator", layout="wide")

# Title bonus rates
TITLE_BONUS_RATES = {
    'Ambassador (AMB)': {
        'level1_bonus': 0.0008,
        'level2_bonus': 0,
        'level3_bonus': 0,
        'has_profit_share': False
    },
    'Active Ambassador (AAMB)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0,
        'level3_bonus': 0,
        'has_profit_share': False
    },
    'Ambassador 2 (AMB2)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.0007,
        'level3_bonus': 0,
        'has_profit_share': False
    },
    'Ambassador 3 (AMB3)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.0007,
        'level3_bonus': 0.0005,
        'has_profit_share': False
    },
    'Director 1 (DIR1)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007,
        'has_profit_share': False
    },
    'Director 2 (DIR2)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007,
        'has_profit_share': False
    },
    'Director 3 (DIR3)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007,
        'has_profit_share': True
    }
}

def calculate_rev_share(title, level, units, avg_loan_size=445000, generation_bonus=0.0001):
    rates = TITLE_BONUS_RATES[title]
    volume = units * avg_loan_size
    commissionable_volume = volume * 0.20  # 20% of volume is commissionable
    
    if level == 'Level 1':
        bonus_rate = rates['level1_bonus']
    elif level == 'Level 2':
        bonus_rate = rates['level2_bonus']
    else:
        bonus_rate = rates['level3_bonus']
    
    rev_share = commissionable_volume * (bonus_rate + generation_bonus)
    
    return {
        'volume': volume,
        'commissionable_volume': commissionable_volume,
        'rev_share': rev_share,
        'bonus_rate': bonus_rate
    }

def calculate_profit_sharing(company_volume=2136000000):
    profit_sharing_rate = 0.0001  # 0.01%
    profit_sharing_share = 0.25   # 25%
    return company_volume * profit_sharing_rate * profit_sharing_share

# User Interface
st.title("🏦 Ethos Lending Revenue Share Calculator")

# Sidebar inputs
with st.sidebar:
    st.header("User Profile")
    user_name = st.text_input("Enter Your Name")
    
    st.header("Title Selection")
    selected_title = st.selectbox(
        "Select Your Title", 
        options=list(TITLE_BONUS_RATES.keys()),
        index=6  # Default to DIR3
    )
    
    st.header("Team Structure")
    level1_count = st.number_input("Level 1 LO Count", value=10, min_value=0)
    level2_count = st.number_input("Level 2 LO Count", value=20, min_value=0)
    level3_count = st.number_input("Level 3 LO Count", value=30, min_value=0)

if user_name:
    # Main calculation area
    st.header(f"Revenue Share Analysis for {user_name}")
    
    # Level calculations
    levels_data = {
        'Level 1': {'units': 200},
        'Level 2': {'units': 480},
        'Level 3': {'units': 510}
    }
    
    all_results = []
    total_rev_share = 0
    
    for level, data in levels_data.items():
        results = calculate_rev_share(selected_title, level, data['units'])
        all_results.append({
            'Level': level,
            'Units': data['units'],
            'Volume': results['volume'],
            'Commissionable Volume': results['commissionable_volume'],
            'Bonus Rate': f"{results['bonus_rate']*100:.2f}%",
            'Generation Bonus': "0.01%",
            'Rev Share': results['rev_share']
        })
        total_rev_share += results['rev_share']
    
    # Display results
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Summary metrics
        metrics_cols = st.columns(2)
        with metrics_cols[0]:
            st.metric("Total Revenue Share", f"${total_rev_share:,.2f}")
        with metrics_cols[1]:
            st.metric("Selected Title", selected_title)
            
        # Create DataFrame for display
        df = pd.DataFrame(all_results)
        
        # Revenue share chart
        fig = px.bar(
            df,
            x='Level',
            y='Rev Share',
            title='Revenue Share by Level',
            text=df['Rev Share'].apply(lambda x: f"${x:,.2f}")
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.header("Level Details")
        for result in all_results:
            with st.expander(result['Level'], expanded=True):
                st.write(f"Units: {result['Units']}")
                st.write(f"Volume: ${result['Volume']:,.2f}")
                st.write(f"Commissionable Volume: ${result['Commissionable Volume']:,.2f}")
                st.write(f"Bonus Rate: {result['Bonus Rate']}")
                st.write(f"Generation Bonus: {result['Generation Bonus']}")
                st.write(f"Rev Share: ${result['Rev Share']:,.2f}")
    
    # Profit Sharing Section
    st.write("---")
    if TITLE_BONUS_RATES[selected_title]['has_profit_share']:
        st.header("Profit Sharing")
        profit_sharing = calculate_profit_sharing()
        st.metric("Profit Sharing Bonus", f"${profit_sharing:,.2f}")
    
    # Final metrics (showing separately)
    st.write("---")
    col3, col4 = st.columns(2)
    with col3:
        st.header("Revenue Share Total")
        st.metric("Total Revenue Share", f"${total_rev_share:,.2f}")
    
    if TITLE_BONUS_RATES[selected_title]['has_profit_share']:
        with col4:
            st.header("Profit Share")
            st.metric("Profit Sharing Amount", f"${profit_sharing:,.2f}")
    
    # Download results
    st.download_button(
        "Download Results",
        df.to_csv(index=False),
        f"revenue_share_{user_name.lower().replace(' ', '_')}.csv",
        "text/csv"
    )
else:
    st.info("👆 Please enter your name in the sidebar to view your revenue share calculations")