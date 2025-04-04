# AI Luxury Travel Concierge Chatbot

A sophisticated chatbot designed to provide personalized luxury travel recommendations and experiences. The chatbot uses Google's Gemini AI to understand user preferences and suggest high-end travel options.

## Features

- Real-time travel recommendations
- Personalized luxury experiences
- Multi-channel integration
- User preference tracking
- Comprehensive luxury travel database
- Beautiful chat interface with quick reply buttons
- Preferences panel for easy customization

## Prerequisites

- Python 3.8 or higher
- Google API key for Gemini
- (Optional) Amadeus Travel API credentials

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
GOOGLE_API_KEY=your-google-api-key-here
AMADEUS_CLIENT_ID=your_amadeus_client_id_here
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret_here
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. The chatbot interface will be available at this URL. You can start chatting with the AI Luxury Travel Concierge immediately.

## Usage

1. Open the application in your web browser at `http://localhost:5000`
2. The chat interface will appear with a welcome message
3. Type your travel-related queries in the input box
4. Use the quick reply buttons for common queries
5. Access the preferences panel to customize your experience

## Features in Detail

### User Interface
- Modern, responsive design
- Real-time chat interface
- Quick reply buttons for common queries
- Preferences panel for customization
- Mobile-friendly layout

### AI Capabilities
- Natural language understanding
- Context-aware responses
- Personalized recommendations
- Multi-turn conversations
- Preference learning

### Travel Features
- Luxury hotel recommendations
- Exclusive experience suggestions
- Fine dining options
- Private activity planning
- Cultural and heritage experiences
- Price estimates in INR and USD

## Troubleshooting

If you encounter any issues:

1. Check that your API keys are correctly set in the `.env` file
2. Ensure all required packages are installed
3. Verify that the Flask server is running
4. Check the browser console for any JavaScript errors
5. Look for error messages in the terminal where Flask is running

## Support

For support or questions, please [create an issue](https://github.com/yourusername/your-repo/issues) in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.