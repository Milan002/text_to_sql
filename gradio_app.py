import gradio as gr
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Initialize database and LLM
db = SQLDatabase.from_uri("sqlite:///Chinook.db", sample_rows_in_table_info=0)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

def get_schema():
    """Get database schema"""
    return db.get_table_info()

def run_query(query):
    """Execute SQL query"""
    try:
        result = db.run(query)
        return result, None
    except Exception as e:
        return None, str(e)

def write_sql_query():
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
        inputs_with_schema = {**inputs, "schema": get_schema()}
        # Format prompt
        formatted_prompt = prompt.format_messages(**inputs_with_schema)
        # Get response from LLM
        response = llm.invoke(formatted_prompt)
        # Parse output
        return response.content.strip()
    
    return generate_sql

def process_query(question):
    """Process natural language question and return results"""
    if not question.strip():
        return "Please enter a question.", "", ""
    
    try:
        # Generate SQL query
        sql_generator = write_sql_query()
        generated_sql = sql_generator({"question": question})
        
        # Execute SQL query
        raw_results, sql_error = run_query(generated_sql)
        
        if sql_error:
            return f"SQL Error: {sql_error}", generated_sql, ""
        
        # Generate natural language response
        template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
        {schema}

        Question: {question}
        SQL Query: {query}
        SQL Response: {response}"""

        prompt_response = ChatPromptTemplate.from_messages([
            ("system", "Given an input question and SQL response, convert it to a natural language answer. No pre-amble."),
            ("human", template),
        ])

        # Generate natural language response
        response_inputs = {
            "question": question,
            "query": generated_sql,
            "schema": get_schema(),
            "response": raw_results
        }
        
        formatted_prompt = prompt_response.format_messages(**response_inputs)
        natural_response = llm.invoke(formatted_prompt)
        
        return natural_response.content, generated_sql, str(raw_results)
        
    except Exception as e:
        return f"Error: {str(e)}", "", ""

def show_schema():
    """Return database schema"""
    return get_schema()

# Sample queries for the interface
sample_queries = [
    "Give me the name of 10 Artists",
    "Give me the name and artist ID of 10 Artists", 
    "Give me 10 Albums by the Artist with ID 1",
    "Give some Albums by the Artist name Audioslave",
    "Give some Tracks by the Artist name Audioslave",
    "Show me all tracks longer than 5 minutes",
    "Which artist has the most albums?",
    "List all genres in the database"
]

# Create Gradio interface
with gr.Blocks(title="Text-to-SQL Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🗄️ Text-to-SQL Assistant")
    gr.Markdown("Ask questions about your database in natural language and get AI-powered answers!")
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("## 💬 Ask Your Question")
            
            question_input = gr.Textbox(
                label="Your Question",
                placeholder="e.g., Give some Tracks by the Artist name Audioslave",
                lines=3
            )
            
            # Sample questions dropdown
            sample_dropdown = gr.Dropdown(
                choices=sample_queries,
                label="📝 Or choose a sample question:",
                value=None
            )
            
            def update_question(sample):
                return sample if sample else ""
            
            sample_dropdown.change(update_question, inputs=[sample_dropdown], outputs=[question_input])
            
            submit_btn = gr.Button("🚀 Execute Query", variant="primary")
            
            gr.Markdown("## 📖 Results")
            
            # Results
            answer_output = gr.Textbox(
                label="Natural Language Answer",
                lines=4,
                interactive=False
            )
            
            with gr.Accordion("🔍 Generated SQL Query", open=False):
                sql_output = gr.Code(
                    label="SQL Query",
                    language="sql",
                    interactive=False
                )
            
            with gr.Accordion("📊 Raw Database Results", open=False):
                raw_output = gr.Textbox(
                    label="Raw Results",
                    lines=6,
                    interactive=False
                )
        
        with gr.Column(scale=1):
            gr.Markdown("## ℹ️ Information")
            
            gr.Markdown("""
            **How to use:**
            1. Type your question in natural language
            2. Click 'Execute Query' 
            3. View the AI-generated answer
            
            **Examples:**
            - "Show me all artists"
            - "Which albums are by Metallica?"
            - "List tracks longer than 5 minutes"
            """)
            
            gr.Markdown("## 🔧 Configuration")
            gr.Markdown("**Model:** Gemini 2.5 Flash")
            gr.Markdown("**Database:** Chinook SQLite")
            
            # API Key status
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                gr.Markdown("✅ **Status:** Google API Key configured")
            else:
                gr.Markdown("❌ **Status:** Google API Key not found")
            
            gr.Markdown("## 📋 Database Schema")
            
            schema_btn = gr.Button("Show Database Schema")
            schema_output = gr.Textbox(
                label="Database Schema",
                lines=10,
                interactive=False,
                visible=False
            )
            
            def toggle_schema():
                schema = show_schema()
                return gr.update(value=schema, visible=True)
            
            schema_btn.click(toggle_schema, outputs=[schema_output])
    
    # Set up the main functionality
    submit_btn.click(
        process_query,
        inputs=[question_input],
        outputs=[answer_output, sql_output, raw_output]
    )
    
    # Also allow Enter key to submit
    question_input.submit(
        process_query,
        inputs=[question_input],
        outputs=[answer_output, sql_output, raw_output]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True  # Set to True if you want to create a public link
    )