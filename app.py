from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Google Gemini
try:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your-google-api-key-here':
        raise ValueError("Google API key not found or is invalid")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"Error initializing Gemini: {str(e)}")
    GEMINI_AVAILABLE = False

# Initialize Amadeus (optional)
try:
    from amadeus import Client, ResponseError
    amadeus_client_id = os.getenv('AMADEUS_CLIENT_ID')
    amadeus_client_secret = os.getenv('AMADEUS_CLIENT_SECRET')
    
    if amadeus_client_id and amadeus_client_secret:
        amadeus = Client(
            client_id=amadeus_client_id,
            client_secret=amadeus_client_secret
        )
        AMADEUS_AVAILABLE = True
    else:
        AMADEUS_AVAILABLE = False
except ImportError:
    AMADEUS_AVAILABLE = False

# Enhanced luxury travel database
LUXURY_DESTINATIONS = {
    'maldives': {
        'hotels': [
            'Soneva Jani',
            'Cheval Blanc Randheli',
            'Four Seasons Private Island at Voavah',
            'Velaa Private Island'
        ],
        'experiences': [
            'Private Island Dinner',
            'Underwater Spa Treatment',
            'Private Yacht Charter',
            'Helicopter Transfer'
        ],
        'restaurants': [
            'Subsix at Niyama Private Islands',
            'Ithaa Undersea Restaurant',
            'Sea. Fire. Salt at Soneva Jani'
        ],
        'activities': [
            'Private Beach Picnic',
            'Sunset Champagne Cruise',
            'Private Diving Experience',
            'Stargazing Dinner'
        ]
    },
    'india': {
        'hotels': [
            'The Oberoi Udaivilas, Udaipur',
            'Taj Lake Palace, Udaipur',
            'The Leela Palace, New Delhi',
            'Taj Falaknuma Palace, Hyderabad',
            'Amanbagh, Rajasthan',
            'The Oberoi Amarvilas, Agra',
            'Taj Mahal Palace, Mumbai',
            'The Leela Palace, Bengaluru'
        ],
        'experiences': [
            'Private Heritage Walk',
            'Royal Elephant Ride',
            'Private Yoga Session',
            'Luxury Spa Treatment',
            'Private Cooking Class',
            'Sunset Boat Ride on Lake Pichola',
            'Private Tour of Taj Mahal',
            'Luxury Train Journey on Palace on Wheels'
        ],
        'restaurants': [
            'Indian Accent, New Delhi',
            'Bukhara, New Delhi',
            'Masala Library, Mumbai',
            'Varq, New Delhi',
            'Peshawri, Mumbai',
            'Karavalli, Bengaluru',
            'Dum Pukht, New Delhi',
            'The Table, Mumbai'
        ],
        'activities': [
            'Private Heritage Tour',
            'Luxury Shopping Experience',
            'Private Yoga and Meditation',
            'Royal Dining Experience',
            'Private Cultural Show',
            'Luxury Spa Day',
            'Private Cooking Masterclass',
            'Sunset Cruise with Dinner'
        ]
    },
    'switzerland': {
        'hotels': [
            'Badrutt\'s Palace Hotel',
            'The Alpina Gstaad',
            'Grand Hotel Zermatterhof',
            'The Chedi Andermatt'
        ],
        'experiences': [
            'Private Ski Instructor',
            'Helicopter Skiing',
            'Private Wine Tasting',
            'Luxury Spa Treatment'
        ],
        'restaurants': [
            'Cheval Blanc by Peter Knogl',
            'La Grande Terrasse',
            'IGNIV by Andreas Caminada'
        ],
        'activities': [
            'Private Mountain Tour',
            'Chocolate Tasting Experience',
            'Cheese Fondue in Igloo',
            'Private Helicopter Tour'
        ]
    },
    'dubai': {
        'hotels': [
            'Burj Al Arab',
            'One&Only Royal Mirage',
            'Atlantis The Royal',
            'Armani Hotel Dubai'
        ],
        'experiences': [
            'Desert Safari with Private Dinner',
            'Helicopter Tour',
            'Private Yacht Experience',
            'Ski Dubai Private Session'
        ],
        'restaurants': [
            'Nathan Outlaw at Al Mahara',
            'Ossiano',
            'Pierchic',
            'At.mosphere'
        ],
        'activities': [
            'Private Desert Camp',
            'Ferrari World VIP Tour',
            'Dubai Mall Private Shopping',
            'Burj Khalifa Private Viewing'
        ]
    }
}

# User preferences storage (in a real application, this would be in a database)
user_preferences = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not GEMINI_AVAILABLE:
            return jsonify({
                'error': 'Gemini API is not properly configured. Please check your Google API key.',
                'status': 'error'
            }), 500

        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default')
        
        # Get or initialize user preferences
        if user_id not in user_preferences:
            user_preferences[user_id] = {
                'past_trips': [],
                'preferred_hotels': [],
                'favorite_cuisines': [],
                'budget_range': 'luxury',
                'travel_style': 'luxury'
            }
        
        # Create a context-aware prompt for Gemini
        system_prompt = """You are an AI Luxury Travel Concierge specializing in high-end, exclusive travel experiences, with a focus on Indian destinations and pricing in Indian Rupees (INR).
        Your responses should be:
        1. Professional yet warm and engaging
        2. Include specific details about luxury experiences
        3. Use emojis occasionally for a friendly touch
        4. Focus on exclusive and premium services
        5. Include prices in INR (Indian Rupees) when relevant
        6. Be detailed and informative
        7. Always maintain a luxury-focused tone
        8. Use the provided luxury database for specific destinations
        9. Suggest personalized recommendations based on user preferences
        10. Include booking assistance information
        11. When mentioning prices, always convert to INR and show both INR and USD values
        12. Prioritize Indian luxury hotels and experiences when relevant
        13. Include Indian cultural experiences and heritage sites
        14. Suggest Indian luxury train journeys when appropriate"""

        user_prompt = f"""User message: {user_message}
        User preferences: {json.dumps(user_preferences[user_id], indent=2)}
        Available luxury destinations: {json.dumps(LUXURY_DESTINATIONS, indent=2)}
        
        Please provide a detailed, luxury-focused response that includes:
        1. Specific recommendations based on the user's request
        2. Relevant luxury accommodations (prioritizing Indian hotels when appropriate)
        3. Exclusive experiences (including Indian cultural experiences)
        4. Fine dining options (including Indian cuisine)
        5. Private activities
        6. Estimated costs in both INR and USD
        7. Booking assistance information
        8. Indian heritage and cultural experiences when relevant"""
        
        # Get Gemini response
        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["I understand. I will provide luxury travel recommendations with a focus on high-end experiences."]},
                {"role": "user", "parts": [user_prompt]}
            ],
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1000,
            }
        )
        
        ai_response = response.text
        
        # Update user preferences based on the conversation
        update_user_preferences(user_id, user_message, ai_response)
        
        return jsonify({
            'response': ai_response,
            'preferences': user_preferences[user_id],
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")  # Add logging
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

def update_user_preferences(user_id, user_message, ai_response):
    """Update user preferences based on the conversation"""
    preferences = user_preferences[user_id]
    
    # Extract destination mentions
    destinations = [dest for dest in LUXURY_DESTINATIONS.keys() 
                   if dest.lower() in user_message.lower()]
    if destinations:
        preferences['past_trips'].extend(destinations)
    
    # Extract hotel mentions
    for dest in LUXURY_DESTINATIONS.values():
        for hotel in dest['hotels']:
            if hotel.lower() in user_message.lower():
                preferences['preferred_hotels'].append(hotel)
    
    # Extract cuisine preferences
    cuisine_keywords = ['italian', 'french', 'japanese', 'indian', 'mediterranean']
    for cuisine in cuisine_keywords:
        if cuisine in user_message.lower():
            preferences['favorite_cuisines'].append(cuisine)
    
    # Update budget range if mentioned
    if 'budget' in user_message.lower():
        if 'luxury' in user_message.lower():
            preferences['budget_range'] = 'ultra-luxury'
        elif 'moderate' in user_message.lower():
            preferences['budget_range'] = 'luxury'
    
    # Update travel style
    if 'romantic' in user_message.lower():
        preferences['travel_style'] = 'romantic'
    elif 'adventure' in user_message.lower():
        preferences['travel_style'] = 'adventure'
    elif 'relaxation' in user_message.lower():
        preferences['travel_style'] = 'relaxation'

@app.route('/api/destinations', methods=['GET'])
def get_destinations():
    try:
        return jsonify({
            'destinations': LUXURY_DESTINATIONS,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/flights', methods=['GET'])
def search_flights():
    if not AMADEUS_AVAILABLE:
        return jsonify({
            'error': 'Flight search is currently unavailable. Please try again later.',
            'status': 'error'
        }), 503
        
    try:
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        date = request.args.get('date')
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            currencyCode='USD',
            max=5
        )
        
        return jsonify({
            'flights': response.data,
            'status': 'success'
        })
        
    except ResponseError as error:
        return jsonify({
            'error': str(error),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)