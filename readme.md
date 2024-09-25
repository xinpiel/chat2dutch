## Setup and Running the Application

1. **Clone the Repository**:
   ```
   git clone https://github.com/your-username/chat2dutch.git
   cd chat2dutch
   ```

2. **Install Poetry** (if not already installed):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install Dependencies**:
   ```
   poetry install
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. **Prepare the Dutch Dictionary**:
   Ensure you have a `dutch_dictionary.csv` file in the project root with the required format.

6. **Run the Backend**:
   In one terminal window, run:
   ```
   poetry run uvicorn app_main:app --reload
   ```

7. **Run the Frontend**:
   In another terminal window, run:
   ```
   poetry run python chat_interface.py
   ```

8. **Access the Web Interface**:
   Open a web browser and go to the URL displayed in the console (usually `http://127.0.0.1:7860`).

## Usage

1. Ensure both the backend and frontend are running.
2. Access the web interface in your browser.
3. Set your daily target and define milestones in the Settings tab.
4. Type "daily quiz" in the chat to start a word quiz.
5. Search for specific words by ending your message with a question mark (e.g., "huis?").
6. Use the Known and Unknown buttons during quizzes to mark your understanding of words.

## Dependencies

Dependencies are managed through Poetry. Key dependencies include:

- FastAPI: For the backend API
- Uvicorn: ASGI server for running the backend
- Gradio: For the chat interface
- OpenAI: For word information retrieval and Dutch language verification
- Pandas: For data manipulation

Refer to the `pyproject.toml` file for a complete list of dependencies.