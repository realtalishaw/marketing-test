
import streamlit as st
import pandas as pd

# Initialize or get Streamlit state variable for temp_data
def get_state():
    if 'temp_data' not in st.session_state:
        st.session_state.temp_data = []
    return st.session_state.temp_data

# Function to calculate forecasts for multiple channels and mediums
def calculate_forecast(temp_data, months, growth_rate):
    forecast_data = []
    total_cost = 0
    total_mrr = 0
    total_customers = 0
    
    for entry in temp_data:
        site_visitors = entry['site_visitors']
        conversion_to_trial = entry['conversion_to_trial'] / 100
        conversion_to_paid = entry['conversion_to_paid'] / 100
        churn_rate = entry['churn_rate'] / 100
        cost = entry['cost']
        channel = entry['channel']
        medium = entry['medium']
        
        for month in range(1, months + 1):
            trials = site_visitors * conversion_to_trial
            paid_customers = trials * conversion_to_paid
            mrr = paid_customers * 99  # Monthly rate of $99 per customer
            
            # Factor in churn rate for MRR and customers
            mrr *= (1 - churn_rate)
            paid_customers *= (1 - churn_rate)
            
            # Calculate CAC, LTV, and ROI
            cac = cost / paid_customers if paid_customers > 0 else 0
            ltv = (mrr * 12) / churn_rate if churn_rate > 0 else 0
            roi = (ltv - cac) / cac if cac > 0 else 0
            
            # Update totals for summary
            total_cost += cost
            total_mrr += mrr
            total_customers += paid_customers
            
            forecast_data.append({
                'Month': month,
                'Channel': channel,
                'Medium': medium,
                'Site Visitors': round(site_visitors, 2),
                'Trials': round(trials, 2),
                'Paid Customers': round(paid_customers, 2),
                'MRR': round(mrr, 2),
                'Cost': round(cost, 2),
                'CAC': round(cac, 2),
                'LTV': round(ltv, 2),
                'ROI': round(roi, 2)
            })
            
            site_visitors *= (1 + (growth_rate / 100))
            
    return pd.DataFrame(forecast_data), round(total_cost, 2), round(total_mrr, 2), round(total_customers, 2)

# Streamlit layout
st.sidebar.header('Navigation')
navigation = st.sidebar.selectbox('Go To', ['Home', 'Predictive', 'Actual'])

# Home Tab
if navigation == 'Home':
    st.title('Dashboard')
    # Add your Home tab content here

# Predictive Tab
elif navigation == 'Predictive':
    st.title('Predictive Modeling')
    st.header('Input Initial Metrics')
    
    # Get or initialize temp_data from session state
    temp_data = get_state()

    # Input fields for channel, medium, and initial metrics
    selected_channel = st.selectbox('Select Channel', ['Channel 1', 'Channel 2', 'Channel 3'])
    medium = st.text_input('Enter Medium', 'Example: Facebook Ad')
    site_visitors = st.number_input('Site Visitors', min_value=0, value=1000)
    conversion_to_trial = st.number_input('Conversion Rate to Trial (%)', min_value=0.0, max_value=100.0, value=2.0)
    conversion_to_paid = st.number_input('Conversion Rate to Paid (%)', min_value=0.0, max_value=100.0, value=20.0)
    churn_rate = st.number_input('Churn Rate (%)', min_value=0.0, max_value=100.0, value=2.0)
    cost = st.number_input('Cost', min_value=0, value=500)

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
    growth_rate = st.number_input('Growth Rate for Site Visitors (%)', min_value=0.0, max_value=100.0, value=10.0)
    forecast_months = st.number_input('Number of Months for Forecast', min_value=1, max_value=120, value=12)

    # Button to generate the complete forecast
    if st.button('Generate Forecast'):
        if len(temp_data) == 0:
            st.write('Please add at least one set of metrics.')
        else:
            forecast_df, total_cost, total_mrr, total_customers = calculate_forecast(temp_data, forecast_months, growth_rate)
            
            # Display summary metrics
            st.write(f"Total Cost: ${total_cost}")
            st.write(f"Total MRR: ${total_mrr}")
            st.write(f"Total Customers: {total_customers}")
            st.write(f"CAC: ${total_cost / total_customers if total_customers > 0 else 0}")
            st.write(f"LTV: ${(total_mrr * 12) / (total_customers * forecast_months) if total_customers > 0 else 0}")
            
            # Display detailed table
            st.write(forecast_df)

# Actual Tab
elif navigation == 'Actual':
    st.title('Actual Metrics')
    st.write('This section is under development.')
