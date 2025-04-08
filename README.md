# Investment Advisor AI Chatbot

A Flask-based chatbot application powered by Google's Gemini AI that provides specialized investment advice with a strict focus on financial topics only.

## Setup Instructions

1. **Install Python dependencies**

   ```
   pip install -r requirements.txt
   ```

2. **Set up environment variables**

   You need to obtain a Gemini API key from Google AI Studio (https://ai.google.dev/) and add it to the `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Run the application**

   ```
   python app.py
   ```

4. **Access the chatbot**

   Open your browser and go to:
   ```
   http://localhost:5000
   ```

## Features

- Strictly focused on investment topics only - will decline to answer non-financial questions
- AI-powered investment advice using Google's Gemini API with fallback to rule-based responses
- Conversation memory that maintains context across messages
- Investment-themed chat interface with modern design
- Session tracking for multiple concurrent users

## Technical Implementation

- **Topic Filtering**: Pre-screens all questions to ensure they're related to investments
- **Dual Response System**: Uses AI when available and rule-based responses as backup
- **Context Management**: Maintains conversation history for contextual responses
- **Investment Keyword Detection**: Uses a comprehensive list of investment terms to filter questions

## Example Investment Questions

Try asking the AI about:
- "What investment strategies are suitable for beginners?"
- "How should I balance my portfolio between stocks and bonds?"
- "What are the tax implications of different retirement accounts?"
- "Can you explain dollar-cost averaging?"
- "What factors should I consider when investing for retirement?"
- "How do dividend stocks compare to growth stocks?"
- "What are the pros and cons of index fund investing?" 