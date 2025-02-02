import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from PIL import Image as PILImage

# Configure the page
st.set_page_config(page_title="Ethos Lending Calculator Suite", layout="wide")

# Define your TITLE_BONUS_RATES dictionary here
TITLE_BONUS_RATES = {
    'Ambassador (AMB)': {
        'level1_bonus': 0.0005,
        'level2_bonus': 0,
        'level3_bonus': 0,
        'level1_gen_bonus': 0,
        'level2_gen_bonus': 0,
        'level3_gen_bonus': 0,
        'has_profit_share': False,
        'profit_share_bonus': 0
    },
    'Active Ambassador (AAMB)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0,
        'level3_bonus': 0,
        'level1_gen_bonus': 0,
        'level2_gen_bonus': 0,
        'level3_gen_bonus': 0,
        'has_profit_share': False,
        'profit_share_bonus': 0
    },
    'Ambassador 2 (AMB2)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.0005,
        'level3_bonus': 0,
        'level1_gen_bonus': 0,
        'level2_gen_bonus': 0,
        'level3_gen_bonus': 0,
        'has_profit_share': False,
        'profit_share_bonus': 0
    },
    'Ambassador 3 (AMB3)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.0007,
        'level3_bonus': 0.0005,
        'level1_gen_bonus': 0,
        'level2_gen_bonus': 0,
        'level3_gen_bonus': 0,
        'has_profit_share': False,
        'profit_share_bonus': 0
    },
    'Director 1 (DIR1)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007,
        'level1_gen_bonus': 0.0001,
        'level2_gen_bonus': 0,
        'level3_gen_bonus': 0,
        'has_profit_share': False,
        'profit_share_bonus': 0
    },
    'Director 2 (DIR2)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007,
        'level1_gen_bonus': 0.0001,
        'level2_gen_bonus': 0.0001,
        'level3_gen_bonus': 0,
        'has_profit_share': False,
        'profit_share_bonus': 0
    },
    'Director 3 (DIR3)': {
        'level1_bonus': 0.001,
        'level2_bonus': 0.001,
        'level3_bonus': 0.0007,
        'level1_gen_bonus': 0.0001,
        'level2_gen_bonus': 0.0001,
        'level3_gen_bonus': 0.0001,
        'has_profit_share': True,
        'profit_share_bonus': 0.0001
    }
}

def calculate_compensation(loan_amount, interest_rate, rebate, upline_contribution, transaction_fee, annual_units):
    net_comp = loan_amount * (rebate/100) * (1 - upline_contribution/100) - transaction_fee
    annual_comp = net_comp * annual_units
    return net_comp, annual_comp

def create_monthly_projection(annual_units, net_comp_per_loan):
    monthly_units = annual_units / 12
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data = []
    cumulative_income = 0
    
    for month in months:
        income = monthly_units * net_comp_per_loan
        cumulative_income += income
        monthly_data.append({
            'Month': month,
            'Monthly Income': income,
            'Cumulative Income': cumulative_income
        })
    
    return pd.DataFrame(monthly_data)

def calculate_rev_share(title, level, units, avg_loan_size=445000):
    rates = TITLE_BONUS_RATES[title]
    volume = units * avg_loan_size
    commissionable_volume = volume * 0.80  # 80% of volume is commissionable
    
    # Get base bonus rate and generational bonus for the specific level
    if level == 'Level 1':
        bonus_rate = rates['level1_bonus']
        gen_bonus = rates['level1_gen_bonus']
    elif level == 'Level 2':
        bonus_rate = rates['level2_bonus']
        gen_bonus = rates['level2_gen_bonus']
    else:
        bonus_rate = rates['level3_bonus']
        gen_bonus = rates['level3_gen_bonus']
    
    # Calculate revenue share including both base bonus and generational bonus
    rev_share = commissionable_volume * (bonus_rate + gen_bonus)
    
    return {
        'volume': volume,
        'commissionable_volume': commissionable_volume,
        'rev_share': rev_share,
        'bonus_rate': bonus_rate,
        'gen_bonus': gen_bonus
    }

def calculate_profit_sharing(company_volume=2136000000):
    profit_sharing_rate = 0.0001  # 0.01%
    profit_sharing_share = 0.25   # 25%
    return company_volume * profit_sharing_rate * profit_sharing_share

def create_chart_image(fig):
    """Convert Plotly figure to image bytes for PDF"""
    try:
        img_bytes = fig.to_image(format="png", width=800, height=400)
        img = PILImage.open(io.BytesIO(img_bytes))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return Image(img_buffer, width=6*inch, height=3*inch)
    except Exception as e:
        print(f"Error creating chart image: {e}")
        return None

def create_detailed_pdf_report(user_name, selected_title, all_results, total_rev_share, chart_fig, 
                             has_profit_share=False, profit_sharing=0, report_type='detailed', 
                             selected_sections=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    styles = getSampleStyleSheet()
    elements = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#1a237e')
    )
    
    # Title Section
    elements.append(Paragraph(f"Revenue Share Analysis for {user_name}", title_style))
    elements.append(Spacer(1, 20))
    
    # Executive Summary Section
    if not selected_sections or 'executive_summary' in selected_sections:
        elements.append(Paragraph("Executive Summary", section_style))
        summary_data = [
            ['Title', selected_title],
            ['Total Revenue Share', f"${int(total_rev_share):,}"],
            ['Total Loans', sum(r['Total Loans'] for r in all_results)],
            ['Total Volume', f"${int(sum(r['Volume'] for r in all_results)):,}"]
        ]
        if has_profit_share:
            summary_data.append(['Profit Sharing', f"${int(profit_sharing):,}"])
            summary_data.append(['Total Compensation', f"${int(total_rev_share + profit_sharing):,}"])
            
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
    
    # Revenue Chart Section
    if report_type == 'detailed' and (not selected_sections or 'revenue_chart' in selected_sections):
        elements.append(Paragraph("Revenue Distribution by Level", section_style))
        try:
            chart_img = create_chart_image(chart_fig)
            if chart_img:
                elements.append(chart_img)
            elements.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error adding chart to PDF: {e}")
            elements.append(Paragraph("Chart could not be generated", styles['Normal']))
            elements.append(Spacer(1, 20))
    
    # Detailed Breakdown Section
    if report_type == 'detailed' and (not selected_sections or 'level_breakdown' in selected_sections):
        elements.append(Paragraph("Detailed Level Breakdown", section_style))
        for result in all_results:
            elements.append(Paragraph(f"{result['Level']} Analysis", styles['Heading3']))
            detail_data = [
                ['Metric', 'Value'],
                ['LO Count', str(result['LO Count'])],
                ['Loans per LO', str(result['Loans per LO'])],
                ['Total Loans', str(result['Total Loans'])],
                ['Volume', f"${int(result['Volume']):,}"],
                ['Commissionable Volume', f"${int(result['Commissionable Volume']):,}"],
                ['Level Bonus Rate', f"{result['Bonus Rate']*100:.2f}%"],
                ['Generational Bonus', f"{result['Gen Bonus']*100:.2f}%"],
                # ['Total Bonus Rate', f"{(result['Bonus Rate'] + result['Gen Bonus'])*100:.2f}%"],
                ['Revenue Share', f"${int(result['Rev Share']):,}"]
            ]
            
            detail_table = Table(detail_data, colWidths=[2.5*inch, 3.5*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(detail_table)
            elements.append(Spacer(1, 15))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def add_report_customization():
    st.sidebar.write("---")
    st.sidebar.header("Report Customization")
    report_type = st.sidebar.radio(
        "Report Type",
        options=['Simple', 'Detailed'],
        index=1
    )
    
    selected_sections = None
    if report_type == 'Detailed':
        st.sidebar.subheader("Select Sections to Include")
        selected_sections = []
        if st.sidebar.checkbox("Executive Summary", value=True):
            selected_sections.append('executive_summary')
        if st.sidebar.checkbox("Revenue Chart", value=True):
            selected_sections.append('revenue_chart')
        if st.sidebar.checkbox("Level Breakdown", value=True):
            selected_sections.append('level_breakdown')
    
    return report_type.lower(), selected_sections


# Create tabs for different calculators
calculator_type = st.sidebar.radio(
    "Select Calculator",
    ["Revenue Share Calculator", "Loan Advisor Compensation Calculator"]
)

if calculator_type == "Revenue Share Calculator":
    st.title("🏦 Ethos Lending Revenue Share Calculator")

    # Sidebar inputs
    with st.sidebar:
        st.header("User Profile")
        user_name = st.text_input("Enter Your Name")
        
        st.header("Title Selection")
        selected_title = st.selectbox(
            "Select Your Title", 
            options=list(TITLE_BONUS_RATES.keys()),
            index=6
        )
        
        st.header("Team Structure")
        
        # Level 1
        st.subheader("Level 1")
        col1_l1, col2_l1 = st.columns(2)
        with col1_l1:
            level1_count = st.number_input("LO Count", value=10, min_value=0, key="l1_count")
        with col2_l1:
            level1_units_per_lo = st.number_input("Loans per LO", value=10, min_value=0, key="l1_units")
        
        # Level 2
        st.subheader("Level 2")
        col1_l2, col2_l2 = st.columns(2)
        with col1_l2:
            level2_count = st.number_input("LO Count", value=20, min_value=0, key="l2_count")
        with col2_l2:
            level2_units_per_lo = st.number_input("Loans per LO", value=20, min_value=0, key="l2_units")
        
        # Level 3
        st.subheader("Level 3")
        col1_l3, col2_l3 = st.columns(2)
        with col1_l3:
            level3_count = st.number_input("LO Count", value=30, min_value=0, key="l3_count")
        with col2_l3:
            level3_units_per_lo = st.number_input("Loans per LO", value=30, min_value=0, key="l3_units")
        
        # Loan Parameters
        st.header("Loan Parameters")
        avg_loan_size = st.number_input("Average Loan Size ($)", value=445000, min_value=0, step=1000)

        # Display calculated total units
        st.header("Calculated Total Units")
        level1_total_units = level1_count * level1_units_per_lo
        level2_total_units = level2_count * level2_units_per_lo
        level3_total_units = level3_count * level3_units_per_lo
        
        st.info(f"""
        Level 1: {level1_total_units} units ({level1_count} LOs × {level1_units_per_lo} units)
        Level 2: {level2_total_units} units ({level2_count} LOs × {level2_units_per_lo} units)
        Level 3: {level3_total_units} units ({level3_count} LOs × {level3_units_per_lo} units)
        Total: {level1_total_units + level2_total_units + level3_total_units} units
        """)

    if user_name:
        # Main calculation area
        st.header(f"Revenue Share Analysis for {user_name}")
        
        # Level calculations
        levels_data = {
            'Level 1': {'units': level1_count * level1_units_per_lo},
            'Level 2': {'units': level2_count * level2_units_per_lo},
            'Level 3': {'units': level3_count * level3_units_per_lo}
        }
        
        all_results = []
        total_rev_share = 0
        
        for level, data in levels_data.items():
            results = calculate_rev_share(selected_title, level, data['units'], avg_loan_size=avg_loan_size)
            all_results.append({
                'Level': level,
                'LO Count': level1_count if level == 'Level 1' else level2_count if level == 'Level 2' else level3_count,
                'Loans per LO': level1_units_per_lo if level == 'Level 1' else level2_units_per_lo if level == 'Level 2' else level3_units_per_lo,
                'Total Loans': data['units'],
                'Volume': results['volume'],
                'Commissionable Volume': results['commissionable_volume'],
                'Bonus Rate': results['bonus_rate'],  # Changed from string format to raw number
                'Gen Bonus': results['gen_bonus'],    # Added to match with calculate_rev_share
                'Rev Share': results['rev_share']
            })
            total_rev_share += results['rev_share']
        
        # Display results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Summary metrics
            metrics_cols = st.columns(2)
            with metrics_cols[0]:
                st.metric("Total Revenue Share", f"${int(total_rev_share):,}")
            with metrics_cols[1]:
                st.metric("Selected Title", selected_title)
                
            # Revenue share chart
            df = pd.DataFrame(all_results)
            fig = px.bar(
                df,
                x='Level',
                y='Rev Share',
                title='Revenue Share by Level',
                text=df['Rev Share'].apply(lambda x: f"${int(x):,}")
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.header("Level Details")
            for result in all_results:
                with st.expander(result['Level'], expanded=True):
                    st.write(f"LO Count: {result['LO Count']}")
                    st.write(f"Loans per LO: {result['Loans per LO']}")
                    st.write(f"Total Loans: {result['Total Loans']}")
                    st.write(f"Volume: ${int(result['Volume']):,}")
                    st.write(f"Commissionable Volume: ${int(result['Commissionable Volume']):,}")
                    st.write(f"Level Bonus Rate: {result['Bonus Rate']*100:.2f}%")
                    st.write(f"Generational Bonus: {result['Gen Bonus']*100:.2f}%")
                    st.write(f"Total Bonus Rate: {(result['Bonus Rate'] + result['Gen Bonus'])*100:.2f}%")
                    st.write(f"Rev Share: ${int(result['Rev Share']):,}")
        
        # Profit Sharing Section
        st.write("---")
        if TITLE_BONUS_RATES[selected_title]['has_profit_share']:
            st.header("Profit Sharing")
            profit_sharing = calculate_profit_sharing()
            st.metric("Profit Sharing Bonus", f"${int(profit_sharing):,}")
        else:
            profit_sharing = 0
        
        # Final metrics
        st.write("---")
        col3, col4 = st.columns(2)
        with col3:
            st.header("Revenue Share Total")
            st.metric("Total Revenue Share", f"${int(total_rev_share):,}")
        
        if TITLE_BONUS_RATES[selected_title]['has_profit_share']:
            with col4:
                st.header("Total Compensation")
                st.metric("Total Amount", f"${int(total_rev_share + profit_sharing):,}")
        
        # Get report preferences
        report_type, selected_sections = add_report_customization()
        
        # Generate and offer PDF download
        pdf_buffer = create_detailed_pdf_report(
            user_name,
            selected_title,
            all_results,
            total_rev_share,
            fig,
            TITLE_BONUS_RATES[selected_title]['has_profit_share'],
            profit_sharing if TITLE_BONUS_RATES[selected_title]['has_profit_share'] else 0,
            report_type,
            selected_sections
        )
        
        st.download_button(
            "Download PDF Report",
            pdf_buffer,
            f"revenue_share_{user_name.lower().replace(' ', '_')}.pdf",
            "application/pdf"
        )

else:  # Loan Advisor Compensation Calculator
    st.title("💰 Loan Advisor Compensation Calculator")
    
    tab1, tab2, tab3 = st.tabs(["Calculator", "Monthly Projections", "Team Management"])
    
    with tab1:
        st.write("Compare your compensation between current lender and ETHOS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Loan Details")
            loan_amount = st.number_input(
                "Average Loan Amount ($)", 
                min_value=0, 
                value=500000, 
                step=1000, 
                format="%d",
                help="Enter the total loan amount"
            )
            interest_rate = st.number_input(
                "Interest Rate (%)", 
                min_value=0.0, 
                value=6.75, 
                step=0.125,
                help="Enter the annual interest rate"
            )
            annual_units = st.number_input(
                "Annual Units", 
                min_value=0, 
                value=50, 
                step=1,
                help="Number of loans processed per year"
            )

        with col2:
            st.subheader("Current Lender")
            current_rebate = st.number_input(
                "Current Rebate (%)", 
                min_value=0.0, 
                value=1.0, 
                step=0.1,
                help="Current lender's rebate percentage"
            )
            company_split = st.number_input(
                "Company Split (%)", 
                min_value=0.0, 
                value=0.0, 
                step=0.1,
                help="Percentage split with current company"
            )
            current_transaction_fee = st.number_input(
                "Current Transaction Fee ($)", 
                min_value=0.0, 
                value=0.0, 
                step=1.0,
                help="Fee charged per transaction"
            )

        # ETHOS calculations
        ethos_rebate = 1.70 
        ethos_transaction_fee = 495
        ethos_before_upline = 0.25  # Before cap upline contribution
        ethos_after_upline = 0.0    # After cap upline contribution
        cap_units = 20
        remaining_units = annual_units - cap_units if annual_units > cap_units else 0
        before_cap_units = min(annual_units, cap_units)

        # Calculate compensations
        current_net, current_annual = calculate_compensation(
            loan_amount, interest_rate, current_rebate, company_split, 
            current_transaction_fee, annual_units
        )

        ethos_before_net, ethos_before_annual = calculate_compensation(
            loan_amount, interest_rate, ethos_rebate, ethos_before_upline, 
            ethos_transaction_fee, before_cap_units
        )

        ethos_after_net, ethos_after_annual = calculate_compensation(
            loan_amount, interest_rate, ethos_rebate, ethos_after_upline, 
            ethos_transaction_fee, remaining_units
        )

        total_ethos_annual = ethos_before_annual + ethos_after_annual
        additional_comp = total_ethos_annual - current_annual

        # Enhanced Results display
        st.header("Compensation Comparison")
        
        cap_volume = 10000000  # $10 million cap
        total_volume = loan_amount * annual_units
        before_cap_volume = min(total_volume, cap_volume)
        after_cap_volume = max(0, total_volume - cap_volume)

        before_cap_units = before_cap_volume / loan_amount
        after_cap_units = after_cap_volume / loan_amount
        # Modify the comp_cols section to add loan volume
        comp_cols = st.columns(4)

        with comp_cols[0]:
            st.subheader("Current Lender")
            metrics_current = {
                "Loan Volume": total_volume  ,# Add loan volume metric
                "Comp per Loan": current_net,
                "Monthly Average": current_annual/12,
                "Annual Compensation": current_annual,
                
            }
            for label, value in metrics_current.items():
                st.metric(label, f"${value:,.2f}")

        with comp_cols[1]:
            st.subheader("ETHOS (Before Cap)")
            metrics_before = {
                "Loan Volume": before_cap_volume , # Add before cap volume
                "Comp per Loan": ethos_before_net,
                "Monthly Average": ethos_before_annual/12,
                "Annual Compensation": ethos_before_annual,
                
            }
            for label, value in metrics_before.items():
                st.metric(label, f"${value:,.2f}")

        with comp_cols[2]:
            st.subheader("ETHOS (After Cap)")
            metrics_after = {
                "Loan Volume": after_cap_volume , # Add after cap volume
                "Comp per Loan": ethos_after_net,
                "Monthly Average": ethos_after_annual/12,
                "Annual Compensation": ethos_after_annual,
                
            }
            for label, value in metrics_after.items():
                st.metric(label, f"${value:,.2f}")

        with comp_cols[3]:
            st.subheader("Total ETHOS")
            total_net_comp = (ethos_before_net * before_cap_units + ethos_after_net * remaining_units) / annual_units
            metrics_total = {
                "Loan Volume": total_volume,  # Add total loan volume
                "Comp per Loan": total_net_comp,
                "Monthly Average": total_ethos_annual/12,
                "Annual Compensation": total_ethos_annual,
                
            }
            for label, value in metrics_total.items():
                st.metric(
                    label, 
                    f"${value:,.2f}",
                    delta=f"{((value/metrics_current[label]-1)*100):.1f}% vs Current lender" if metrics_current[label] != 0 else None
                )

        # Enhanced visualization
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Current Lender',
            x=['Annual Compensation'],
            y=[current_annual],
            text=[f'${current_annual:,.0f}'],
            textposition='auto',
            marker_color='rgb(55, 83, 109)'
        ))

        fig.add_trace(go.Bar(
            name='ETHOS (Before Cap)',
            x=['Annual Compensation'],
            y=[ethos_before_annual],
            text=[f'${ethos_before_annual:,.0f}'],
            textposition='auto',
            marker_color='rgb(26, 118, 255)'
        ))

        fig.add_trace(go.Bar(
            name='ETHOS (After Cap)',
            x=['Annual Compensation'],
            y=[ethos_after_annual],
            text=[f'${ethos_after_annual:,.0f}'],
            textposition='auto',
            marker_color='rgb(58, 149, 255)'
        ))

        fig.add_trace(go.Bar(
            name='Total ETHOS',
            x=['Annual Compensation'],
            y=[total_ethos_annual],
            text=[f'${total_ethos_annual:,.0f}'],
            textposition='auto',
            marker_color='rgb(0, 191, 255)'  # A distinct blue shade for total
        ))

        fig.update_layout(
            title='Annual Compensation Breakdown',
            yaxis_title='Compensation ($)',
            barmode='group',
            showlegend=True,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Monthly Projections")
        
        # Create monthly projections
        current_monthly = create_monthly_projection(annual_units, current_net)
        ethos_monthly = create_monthly_projection(annual_units, (ethos_before_net * before_cap_units + ethos_after_net * remaining_units) / annual_units)
        
        # Monthly comparison visualization
        fig_monthly = px.line(
            title="Monthly Income Comparison"
        )
        
        fig_monthly.add_scatter(
            x=current_monthly['Month'],
            y=current_monthly['Cumulative Income'],
            name='Current Lender',
            mode='lines+markers'
        )
        
        fig_monthly.add_scatter(
            x=ethos_monthly['Month'],
            y=ethos_monthly['Cumulative Income'],
            name='ETHOS',
            mode='lines+markers'
        )
        
        fig_monthly.update_layout(
            xaxis_title='Month',
            yaxis_title='Cumulative Income ($)',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Monthly comparison table
        st.subheader("Monthly Income Breakdown")
        comparison_df = pd.DataFrame({
            'Month': current_monthly['Month'],
            'Current Monthly': current_monthly['Monthly Income'],
            'ETHOS Monthly': ethos_monthly['Monthly Income'],
            'Monthly Difference': ethos_monthly['Monthly Income'] - current_monthly['Monthly Income']
        })
        
        st.dataframe(
            comparison_df.style.format({
                'Current Monthly': '${:,.2f}',
                'ETHOS Monthly': '${:,.2f}',
                'Monthly Difference': '${:,.2f}'
            }),
            use_container_width=True
        )
    with tab3:
        st.title("Team Performance Dashboard")

        # Initialize session state for team members if it doesn't exist
        if 'team_members' not in st.session_state:
            st.session_state.team_members = []

        # Add team member section
        with st.expander("Manage Team Members", expanded=True):
            # File uploader section
            st.subheader("Bulk Upload via File")
            uploaded_file = st.file_uploader(
                "Upload Team File (Excel or CSV)", 
                type=["xlsx", "csv"],
                help="Upload file with columns: Name, Loan Size, Units"
            )
            
            # Template download
            if st.button("Download Template"):
                sample_data = pd.DataFrame({
                    'Name': ['John Doe', 'Jane Smith'],
                    'Loan Size': [500000, 450000],
                    'Units': [50, 60]
                })
                
                towrite = io.BytesIO()
                sample_data.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                
                st.download_button(
                    label="Download Excel Template",
                    data=towrite,
                    file_name="team_template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            if uploaded_file is not None:
                try:
                    # Read file based on extension
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file, engine='openpyxl')

                    # Validate columns
                    required_columns = ['Name', 'Loan Size', 'Units']
                    if not all(col in df.columns for col in required_columns):
                        st.error(f"Missing required columns. File must contain: {', '.join(required_columns)}")
                    else:
                        # Clear existing team if desired
                        if st.checkbox("Replace existing team with uploaded data"):
                            st.session_state.team_members = []

                        # Process uploaded data
                        new_members = []
                        for _, row in df.iterrows():
                            try:
                                loan_size = float(row['Loan Size'])
                                units = int(row['Units'])
                                
                                new_members.append({
                                    "name": row['Name'],
                                    "loan_size": loan_size,
                                    "units": units,
                                    "volume": loan_size * units,
                                    "currentComp": calculate_compensation(
                                        loan_size, interest_rate, current_rebate,
                                        company_split, current_transaction_fee, units)[1],
                                    "ethosComp": calculate_compensation(
                                        loan_size, interest_rate, ethos_rebate,
                                        ethos_before_upline, ethos_transaction_fee,
                                        min(units, cap_units))[1] + 
                                        calculate_compensation(
                                            loan_size, interest_rate, ethos_rebate,
                                            ethos_after_upline, ethos_transaction_fee,
                                            max(0, units - cap_units))[1]
                                })
                            except Exception as e:
                                st.error(f"Error processing row {_+1}: {str(e)}")
                                continue
                        
                        st.session_state.team_members += new_members
                        st.success(f"Successfully added {len(new_members)} members from file!")
                        st.experimental_rerun()

                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
            input_method = st.radio("Select Input Method", ["Add Single Member", "Add Multiple Members"], horizontal=True)

            if input_method == "Add Single Member":
                cols = st.columns([3, 3, 3, 2])
                with cols[0]:
                    name = st.text_input("Name")
                with cols[1]:
                    loan_size = st.number_input("Loan Size", value=500000, step=1000)
                with cols[2]:
                    units = st.number_input("Annual Units", value=50)

                if cols[3].button("Calculate"):
                    if name:
                        # Calculate both compensations
                        current_comp = calculate_compensation(
                            loan_size, interest_rate, current_rebate, 
                            company_split, current_transaction_fee, units)[1]

                        ethos_before_comp = calculate_compensation(
                            loan_size, interest_rate, ethos_rebate,
                            ethos_before_upline, ethos_transaction_fee, 
                            min(units, cap_units))[1]

                        ethos_after_comp = calculate_compensation(
                            loan_size, interest_rate, ethos_rebate,
                            ethos_after_upline, ethos_transaction_fee, 
                            max(0, units - cap_units))[1]

                        ethos_total = ethos_before_comp + ethos_after_comp

                        # Show calculation results
                        st.subheader("Compensation Comparison")
                        comp_cols = st.columns(2)
                        comp_cols[0].metric("Current Lender", f"${current_comp:,.2f}")
                        comp_cols[1].metric("ETHOS", f"${ethos_total:,.2f}", 
                                            f"{((ethos_total/current_comp - 1) * 100):,.1f}%")

                        # Monthly projection comparison
                        current_monthly = create_monthly_projection(units, current_comp/units)
                        ethos_monthly = create_monthly_projection(units, ethos_total/units)

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=current_monthly['Month'],
                            y=current_monthly['Cumulative Income'],
                            name='Current Lender'
                        ))
                        fig.add_trace(go.Scatter(
                            x=ethos_monthly['Month'],
                            y=ethos_monthly['Cumulative Income'],
                            name='ETHOS'
                        ))
                        fig.update_layout(
                            title="Monthly Income Projection",
                            xaxis_title="Month",
                            yaxis_title="Cumulative Income ($)"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        if st.button("Add to Team"):
                            st.session_state.team_members.append({
                                "name": name,
                                "loan_size": loan_size,
                                "units": units,
                                "volume": loan_size * units,
                                "currentComp": current_comp,
                                "ethosComp": ethos_total
                            })
                            st.success(f"Added {name} to team!")
                            st.experimental_rerun()

            else:  # Multiple members input section
                n_members = st.number_input("Number of Team Members", min_value=1, value=1)
                members_data = []

                for i in range(int(n_members)):
                    st.subheader(f"Member {i+1}")
                    cols = st.columns(3)
                    members_data.append({
                        "name": cols[0].text_input("Name", key=f"name_{i}"),
                        "loan_size": cols[1].number_input("Loan Size", value=500000, step=1000, key=f"loan_{i}"),
                        "units": cols[2].number_input("Units", value=50, key=f"units_{i}")
                    })

                if st.button("Calculate All"):
                    for member in members_data:
                        if member["name"]:
                            st.subheader(f"Calculation for {member['name']}")

                            current_comp = calculate_compensation(
                                member["loan_size"], interest_rate, current_rebate,
                                company_split, current_transaction_fee, member["units"])[1]

                            ethos_before = calculate_compensation(
                                member["loan_size"], interest_rate, ethos_rebate,
                                ethos_before_upline, ethos_transaction_fee,
                                min(member["units"], cap_units))[1]

                            ethos_after = calculate_compensation(
                                member["loan_size"], interest_rate, ethos_rebate,
                                ethos_after_upline, ethos_transaction_fee,
                                max(0, member["units"] - cap_units))[1]

                            ethos_total = ethos_before + ethos_after

                            cols = st.columns(2)
                            cols[0].metric("Current", f"${current_comp:,.2f}")
                            cols[1].metric("ETHOS", f"${ethos_total:,.2f}",
                                            f"{((ethos_total/current_comp - 1) * 100):,.1f}%")

                    if st.button("Add All to Team"):
                        for member in members_data:
                            if member["name"]:
                                current_comp = calculate_compensation(
                                    member["loan_size"], interest_rate, current_rebate,
                                    company_split, current_transaction_fee, member["units"])[1]

                                ethos_total = calculate_compensation(
                                    member["loan_size"], interest_rate, ethos_rebate,
                                    ethos_before_upline, ethos_transaction_fee,
                                    min(member["units"], cap_units))[1] + \
                                    calculate_compensation(
                                        member["loan_size"], interest_rate, ethos_rebate,
                                        ethos_after_upline, ethos_transaction_fee,
                                        max(0, member["units"] - cap_units))[1]

                                st.session_state.team_members.append({
                                    "name": member["name"],
                                    "loan_size": member["loan_size"],
                                    "units": member["units"],
                                    "volume": member["loan_size"] * member["units"],
                                    "currentComp": current_comp,
                                    "ethosComp": ethos_total
                                })
                        st.success("Added all members to team!")
                        st.experimental_rerun()

        # New Dashboard Section
        if st.session_state.team_members:
            team = st.session_state.team_members

            # Create tabs for Team Overview and Individual Analysis
            team_tabs = st.tabs(["Team Overview", "Individual Analysis"])

            with team_tabs[0]:  # Team Overview
                CAP_VOLUME = 10000000  # $10M cap

                # Calculate team metrics
                total_units = sum(m["units"] for m in team)
                total_volume = sum(m["volume"] for m in team)
                avg_loan_size = sum(m["loan_size"] for m in team) / len(team)

                # Calculate before/after cap volumes
                team_before_cap = sum(min(m["volume"], CAP_VOLUME) for m in team)
                team_after_cap = sum(max(0, m["volume"] - CAP_VOLUME) for m in team)

                # Display team metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Units", f"{total_units:,}")
                col2.metric("Total Volume", f"${total_volume:,.0f}")
                col3.metric("Average Loan Size", f"${avg_loan_size:,.0f}")

                col4, col5 = st.columns(2)
                col4.metric("Volume Before Cap", f"${team_before_cap:,.0f}")
                col5.metric("Volume After Cap", f"${team_after_cap:,.0f}")

                # Team volume distribution chart
                volume_data = pd.DataFrame(team)[['name', 'volume']]
                fig_volume = px.pie(volume_data, values='volume', names='name',
                                    title="Volume Distribution")
                st.plotly_chart(fig_volume, use_container_width=True)

                # Compensation comparison chart
                comp_data = pd.DataFrame([
                    {"name": m["name"], "type": "Current", "amount": m["currentComp"]} for m in team
                ] + [
                    {"name": m["name"], "type": "ETHOS", "amount": m["ethosComp"]} for m in team
                ])
                fig_comp = px.bar(comp_data, x="name", y="amount", color="type",
                                    title="Compensation Comparison", barmode="group")
                st.plotly_chart(fig_comp, use_container_width=True)

            with team_tabs[1]:  # Individual Analysis
                # Member selection
                selected_member = st.selectbox("Select Team Member", 
                                            [m["name"] for m in team])

                if selected_member:
                    member = next(m for m in team if m["name"] == selected_member)

                    # Calculate individual metrics
                    member_volume = member["loan_size"] * member["units"]
                    before_cap_volume = min(member_volume, CAP_VOLUME)
                    after_cap_volume = max(0, member_volume - CAP_VOLUME)
                    before_cap_units = before_cap_volume / member["loan_size"]
                    after_cap_units = after_cap_volume / member["loan_size"]

                    # Display individual metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Units", member["units"])
                    col2.metric("Total Volume", f"${member_volume:,.0f}")
                    col3.metric("Loan Size", f"${member['loan_size']:,.0f}")

                    col4, col5 = st.columns(2)
                    col4.metric("Units Before Cap", f"{int(before_cap_units)}")
                    col5.metric("Units After Cap", f"{int(after_cap_units)}")

                    col6, col7 = st.columns(2)
                    col6.metric("Volume Before Cap", f"${before_cap_volume:,.0f}")
                    col7.metric("Volume After Cap", f"${after_cap_volume:,.0f}")

                    # Monthly projections
                    current_monthly = create_monthly_projection(member["units"], 
                        member["currentComp"]/member["units"])
                    ethos_monthly = create_monthly_projection(member["units"], 
                        member["ethosComp"]/member["units"])

                    fig_monthly = go.Figure()
                    fig_monthly.add_trace(go.Scatter(
                        x=current_monthly['Month'],
                        y=current_monthly['Cumulative Income'],
                        name='Current Lender'
                    ))
                    fig_monthly.add_trace(go.Scatter(
                        x=ethos_monthly['Month'],
                        y=ethos_monthly['Cumulative Income'],
                        name='ETHOS'
                    ))
                    fig_monthly.update_layout(
                        title=f"Monthly Income Projection - {selected_member}",
                        xaxis_title="Month",
                        yaxis_title="Cumulative Income ($)"
                    )
                    st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.info("Add team members to see the dashboard")