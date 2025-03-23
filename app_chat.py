import streamlit as st
from main_chat import get_response

# Set page title and icon
st.set_page_config(page_title="Plant Care Chatbot 🌿", page_icon="🌱")

# Title
st.title("🌱 Plant Care Assistant")
st.write("Ask me anything about plant care, and I'll help you keep your plants healthy!")

# Chat history
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
