# Import required modules
import streamlit as st
import pandas as pd

# Initialize or get Streamlit state variable for temp_data
def get_state(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]

# Initialize session states
temp_data = get_state('temp_data', [])

# Function to calculate forecasts for multiple channels and mediums
def calculate_forecast(temp_data, months, growth_rate):
    forecast_data = []
    current_mrr = 0
    total_cost = 0
    total_customers = 0
    
    initial_mrr_contribution = {}
    
    # Calculate the initial MRR and MRR contributions for each channel
    for entry in temp_data:
        trials = entry['site_visitors'] * (entry['conversion_to_trial'] / 100)
        paid_customers = trials * (entry['conversion_to_paid'] / 100)
        channel_mrr = paid_customers * 99
        current_mrr += channel_mrr
        initial_mrr_contribution[entry['channel'] + entry['medium']] = channel_mrr
    
    for month in range(1, months + 1):
        # Calculate MRR target for the month based on growth_rate
        if month != 1:
            current_mrr *= (1 + (growth_rate / 100))
        
        for entry in temp_data:
            conversion_to_trial = entry['conversion_to_trial'] / 100
            conversion_to_paid = entry['conversion_to_paid'] / 100
            cost = entry['cost']
            channel = entry['channel']
            medium = entry['medium']
            
            # Calculate Site Visitors needed for the month's MRR for this specific channel and medium
            channel_medium_key = channel + medium
            channel_mrr = (initial_mrr_contribution[channel_medium_key] / sum(initial_mrr_contribution.values())) * current_mrr
            
            paid_customers = channel_mrr / 99
            trials = paid_customers / conversion_to_paid
            site_visitors = trials / conversion_to_trial
            
            forecast_data.append({
                'Month': month,
                'Channel': channel,
                'Medium': medium,
                'Site Visitors': round(site_visitors),
                'Paid Customers': round(paid_customers),
                'MRR': round(channel_mrr),
                'ARR': round(channel_mrr * 12),
                'Cost': round(cost),
                'CAC': round(cost / paid_customers if paid_customers > 0 else 0),
            })
            
            total_cost += cost
            total_customers += paid_customers
    
    return pd.DataFrame(forecast_data), round(total_cost, 2), round(current_mrr, 2), round(total_customers, 2)
    forecast_data = []
    current_mrr = 0
    total_cost = 0
    total_customers = 0
    
    for month in range(1, months + 1):
        # Calculate MRR target for the month based on growth_rate
        if month == 1:
            for entry in temp_data:
                trials = entry['site_visitors'] * (entry['conversion_to_trial'] / 100)
                paid_customers = trials * (entry['conversion_to_paid'] / 100)
                current_mrr += paid_customers * 99
        else:
            current_mrr *= (1 + (growth_rate / 100))
        
        for entry in temp_data:
            conversion_to_trial = entry['conversion_to_trial'] / 100
            conversion_to_paid = entry['conversion_to_paid'] / 100
            cost = entry['cost']
            channel = entry['channel']
            medium = entry['medium']
            
            # Reverse calculate Site Visitors needed for the month's MRR
            paid_customers = current_mrr / 99
            trials = paid_customers / conversion_to_paid
            site_visitors = trials / conversion_to_trial
            
            forecast_data.append({
                'Month': month,
                'Channel': channel,
                'Medium': medium,
                'Site Visitors': round(site_visitors),
                'Paid Customers': round(paid_customers),
                'MRR': round(current_mrr),
                'ARR': round(current_mrr * 12),
                'Cost': round(cost),
                'CAC': round(cost / paid_customers if paid_customers > 0 else 0),
            })
            
            total_cost += cost
            total_customers += paid_customers
    
    return pd.DataFrame(forecast_data), round(total_cost, 2), round(current_mrr, 2), round(total_customers, 2)

# Streamlit layout
st.title('Marketing Predictive Modeling')
st.header('Input Initial Metrics')

# Get or initialize temp_data from session state
temp_data = get_state('temp_data', [])

# Create columns for the input fields
col1, col2 = st.columns(2)
with col1:
    channel_options = ['Targeting Blogs', 'Publicity', 'Unconventional PR', 'Search Engine Marketing', 
                       'Social & Display Ads', 'Offline Ads', 'Search Engine Optimization', 'Content Marketing', 
                       'Email Marketing', 'Viral Marketing', 'Engineering as Marketing', 'Business Development', 
                       'Sales', 'Affiliate Programs', 'Existing Platforms', 'Trade Shows', 'Offline Events', 
                       'Speaking Engagements', 'Community Building']
    selected_channel = st.selectbox('Select Channel', channel_options)
with col2:
    medium = st.text_input('Enter Medium', 'Example: Facebook Ad')

col3, col4, col5 = st.columns(3)
with col3:
    site_visitors = st.number_input('Site Visitors', min_value=0)
with col4:
    cost = st.number_input('Cost', min_value=0)
with col5:
    churn_rate = st.number_input('Churn Rate (%)', min_value=0.0, max_value=100.0)

col6, col7 = st.columns(2)
with col6:
    conversion_to_trial = st.number_input('Conversion Rate to Trial (%)', min_value=0.0, max_value=100.0)
with col7:
    conversion_to_paid = st.number_input('Conversion Rate to Paid (%)', min_value=0.0, max_value=100.0)

# Button to add the current metrics to the forecast
if st.button('Add to Forecast'):
    temp_data.append({
        'channel': selected_channel,
        'medium': medium,
        'site_visitors': site_visitors,
        'conversion_to_trial': conversion_to_trial,
        'conversion_to_paid': conversion_to_paid,
        'churn_rate': churn_rate,
        'cost': cost
    })
    st.write(f'Added {medium} under {selected_channel} to the forecast.')

# Display current contents of temp_data
st.write('Current Forecast Data:')
st.write(pd.DataFrame(temp_data))

# Input fields for forecast adjustments
growth_rate = st.number_input('Growth Rate for MRR (%)', min_value=0.0, max_value=100.0, value=10.0)
forecast_months = st.number_input('Number of Months for Forecast', min_value=1, max_value=120, value=12)

# Button to generate the complete forecast
if st.button('Generate Forecast'):
    if len(temp_data) == 0:
        st.write('Please add at least one set of metrics.')
    else:
        forecast_df, total_cost, total_mrr, total_customers = calculate_forecast(temp_data, forecast_months, growth_rate)
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader('Total Customers')
            st.write(f"{total_customers:,.0f}")
        with col2:
            st.subheader('CAC')
            st.write(f"${total_cost / total_customers if total_customers > 0 else 0:,.2f}")
        with col3:
            st.subheader('Total MRR')
            st.write(f"${total_mrr:,.2f}")
        with col4:
            st.subheader('Total ARR')
            st.write(f"${total_mrr * 12:,.2f}")
        
        # Display forecast dataframe
        st.write('Forecast Data:')
        st.write(forecast_df)
