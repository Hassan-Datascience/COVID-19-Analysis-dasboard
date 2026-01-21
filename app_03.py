import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
import os

warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="COVID-19 Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS STYLING ====================
st.markdown("""
    <style>
    /* Professional Corporate Color Scheme */
    :root {
        --primary-color: #3b82f6;
        --secondary-color: #60a5fa;
        --accent-color: #8b5cf6;
        --background-color: #0f172a;
        --surface-color: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --success-color: #10b981;
        --warning-color: #f59e0b;
    }
    
    /* Overall styling - Professional Dark Theme */
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f35 100%);
        color: #f1f5f9;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar styling - Premium gradient */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 3px solid #3b82f6;
        box-shadow: 4px 0 20px rgba(59, 130, 246, 0.1);
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f35 100%);
    }
    
    /* Header styling - Professional */
    h1, h2, h3 {
        color: #f1f5f9;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric cards - Sleek professional look */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b 0%, #1a1f35 100%);
        border: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
    }
    
    /* Buttons - Professional gradient */
    button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: #f1f5f9;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    button:hover {
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
        transform: translateY(-3px);
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }
    
    /* Input fields - Professional styling */
    input, select {
        background-color: #0f172a !important;
        color: #f1f5f9 !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-weight: 500;
    }
    
    input:focus, select:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebarUserContent"] > div > div > h2 {
        color: #60a5fa;
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 18px;
    }
    
    /* Custom metric box - Premium styling */
    .metric-box {
        background: linear-gradient(135deg, #1e293b 0%, #1a1f35 100%);
        border-left: 5px solid #3b82f6;
        padding: 18px;
        border-radius: 10px;
        margin: 12px 0;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.12);
        transition: all 0.3s ease;
    }
    
    .metric-box:hover {
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.18);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: 800;
        color: #60a5fa;
        letter-spacing: -1px;
    }
    
    .metric-label {
        font-size: 11px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    /* Divider lines */
    hr {
        border-color: rgba(59, 130, 246, 0.2) !important;
        margin: 20px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== LOAD AND CACHE DATA ====================
@st.cache_data
def load_covid_data():
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try different file path variations for various environments
    file_paths = [
        os.path.join(current_dir, 'Covid Data.csv'),
        'Covid Data.csv',
        os.path.join(current_dir, '..', 'Covid Data.csv'),
        '/mount/src/COVID-19-Analysis-dasboard/Covid Data.csv',
        '/mount/src/covid-19-analysis-dasboard/Covid Data.csv',
        '/app/Covid Data.csv'
    ]
    
    df = None
    last_error = None
    
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            break
        except FileNotFoundError:
            last_error = f"Not found: {file_path}"
            continue
        except Exception as e:
            last_error = f"Error reading {file_path}: {str(e)}"
            continue
    
    if df is None:
        st.error(f"""
        ❌ **Error Loading Data**
        
        Unable to locate 'Covid Data.csv' file.
        
        Current directory: {current_dir}
        Last error: {last_error}
        
        Please ensure the CSV file is in the same directory as app_03.py
        """)
        st.stop()
    
    # Create mapping dictionaries for encoded values
    sex_map = {1: 'Male', 2: 'Female', 97: 'Unknown'}
    patient_type_map = {1: 'Ambulatory', 2: 'Hospitalized', 97: 'Unknown'}
    classification_map = {
        1: 'Suspected',
        2: 'Confirmed',
        3: 'Suspected Not COVID-19',
        4: 'Confirmed COVID-19 Not Related',
        5: 'COVID-19 Patient',
        6: 'Suspected COVID-19 Related',
        7: 'Confirmed COVID-19 Related Death',
    }
    
    # Decode columns
    df['SEX'] = df['SEX'].map(sex_map)
    df['PATIENT_TYPE'] = df['PATIENT_TYPE'].map(patient_type_map)
    df['CLASSIFICATION'] = df['CLASIFFICATION_FINAL'].map(classification_map)
    df['DATE_DIED'] = pd.to_datetime(df['DATE_DIED'], errors='coerce')
    
    # Create mortality flag
    df['MORTALITY'] = df['DATE_DIED'].notna().astype(int)
    
    # Create comorbidity columns
    comorbidities = ['DIABETES', 'COPD', 'ASTHMA', 'INMSUPR', 'HIPERTENSION', 
                     'OTHER_DISEASE', 'CARDIOVASCULAR', 'OBESITY', 'RENAL_CHRONIC', 'TOBACCO']
    df['COMORBIDITY_COUNT'] = df[comorbidities].apply(lambda x: (x == 1).sum(), axis=1)
    
    return df

df = load_covid_data()

# ==================== DASHBOARD HEADER ====================
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("📊")
with col_title:
    st.markdown("""
    # COVID-19 ANALYTICS DASHBOARD
    *Executive Intelligence Platform | Real-Time Epidemiological Analysis*
    """)

st.markdown("---")

# ==================== SIDEBAR FILTERS ====================
st.sidebar.markdown("### 🎯 ADVANCED FILTERS")

# Sex Filter
sex_options = ['All'] + sorted(df['SEX'].dropna().unique().tolist())
selected_sex = st.sidebar.multiselect('**Patient Gender**', sex_options, default='All')
if 'All' not in selected_sex and selected_sex:
    df_filtered = df[df['SEX'].isin(selected_sex)]
else:
    df_filtered = df.copy()

# Patient Type Filter
patient_types = ['All'] + sorted(df_filtered['PATIENT_TYPE'].dropna().unique().tolist())
selected_patient_type = st.sidebar.multiselect('**Patient Type**', patient_types, default='All')
if 'All' not in selected_patient_type and selected_patient_type:
    df_filtered = df_filtered[df_filtered['PATIENT_TYPE'].isin(selected_patient_type)]

# Age Range Filter
age_min, age_max = st.sidebar.slider('**Age Range**', 0, 130, (0, 130))
df_filtered = df_filtered[(df_filtered['AGE'] >= age_min) & (df_filtered['AGE'] <= age_max)]

# Mortality Status Filter
mortality_options = st.sidebar.multiselect('**Patient Outcome**', 
                                          ['All', 'Survived', 'Deceased'], 
                                          default='All')
if 'All' not in mortality_options and mortality_options:
    mortality_filter = []
    if 'Deceased' in mortality_options:
        mortality_filter.append(1)
    if 'Survived' in mortality_options:
        mortality_filter.append(0)
    df_filtered = df_filtered[df_filtered['MORTALITY'].isin(mortality_filter)]

# ICU Status Filter
icu_hospitalized = st.sidebar.checkbox('**Limit to ICU Patients**', value=False)
if icu_hospitalized:
    df_filtered = df_filtered[df_filtered['ICU'].isin([1, 2])]

# Comorbidity Filter
min_comorbidities = st.sidebar.slider('**Minimum Comorbidities**', 0, 10, 0)
df_filtered = df_filtered[df_filtered['COMORBIDITY_COUNT'] >= min_comorbidities]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📈 Records Selected:** {len(df_filtered):,} / {len(df):,}")
st.sidebar.markdown(f"**Data Coverage:** {(len(df_filtered)/len(df)*100):.1f}%")

# ==================== KEY METRICS ====================
st.markdown("### 📊 KEY PERFORMANCE INDICATORS")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_cases = len(df_filtered)
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Total Cases</div>
        <div class="metric-value">{total_cases:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    mortality_rate = (df_filtered['MORTALITY'].sum() / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Mortality Rate</div>
        <div class="metric-value">{mortality_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    deaths = df_filtered['MORTALITY'].sum()
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Total Deaths</div>
        <div class="metric-value">{deaths:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_age = df_filtered['AGE'].mean()
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Average Age</div>
        <div class="metric-value">{avg_age:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    hospitalized = len(df_filtered[df_filtered['PATIENT_TYPE'] == 'Hospitalized'])
    hosp_rate = (hospitalized / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Hospitalization Rate</div>
        <div class="metric-value">{hosp_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==================== ADVANCED VISUALIZATIONS ====================
st.markdown("### 📈 EPIDEMIOLOGICAL INSIGHTS")

col_viz1, col_viz2 = st.columns(2)

# 1. Mortality by Age Distribution
with col_viz1:
    st.markdown("#### Mortality Risk by Age Group")
    
    age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 130]
    age_labels = ['0-17', '18-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
    df_filtered['AGE_GROUP'] = pd.cut(df_filtered['AGE'], bins=age_bins, labels=age_labels, right=False)
    
    age_mortality = df_filtered.groupby('AGE_GROUP', observed=True).agg({
        'MORTALITY': ['sum', 'count']
    }).reset_index()
    age_mortality.columns = ['AGE_GROUP', 'Deaths', 'Total']
    age_mortality['Mortality_Rate'] = (age_mortality['Deaths'] / age_mortality['Total'] * 100)
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=age_mortality['AGE_GROUP'],
        y=age_mortality['Mortality_Rate'],
        marker=dict(
            color=age_mortality['Mortality_Rate'],
            colorscale='Reds',
            showscale=False,
            line=dict(color='#00d4ff', width=1)
        ),
        text=[f"{x:.1f}%" for x in age_mortality['Mortality_Rate']],
        textposition='outside',
        hovertemplate='<b>Age: %{x}</b><br>Mortality Rate: %{y:.1f}%<extra></extra>'
    ))
    fig1.update_layout(
        template='plotly_dark',
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        font=dict(color='#f1f5f9', family='Arial, sans-serif'),
        xaxis_title='Age Group',
        yaxis_title='Mortality Rate (%)',
        hovermode='x unified',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig1, use_container_width=True)

# 2. Gender Distribution & Mortality Comparison
with col_viz2:
    st.markdown("#### Gender Analysis")
    
    gender_stats = df_filtered.groupby('SEX', observed=True).agg({
        'MORTALITY': ['sum', 'count']
    }).reset_index()
    gender_stats.columns = ['SEX', 'Deaths', 'Total']
    gender_stats['Mortality_Rate'] = (gender_stats['Deaths'] / gender_stats['Total'] * 100)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=gender_stats['SEX'],
        y=gender_stats['Total'],
        name='Total Cases',
        marker=dict(color='#0099ff'),
        hovertemplate='<b>%{x}</b><br>Cases: %{y:,.0f}<extra></extra>'
    ))
    fig2.add_trace(go.Bar(
        x=gender_stats['SEX'],
        y=gender_stats['Deaths'],
        name='Deaths',
        marker=dict(color='#ff4444'),
        hovertemplate='<b>%{x}</b><br>Deaths: %{y:,.0f}<extra></extra>'
    ))
    fig2.update_layout(
        template='plotly_dark',
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        font=dict(color='#f1f5f9', family='Arial, sans-serif'),
        barmode='group',
        xaxis_title='Gender',
        yaxis_title='Count',
        hovermode='x',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig2, use_container_width=True)

col_viz3, col_viz4 = st.columns(2)

# 3. Comorbidity Impact on Mortality
with col_viz3:
    st.markdown("#### Comorbidity Impact on Mortality")
    
    comorbidity_mortality = df_filtered.groupby('COMORBIDITY_COUNT', observed=True).agg({
        'MORTALITY': ['sum', 'count']
    }).reset_index()
    comorbidity_mortality.columns = ['COMORBIDITY_COUNT', 'Deaths', 'Total']
    comorbidity_mortality['Mortality_Rate'] = (comorbidity_mortality['Deaths'] / comorbidity_mortality['Total'] * 100)
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=comorbidity_mortality['COMORBIDITY_COUNT'],
        y=comorbidity_mortality['Mortality_Rate'],
        mode='lines+markers',
        name='Mortality Rate',
        line=dict(color='#00d4ff', width=3),
        marker=dict(size=10, color='#00d4ff', line=dict(color='#0099ff', width=2)),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.1)',
        hovertemplate='<b>Comorbidities: %{x}</b><br>Mortality Rate: %{y:.1f}%<extra></extra>'
    ))
    fig3.update_layout(
        template='plotly_dark',
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        font=dict(color='#f1f5f9', family='Arial, sans-serif'),
        xaxis_title='Number of Comorbidities',
        yaxis_title='Mortality Rate (%)',
        hovermode='x',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)

# 4. Patient Type Distribution
with col_viz4:
    st.markdown("#### Patient Type Distribution")
    
    patient_type_dist = df_filtered['PATIENT_TYPE'].value_counts()
    
    fig4 = go.Figure(data=[go.Pie(
        labels=patient_type_dist.index,
        values=patient_type_dist.values,
        marker=dict(
            colors=['#0099ff', '#00d4ff', '#ff6b6b'],
            line=dict(color='#1a1f26', width=2)
        ),
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>Count: %{value:,.0f}<br>Share: %{percent}<extra></extra>'
    )])
    fig4.update_layout(
        template='plotly_dark',
        paper_bgcolor='#1e293b',
        font=dict(color='#f1f5f9', family='Arial, sans-serif'),
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

col_viz5, col_viz6 = st.columns(2)

# 5. Intubation & ICU Admission Rates
with col_viz5:
    st.markdown("#### Critical Care Utilization")
    
    critical_care = pd.DataFrame({
        'Metric': ['Intubated', 'ICU Admitted', 'Both'],
        'Count': [
            len(df_filtered[df_filtered['INTUBED'].isin([1, 2])]),
            len(df_filtered[df_filtered['ICU'].isin([1, 2])]),
            len(df_filtered[(df_filtered['INTUBED'].isin([1, 2])) & (df_filtered['ICU'].isin([1, 2]))])
        ]
    })
    
    fig5 = go.Figure(data=[go.Bar(
        x=critical_care['Metric'],
        y=critical_care['Count'],
        marker=dict(
            color=['#ff9900', '#ff4444', '#ff0000'],
            line=dict(color='#00d4ff', width=2)
        ),
        text=[f"{x:,}" for x in critical_care['Count']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>'
    )])
    fig5.update_layout(
        template='plotly_dark',
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        font=dict(color='#f1f5f9', family='Arial, sans-serif'),
        xaxis_title='Care Type',
        yaxis_title='Count',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig5, use_container_width=True)

# 6. Classification Distribution
with col_viz6:
    st.markdown("#### Case Classification")
    
    classification_dist = df_filtered['CLASSIFICATION'].value_counts()
    
    fig6 = go.Figure(data=[go.Bar(
        y=classification_dist.index,
        x=classification_dist.values,
        orientation='h',
        marker=dict(
            color=classification_dist.values,
            colorscale='Viridis',
            line=dict(color='#00d4ff', width=1)
        ),
        text=[f"{x:,}" for x in classification_dist.values],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>'
    )])
    fig6.update_layout(
        template='plotly_dark',
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        font=dict(color='#f1f5f9', family='Arial, sans-serif'),
        xaxis_title='Count',
        yaxis_title='Classification',
        height=400,
        margin=dict(l=200, r=0, t=30, b=0)
    )
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ==================== ADVANCED ANALYTICS ====================
st.markdown("### 🔬 DETAILED COMORBIDITY ANALYSIS")

comorbidities_list = ['DIABETES', 'COPD', 'ASTHMA', 'INMSUPR', 'HIPERTENSION', 
                      'OTHER_DISEASE', 'CARDIOVASCULAR', 'OBESITY', 'RENAL_CHRONIC', 'TOBACCO']

# Calculate comorbidity prevalence and mortality impact
comorbidity_analysis = []
for comorbidity in comorbidities_list:
    with_condition = df_filtered[df_filtered[comorbidity] == 1]
    without_condition = df_filtered[df_filtered[comorbidity] != 1]
    
    if len(with_condition) > 0 and len(without_condition) > 0:
        with_mortality = with_condition['MORTALITY'].sum() / len(with_condition) * 100
        without_mortality = without_condition['MORTALITY'].sum() / len(without_condition) * 100
        prevalence = len(with_condition) / len(df_filtered) * 100
        
        comorbidity_analysis.append({
            'Condition': comorbidity.replace('_', ' ').title(),
            'Prevalence (%)': prevalence,
            'Mortality with Condition (%)': with_mortality,
            'Mortality without Condition (%)': without_mortality,
            'Excess Risk (%)': with_mortality - without_mortality
        })

comorbidity_df = pd.DataFrame(comorbidity_analysis).sort_values('Excess Risk (%)', ascending=False)

col_analysis1, col_analysis2 = st.columns(2)

with col_analysis1:
    st.markdown("#### Excess Mortality Risk by Condition")
    
    fig7 = go.Figure(data=[go.Bar(
        y=comorbidity_df['Condition'],
        x=comorbidity_df['Excess Risk (%)'],
        orientation='h',
        marker=dict(
            color=comorbidity_df['Excess Risk (%)'],
            colorscale='Reds',
            line=dict(color='#00d4ff', width=1)
        ),
        text=[f"{x:.1f}%" for x in comorbidity_df['Excess Risk (%)']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Excess Risk: %{x:.1f}%<extra></extra>'
    )])
    fig7.update_layout(
        template='plotly_dark',
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        font=dict(color='#f1f5f9', family='Arial, sans-serif'),
        xaxis_title='Excess Mortality Risk (%)',
        yaxis_title='Condition',
        height=450,
        margin=dict(l=180, r=0, t=30, b=0)
    )
    st.plotly_chart(fig7, use_container_width=True)

with col_analysis2:
    st.markdown("#### Condition Prevalence")
    
    fig8 = go.Figure(data=[go.Bar(
        y=comorbidity_df['Condition'],
        x=comorbidity_df['Prevalence (%)'],
        orientation='h',
        marker=dict(
            color='#0099ff',
            line=dict(color='#00d4ff', width=1)
        ),
        text=[f"{x:.1f}%" for x in comorbidity_df['Prevalence (%)']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Prevalence: %{x:.1f}%<extra></extra>'
    )])
    fig8.update_layout(
        template='plotly_dark',
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        font=dict(color='#f1f5f9', family='Arial, sans-serif'),
        xaxis_title='Prevalence (%)',
        yaxis_title='Condition',
        height=450,
        margin=dict(l=180, r=0, t=30, b=0)
    )
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")

# ==================== DETAILED DATA TABLE ====================
st.markdown("### 📋 FILTERED DATASET")

display_cols = ['SEX', 'AGE', 'PATIENT_TYPE', 'MORTALITY', 'COMORBIDITY_COUNT', 
                'DIABETES', 'CARDIOVASCULAR', 'HIPERTENSION', 'OBESITY', 'INTUBED', 'ICU']

if st.checkbox('Show raw data table', value=False):
    st.dataframe(
        df_filtered[display_cols].head(100),
        use_container_width=True,
        height=400
    )

st.markdown("---")

# ==================== SUMMARY STATISTICS ====================
st.markdown("### 📊 SUMMARY STATISTICS")

col_stat1, col_stat2, col_stat3 = st.columns(3)

with col_stat1:
    st.markdown("#### Outcome Summary")
    outcome_data = {
        'Outcome': ['Survived', 'Deceased'],
        'Count': [
            len(df_filtered[df_filtered['MORTALITY'] == 0]),
            len(df_filtered[df_filtered['MORTALITY'] == 1])
        ]
    }
    outcome_df = pd.DataFrame(outcome_data)
    st.dataframe(outcome_df, use_container_width=True, hide_index=True)

with col_stat2:
    st.markdown("#### Gender Distribution")
    gender_data = df_filtered['SEX'].value_counts().reset_index()
    gender_data.columns = ['Gender', 'Count']
    st.dataframe(gender_data, use_container_width=True, hide_index=True)

with col_stat3:
    st.markdown("#### Medical Unit Distribution")
    unit_data = df_filtered['MEDICAL_UNIT'].value_counts().head(10).reset_index()
    unit_data.columns = ['Unit', 'Count']
    st.dataframe(unit_data, use_container_width=True, hide_index=True)

st.markdown("---")

# ==================== FOOTER ====================
st.markdown("""
<div style='text-align: center; color: #cbd5e1; margin-top: 50px; padding: 20px; border-top: 2px solid #3b82f6; border-radius: 8px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);'>
    <p style='font-weight: 600; font-size: 16px; color: #60a5fa;'><b>COVID-19 Analytics Dashboard</b></p>
    <p style='color: #94a3b8; font-size: 13px; margin: 8px 0;'>Executive Intelligence Platform | Data-Driven Epidemiological Analysis</p>
    <small style='color: #64748b;'>Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</small>
</div>
""", unsafe_allow_html=True)