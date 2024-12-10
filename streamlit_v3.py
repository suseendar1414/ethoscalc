import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Revenue Share Calculator", layout="wide")

# Title hierarchy with exact bonus percentages from Excel
TITLE_REQUIREMENTS = {
    'Ambassador (AMB)': {
        'level1_bonus': 0.0008,
        'level2_bonus': 0.0008,
        'level3_bonus': 0.0005
    },
    'Active Ambassador (AAMB)': {
        'level1_bonus': 0.00085,
        'level2_bonus': 0.00085,
        'level3_bonus': 0.00055
    },
    'Ambassador 2 (AMB2)': {
        'level1_bonus': 0.0009,
        'level2_bonus': 0.0009,
        'level3_bonus': 0.0006
    },
    'Ambassador 3 (AMB3)': {
        'level1_bonus': 0.00095,
        'level2_bonus': 0.00095,
        'level3_bonus': 0.00065
    },
    'Director 1 (DIR1)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007
    },
    'Director 2 (DIR2)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007
    },
    'Director 3 (DIR3)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007
    }
}

def calculate_revenue_share(
    level1_lo_count: int,
    level2_lo_count: int,
    level3_lo_count: int,
    paid_as_title: str,
    avg_loan_size: float = 445000,
    generation_bonus_pct: float = 0.0001,  # 0.01%
    target_units: dict = {'level1': 200, 'level2': 480, 'level3': 510}  # From Excel
):
    # Get bonus rates based on title
    title_rates = TITLE_REQUIREMENTS[paid_as_title]
    
    # Use exact units from Excel
    level1_units = target_units['level1']
    level2_units = target_units['level2']
    level3_units = target_units['level3']
    
    # Calculate volumes
    level1_volume = level1_units * avg_loan_size
    level2_volume = level2_units * avg_loan_size
    level3_volume = level3_units * avg_loan_size
    total_rev_share_volume = level1_volume + level2_volume + level3_volume
    
    # Calculate revenue shares with exact bonus rates
    level1_rev_share = level1_volume * (title_rates['level1_bonus'] + generation_bonus_pct)
    level2_rev_share = level2_volume * (title_rates['level2_bonus'] + generation_bonus_pct)
    level3_rev_share = level3_volume * (title_rates['level3_bonus'] + generation_bonus_pct)
    
    # Calculate profit sharing bonus
    company_volume = 2136000000  # From Excel
    profit_sharing_bonus = company_volume * 0.0001 * 0.25  # 0.01% bonus rate, 25% share
    
    # Calculate total revenue share
    total_rev_share = level1_rev_share + level2_rev_share + level3_rev_share + profit_sharing_bonus
    
    return {
        'Level Details': {
            'Level 1': {
                'LO Count': level1_lo_count,
                'Units': level1_units,
                'Volume': level1_volume,
                'Rev Share': level1_rev_share,
                'Bonus Rate': title_rates['level1_bonus']
            },
            'Level 2': {
                'LO Count': level2_lo_count,
                'Units': level2_units,
                'Volume': level2_volume,
                'Rev Share': level2_rev_share,
                'Bonus Rate': title_rates['level2_bonus']
            },
            'Level 3': {
                'LO Count': level3_lo_count,
                'Units': level3_units,
                'Volume': level3_volume,
                'Rev Share': level3_rev_share,
                'Bonus Rate': title_rates['level3_bonus']
            }
        },
        'Summary': {
            'Paid-As Title': paid_as_title,
            'Total Rev Share Volume': total_rev_share_volume,
            'Profit Sharing Bonus': profit_sharing_bonus,
            'Total Rev Share': total_rev_share
        }
    }

# Streamlit UI
st.title("🏦 Ethos Lending Revenue Share Calculator")

# Sidebar inputs
with st.sidebar:
    st.header("Input Parameters")
    
    # Title Selection
    paid_as_title = st.selectbox(
        "Select Paid-As Title",
        options=list(TITLE_REQUIREMENTS.keys()),
        index=6  # Default to DIR3
    )
    
    # Team Structure
    st.subheader("Team Structure")
    level1_lo_count = st.number_input("Level 1 LO Count", value=10, min_value=0)
    level2_lo_count = st.number_input("Level 2 LO Count", value=20, min_value=0)
    level3_lo_count = st.number_input("Level 3 LO Count", value=30, min_value=0)
    
    # Loan Parameters
    st.subheader("Loan Parameters")
    avg_loan_size = st.number_input("Average Loan Size ($)", value=445000, min_value=0)

# Calculate results
results = calculate_revenue_share(
    level1_lo_count=level1_lo_count,
    level2_lo_count=level2_lo_count,
    level3_lo_count=level3_lo_count,
    paid_as_title=paid_as_title,
    avg_loan_size=avg_loan_size
)

# Display Results
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Revenue Share Results")
    
    # Summary metrics
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("Total Revenue Share", f"${results['Summary']['Total Rev Share']:,.2f}")
    with metric_col2:
        st.metric("Total Volume", f"${results['Summary']['Total Rev Share Volume']:,.2f}")

    # Revenue share chart
    level_data = []
    for level, details in results['Level Details'].items():
        level_data.append({
            'Level': level,
            'Revenue Share': details['Rev Share'],
            'Volume': details['Volume']
        })
    
    df = pd.DataFrame(level_data)
    fig = px.bar(df, x='Level', y='Revenue Share',
                 title='Revenue Share by Level',
                 text=df['Revenue Share'].apply(lambda x: f'${x:,.2f}'))
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("Level Details")
    for level, details in results['Level Details'].items():
        with st.expander(level, expanded=True):
            st.write(f"LO Count: {details['LO Count']}")
            st.write(f"Units: {details['Units']}")
            st.write(f"Volume: ${details['Volume']:,.2f}")
            st.write(f"Bonus Rate: {details['Bonus Rate']*100:.3f}%")
            st.write(f"Rev Share: ${details['Rev Share']:,.2f}")

# Download button
st.download_button(
    "Download Results as CSV",
    df.to_csv(index=False),
    "revenue_share_results.csv",
    "text/csv"
)