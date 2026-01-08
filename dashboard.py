import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import random
import time

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(layout="wide", page_title="Capital Projects Dashboard")

# ==========================================
# 2. DATA GENERATION (Simulating your real data)
# ==========================================
@st.cache_data
def load_data():
    # Configuration
    NUM_STORES = 1000
    DATE_START = datetime(2020, 1, 1)
    DATE_END = datetime(2024, 12, 31)
    REGIONS = ['North East', 'South East', 'Midwest', 'South West', 'West',
               'North Central', 'South Central', 'Pacific', 'Mountain']
    GROUPS = ['Flagship', 'Outlet', 'Mall', 'Street', 'Kiosk',
              'Drive-Thru', 'Airport', 'Campus', 'Pop-up', 'Reserve']
    VENDORS = ['Acme Const.', 'Global Tech', 'City Services', 'BuildRight',
               'Apex Solutions', 'Zenith HVAC', 'Prime Electric', 'Safety First']

    # Generate Stores
    stores_data = []
    random.seed(42) # Fixed seed so data looks the same every time you run it
    
    for i in range(1, NUM_STORES + 1):
        store_id = f"S-{i:04d}"
        region = random.choice(REGIONS)
        group = random.choice(GROUPS)
        # Lat/Lon mostly within US bounds
        lat = round(random.uniform(25.0, 49.0), 4)
        lon = round(random.uniform(-125.0, -67.0), 4)
        stores_data.append({'Store_ID': store_id, 'Region': region, 'Store_Group': group, 'Latitude': lat, 'Longitude': lon})
    
    df_stores = pd.DataFrame(stores_data)
    
    # Generate Transactions (One-to-Many logic)
    transactions = []
    for index, store in df_stores.iterrows():
        num_projects = random.randint(1, 6) # 1 to 6 projects per store
        for p in range(num_projects):
            project_id = f"PROJ-{store['Store_ID']}-{p+1}"
            num_vendors = random.randint(1, 2) # 1 or 2 vendors per project
            for v in range(num_vendors):
                days_diff = (DATE_END - DATE_START).days
                r_date = DATE_START + timedelta(days=random.randint(0, days_diff))
                cost = round(random.uniform(1000, 50000), 2)
                transactions.append({
                    'Date': r_date,
                    'Project_ID': project_id,
                    'Store_ID': store['Store_ID'],
                    'Region': store['Region'],
                    'Store_Group': store['Store_Group'],
                    'Latitude': store['Latitude'],
                    'Longitude': store['Longitude'],
                    'Vendor': random.choice(VENDORS),
                    'Cost': cost
                })
    
    df = pd.DataFrame(transactions)
    return df

# Load the data
df = load_data()

# ==========================================
# 3. SIDEBAR CONFIGURATION (Tabs for Filters & AI)
# ==========================================
st.sidebar.header("Capital Projects Dashboard")
tab_filters, tab_chat = st.sidebar.tabs(["🎛️ Filters", "🤖 AI Analyst"])

# --- TAB 1: FILTERS ---
with tab_filters:
    st.write("### Filter Projects")
    
    # Region Filter
    selected_regions = st.multiselect(
        "Select Region",
        options=df['Region'].unique(),
        default=df['Region'].unique()
    )

    # Store Group Filter
    selected_groups = st.multiselect(
        "Select Store Group",
        options=df['Store_Group'].unique(),
        default=df['Store_Group'].unique()
    )

    # Vendor Filter (Important for Drill-down)
    selected_vendors = st.multiselect(
        "Select Vendor",
        options=df['Vendor'].unique(),
        default=df['Vendor'].unique()
    )

    st.markdown("---")
    st.info(f"Showing {len(selected_regions)} Regions, {len(selected_groups)} Groups")

# Apply Filters (Global)
df_filtered = df[
    (df['Region'].isin(selected_regions)) &
    (df['Store_Group'].isin(selected_groups)) &
    (df['Vendor'].isin(selected_vendors))
]

# --- TAB 2: AI CHAT ---
with tab_chat:
    st.write("### Chat with Data")
    st.caption("Ask questions about the filtered data.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm analyzing your current data view. Ask me anything!"}
        ]

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    # Note: In sidebar, chat_input is automatically pinned to bottom!
    if prompt := st.chat_input("Ask a question..."):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("Thinking..."):
                time.sleep(1.0) # Fake latency
                
            # Mock Response Logic
            row_count = len(df_filtered)
            total_spend = df_filtered['Cost'].sum()
            
            mock_responses = [
                f"Analyzing **{row_count} projects**.\nTotal spend: **${total_spend/1e6:.1f}M**.\nTop region: **{df_filtered['Region'].mode()[0]}**.",
                f"The top vendor here is **{df_filtered['Vendor'].mode()[0]}**.",
                "I see seasonality in the data. Want a chart?",
                f"Your query: '{prompt}'\n\nAvg Cost: **${df_filtered['Cost'].mean():,.0f}**."
            ]
            
            if "spend" in prompt.lower() or "cost" in prompt.lower():
                response_text = mock_responses[0]
            elif "vendor" in prompt.lower():
                response_text = mock_responses[1]
            else:
                response_text = mock_responses[3]
                
            for chunk in response_text.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# ==========================================
# 4. KPI METRICS (Top Row)
# ==========================================
st.title("🏗️ Capital Projects Interactive Dashboard")
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Spend", f"${df_filtered['Cost'].sum()/1e6:.1f}M")
c2.metric("Total Projects", f"{df_filtered['Project_ID'].nunique()}")
c3.metric("Active Stores", f"{df_filtered['Store_ID'].nunique()}")
c4.metric("Vendors Engaged", f"{df_filtered['Vendor'].nunique()}")

st.markdown("---")

# ==========================================
# 5. CHARTS ROW (Sunburst & Bar)
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Spend by Region & Group")
    fig_sun = px.sunburst(
        df_filtered, 
        path=['Region', 'Store_Group'], 
        values='Cost',
        color='Cost',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_sun, use_container_width=True)

with col2:
    st.subheader("Top Vendors by Spend")
    vendor_group = df_filtered.groupby('Vendor')['Cost'].sum().reset_index().sort_values('Cost', ascending=True)
    fig_bar = px.bar(
        vendor_group, 
        x='Cost', 
        y='Vendor', 
        orientation='h', 
        text_auto='.2s'
    )
    fig_bar.update_layout(xaxis_title="Total Spend", yaxis_title="")
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 6. DETAILED DATA & TIME SERIES
# ==========================================
st.markdown("---")
st.subheader("📅 Spending Trends & Details")

tab1, tab2 = st.tabs(["Spending Over Time", "Detailed Project List"])

with tab1:
    # Aggregating by Month for cleaner line chart
    df_filtered['Month_Year'] = df_filtered['Date'].dt.to_period('M').astype(str)
    time_data = df_filtered.groupby('Month_Year')['Cost'].sum().reset_index()
    fig_line = px.line(time_data, x='Month_Year', y='Cost', markers=True)
    fig_line.update_xaxes(type='category') # Ensures dates don't get squashed
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    # The detailed table
    st.dataframe(
        df_filtered[['Date', 'Store_ID', 'Project_ID', 'Vendor', 'Cost', 'Region', 'Store_Group']].sort_values('Date', ascending=False),
        use_container_width=True
    )

# ==========================================
# 7. GEOSPATIAL MAP (At the bottom)
# ==========================================
st.markdown("---")
st.subheader("📍 Geospatial Spend Map")
st.caption("Map shows stores matching your filters. Zoom in to see individual locations.")

# Aggregate data for the map (1 bubble = 1 Store)
map_data = df_filtered.groupby(['Store_ID', 'Latitude', 'Longitude', 'Region']).agg({
    'Cost': 'sum',
    'Project_ID': 'count',
    'Vendor': lambda x: x.mode()[0] if not x.mode().empty else 'Mixed'
}).reset_index()

# Only render map if there is data
if not map_data.empty:
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in map_data.iterrows():
        # Create HTML for the tooltip
        tooltip_html = f"""
        <b>Store:</b> {row['Store_ID']}<br>
        <b>Region:</b> {row['Region']}<br>
        <b>Total Spend:</b> ${row['Cost']:,.0f}<br>
        <b>Projects:</b> {row['Project_ID']}
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            tooltip=f"Store {row['Store_ID']} (${row['Cost']/1000:.0f}k)",
            popup=folium.Popup(tooltip_html, max_width=300),
            color='#3186cc',
            fill=True,
            fill_color='#3186cc'
        ).add_to(marker_cluster)

    st_folium(m, width=1200, height=500)
else:
    st.warning("No stores match your current filters.")
