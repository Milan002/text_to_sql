import streamlit as st
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL Assistant",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

@st.cache_resource
def init_database():
    """Initialize database connection"""
    try:
        db = SQLDatabase.from_uri("sqlite:///Chinook.db", sample_rows_in_table_info=0)
        return db
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

@st.cache_resource
def get_llm():
    """Initialize the LLM"""
    try:
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
    except Exception as e:
        st.error(f"Error initializing LLM: {e}")
        return None

def get_schema(db):
    """Get database schema"""
    if db:
        return db.get_table_info()
    return "Database not connected"

def run_query(db, query):
    """Execute SQL query"""
    if db:
        try:
            result = db.run(query)
            return result, None
        except Exception as e:
            return None, str(e)
    return None, "Database not connected"

def write_sql_query(llm, db):
    """Create SQL query generation chain"""
    template = """Based on the table schema below, write a SQL query that would answer the user's question:
    {schema}

    Question: {question}
    SQL Query:"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Given an input question, convert it to a SQL query. No pre-amble. "
         "Please do not return anything else apart from the SQL query, no prefix or suffix quotes, no sql keyword, nothing please"),
        ("human", template),
    ])

    def generate_sql(inputs):
        # Add schema to inputs
        inputs_with_schema = {**inputs, "schema": get_schema(db)}
        # Format prompt
        formatted_prompt = prompt.format_messages(**inputs_with_schema)
        # Get response from LLM
        response = llm.invoke(formatted_prompt)
        # Parse output
        return response.content.strip()
    
    return generate_sql

def answer_user_query(query, llm, db):
    """Generate natural language answer"""
    template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
    {schema}

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}"""

    prompt_response = ChatPromptTemplate.from_messages([
        ("system", "Given an input question and SQL response, convert it to a natural language answer. No pre-amble."),
        ("human", template),
    ])

    sql_generator = write_sql_query(llm, db)
    
    # Generate SQL query
    sql_result = sql_generator({"question": query})
    
    # Execute SQL query
    db_result, error = run_query(db, sql_result)
    
    if error:
        raise Exception(f"SQL Error: {error}")
    
    # Prepare inputs for natural language response
    response_inputs = {
        "question": query,
        "query": sql_result,
        "schema": get_schema(db),
        "response": db_result
    }
    
    # Generate natural language response
    formatted_prompt = prompt_response.format_messages(**response_inputs)
    response = llm.invoke(formatted_prompt)
    
    return response

def main():
    st.title("🗄️ Text-to-SQL Assistant")
    st.markdown("Ask questions about your database in natural language!")
    
    # Initialize components
    db = init_database()
    llm = get_llm()
    
    if not db or not llm:
        st.error("Failed to initialize application. Please check your configuration.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Database Schema")
        if st.button("Show Schema"):
            with st.expander("Database Tables", expanded=True):
                schema = get_schema(db)
                st.text(schema)
        
        st.header("🕒 Query History")
        if st.session_state.query_history:
            for i, (q, _) in enumerate(reversed(st.session_state.query_history[-5:])):
                if st.button(f"Query {len(st.session_state.query_history)-i}", key=f"history_{i}"):
                    st.session_state.selected_query = q
        
        if st.button("Clear History"):
            st.session_state.query_history = []
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Your Question")
        
        # Query input
        query_input = st.text_area(
            "Enter your question:",
            placeholder="e.g., Give some Tracks by the Artist name Audioslave",
            height=100,
            value=st.session_state.get('selected_query', '')
        )
        
        # Sample questions
        st.subheader("📝 Sample Questions")
        sample_queries = [
            "Give me the name of 10 Artists",
            "Give me the name and artist ID of 10 Artists", 
            "Give me 10 Albums by the Artist with ID 1",
            "Give some Albums by the Artist name Audioslave",
            "Give some Tracks by the Artist name Audioslave"
        ]
        
        selected_sample = st.selectbox("Or choose a sample question:", [""] + sample_queries)
        
        if selected_sample:
            query_input = selected_sample
        
        # Execute button
        if st.button("🚀 Execute Query", type="primary", disabled=not query_input.strip()):
            if query_input.strip():
                with st.spinner("Processing your question..."):
                    try:
                        # Generate SQL and get answer
                        response = answer_user_query(query_input, llm, db)
                        
                        # Get the SQL query for display
                        sql_generator = write_sql_query(llm, db)
                        generated_sql = sql_generator({"question": query_input})
                        
                        # Execute SQL to get raw results
                        raw_results, sql_error = run_query(db, generated_sql)
                        
                        # Store in history
                        st.session_state.query_history.append((query_input, response.content))
                        
                        # Display results
                        st.success("Query executed successfully!")
                        
                        # Natural language answer
                        st.subheader("📖 Answer")
                        st.write(response.content)
                        
                        # Show generated SQL
                        with st.expander("🔍 Generated SQL Query", expanded=False):
                            st.code(generated_sql, language="sql")
                        
                        # Show raw results
                        with st.expander("📊 Raw Results", expanded=False):
                            if raw_results:
                                st.text(raw_results)
                            else:
                                st.write("No results returned")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col2:
        st.header("ℹ️ Information")
        
        st.info("""
        **How to use:**
        1. Type your question in natural language
        2. Click 'Execute Query' 
        3. View the AI-generated answer
        
        **Examples:**
        - "Show me all artists"
        - "Which albums are by Metallica?"
        - "List tracks longer than 5 minutes"
        """)
        
        st.header("🔧 Configuration")
        st.write(f"**Model:** Gemini 2.5 Flash")
        st.write(f"**Database:** Chinook SQLite")
        
        # API Key status
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            st.success("✅ Google API Key configured")
        else:
            st.error("❌ Google API Key not found")

if __name__ == "__main__":
    main()