import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from PIL import Image as PILImage

st.set_page_config(page_title="Revenue Share Calculator", layout="wide")

# Updated bonus rates
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

# Main UI
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