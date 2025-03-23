import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import altair as alt
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from main_chat import get_response

# from app_chat import chat_bot

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
                {"date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), "moisture": 75, "light": 80, "temperature": 72, "health_score": 85, "notes": "Repotted with fresh soil."},
                {"date": (datetime.now() - timedelta(days=24)).strftime("%Y-%m-%d"), "moisture": 65, "light": 78, "temperature": 73, "health_score": 82, "notes": "New leaf unfurling."},
                {"date": (datetime.now() - timedelta(days=18)).strftime("%Y-%m-%d"), "moisture": 55, "light": 82, "temperature": 75, "health_score": 79, "notes": "Leaves looking a bit droopy, needs water."},
                {"date": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"), "moisture": 85, "light": 80, "temperature": 74, "health_score": 88, "notes": "Watered thoroughly, looking better."},
                {"date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"), "moisture": 70, "light": 79, "temperature": 73, "health_score": 85, "notes": "Dusted leaves. Plant looks healthy."}
            ]
        },
        "Peace Lily": {
            "type": "Spathiphyllum",
            "location": "Bedroom",
            "light_needs": "Low to medium light",
            "water_frequency": 5,
            "last_watered": datetime.now() - timedelta(days=4),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"), "moisture": 60, "light": 65, "temperature": 71, "health_score": 72, "notes": "Leaves turning slightly yellow at tips."},
                {"date": (datetime.now() - timedelta(days=22)).strftime("%Y-%m-%d"), "moisture": 82, "light": 63, "temperature": 72, "health_score": 80, "notes": "Watered and moved away from direct sunlight."},
                {"date": (datetime.now() - timedelta(days=17)).strftime("%Y-%m-%d"), "moisture": 75, "light": 67, "temperature": 70, "health_score": 85, "notes": "New flower bud forming."},
                {"date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"), "moisture": 55, "light": 65, "temperature": 69, "health_score": 75, "notes": "Soil looking dry, needs watering."},
                {"date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), "moisture": 85, "light": 66, "temperature": 70, "health_score": 82, "notes": "Watered thoroughly, plant perked up."}
            ]
        },
        "Snake Plant": {
            "type": "Sansevieria",
            "location": "Home Office",
            "light_needs": "Low to bright indirect light",
            "water_frequency": 14,
            "last_watered": datetime.now() - timedelta(days=10),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=42)).strftime("%Y-%m-%d"), "moisture": 45, "light": 70, "temperature": 74, "health_score": 90, "notes": "Looking healthy and sturdy."},
                {"date": (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d"), "moisture": 30, "light": 72, "temperature": 75, "health_score": 88, "notes": "Soil very dry but plant still looks good."},
                {"date": (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"), "moisture": 80, "light": 71, "temperature": 73, "health_score": 91, "notes": "Watered after long period, plant thriving."},
                {"date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"), "moisture": 60, "light": 73, "temperature": 74, "health_score": 90, "notes": "New shoot growing from base."},
                {"date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), "moisture": 40, "light": 75, "temperature": 75, "health_score": 87, "notes": "Starting to dry out but still healthy."}
            ]
        },
        "Fiddle Leaf Fig": {
            "type": "Ficus lyrata",
            "location": "Dining Room",
            "light_needs": "Bright indirect light",
            "water_frequency": 10,
            "last_watered": datetime.now() - timedelta(days=2),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d"), "moisture": 65, "light": 85, "temperature": 73, "health_score": 75, "notes": "Some brown spots on lower leaves."},
                {"date": (datetime.now() - timedelta(days=29)).strftime("%Y-%m-%d"), "moisture": 50, "light": 84, "temperature": 74, "health_score": 72, "notes": "Removed damaged leaves, reduced watering."},
                {"date": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"), "moisture": 70, "light": 86, "temperature": 75, "health_score": 78, "notes": "New growth at top, looking better."},
                {"date": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"), "moisture": 55, "light": 83, "temperature": 74, "health_score": 82, "notes": "Added humidifier nearby, plant responding well."},
                {"date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"), "moisture": 80, "light": 85, "temperature": 73, "health_score": 85, "notes": "Watered and rotated, even growth pattern."}
            ]
        },
        "Boston Fern": {
            "type": "Nephrolepis exaltata",
            "location": "Bathroom",
            "light_needs": "Medium indirect light",
            "water_frequency": 4,
            "last_watered": datetime.now() - timedelta(days=1),
            "health_history": [
                {"date": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"), "moisture": 70, "light": 60, "temperature": 72, "health_score": 90, "notes": "Thriving in humid bathroom environment."},
                {"date": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"), "moisture": 55, "light": 62, "temperature": 73, "health_score": 85, "notes": "Some fronds turning slightly brown at tips."},
                {"date": (datetime.now() - timedelta(days=16)).strftime("%Y-%m-%d"), "moisture": 85, "light": 61, "temperature": 74, "health_score": 88, "notes": "Misted and watered, looking lush again."},
                {"date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"), "moisture": 65, "light": 63, "temperature": 72, "health_score": 89, "notes": "New fronds developing, good growth."},
                {"date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), "moisture": 50, "light": 62, "temperature": 71, "health_score": 83, "notes": "Needs watering soon, slight drooping."}
            ]
        }
    }

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Define plant recommendation system with common problems and solutions
plant_issues = {
    "low_moisture": {
        "symptoms": ["drooping leaves", "dry soil", "brown leaf tips", "wilting"],
        "diagnosis": "Your plant is under-watered.",
        "solution": "Water thoroughly until water runs through drainage holes. For most plants, water when the top inch of soil feels dry."
    },
    "over_watering": {
        "symptoms": ["yellowing leaves", "soft stems", "moldy soil", "fungus gnats"],
        "diagnosis": "Your plant is being over-watered.",
        "solution": "Reduce watering frequency. Let the soil dry out more between waterings. Check for proper drainage."
    },
    "low_light": {
        "symptoms": ["leggy growth", "small leaves", "slow growth", "pale leaves"],
        "diagnosis": "Your plant is not getting enough light.",
        "solution": "Move to a brighter location. Consider a grow light if natural light is limited."
    },
    "too_much_light": {
        "symptoms": ["scorched leaves", "bleached spots", "leaf drop", "curling leaves"],
        "diagnosis": "Your plant is getting too much direct light.",
        "solution": "Move away from direct sunlight or provide filtered light through a sheer curtain."
    },
    "nutrient_deficiency": {
        "symptoms": ["yellowing between leaf veins", "stunted growth", "unusual leaf color"],
        "diagnosis": "Your plant may have a nutrient deficiency.",
        "solution": "Consider fertilizing with a balanced houseplant fertilizer during growing season."
    },
    "pest_infestation": {
        "symptoms": ["tiny bugs", "webbing", "sticky residue", "holes in leaves"],
        "diagnosis": "Your plant appears to have a pest problem.",
        "solution": "Inspect thoroughly and treat with appropriate measures like neem oil, insecticidal soap, or wiping leaves with diluted alcohol."
    }
}

# Application header
st.title("🌱 Plant Healthcare Monitor")
st.markdown("Track your plants' health and get personalized care recommendations")

# Create tabs for different sections of the app
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Plant Details", "Plant Assistant","Plant ChatBot"])

# Dashboard tab
with tab1:
    st.header("Plant Health Overview")
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate days since last watered for each plant
    plants_needing_water = [name for name, data in st.session_state.plants.items() 
                           if (datetime.now() - data["last_watered"]).days >= data["water_frequency"]]
    
    # Calculate average health score across all plants (using most recent entry)
    avg_health = sum(data["health_history"][-1]["health_score"] for data in st.session_state.plants.values()) / len(st.session_state.plants)
    
    with col1:
        st.metric("Total Plants", len(st.session_state.plants))
    with col2:
        st.metric("Need Watering", len(plants_needing_water))
    with col3:
        st.metric("Average Health", f"{avg_health:.1f}%")
    with col4:
        excellent_plants = sum(1 for data in st.session_state.plants.values() 
                               if data["health_history"][-1]["health_score"] >= 85)
        st.metric("Excellent Health", f"{excellent_plants}/{len(st.session_state.plants)}")
    
    # Create a DataFrame for the chart
    chart_data = []
    for plant_name, plant_data in st.session_state.plants.items():
        for entry in plant_data["health_history"]:
            chart_data.append({
                "Plant": plant_name,
                "Date": entry["date"],
                "Health Score": entry["health_score"]
            })
    
    chart_df = pd.DataFrame(chart_data)
    
    # Create health trend chart
    st.subheader("Health Score Trends")
    chart = alt.Chart(chart_df).mark_line(point=True).encode(
        x='Date:T',
        y=alt.Y('Health Score:Q', scale=alt.Scale(domain=[50, 100])),
        color='Plant:N',
        tooltip=['Plant', 'Date', 'Health Score']
    ).properties(
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
    
    # Plants needing attention
    st.subheader("Plants Needing Attention")
    if plants_needing_water:
        for plant in plants_needing_water:
            days_since = (datetime.now() - st.session_state.plants[plant]["last_watered"]).days
            st.warning(f"🚿 {plant} needs watering! Last watered {days_since} days ago.")
    else:
        st.success("All plants are currently well watered! 🌱")

# Plant details tab
with tab2:
    st.header("Plant Details")
    
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
            
            # Add water button
            if st.button("🚿 Log Watering"):
                st.session_state.plants[selected_plant]["last_watered"] = datetime.now()
                st.success(f"{selected_plant} watered successfully!")
                st.rerun()
        
        with col2:
            # Display history
            st.subheader("Health History")
            history_df = pd.DataFrame(plant_data["health_history"])
            
            # Create multiple line charts for each metric
            # Fixed approach: Create separate charts for each metric instead of using transform_fold
            moisture_chart = alt.Chart(history_df).mark_line(point=True, color='blue').encode(
                x='date:T',
                y=alt.Y('moisture:Q', title='Moisture (%)'),
                tooltip=['date', 'moisture', 'notes']
            ).properties(height=100)
            
            light_chart = alt.Chart(history_df).mark_line(point=True, color='orange').encode(
                x='date:T',
                y=alt.Y('light:Q', title='Light (%)'),
                tooltip=['date', 'light', 'notes']
            ).properties(height=100)
            
            temperature_chart = alt.Chart(history_df).mark_line(point=True, color='red').encode(
                x='date:T',
                y=alt.Y('temperature:Q', title='Temperature (°F)'),
                tooltip=['date', 'temperature', 'notes']
            ).properties(height=100)
            
            health_chart = alt.Chart(history_df).mark_line(point=True, color='green').encode(
                x='date:T',
                y=alt.Y('health_score:Q', title='Health Score (%)'),
                tooltip=['date', 'health_score', 'notes']
            ).properties(height=100)
            
            # Combine charts vertically
            metrics_chart = alt.vconcat(moisture_chart, light_chart, temperature_chart, health_chart)
            
            # Display the combined chart
            st.altair_chart(metrics_chart, use_container_width=True)
            
            # Display history table
            history_df = history_df.sort_values('date', ascending=False)
            st.dataframe(history_df, use_container_width=True)
            
            # Add new entry form
            st.subheader("Add Health Check Entry")
            with st.form("new_entry_form"):
                col1, col2 = st.columns(2)
                with col1:
                    moisture = st.slider("Soil Moisture (%)", 0, 100, 70)
                    light = st.slider("Light Level (%)", 0, 100, 75)
                with col2:
                    temperature = st.slider("Temperature (°F)", 60, 85, 72)
                    health_score = st.slider("Overall Health Score (%)", 0, 100, 80)
                
                notes = st.text_area("Notes", "")
                
                submitted = st.form_submit_button("Save Health Check")
                if submitted:
                    new_entry = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "moisture": moisture,
                        "light": light,
                        "temperature": temperature,
                        "health_score": health_score,
                        "notes": notes
                    }
                    st.session_state.plants[selected_plant]["health_history"].append(new_entry)
                    st.success("Health check saved successfully!")
                    st.rerun()

# Plant assistant chatbot tab
with tab3:
    
    st.header("Plant Care Assistant")
    st.write("Chat with our plant care assistant about your plants' health issues and get personalized recommendations.")
    
    # # Display chat history
    # for message in st.session_state.chat_history:
    #     if message["role"] == "user":
    #         st.chat_message("user").write(message["content"])
    #     else:
    #         st.chat_message("assistant").write(message["content"])
    
    # # Chat input
    # user_input = st.chat_input("Ask about plant care...")
    # if user_input:
    #     # Add user message to chat history
    #     st.session_state.chat_history.append({"role": "user", "content": user_input})
    #     st.chat_message("user").write(user_input)
        
    #     # Process user input and generate response
    #     response = ""
        
    #     # Check if user is asking about a specific plant
    #     plant_mentioned = None
    #     for plant_name in st.session_state.plants.keys():
    #         if plant_name.lower() in user_input.lower():
    #             plant_mentioned = plant_name
    #             break
        
    #     # Check if user is describing symptoms
    #     identified_issue = None
    #     for issue, data in plant_issues.items():
    #         for symptom in data["symptoms"]:
    #             if symptom.lower() in user_input.lower():
    #                 identified_issue = issue
    #                 break
    #         if identified_issue:
    #             break
        
    #     # Generate response based on input analysis
    #     if "water" in user_input.lower() or "watering" in user_input.lower():
    #         if plant_mentioned:
    #             plant_data = st.session_state.plants[plant_mentioned]
    #             days_since = (datetime.now() - plant_data["last_watered"]).days
    #             days_until = plant_data["water_frequency"] - days_since
                
    #             if days_until <= 0:
    #                 response = f"Your {plant_mentioned} needs watering now! It was last watered {days_since} days ago, and its recommended watering frequency is every {plant_data['water_frequency']} days."
    #             else:
    #                 response = f"Your {plant_mentioned} was last watered {days_since} days ago. It should be watered again in about {days_until} days. {plant_mentioned} typically needs water every {plant_data['water_frequency']} days."
    #         else:
    #             response = "Here are some general watering tips:\n\n- Most houseplants prefer to dry out slightly between waterings\n- Water thoroughly until water runs through drainage holes\n- Adjust watering frequency based on season (less in winter, more in summer)\n- Which plant are you specifically asking about?"
        
    #     elif "light" in user_input.lower():
    #         if plant_mentioned:
    #             plant_data = st.session_state.plants[plant_mentioned]
    #             response = f"Your {plant_mentioned} needs {plant_data['light_needs']}. Based on the recent light levels recorded, it appears to be getting adequate light in its current location ({plant_data['location']})."
    #         else:
    #             response = "Different plants have different light requirements. Some plants like direct sunlight while others prefer indirect light or shade. Which plant are you asking about?"
        
    #     elif identified_issue:
    #         issue_data = plant_issues[identified_issue]
    #         if plant_mentioned:
    #             response = f"For your {plant_mentioned} showing symptoms like {', '.join(issue_data['symptoms'][:2])}: {issue_data['diagnosis']} {issue_data['solution']}"
    #         else:
    #             response = f"It sounds like you're describing {', '.join(issue_data['symptoms'][:2])}. {issue_data['diagnosis']} {issue_data['solution']}"
        
    #     elif "health" in user_input.lower() or "status" in user_input.lower():
    #         if plant_mentioned:
    #             plant_data = st.session_state.plants[plant_mentioned]
    #             latest = plant_data["health_history"][-1]
    #             response = f"Your {plant_mentioned} is currently at {latest['health_score']}% health. Latest notes: {latest['notes']} It's located in the {plant_data['location']}."
    #         else:
    #             unhealthy_plants = [name for name, data in st.session_state.plants.items() 
    #                               if data["health_history"][-1]["health_score"] < 80]
    #             if unhealthy_plants:
    #                 response = f"Plants that might need attention: {', '.join(unhealthy_plants)}. Would you like specific information about any of these?"
    #             else:
    #                 response = "All your plants appear to be in good health right now! Their health scores are all above 80%."
        
    #     elif any(greeting in user_input.lower() for greeting in ["hello", "hi", "hey", "greetings"]):
    #         response = "Hello! I'm your plant care assistant. How can I help you with your plants today? You can ask about watering schedules, light requirements, or specific plant health issues."
        
    #     elif "add" in user_input.lower() and "plant" in user_input.lower():
    #         response = "To add a new plant, please go to the Plant Details tab and use the Add New Plant form. Make sure to include information like plant type, location, and watering frequency."
        
    #     elif any(plant_type.lower() in user_input.lower() for plant_type in ["monstera", "peace lily", "snake plant", "fiddle leaf", "fern"]):
    #         # User is asking about a specific plant type
    #         for plant_name, plant_data in st.session_state.plants.items():
    #             if plant_data["type"].lower() in user_input.lower() or plant_name.lower() in user_input.lower():
    #                 response = f"Your {plant_name} ({plant_data['type']}) is located in the {plant_data['location']}. It needs {plant_data['light_needs']} and should be watered every {plant_data['water_frequency']} days. Current health score: {plant_data['health_history'][-1]['health_score']}%."
    #                 break
        
    #     else:
    #         # Generic response for unrecognized queries
    #         response = "I'm here to help with your plant care questions. You can ask about:\n\n- Watering schedules for specific plants\n- Light requirements\n- Diagnosing common plant problems\n- Health status of your plants\n\nWhat would you like to know about your plants?"
        
    #     # Add assistant response to chat history
    #     st.session_state.chat_history.append({"role": "assistant", "content": response})
    #     st.chat_message("assistant").write(response)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'plants' not in st.session_state:
        # Sample plant data with more detailed care information
        st.session_state.plants = {
            "Fiddle Leaf Fig": {
                "type": "Ficus lyrata",
                "location": "Living Room",
                "light_needs": "bright indirect light",
                "water_frequency": 7,
                "last_watered": datetime.now() - timedelta(days=5),
                "humidity_needs": "high",
                "fertilizing": "monthly during growing season",
                "common_issues": ["brown spots", "leaf drop", "drooping"],
                "health_history": [
                    {"date": datetime.now() - timedelta(days=30), "health_score": 85, "notes": "New leaf growing."},
                    {"date": datetime.now() - timedelta(days=15), "health_score": 82, "notes": "Some leaf tips brown."},
                    {"date": datetime.now(), "health_score": 88, "notes": "Recovering well after repotting."}
                ]
            },
            "Monstera": {
                "type": "Monstera deliciosa",
                "location": "Office",
                "light_needs": "medium to bright indirect light",
                "water_frequency": 10,
                "last_watered": datetime.now() - timedelta(days=3),
                "humidity_needs": "medium to high",
                "fertilizing": "monthly spring through fall",
                "common_issues": ["yellow leaves", "brown edges", "lack of fenestration"],
                "health_history": [
                    {"date": datetime.now() - timedelta(days=30), "health_score": 90, "notes": "Vibrant new growth."},
                    {"date": datetime.now() - timedelta(days=15), "health_score": 92, "notes": "New fenestrated leaf forming."},
                    {"date": datetime.now(), "health_score": 95, "notes": "Excellent condition."}
                ]
            },
            "Snake Plant": {
                "type": "Sansevieria trifasciata",
                "location": "Bedroom",
                "light_needs": "low to bright indirect light",
                "water_frequency": 21,
                "last_watered": datetime.now() - timedelta(days=10),
                "humidity_needs": "low",
                "fertilizing": "quarterly during growing season",
                "common_issues": ["overwatering", "root rot", "pest infestations"],
                "health_history": [
                    {"date": datetime.now() - timedelta(days=30), "health_score": 95, "notes": "Healthy overall."},
                    {"date": datetime.now() - timedelta(days=15), "health_score": 93, "notes": "Minor leaf damage at tip."},
                    {"date": datetime.now(), "health_score": 94, "notes": "Stable and healthy."}
                ]
            }
        }

    # Expanded plant issues database
    plant_issues = {
        "leaf yellowing": {
            "symptoms": ["yellow leaves", "discoloration", "fading color"],
            "diagnosis": "Yellowing leaves often indicate overwatering, nutrient deficiency, or insufficient light.",
            "solution": "Check soil moisture and allow to dry if wet. Consider a balanced fertilizer if it's been over 3 months since last feeding. Ensure the plant receives adequate light for its species.",
            "prevention": "Water only when the top 1-2 inches of soil is dry, use well-draining soil, and ensure proper light conditions."
        },
        "brown leaf tips": {
            "symptoms": ["brown tips", "crispy edges", "leaf margin browning"],
            "diagnosis": "Brown leaf tips usually suggest low humidity, mineral buildup from tap water, or fertilizer burn.",
            "solution": "Increase humidity with a humidifier or pebble tray. Consider using filtered or distilled water. Flush the soil thoroughly if fertilizer buildup is suspected.",
            "prevention": "Maintain appropriate humidity levels, avoid tap water with high mineral content, and follow fertilizer instructions carefully."
        },
        "root rot": {
            "symptoms": ["mushy stems", "foul smell", "wilting despite wet soil", "blackened roots"],
            "diagnosis": "Root rot is caused by overwatering leading to fungal or bacterial growth in the roots.",
            "solution": "Remove the plant from its pot, trim away rotted roots, treat with hydrogen peroxide solution, and repot in fresh, well-draining soil.",
            "prevention": "Use pots with drainage holes, well-draining soil mix, and only water when the top layer of soil is dry."
        },
        "pest infestation": {
            "symptoms": ["tiny bugs", "webbing", "sticky residue", "speckled leaves", "leaf distortion"],
            "diagnosis": "Common houseplant pests include spider mites, mealybugs, scale, and fungus gnats.",
            "solution": "Isolate affected plants, wash leaves with insecticidal soap, apply neem oil, and maintain treatment for several weeks to break the pest lifecycle.",
            "prevention": "Regularly inspect plants, avoid overwatering, increase air circulation, and quarantine new plants before introducing them to your collection."
        },
        "leggy growth": {
            "symptoms": ["stretched stems", "sparse foliage", "leaning toward light", "elongated internodes"],
            "diagnosis": "Leggy growth indicates the plant is stretching to find adequate light.",
            "solution": "Move the plant to a brighter location, rotate it regularly, and consider pruning to encourage bushier growth.",
            "prevention": "Ensure proper light conditions for each plant species and rotate plants regularly to promote even growth."
        },
        "leaf drop": {
            "symptoms": ["falling leaves", "sudden leaf loss", "thinning foliage"],
            "diagnosis": "Leaf drop can be caused by environmental shock, dramatic temperature changes, overwatering, or seasonal changes.",
            "solution": "Stabilize environmental conditions, ensure proper watering, and give the plant time to adjust. Remove fallen leaves to prevent disease.",
            "prevention": "Avoid placing plants near drafts, heating/cooling vents, and maintain consistent care routines."
        },
        "no growth": {
            "symptoms": ["static size", "no new leaves", "dormant appearance"],
            "diagnosis": "Lack of growth can indicate dormancy, root binding, nutrient deficiency, or improper light conditions.",
            "solution": "Check if the plant is root-bound and needs repotting. Ensure adequate light and consider a balanced fertilizer to boost growth.",
            "prevention": "Repot plants when necessary, provide appropriate light and nutrition, and recognize seasonal growth patterns."
        }
    }

    # Plant care recommendations database - expanded to include more plants
    plant_care_database = {
        "fiddle leaf fig": {
            "scientific_name": "Ficus lyrata",
            "light": "Bright indirect light, can tolerate a few hours of direct morning sun",
            "water": "Allow top 2 inches of soil to dry between waterings; typically every 7-10 days",
            "humidity": "Prefers 40-60% humidity; mist leaves regularly in dry conditions",
            "soil": "Well-draining potting mix with extra perlite for aeration",
            "fertilizer": "Balanced liquid fertilizer monthly during spring and summer",
            "tips": "Rotate regularly for even growth; sensitive to relocation; clean leaves monthly to remove dust",
            "common_issues": "Brown spots (overwatering), leaf drop (environmental stress), bacterial leaf spot"
        },
        "monstera": {
            "scientific_name": "Monstera deliciosa",
            "light": "Medium to bright indirect light; avoid direct sun",
            "water": "Allow top 2-3 inches to dry out between waterings; about every 1-2 weeks",
            "humidity": "Thrives in humidity 60%+; benefits from regular misting",
            "soil": "Rich, well-draining aroid mix with orchid bark, perlite, and charcoal",
            "fertilizer": "Balanced fertilizer monthly during growing season (spring-fall)",
            "tips": "Provide support for climbing; fenestration (leaf holes) develops with maturity and good light",
            "common_issues": "Yellow leaves (overwatering), brown edges (low humidity), lack of fenestration (insufficient light)"
        },
        "snake plant": {
            "scientific_name": "Sansevieria trifasciata",
            "light": "Adaptable to low, medium, or bright indirect light",
            "water": "Allow to dry completely between waterings; typically every 3-4 weeks",
            "humidity": "Tolerates dry air; no special humidity needs",
            "soil": "Well-draining cactus or succulent mix",
            "fertilizer": "Light feeding 2-3 times per year with balanced fertilizer",
            "tips": "Perfect for beginners; excellent air purifier; can be propagated by leaf cuttings",
            "common_issues": "Overwatering leading to root rot, brown spots on leaves, pest infestations"
        },
        "pothos": {
            "scientific_name": "Epipremnum aureum",
            "light": "Adaptable; thrives in medium to bright indirect light; tolerates low light",
            "water": "Allow top 1-2 inches of soil to dry; generally every 7-10 days",
            "humidity": "Adaptable to normal household humidity",
            "soil": "Standard well-draining potting soil",
            "fertilizer": "Balanced liquid fertilizer every 2-3 months during growing season",
            "tips": "Excellent trailing plant; easy to propagate in water; trim regularly to encourage fullness",
            "common_issues": "Yellow leaves (overwatering), brown tips (low humidity), leggy growth (insufficient light)"
        },
        "peace lily": {
            "scientific_name": "Spathiphyllum",
            "light": "Low to medium indirect light; no direct sunlight",
            "water": "Keep soil consistently moist but not soggy; water when leaves begin to droop",
            "humidity": "Prefers high humidity; mist regularly or use a humidifier",
            "soil": "Rich, well-draining potting mix with added peat moss",
            "fertilizer": "Diluted balanced fertilizer every 6-8 weeks during growing season",
            "tips": "Dramatic when thirsty but recovers quickly after watering; flowers best with more light",
            "common_issues": "Brown leaf tips (low humidity/tap water), yellow leaves (overwatering), lack of flowers (insufficient light)"
        },
        "zz plant": {
            "scientific_name": "Zamioculcas zamiifolia",
            "light": "Low to bright indirect light; very adaptable",
            "water": "Allow to dry completely between waterings; approximately every 2-3 weeks",
            "humidity": "Tolerates dry air; no special humidity requirements",
            "soil": "Well-draining potting mix with added perlite",
            "fertilizer": "Light feeding 2-3 times per year with balanced fertilizer",
            "tips": "Extremely drought-tolerant; shiny leaves indicate health; slow-growing but very low-maintenance",
            "common_issues": "Yellow leaves (overwatering), stems falling over (insufficient light), rarely has pest problems"
        },
        "orchid": {
            "scientific_name": "Phalaenopsis spp. (most common houseplant variety)",
            "light": "Bright, indirect light; east or west-facing window ideal",
            "water": "Soak roots for 15 minutes once a week, then drain completely; allow to dry between waterings",
            "humidity": "Requires 50-70% humidity; use humidifier or humidity tray",
            "soil": "Specialized orchid bark mix with charcoal and sphagnum moss; never use regular potting soil",
            "fertilizer": "Specialized orchid fertilizer at quarter-strength every other watering when in active growth",
            "tips": "Flowers last months; reblooms from old flower spikes or new ones; clear pots help monitor root health",
            "common_issues": "Root rot (overwatering), bud blast (environmental change), yellow leaves (natural aging or overwatering)"
        },
        "aloe vera": {
            "scientific_name": "Aloe barbadensis miller",
            "light": "Bright indirect to direct light; at least 6 hours of sunlight daily",
            "water": "Allow to dry completely between waterings; approximately every 3 weeks",
            "humidity": "Prefers dry conditions; no special humidity requirements",
            "soil": "Cactus/succulent mix with added sand or perlite for drainage",
            "fertilizer": "Cactus fertilizer at half-strength 1-2 times during growing season",
            "tips": "Medicinal properties for burns and skin irritations; produces offsets ('pups') for propagation",
            "common_issues": "Soft, mushy leaves (overwatering), brown, dry leaves (underwatering), stretching (insufficient light)"
        },
        "spider plant": {
            "scientific_name": "Chlorophytum comosum",
            "light": "Bright indirect light; avoid direct sun which can scorch leaves",
            "water": "Keep soil lightly moist; water when top inch is dry; sensitive to fluoride in tap water",
            "humidity": "Average household humidity is sufficient",
            "soil": "Well-draining potting mix",
            "fertilizer": "Balanced houseplant fertilizer monthly during growing season",
            "tips": "Produces 'spiderettes' that can be propagated easily; pet-safe; excellent air purifier",
            "common_issues": "Brown tips (fluoride/chlorine in water), pale leaves (too much sun), lack of babies (insufficient light)"
        },
        "rubber plant": {
            "scientific_name": "Ficus elastica",
            "light": "Medium to bright indirect light; can tolerate some morning sun",
            "water": "Allow top 2 inches to dry out between waterings; about every 7-10 days",
            "humidity": "Average household humidity; benefits from occasional misting",
            "soil": "Well-draining potting mix with added perlite",
            "fertilizer": "Balanced liquid fertilizer monthly during growing season",
            "tips": "Wipe leaves regularly to keep them dust-free and shiny; produces sap that can irritate skin",
            "common_issues": "Leaf drop (temperature fluctuations), yellow leaves (overwatering), brown spots (cold drafts)"
        }
    }

    # Seasonal care tips
    seasonal_care_tips = {
        "spring": [
            "Gradually increase watering frequency as growth resumes",
            "Begin fertilizing most houseplants as new growth appears",
            "Check for new pests that may have emerged from winter dormancy",
            "Repot plants that have become root-bound or need fresh soil",
            "Prune away any dead or damaged growth from winter"
        ],
        "summer": [
            "Increase watering frequency during hot weather",
            "Move sensitive plants away from air conditioning vents",
            "Provide extra humidity through misting or humidity trays",
            "Monitor for increased pest activity in warmer temperatures",
            "Protect plants from intense afternoon sun which can scorch leaves"
        ],
        "fall": [
            "Gradually reduce watering as growth slows down",
            "Stop fertilizing most plants as they prepare for dormancy",
            "Bring outdoor tropical plants inside before temperatures drop below 50°F/10°C",
            "Clean leaves thoroughly before bringing plants indoors",
            "Check plants carefully for pests before bringing them indoors"
        ],
        "winter": [
            "Reduce watering frequency significantly for most plants",
            "Move plants away from cold drafts and heating vents",
            "Provide supplemental lighting if natural light is limited",
            "Monitor humidity levels and supplement with humidifiers if needed",
            "Hold off on repotting or heavy pruning until spring"
        ]
    }

    # Helper function to get current season
    def get_current_season():
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"

    # Main app
    # st.set_page_config(page_title="Plant Care Chatbot", page_icon="🌱")

    # st.header("🌿 Plant Care Assistant")
    # st.write("Chat with our plant care assistant about your plants' health issues and get personalized recommendations.")

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

    # Chat input
    user_input = st.chat_input("Ask about plant care...")
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # Process user input and generate response
        response = ""
        
        # Check if user is asking about a specific plant
        plant_mentioned = None
        for plant_name in st.session_state.plants.keys():
            if plant_name.lower() in user_input.lower():
                plant_mentioned = plant_name
                break
        
        # Check for plant types in the broader database
        plant_type_mentioned = None
        for plant_type in plant_care_database.keys():
            if plant_type.lower() in user_input.lower():
                plant_type_mentioned = plant_type
                break
        
        # Check if user is describing symptoms
        identified_issue = None
        for issue, data in plant_issues.items():
            for symptom in data["symptoms"]:
                if symptom.lower() in user_input.lower():
                    identified_issue = issue
                    break
            if identified_issue:
                break
        
        # Generate response based on input analysis
        if "water" in user_input.lower() or "watering" in user_input.lower():
            if plant_mentioned:
                plant_data = st.session_state.plants[plant_mentioned]
                days_since = (datetime.now() - plant_data["last_watered"]).days
                days_until = plant_data["water_frequency"] - days_since
                
                if days_until <= 0:
                    response = f"Your {plant_mentioned} needs watering now! It was last watered {days_since} days ago, and its recommended watering frequency is every {plant_data['water_frequency']} days."
                else:
                    response = f"Your {plant_mentioned} was last watered {days_since} days ago. It should be watered again in about {days_until} days. {plant_mentioned} typically needs water every {plant_data['water_frequency']} days."
                    
                # Add seasonal watering tip
                current_season = get_current_season()
                if current_season == "winter":
                    response += "\n\nWinter tip: Remember to reduce watering frequency in winter as plants grow more slowly."
                elif current_season == "summer":
                    response += "\n\nSummer tip: Check soil moisture more frequently during hot weather as plants may need more water."
                    
            elif plant_type_mentioned:
                plant_info = plant_care_database[plant_type_mentioned]
                response = f"Watering guide for {plant_type_mentioned} ({plant_info['scientific_name']}):\n\n{plant_info['water']}"
                
                # Add an extra tip
                response += f"\n\nTip: {random.choice(seasonal_care_tips[get_current_season()])}"
                
            else:
                response = "Here are some general watering tips:\n\n- Most houseplants prefer to dry out slightly between waterings\n- Water thoroughly until water runs through drainage holes\n- Adjust watering frequency based on season (less in winter, more in summer)\n- Consider the specific needs of each plant species\n- Which plant are you specifically asking about?"
        
        elif "light" in user_input.lower():
            if plant_mentioned:
                plant_data = st.session_state.plants[plant_mentioned]
                response = f"Your {plant_mentioned} needs {plant_data['light_needs']}. Based on the recent light levels recorded, it appears to be getting adequate light in its current location ({plant_data['location']})."
            elif plant_type_mentioned:
                plant_info = plant_care_database[plant_type_mentioned]
                response = f"Light requirements for {plant_type_mentioned} ({plant_info['scientific_name']}):\n\n{plant_info['light']}"
            else:
                response = "Different plants have different light requirements:\n\n- Low light plants (Snake Plant, ZZ Plant, Pothos): Can survive in darker corners\n- Medium light plants (Peace Lily, Philodendron): Thrive in bright indirect light\n- High light plants (Succulents, Fiddle Leaf Fig): Need several hours of bright light\n\nWhich plant are you asking about?"
        
        elif "humidity" in user_input.lower():
            if plant_mentioned:
                plant_data = st.session_state.plants[plant_mentioned]
                response = f"Your {plant_mentioned} prefers {plant_data['humidity_needs']} humidity. "
                if plant_data['humidity_needs'] == "high":
                    response += "Consider using a humidifier, grouping it with other plants, or placing it on a pebble tray with water."
                elif plant_data['humidity_needs'] == "low":
                    response += "It's well-suited for average indoor conditions and doesn't require additional humidity."
            elif plant_type_mentioned:
                plant_info = plant_care_database[plant_type_mentioned]
                response = f"Humidity needs for {plant_type_mentioned} ({plant_info['scientific_name']}):\n\n{plant_info['humidity']}"
            else:
                response = "Humidity needs vary by plant type:\n\n- Tropical plants like Calathea, Monstera, and Ferns prefer high humidity (60%+)\n- Most common houseplants do well in average humidity (40-60%)\n- Succulents, Snake Plants, and ZZ Plants tolerate dry air\n\nWhich plant's humidity needs are you curious about?"
        
        elif "fertiliz" in user_input.lower() or "feed" in user_input.lower():
            if plant_mentioned:
                plant_data = st.session_state.plants[plant_mentioned]
                response = f"Fertilizing recommendation for your {plant_mentioned}: {plant_data['fertilizing']}. "
                current_season = get_current_season()
                if current_season in ["spring", "summer"]:
                    response += "Now is a good time to fertilize as we're in the growing season."
                else:
                    response += "Consider reducing or pausing fertilization during fall/winter months."
            elif plant_type_mentioned:
                plant_info = plant_care_database[plant_type_mentioned]
                response = f"Fertilizing guide for {plant_type_mentioned} ({plant_info['scientific_name']}):\n\n{plant_info['fertilizer']}"
            else:
                response = "General fertilizing tips:\n\n- Most houseplants benefit from fertilizing during the growing season (spring through fall)\n- Use a balanced houseplant fertilizer (NPK numbers roughly equal)\n- Always follow package directions and consider using at half-strength\n- It's better to under-fertilize than over-fertilize\n- Which plant are you asking about fertilizing?"
        
        elif identified_issue:
            issue_data = plant_issues[identified_issue]
            if plant_mentioned:
                response = f"For your {plant_mentioned} showing symptoms like {', '.join(issue_data['symptoms'][:2])}: \n\n{issue_data['diagnosis']}\n\n{issue_data['solution']}\n\nPrevention: {issue_data['prevention']}"
            elif plant_type_mentioned:
                plant_info = plant_care_database[plant_type_mentioned]
                response = f"I notice you're describing {', '.join(issue_data['symptoms'][:2])} for a {plant_type_mentioned}.\n\n{issue_data['diagnosis']}\n\n{issue_data['solution']}\n\nCommon issues for {plant_type_mentioned}: {plant_info['common_issues']}"
            else:
                response = f"It sounds like you're describing {', '.join(issue_data['symptoms'][:2])}.\n\n{issue_data['diagnosis']}\n\n{issue_data['solution']}\n\nPrevention: {issue_data['prevention']}"
        
        elif "health" in user_input.lower() or "status" in user_input.lower():
            if plant_mentioned:
                plant_data = st.session_state.plants[plant_mentioned]
                latest = plant_data["health_history"][-1]
                response = f"Your {plant_mentioned} is currently at {latest['health_score']}% health. Latest notes: {latest['notes']} It's located in the {plant_data['location']}."
                
                # Add specific recommendations based on health score
                if latest['health_score'] < 70:
                    response += f"\n\nRecommendations to improve health:\n- Check for signs of {', '.join(plant_data['common_issues'][:2])}\n- Review watering schedule and light conditions\n- Consider inspecting roots for any issues"
            else:
                unhealthy_plants = [name for name, data in st.session_state.plants.items() 
                                if data["health_history"][-1]["health_score"] < 80]
                if unhealthy_plants:
                    response = f"Plants that might need attention: {', '.join(unhealthy_plants)}. Would you like specific information about any of these?"
                else:
                    response = "All your plants appear to be in good health right now! Their health scores are all above 80%."
        
        elif "season" in user_input.lower() or "seasonal" in user_input.lower():
            current_season = get_current_season()
            response = f"Current season: {current_season.capitalize()}\n\nSeasonal plant care tips:\n"
            for tip in seasonal_care_tips[current_season]:
                response += f"- {tip}\n"
        
        elif "soil" in user_input.lower() or "potting" in user_input.lower() or "repot" in user_input.lower():
            if plant_mentioned:
                response = f"For your {plant_mentioned}, use a well-draining potting mix. Consider repotting every 1-2 years or when it becomes root-bound."
            elif plant_type_mentioned:
                plant_info = plant_care_database[plant_type_mentioned]
                response = f"Soil recommendations for {plant_type_mentioned} ({plant_info['scientific_name']}):\n\n{plant_info['soil']}"
            else:
                response = "General soil and potting tips:\n\n- Most houseplants prefer well-draining soil\n- Consider adding perlite or pumice to improve drainage\n- Repot when plants become root-bound (roots circling the pot)\n- The best time to repot is usually spring or early summer\n- Which plant are you asking about?"
        
        elif any(info_word in user_input.lower() for info_word in ["care", "guide", "how to", "tips", "advice"]) and plant_type_mentioned:
            # User is asking for general care info about a specific plant type
            plant_info = plant_care_database[plant_type_mentioned]
            response = f"Complete care guide for {plant_type_mentioned} ({plant_info['scientific_name']}):\n\n"
            response += f"🌞 Light: {plant_info['light']}\n\n"
            response += f"💧 Water: {plant_info['water']}\n\n"
            response += f"💨 Humidity: {plant_info['humidity']}\n\n"
            response += f"🌱 Soil: {plant_info['soil']}\n\n"
            response += f"🌿 Fertilizer: {plant_info['fertilizer']}\n\n"
            response += f"💡 Tips: {plant_info['tips']}\n\n"
            response += f"⚠️ Common Issues: {plant_info['common_issues']}"
        
        elif any(greeting in user_input.lower() for greeting in ["hello", "hi", "hey", "greetings"]):
            response = "Hello! I'm your plant care assistant. How can I help you with your plants today? You can ask about:\n\n- Watering schedules\n- Light requirements\n- Humidity needs\n- Fertilizing guidance\n- Seasonal care tips\n- Specific plant issues\n- Care guides for different plant types"
        
        elif "add" in user_input.lower() and "plant" in user_input.lower():
            response = "To add a new plant to your collection, please go to the Plant Details tab and use the Add New Plant form. Make sure to include information like plant type, location, and watering frequency."
        
        elif any(plant_type in user_input.lower() for plant_type in plant_care_database.keys()):
            # User is asking about a specific plant type from database
            for plant_type in plant_care_database.keys():
                if plant_type.lower() in user_input.lower():
                    plant_info = plant_care_database[plant_type]
                    response = f"{plant_type.capitalize()} ({plant_info['scientific_name']}) care essentials:\n\nLight: {plant_info['light']}\nWater: {plant_info['water']}\nHumidity: {plant_info['humidity']}\n\nTip: {plant_info['tips']}\n\nAsk for complete care guide for more details!"
                    break
        
        else:
            # Generic response for unrecognized queries
            response = "I'm here to help with your plant care questions. You can ask about:\n\n- Watering schedules for specific plants\n- Light requirements\n- Humidity and temperature needs\n- Diagnosing common plant problems\n- Seasonal care recommendations\n- Soil and fertilizer advice\n- Specific plant care guides\n\nWhat would you like to know about your plants?"
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

    # Sidebar for app navigation
    with st.sidebar:
        st.title("Plant Care Helper")
        st.write("This chatbot provides personalized plant care advice and recommendations.")
        
        st.subheader("Available Features")
        st.write("- Chat with the plant assistant")
        st.write("- Get care guides for common houseplants")
        st.write("- Track watering schedules")
        st.write("- Identify plant issues")
        st.write("- Receive seasonal care tips")
        
        # Simple plant database display
        st.subheader("Your Plant Collection")
        for plant_name, plant_data in st.session_state.plants.items():
            st.write(f"**{plant_name}** ({plant_data['type']})")
            health = plant_data["health_history"][-1]["health_score"]
            st.progress(health/100)
        
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
                                #  f"**Issue:** {response.issue}\n\n" \
                                #  f"**Care Tips:** {response.care_tips}\n\n" \
                                #  f"**Solution:** {response.solution}\n"
        else:
            formatted_response = "Sorry, I couldn't process your request. Try again!"

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(formatted_response)

        # Store AI response
        st.session_state.messages.append({"role": "assistant", "content": formatted_response})
        