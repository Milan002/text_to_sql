# Text-to-SQL Assistant

A powerful AI-powered application that converts natural language questions into SQL queries and provides natural language answers using your database.

## Features

- 🗣️ **Natural Language to SQL**: Ask questions in plain English
- 🤖 **AI-Powered**: Uses Google's Gemini 2.5 Flash for intelligent query generation
- 📊 **Multiple Interfaces**: Available in both Streamlit and Gradio
- 🗄️ **Database Integration**: Works with SQLite databases (Chinook sample included)
- 📋 **Schema Viewer**: Explore your database structure
- 🕒 **Query History**: Keep track of previous queries (Streamlit version)
- 🎯 **Sample Questions**: Pre-built examples to get you started

## Installation

1. **Clone or download this project**

2. **Set up your environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   Create a `.env` file in the project root:
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### Streamlit Version (Recommended)
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Features:**
- Clean, professional interface
- Sidebar with schema viewer and query history
- Sample questions for quick testing
- Expandable sections for SQL queries and raw results

### Gradio Version
```bash
python gradio_app.py
```
Then open http://localhost:7860 in your browser.

**Features:**
- Modern, responsive interface
- Integrated schema viewer
- Sample questions dropdown
- Accordion sections for organized results

## Sample Questions

Try these example questions:

1. **Basic Queries:**
   - "Give me the name of 10 Artists"
   - "Show me all genres in the database"

2. **Filtered Queries:**
   - "Give me 10 Albums by the Artist with ID 1"
   - "Show me all tracks longer than 5 minutes"

3. **Join Queries:**
   - "Give some Albums by the Artist name Audioslave"
   - "Give some Tracks by the Artist name Audioslave"

4. **Analytical Queries:**
   - "Which artist has the most albums?"
   - "What are the top 10 longest tracks?"

## Database Schema

The application uses the Chinook sample database which includes:

- **Artists**: Artist information
- **Albums**: Album details linked to artists
- **Tracks**: Individual tracks with album associations
- **Genres**: Music genres
- **Customers**: Customer information
- **Invoices**: Sales data
- **And more...**

## How It Works

1. **Input**: You ask a question in natural language
2. **SQL Generation**: Gemini AI converts your question to SQL using the database schema
3. **Execution**: The SQL query runs against your database
4. **Response**: The results are converted back to natural language

## Configuration

- **Model**: Google Gemini 2.5 Flash (fast and accurate)
- **Temperature**: 0.0 (for consistent, deterministic responses)
- **Database**: SQLite with Chinook sample data

## Troubleshooting

### API Key Issues
- Make sure your `.env` file is in the project root
- Verify your Google API key is valid
- Check that you have sufficient API quota

### Database Connection Issues
- Ensure `Chinook.db` is in the project directory
- Verify the database file is not corrupted

### Installation Issues
- Make sure you're using Python 3.8 or higher
- Try installing packages individually if bulk installation fails
- On some systems, use `python3` instead of `python`

## Files Structure

```
text-to-sql/
├── app.py              # Streamlit application
├── gradio_app.py       # Gradio application  
├── agent.ipynb         # Original Jupyter notebook
├── Chinook.db          # Sample SQLite database
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
└── README.md          # This file
```

## Dependencies

- **streamlit**: Web app framework
- **gradio**: Alternative UI framework
- **langchain-google-genai**: Google Gemini integration
- **langchain-community**: Database utilities
- **python-dotenv**: Environment variable management
- **pandas**: Data manipulation

## Contributing

Feel free to contribute by:
- Adding support for other databases (PostgreSQL, MySQL, etc.)
- Implementing new UI features
- Adding more sample questions
- Improving error handling
- Adding data visualization features

## License

This project is open source and available under the MIT License.