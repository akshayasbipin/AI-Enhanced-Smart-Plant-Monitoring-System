import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta
import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt
import os
from dotenv import load_dotenv
from main_chat import get_response
import pandas as pd
import plotly.graph_objects as go

load_dotenv()

# Set up page configuration
st.set_page_config(page_title="Plant Healthcare Monitor", page_icon="🌱", layout="wide")

# Initialize session state variables if they don't exist
if 'plants' not in st.session_state:
    # Create sample plants with historical data
    st.session_state.plants = {
        "Monstera Deliciosa": {
            "type": "Monstera",
            "location": "Living Room",
            "light_needs": "Bright indirect light",
            "water_frequency": 7,
            "last_watered": datetime.now() - timedelta(days=3),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), "moisture": 75, "notes": "Repotted with fresh soil."},
                {"date": (datetime.now() - timedelta(days=24)).strftime("%Y-%m-%d"), "moisture": 65, "notes": "New leaf unfurling."},
                {"date": (datetime.now() - timedelta(days=18)).strftime("%Y-%m-%d"), "moisture": 55, "notes": "Leaves looking a bit droopy, needs water."},
                {"date": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"), "moisture": 85, "notes": "Watered thoroughly, looking better."},
                {"date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"), "moisture": 70, "notes": "Dusted leaves. Plant looks healthy."}
            ]
        },
        "Peace Lily": {
            "type": "Spathiphyllum",
            "location": "Bedroom",
            "light_needs": "Low to medium light",
            "water_frequency": 5,
            "last_watered": datetime.now() - timedelta(days=4),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"), "moisture": 60, "notes": "Leaves turning slightly yellow at tips."},
                {"date": (datetime.now() - timedelta(days=22)).strftime("%Y-%m-%d"), "moisture": 82, "notes": "Watered and moved away from direct sunlight."},
                {"date": (datetime.now() - timedelta(days=17)).strftime("%Y-%m-%d"), "moisture": 75, "notes": "New flower bud forming."},
                {"date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"), "moisture": 55, "notes": "Soil looking dry, needs watering."},
                {"date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), "moisture": 85, "notes": "Watered thoroughly, plant perked up."}
            ]
        },
        "Snake Plant": {
            "type": "Sansevieria",
            "location": "Home Office",
            "light_needs": "Low to bright indirect light",
            "water_frequency": 14,
            "last_watered": datetime.now() - timedelta(days=10),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=42)).strftime("%Y-%m-%d"), "moisture": 45, "notes": "Looking healthy and sturdy."},
                {"date": (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d"), "moisture": 30, "notes": "Soil very dry but plant still looks good."},
                {"date": (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"), "moisture": 80, "notes": "Watered after long period, plant thriving."},
                {"date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"), "moisture": 60, "notes": "New shoot growing from base."},
                {"date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), "moisture": 40, "notes": "Starting to dry out but still healthy."}
            ]
        },
        "Fiddle Leaf Fig": {
            "type": "Ficus lyrata",
            "location": "Dining Room",
            "light_needs": "Bright indirect light",
            "water_frequency": 10,
            "last_watered": datetime.now() - timedelta(days=2),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d"), "moisture": 65, "notes": "Some brown spots on lower leaves."},
                {"date": (datetime.now() - timedelta(days=29)).strftime("%Y-%m-%d"), "moisture": 50, "notes": "Removed damaged leaves, reduced watering."},
                {"date": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"), "moisture": 70, "notes": "New growth at top, looking better."},
                {"date": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"), "moisture": 55, "notes": "Added humidifier nearby, plant responding well."},
                {"date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"), "moisture": 80, "notes": "Watered and rotated, even growth pattern."}
            ]
        },
        "Boston Fern": {
            "type": "Nephrolepis exaltata",
            "location": "Bathroom",
            "light_needs": "Medium indirect light",
            "water_frequency": 4,
            "last_watered": datetime.now() - timedelta(days=1),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"), "moisture": 70, "notes": "Thriving in humid bathroom environment."},
                {"date": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"), "moisture": 55, "notes": "Some fronds turning slightly brown at tips."},
                {"date": (datetime.now() - timedelta(days=16)).strftime("%Y-%m-%d"), "moisture": 85, "notes": "Misted and watered, looking lush again."},
                {"date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"), "moisture": 65, "notes": "New fronds developing, good growth."},
                {"date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), "moisture": 50, "notes": "Needs watering soon, slight drooping."}
            ]
        }
    }
    
# Application header
st.title("🌱 Plant Healthcare Monitor")
st.markdown("Track your plants' health and get personalized care recommendations")

# Create tabs for different sections of the app
tab2, tab4, tab5 = st.tabs(["Plant Details","Plant ChatBot", "Latest Analytics"])

# Plant details tab
with tab2:
    st.header("Plant Details")
    
    col1, col2, col3, col4 = st.columns(4)
    # Create a DataFrame for the chart
    chart_data = []
    for plant_name, plant_data in st.session_state.plants.items():
        for entry in plant_data["health_history"]:
            chart_data.append({
                "Plant": plant_name,
                "Date": entry["date"],
                "Moisture level": entry["moisture"]
            })
    
    chart_df = pd.DataFrame(chart_data)
    
    # Create health trend chart
    st.subheader("Moisture level Trends")
    chart = alt.Chart(chart_df).mark_line(point=True).encode(
        x='Date:T',
        y=alt.Y('Moisture level', scale=alt.Scale(domain=[50, 100])),
        color='Plant:N',
        tooltip=['Plant', 'Date', 'Moisture level']
    ).properties(
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
    
    # Plant selector
    selected_plant = st.selectbox("Select a plant", list(st.session_state.plants.keys()))
    
    if selected_plant:
        plant_data = st.session_state.plants[selected_plant]
        
        # Display plant information
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader(selected_plant)
            st.write(f"**Type:** {plant_data['type']}")
            st.write(f"**Location:** {plant_data['location']}")
            st.write(f"**Light needs:** {plant_data['light_needs']}")
            st.write(f"**Water frequency:** Every {plant_data['water_frequency']} days")
            
            days_since_watered = (datetime.now() - plant_data["last_watered"]).days
            
            if days_since_watered >= plant_data["water_frequency"]:
                st.error(f"⚠️ Last watered {days_since_watered} days ago. **Needs water now!**")
            else:
                st.info(f"💧 Last watered {days_since_watered} days ago. Water in {plant_data['water_frequency'] - days_since_watered} days.")
        
        with col2:
            # Display history
            st.subheader("Health History")
            history_df = pd.DataFrame(plant_data["health_history"])
            
            # Create multiple line charts for each metric
            # Fixed approach: Create separate charts for each metric instead of using transform_fold
            moisture_chart = alt.Chart(history_df).mark_line(point=True, color='blue', strokeWidth=3).encode(
                x=alt.X('date:T', title='Date', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('moisture:Q', title='Moisture (%)', scale=alt.Scale(domain=[0, 100])),
                tooltip=['date', 'moisture', 'notes']
            ).properties(height=300, width=600)

            st.altair_chart(moisture_chart, use_container_width=True)
    # Sidebar for app navigation
    with st.sidebar:
        st.title("Plant Care Helper")
        st.write("This chatbot provides personalized plant care advice and recommendations.")
        
        st.subheader("Available Features")
        st.write("- Chat with the plant assistant")
        st.write("- Get care guides for common houseplants")
        st.write("- Track watering schedules")
        st.write("- Receive seasonal care tips")
        st.write("- Download the soil moisture data as CSV")
        st.write("- View plant health history")
        
        # Simple plant database display
        st.subheader("Your Plant Collection")
        for plant_name, plant_data in st.session_state.plants.items():
            st.write(f"**{plant_name}** ({plant_data['type']})")

with tab4:  # 🟢 Embedding the chatbot inside Tab 4
    st.header("Plant Care Assistant")
    st.write("Ask me anything about plant care, and I'll help you keep your plants healthy!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    query = st.chat_input("Type your question here...")

    if query:
        # Display user message
        st.chat_message("user").markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})

        # Get AI response with chat history
        chat_history = "\n".join([msg["content"] for msg in st.session_state.messages])  # Combine past messages
        response = get_response(query)  # ✅ Pass chat_history

        # Format response
        if response:
            formatted_response = f"{response}" 
        else:
            formatted_response = "Sorry, I couldn't process your request. Try again!"

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(formatted_response)

        # Store AI response
        st.session_state.messages.append({"role": "assistant", "content": formatted_response})
        
with tab5:
    st.header("Latest Plant Moisture Details: ")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)

    st.title("🌿 Plant Monitoring Dashboard")
    # Fetch data
    response = supabase.table("data_table").select("plant_name, soil_moisture, created_at").order("created_at", desc=True).execute()
    data = response.data

    if not data:
        st.warning("No data available!")
        st.stop()

    df = pd.DataFrame(data)
    df["created_at"] = pd.to_datetime(df["created_at"])

    # Plant filter
    plants = df["plant_name"].unique()
    selected_plant = st.selectbox("Select Plant", plants)
    filtered_df = df[df["plant_name"] == selected_plant].sort_values("created_at")

    # Show data table
    st.subheader(f"📋 Data Table - {selected_plant.capitalize()}")
    st.dataframe(filtered_df, use_container_width=True)

    # Line chart for soil moisture trend
    st.subheader("📈 Soil Moisture Trend Over Time")
    st.line_chart(filtered_df.set_index("created_at")["soil_moisture"])
    
    #CSV download button
    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"{selected_plant}_soil_moisture_data.csv",
        mime="text/csv"
    )
    # Latest moisture gauge
    latest_value = filtered_df["soil_moisture"].iloc[-1]
    st.subheader("🌡️ Latest Soil Moisture Level")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_value,
        title={'text': "Soil Moisture"},
        gauge={
            'axis': {'range': [0, 4095]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, 1500], 'color': "red"},
                {'range': [1500, 3000], 'color': "yellow"},
                {'range': [3000, 4095], 'color': "lightgreen"},
            ],
        }
    ))
    st.plotly_chart(fig, use_container_width=True)