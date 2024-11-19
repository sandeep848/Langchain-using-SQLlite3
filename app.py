import streamlit as st
import pathlib
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq
import os

st.set_page_config(page_title="Langchain With SQL Database")
st.title("Langchain With SQL Database")

LOCAL = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_options = ["Use SQLite3 Database", "Connect to your SQL Database"]
database_choice = st.sidebar.radio(label="Select the database you would like to use", options=radio_options)
model_selection = st.selectbox(
    "Select model",
    ['llama-3.1-70b-versatile', 'llama-3.1-8b-instant', 'gemma-7b-it', 
     'llama-3.2-90b-vision-preview', 'llama3-70b-8192', "mixtral-8x7b-32768"]
)

if radio_options.index(database_choice) == 1:
    db = MYSQL
    mysql_host = st.sidebar.text_input("Enter MySQL Host")
    mysql_user = st.sidebar.text_input("Enter MySQL User")
    mysql_password = st.sidebar.text_input("Enter MySQL Password", type='password')
    mysql_db = st.sidebar.text_input("Enter MySQL Database Name")
else:
    db = LOCAL

api_key = st.sidebar.text_input(label="Groq API Key", type="password")
if api_key:
    os.environ["GROQ_API_KEY"] = api_key
else:
    st.info("Please provide your Groq API key.")

try:
    llm = ChatGroq(model=model_selection, streaming=True)
except Exception as e:
    st.error(f"Failed to initialize ChatGroq: {str(e)}")
    st.stop()

@st.cache_resource(ttl="2h")
def configure_database(db, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db == LOCAL:
        file = (pathlib.Path(__file__).parent / "student.db").absolute()
        create_connection = lambda: sqlite3.connect(f"file:{file}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=create_connection))
    elif db == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide MySQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

configured_db = configure_database(db, mysql_host, mysql_user, mysql_password, mysql_db) if db == MYSQL else configure_database(db)

toolkit = SQLDatabaseToolkit(db=configured_db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I assist you today?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask Anything")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        callback_handler = StreamlitCallbackHandler(st.container())
        try:
            response = agent.run(user_query, callbacks=[callback_handler])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
