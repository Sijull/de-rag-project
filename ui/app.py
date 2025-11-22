import streamlit as st
import requests
import os

# The API URL is the name of the service in docker-compose.yml
# When running in Docker, we use the service name "api" (or "rag-api")
API_URL = os.getenv("API_URL", "http://api:8000/chat")

st.set_page_config(page_title="Airflow RAG Assistant", layout="wide")

st.title("🤖 Airflow Documentation Assistant")
st.caption("Ask questions about Airflow, and I'll answer using the docs stored in MinIO & Weaviate.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If the message has sources, display them
        if "sources" in message:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.caption(source)

# React to user input
if prompt := st.chat_input("How do I create a DAG in Airflow?"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call API
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"message": prompt})
            response.raise_for_status()
            
            data = response.json()
            bot_response = data.get("response", "No response.")
            sources = data.get("sources", [])

            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(bot_response)
                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.caption(source)
            
            # Save to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": bot_response,
                "sources": sources
            })
        
        except Exception as e:
            st.error(f"Connection Error: {e}")


# import streamlit as st
# import requests
# import os

# # The API URL is the name of the service in docker-compose.yml
# API_URL = "http://rag-api:8000/chat"

# st.set_page_config(layout="wide")
# st.title("My RAG Project 🤖")

# st.info("This is the Weekend 1 test UI. We are just testing the connection to the API.")

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # React to user input
# if prompt := st.chat_input("What is this project about?"):
#     # Display user message in chat message container
#     st.chat_message("user").markdown(prompt)
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     try:
#         # Call the FastAPI backend
#         response = requests.post(API_URL, json={"message": prompt})
#         response.raise_for_status()
        
#         # Get the fake response from the API stub
#         api_data = response.json()
#         bot_response = api_data.get("response", "No response from API")

#         # Display assistant response in chat message container
#         with st.chat_message("assistant"):
#             st.markdown(bot_response)
#         # Add assistant response to chat history
#         st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
#     except requests.exceptions.RequestException as e:
#         st.error(f"Failed to connect to API: {e}")