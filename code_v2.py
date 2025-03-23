import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Plant Healthcare Companion",
    page_icon="🌱",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'plant_data' not in st.session_state:
    # Create some sample plant data
    st.session_state.plant_data = {
        'Snake Plant': {
            'water_freq': 14,  # days
            'light': 'indirect',
            'humidity': 'low',
            'last_watered': datetime.now() - timedelta(days=10),
            'health_score': 85,
            'history': {
                'moisture': [random.randint(30, 70) for _ in range(30)],
                'light': [random.randint(40, 80) for _ in range(30)],
                'health': [random.randint(70, 95) for _ in range(30)]
            }
        },
        'Monstera': {
            'water_freq': 7,
            'light': 'bright indirect',
            'humidity': 'medium',
            'last_watered': datetime.now() - timedelta(days=5),
            'health_score': 92,
            'history': {
                'moisture': [random.randint(40, 80) for _ in range(30)],
                'light': [random.randint(50, 90) for _ in range(30)],
                'health': [random.randint(75, 98) for _ in range(30)]
            }
        },
        'Peace Lily': {
            'water_freq': 5,
            'light': 'low to medium',
            'humidity': 'high',
            'last_watered': datetime.now() - timedelta(days=4),
            'health_score': 78,
            'history': {
                'moisture': [random.randint(50, 90) for _ in range(30)],
                'light': [random.randint(30, 70) for _ in range(30)],
                'health': [random.randint(65, 90) for _ in range(30)]
            }
        }
    }

if 'plants_added' not in st.session_state:
    st.session_state.plants_added = list(st.session_state.plant_data.keys())

# CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #388E3C;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #E8F5E9;
    }
    .chat-message.bot {
        background-color: #F1F8E9;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .chat-message .user-avatar {
        background-color: #4CAF50;
        color: white;
    }
    .chat-message .bot-avatar {
        background-color: #8BC34A;
        color: white;
    }
    .chat-message .content {
        flex-grow: 1;
    }
    .plant-card {
        background-color: #36454F;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .health-indicator {
        height: 20px;
        border-radius: 10px;
    }
    .user-input {
        background-color: #E8F5E9;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for the chatbot
def get_bot_response(user_input, selected_plant=None):
    user_input = user_input.lower()
    
    # Check if user is asking about a specific plant
    if selected_plant:
        plant_data = st.session_state.plant_data.get(selected_plant)
        
        if "water" in user_input:
            days_since_watered = (datetime.now() - plant_data['last_watered']).days
            days_until_next = plant_data['water_freq'] - days_since_watered
            
            if days_until_next <= 0:
                return f"Your {selected_plant} needs water now! It was last watered {days_since_watered} days ago."
            else:
                return f"Your {selected_plant} was last watered {days_since_watered} days ago. You should water it in about {days_until_next} days."
                
        elif "light" in user_input:
            return f"Your {selected_plant} prefers {plant_data['light']} light. Make sure it's positioned appropriately."
            
        elif "humid" in user_input or "humidity" in user_input:
            return f"Your {selected_plant} prefers {plant_data['humidity']} humidity. Current readings show average humidity levels in the acceptable range."
            
        elif "health" in user_input or "status" in user_input:
            score = plant_data['health_score']
            if score > 90:
                return f"Your {selected_plant} is thriving! Health score: {score}/100"
            elif score > 75:
                return f"Your {selected_plant} is doing well. Health score: {score}/100"
            elif score > 60:
                return f"Your {selected_plant} needs some attention. Health score: {score}/100"
            else:
                return f"Your {selected_plant} is struggling and needs immediate care! Health score: {score}/100"
                
        elif "tip" in user_input or "advice" in user_input:
            tips = [
                f"Consider wiping the leaves of your {selected_plant} with a damp cloth to remove dust.",
                f"Rotate your {selected_plant} occasionally to ensure even growth.",
                f"Your {selected_plant} would benefit from occasional fertilizing during the growing season.",
                f"Check for pests regularly, especially on the undersides of the leaves of your {selected_plant}."
            ]
            return random.choice(tips)
    
    # General queries
    if "hello" in user_input or "hi" in user_input:
        return "Hello! I'm your plant care assistant. How can I help you with your plants today?"
        
    elif "help" in user_input:
        return "I can help you monitor your plants' health, give watering reminders, provide light and humidity recommendations, and offer general plant care tips. Just ask me about a specific plant or general plant care!"
        
    elif "add plant" in user_input:
        return "To add a new plant, use the 'Add New Plant' section in the sidebar."
        
    elif "water" in user_input:
        plants_to_water = []
        for plant, data in st.session_state.plant_data.items():
            days_since_watered = (datetime.now() - data['last_watered']).days
            if days_since_watered >= data['water_freq']:
                plants_to_water.append(plant)
                
        if plants_to_water:
            return f"These plants need water now: {', '.join(plants_to_water)}"
        else:
            return "All your plants are currently well watered. Check back tomorrow!"
            
    elif "care tips" in user_input or "advice" in user_input:
        general_tips = [
            "Most houseplants benefit from increased humidity. Consider using a humidifier or pebble tray.",
            "Yellow leaves often indicate overwatering, while brown leaves can signal underwatering.",
            "Wipe leaves regularly to remove dust and help your plants breathe better.",
            "Most houseplants prefer to dry out slightly between waterings.",
            "Rotate your plants regularly to ensure even growth and light exposure."
        ]
        return random.choice(general_tips)
        
    else:
        return "I'm not sure how to help with that. You can ask me about watering schedules, light requirements, humidity needs, plant health status, or general care tips for your plants."

def add_chat_message(role, content):
    st.session_state.chat_history.append({"role": role, "content": content})

def mark_as_watered(plant_name):
    if plant_name in st.session_state.plant_data:
        st.session_state.plant_data[plant_name]['last_watered'] = datetime.now()
        st.session_state.plant_data[plant_name]['health_score'] = min(100, st.session_state.plant_data[plant_name]['health_score'] + 5)
        
        # Add a slight increase to moisture levels in history
        current_moisture = st.session_state.plant_data[plant_name]['history']['moisture']
        new_moisture = min(100, current_moisture[-1] + random.randint(30, 50))
        st.session_state.plant_data[plant_name]['history']['moisture'].append(new_moisture)
        st.session_state.plant_data[plant_name]['history']['moisture'].pop(0)
        
        # Update health history too
        current_health = st.session_state.plant_data[plant_name]['history']['health']
        new_health = min(100, current_health[-1] + random.randint(1, 5))
        st.session_state.plant_data[plant_name]['history']['health'].append(new_health)
        st.session_state.plant_data[plant_name]['history']['health'].pop(0)
        
        return f"Marked {plant_name} as watered today!"
    return f"Plant {plant_name} not found."

def add_new_plant(name, water_freq, light, humidity):
    if name and name not in st.session_state.plant_data:
        st.session_state.plant_data[name] = {
            'water_freq': water_freq,
            'light': light,
            'humidity': humidity,
            'last_watered': datetime.now(),
            'health_score': 85,
            'history': {
                'moisture': [random.randint(50, 80) for _ in range(30)],
                'light': [random.randint(40, 70) for _ in range(30)],
                'health': [random.randint(75, 90) for _ in range(30)]
            }
        }
        st.session_state.plants_added.append(name)
        return f"Successfully added {name} to your plant collection!"
    elif name in st.session_state.plant_data:
        return f"{name} is already in your collection."
    return "Please provide a valid plant name."

# Sidebar for plant selection and adding new plants
with st.sidebar:
    st.markdown("<div class='sub-header'>Your Plants</div>", unsafe_allow_html=True)
    
    selected_plant = st.selectbox(
        "Select a plant to monitor",
        st.session_state.plants_added
    )
    
    if st.button("Mark as Watered Today"):
        response = mark_as_watered(selected_plant)
        st.success(response)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Add New Plant</div>", unsafe_allow_html=True)
    
    new_plant_name = st.text_input("Plant Name")
    water_frequency = st.slider("Watering Frequency (days)", 1, 30, 7)
    light_requirement = st.selectbox(
        "Light Requirement",
        ["Low", "Indirect", "Bright Indirect", "Direct"]
    )
    humidity_requirement = st.selectbox(
        "Humidity Requirement",
        ["Low", "Medium", "High"]
    )
    
    if st.button("Add Plant"):
        response = add_new_plant(new_plant_name, water_frequency, light_requirement.lower(), humidity_requirement.lower())
        st.success(response)

# Main content
st.markdown("<h1 class='main-header'>🌱 Plant Healthcare Companion</h1>", unsafe_allow_html=True)

# Create two columns for the dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='sub-header'>Dashboard</div>", unsafe_allow_html=True)
    
    # Get data for the selected plant
    plant_data = st.session_state.plant_data[selected_plant]
    
    # Create metrics row
    metric1, metric2, metric3 = st.columns(3)
    
    with metric1:
        days_since_watered = (datetime.now() - plant_data['last_watered']).days
        days_until_next = plant_data['water_freq'] - days_since_watered
        
        if days_until_next <= 0:
            st.error(f"WATER NOW! ({abs(days_until_next)} days overdue)")
        else:
            st.info(f"Next water in {days_until_next} days")
        
        st.metric(
            "Moisture Level", 
            f"{plant_data['history']['moisture'][-1]}%",
            f"{plant_data['history']['moisture'][-1] - plant_data['history']['moisture'][-2]}%"
        )
        
    with metric2:
        st.info(f"Light Need: {plant_data['light'].title()}")
        st.metric(
            "Light Level", 
            f"{plant_data['history']['light'][-1]}%",
            f"{plant_data['history']['light'][-1] - plant_data['history']['light'][-2]}%"
        )
        
    with metric3:
        st.info(f"Humidity Need: {plant_data['humidity'].title()}")
        st.metric(
            "Health Score", 
            f"{plant_data['health_score']}%",
            f"{plant_data['history']['health'][-1] - plant_data['history']['health'][-5]}% (5-day)"
        )
    
    # Create charts
    st.markdown("### Health Metrics Over Time")
    
    # Create a dataframe from history data
    dates = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(29, -1, -1)]
    df = pd.DataFrame({
        'Date': dates,
        'Moisture': plant_data['history']['moisture'],
        'Light': plant_data['history']['light'],
        'Health': plant_data['history']['health']
    })
    
    # Plot metrics using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Moisture'], mode='lines', name='Moisture', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Light'], mode='lines', name='Light', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Health'], mode='lines', name='Health', line=dict(color='green')))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title=None,
        yaxis_title="Percentage",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Care recommendations
    st.markdown("### Care Recommendations")
    
    rec1, rec2 = st.columns(2)
    
    with rec1:
        st.markdown(f"<div class='plant-card'><strong>Watering</strong><br>{selected_plant} should be watered every {plant_data['water_freq']} days. Use room temperature water and ensure proper drainage.</div>", unsafe_allow_html=True)
    
    with rec2:
        st.markdown(f"<div class='plant-card'><strong>Light</strong><br>{selected_plant} prefers {plant_data['light']} light. Place accordingly and rotate occasionally for even growth.</div>", unsafe_allow_html=True)
    
    rec3, rec4 = st.columns(2)
    
    with rec3:
        st.markdown(f"<div class='plant-card'><strong>Humidity</strong><br>{selected_plant} prefers {plant_data['humidity']} humidity. Consider using a humidifier or pebble tray if needed.</div>", unsafe_allow_html=True)
    
    with rec4:
        st.markdown(f"<div class='plant-card'><strong>Maintenance</strong><br>Regularly check for pests and clean leaves. Repot every 1-2 years or when rootbound.</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='sub-header'>Plant Care Assistant</div>", unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="avatar user-avatar">👤</div>
                <div class="content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot">
                <div class="avatar bot-avatar">🌱</div>
                <div class="content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask about your plants...", key="chat_input", placeholder="e.g., When should I water my Monstera?")
    
    # Process chat input
    if user_input:
        add_chat_message("user", user_input)
        
        # Get the bot's response
        bot_response = get_bot_response(user_input, selected_plant)
        add_chat_message("bot", bot_response)
        
        # Clear the input
        st.experimental_rerun()

# Footer with plant care tips
st.markdown("---")
st.markdown("### Did You Know?")
tip_of_the_day = [
    "Most houseplants come from tropical regions and appreciate higher humidity.",
    "Misting your plants can help increase humidity, but doesn't replace proper watering.",
    "Yellow lower leaves are often normal as plants age and grow.",
    "Most houseplants go dormant in winter and require less water and fertilizer.",
    "Terracotta pots allow for better soil aeration but dry out faster than plastic pots."
]
st.markdown(f"*{random.choice(tip_of_the_day)}*")