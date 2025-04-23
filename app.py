from flask import Flask, request, jsonify, render_template
import os
import json
import re
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')

# Store conversation history
conversation_history = {}

# Try to import Gemini AI if possible
try:
    import google.generativeai as genai
    # Configure Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        genai.configure(api_key=GEMINI_API_KEY)
        # Use the newer model explicitly
        GEMINI_MODEL = "gemini-1.5-flash"
        print(f"Using Gemini model: {GEMINI_MODEL}")
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
        print("Gemini API key not properly configured")
except (ImportError, Exception) as e:
    print(f"Gemini API not available: {e}")
    GEMINI_AVAILABLE = False

# Define history-related keywords to determine if a question is on-topic
HISTORY_KEYWORDS = [
    'history', 'story', 'stories', 'past', 'ancient', 'heritage', 'culture', 'tradition',
    'legend', 'myth', 'folktale', 'historical', 'monument', 'landmark', 'museum',
    'archaeology', 'artifact', 'civilization', 'dynasty', 'empire', 'kingdom', 'battle',
    'war', 'revolution', 'discovery', 'exploration', 'settlement', 'colony', 'independence',
    'freedom', 'movement', 'reform', 'development', 'progress', 'achievement', 'invention',
    'innovation', 'pioneer', 'leader', 'hero', 'figure', 'personality', 'biography',
    'memoir', 'chronicle', 'archive', 'document', 'record', 'evidence', 'site', 'ruin',
    'preservation', 'conservation', 'restoration', 'exhibition', 'display', 'gallery',
    'collection', 'art', 'architecture', 'building', 'structure', 'place', 'location',
    'region', 'area', 'territory', 'land', 'city', 'town', 'village', 'community',
    'taj mahal', 'amritsar', 'golden temple', 'red fort', 'qutub minar', 'india gate',
    'hawa mahal', 'charminar', 'victoria memorial', 'gateway of india', 'lotus temple',
    'jama masjid', 'meenakshi temple', 'konark temple', 'ajanta caves', 'ellora caves',
    'khajuraho', 'hampi', 'fatehpur sikri', 'sanchi stupa', 'buddhist', 'hindu',
    'muslim', 'sikh', 'jain', 'temple', 'mosque', 'church', 'gurudwara', 'monastery',
    'fort', 'palace', 'tomb', 'mausoleum', 'shrine', 'statue', 'sculpture', 'painting',
    'artwork', 'heritage site', 'world heritage', 'unesco', 'architectural', 'design',
    'construction', 'built', 'created', 'established', 'founded', 'origin', 'beginning',
    'start', 'formation', 'development', 'evolution', 'growth', 'expansion', 'rise',
    'decline', 'fall', 'destruction', 'restoration', 'renovation', 'preservation',
    'conservation', 'protection', 'maintenance', 'repair', 'rebuild', 'reconstruct'
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Check if the question is history-related
    if not is_history_question(user_message):
        off_topic_response = "I'm a Local History and Stories bot. I can help you learn about historical events, local stories, cultural heritage, and interesting tales from the past. Could you please ask me something about history or local stories?"
        
        # Initialize conversation history for this session if it doesn't exist
        if session_id not in conversation_history:
            conversation_history[session_id] = []
            
        # Add user message and bot response to history
        conversation_history[session_id].append({"role": "user", "message": user_message})
        conversation_history[session_id].append({"role": "bot", "message": off_topic_response})
        
        return jsonify({'response': off_topic_response})
    
    # Initialize conversation history for this session if it doesn't exist
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # Add user message to history
    conversation_history[session_id].append({"role": "user", "message": user_message})
    
    try:
        # Try to use Gemini AI if available
        if GEMINI_AVAILABLE:
            try:
                response = generate_ai_response(user_message, session_id)
            except Exception as e:
                print(f"Error with Gemini API: {e}")
                # Fall back to rule-based responses
                response = generate_rule_based_response(user_message)
        else:
            # Use rule-based responses
            response = generate_rule_based_response(user_message)
            
        # Add bot response to history
        conversation_history[session_id].append({"role": "bot", "message": response})
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to process your request'}), 500

def is_history_question(text):
    """Check if the question is related to history"""
    text_lower = text.lower()
    
    # Check if any history keyword is in the text
    for keyword in HISTORY_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
            
    # Special case for very short queries that might be follow-ups
    if len(text_lower.split()) <= 3:
        return True
        
    return False

def limit_response_to_words(text, max_words=100):
    """Limit text to specified number of words"""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'

def generate_ai_response(prompt, session_id='default'):
    """Generate response using Gemini AI"""
    try:
        # Configure the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # Create a new chat session with Gemini
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config=generation_config
        )
        
        # Get conversation history
        history = []
        if session_id in conversation_history:
            # Convert history format for Gemini
            for msg in conversation_history[session_id]:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["message"]]})
        
        # Add strong history focus context with word limit
        system_prompt = """You are a Local History and Stories chatbot with a focus on sharing historical knowledge and interesting tales.
        ONLY provide information about historical events, local stories, cultural heritage, and related topics. 
        If a question is not directly related to history or local stories, politely decline to answer and redirect 
        the conversation to historical topics.
        
        Example of questions to decline: current events, future predictions, technical topics, or any topic not 
        directly related to history or local stories.
        
        Always be engaging and informative. Focus on making history come alive through interesting stories and facts.
        Keep responses concise and strictly focused on historical topics.
        IMPORTANT: Keep your responses under 100 words."""
        
        # Start a new chat
        chat = model.start_chat(history=history)
        
        # Send the system prompt if this is a new conversation
        if len(history) == 0:
            chat.send_message(system_prompt)
        
        # Add a history focus reminder to each prompt
        history_focused_prompt = f"{prompt}\n\nRemember: Only respond with historical information and stories. If the question is not about history or local stories, decline to answer. Keep your response under 100 words."
        
        # Send the user's message and get the response
        response = chat.send_message(history_focused_prompt)
        return limit_response_to_words(response.text)
    
    except Exception as e:
        print(f"Error generating AI response: {e}")
        # Fall back to rule-based response
        return generate_rule_based_response(prompt)

def generate_rule_based_response(prompt):
    """Generate response using rule-based system when AI is not available"""
    # Convert prompt to lowercase for easier matching
    prompt_lower = prompt.lower()
    
    # Check for greetings
    greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    greeting_responses = [
        "Hello! I'm your Local History and Stories bot. I can help you learn about historical events, local stories, and interesting tales from the past. What would you like to know?",
        "Hi there! Welcome to your journey through time! I'm here to share fascinating historical stories and information with you. What interests you?",
        "Greetings! I'm your friendly history companion. I'd love to share some amazing stories from the past with you today!",
        "Hey! I'm excited to help you explore the rich tapestry of history. What historical topic would you like to discover?",
        "Hello! I'm your local history storyteller. I have many interesting tales and historical facts to share with you!",
        "Hi! I'm here to make history come alive through engaging stories and fascinating facts. What would you like to learn about?",
        "Greetings! I'm your historical guide, ready to take you on a journey through time. What historical period interests you?",
        "Hey there! I'm your friendly history bot, and I can't wait to share some amazing historical stories with you!",
        "Hello! I'm here to help you discover the fascinating world of history. What would you like to explore?",
        "Hi! I'm your local history companion, and I'm excited to share some incredible stories from the past with you!"
    ]
    
    for greeting in greetings:
        if greeting in prompt_lower:
            return limit_response_to_words(random.choice(greeting_responses))
    
    # Check for goodbye
    if 'bye' in prompt_lower or 'goodbye' in prompt_lower:
        return "Goodbye! This chatbot was created by Shivam Garg. Have a great day!"
    
    # Check for gratitude
    thanks = ['thank', 'thanks', 'appreciate', 'grateful']
    for word in thanks:
        if word in prompt_lower:
            return "You're welcome! I'm happy to share more historical stories and information with you."
    
    # Check for specific monuments and places
    if 'taj mahal' in prompt_lower:
        return "The Taj Mahal was built by Mughal Emperor Shah Jahan in memory of his wife Mumtaz Mahal. Construction began in 1632 and took about 22 years to complete. It's considered one of the most beautiful buildings in the world and is a UNESCO World Heritage Site."
    
    if 'amritsar' in prompt_lower:
        return "Amritsar was founded in 1577 by Guru Ram Das, the fourth Sikh Guru. The city is home to the Golden Temple, the holiest shrine of Sikhism. It has played a significant role in Indian history, including the Jallianwala Bagh massacre in 1919."
    
    # Predefined responses for history-related queries
    responses = {
        'ancient': [
            "Ancient civilizations have left fascinating legacies that continue to influence our world today.",
            "Archaeological discoveries help us understand how ancient people lived and what they believed.",
            "Many ancient stories and myths have been passed down through generations, shaping our cultural heritage."
        ],
        'medieval': [
            "The medieval period was a time of great castles, knights, and significant cultural development.",
            "Medieval history is rich with stories of exploration, trade, and cultural exchange.",
            "Many modern traditions and customs have their roots in medieval times."
        ],
        'modern': [
            "Modern history has seen rapid changes in technology, society, and global connections.",
            "The stories of modern history show how past events shape our present world.",
            "Understanding modern history helps us make sense of current events and developments."
        ],
        'local': [
            "Local history is full of fascinating stories about the people and events that shaped our communities.",
            "Every place has its own unique history and interesting tales to tell.",
            "Exploring local history helps us understand our roots and cultural heritage."
        ],
        'culture': [
            "Cultural history shows how traditions, beliefs, and customs have evolved over time.",
            "Understanding cultural history helps us appreciate the diversity of human experience.",
            "Many cultural practices have deep historical roots that continue to influence us today."
        ],
        'war': [
            "Historical conflicts have shaped the course of human history in profound ways.",
            "The stories of war and peace show both the best and worst of human nature.",
            "Understanding historical conflicts helps us work towards a more peaceful future."
        ],
        'discovery': [
            "Historical discoveries have expanded our knowledge and changed our understanding of the world.",
            "The stories of exploration and discovery show human curiosity and determination.",
            "Many important discoveries have come from unexpected places and circumstances."
        ]
    }
    
    # Check for specific topics in the prompt
    for topic, topic_responses in responses.items():
        if topic in prompt_lower:
            return limit_response_to_words(random.choice(topic_responses))
    
    # General responses when no specific topic is matched
    general_responses = [
        "History is full of fascinating stories waiting to be discovered.",
        "Every historical event has multiple perspectives and interesting details to explore.",
        "Understanding history helps us better understand our present world.",
        "The past is filled with incredible stories of human achievement and discovery.",
        "Exploring history helps us learn from the experiences of those who came before us."
    ]
    
    return limit_response_to_words(random.choice(general_responses))

if __name__ == '__main__':
    app.run(debug=True, port=10000) 