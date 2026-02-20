import streamlit as st
import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Uber Advanced Analytics Dashboard", layout="wide")

st.title(" Uber Trip Analysis Dashboard")

# -----------------------------------
# Load Data
# -----------------------------------
@st.cache_data
def load_data():
    files = glob.glob("data/uber-raw-data-*.csv")
    df_list = [pd.read_csv(file) for file in files]
    df = pd.concat(df_list, ignore_index=True)
    df['Date/Time'] = pd.to_datetime(df['Date/Time'])
    return df

df = load_data()

# -----------------------------------
# Sidebar Filters
# -----------------------------------
st.sidebar.header("📅 Filter Data")

min_date = df['Date/Time'].min().date()
max_date = df['Date/Time'].max().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

filtered_df = df[
    (df['Date/Time'].dt.date >= start_date) &
    (df['Date/Time'].dt.date <= end_date)
]

# -----------------------------------
# Create Time Features
# -----------------------------------
filtered_df['Hour'] = filtered_df['Date/Time'].dt.hour
filtered_df['Day'] = filtered_df['Date/Time'].dt.day
filtered_df['Month'] = filtered_df['Date/Time'].dt.month
filtered_df['DayOfWeek'] = filtered_df['Date/Time'].dt.day_name()

# -----------------------------------
# KPI Section
# -----------------------------------
st.markdown(" Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric("Total Trips", f"{len(filtered_df):,}")
col2.metric("Average Trips per Day", f"{int(len(filtered_df) / filtered_df['Day'].nunique()):,}")
col3.metric("Peak Hour", filtered_df['Hour'].value_counts().idxmax())

st.markdown("---")

# -----------------------------------
# Trips Per Hour
# -----------------------------------
st.subheader(" Trips per Hour")

hourly = filtered_df.groupby('Hour').size().reset_index(name='Trips')
fig1 = px.bar(hourly, x='Hour', y='Trips', color='Trips')
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------------
# Trips Per Day
# -----------------------------------
st.subheader(" Trips per Day of Week")

daily = filtered_df.groupby('DayOfWeek').size().reset_index(name='Trips')
fig2 = px.bar(daily, x='DayOfWeek', y='Trips', color='Trips')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------
# Monthly Trend
# -----------------------------------
st.subheader(" Monthly Growth Trend")

monthly = filtered_df.groupby('Month').size().reset_index(name='Trips')
fig3 = px.line(monthly, x='Month', y='Trips', markers=True)
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------------
# Hourly Time Series
# -----------------------------------
st.subheader(" Hourly Time Series")

filtered_df.set_index('Date/Time', inplace=True)
hourly_series = filtered_df.resample('H').size()

fig4 = px.line(x=hourly_series.index, y=hourly_series.values)
fig4.update_layout(xaxis_title="Time", yaxis_title="Trips")
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------
# Rolling Average
# -----------------------------------
st.subheader(" 24-Hour Rolling Average")

rolling_avg = hourly_series.rolling(24).mean()

fig5 = px.line(x=rolling_avg.index, y=rolling_avg.values)
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------------
# Heatmap (Hour vs Day)
# -----------------------------------
st.subheader(" Heatmap (Hour vs Day of Week)")

heatmap_data = filtered_df.groupby(['DayOfWeek','Hour']).size().unstack()

fig6, ax = plt.subplots(figsize=(10,5))
sns.heatmap(heatmap_data, cmap="YlOrRd")
st.pyplot(fig6)

# -----------------------------------
# Base Performance
# -----------------------------------
st.subheader(" Base Performance")

base_data = filtered_df.groupby('Base').size().reset_index(name='Trips')
fig7 = px.bar(base_data, x='Base', y='Trips', color='Trips')
st.plotly_chart(fig7, use_container_width=True)

# -----------------------------------
# Map Visualization
# -----------------------------------
st.subheader("🗺 Pickup Location Map")

sample_map = filtered_df.sample(min(5000, len(filtered_df)))

fig8 = px.scatter_mapbox(
    sample_map,
    lat="Lat",
    lon="Lon",
    zoom=10,
    height=500
)

fig8.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig8, use_container_width=True)

# -----------------------------------
# Business Insights Section
# -----------------------------------
st.markdown("---")
st.markdown("## Business Insights")

st.markdown("""
-  Peak demand occurs during evening hours (5 PM – 9 PM).
-  Weekend trips are significantly higher than weekdays.
-  Demand increased steadily from April to September.
-  Strong daily seasonality observed.
-  Certain bases handle higher trip volumes.
-  High pickup concentration in Manhattan area.

Recommendations:
- Increase driver allocation during evening peak hours.
- Optimize pricing strategies for weekends.
- Improve fleet distribution based on heatmap demand zones.
- Use demand forecasting for dynamic driver scheduling.
""")

st.markdown("---")

