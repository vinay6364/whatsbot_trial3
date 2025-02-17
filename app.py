from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from chatterbot2 import ChatBot
from chatterbot2.trainers import ChatterBotCorpusTrainer

# Initialize the Flask app
app = Flask(__name__)

# Initialize the chatbot
chatbot = ChatBot('WhatsAppBot')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")  # Train on English corpus

# Track user sessions and data
user_sessions = {}

# URL of the animated honey bee image (replace with your actual image URL)
HONEY_BEE_IMAGE_URL = "https://example.com/honey-bee.gif"  # Replace with a valid URL

# Menu options
MENU_OPTIONS = (
    "Please choose an option by typing the number:\n"
    "1. Areka nut plantation\n"
    "2. Apiary\n"
    "3. Nursery kit\n"
    "4. Seedling kit\n"
    "5. Honey products\n"
    "6. Exit\n"
    "7. Restart"
)

# Twilio webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    # Get the incoming message from WhatsApp
    incoming_message = request.form.get("Body", "").strip().lower()
    sender = request.form.get("From", "")

    print(f"Received message from {sender}: {incoming_message}")

    # Initialize Twilio response object
    twilio_response = MessagingResponse()

    # Check if the user is starting the conversation
    if incoming_message == "start":
        # Send a welcome message and ask for the user's name
        welcome_message = (
            "👋 Hello! Welcome to the chatbot. I'm here to help you.\n"
            "What's your name?"
        )
        twilio_response.message(welcome_message)
        # Initialize user session
        user_sessions[sender] = {"step": "ask_name"}
    elif sender in user_sessions:
        # Handle conversation flow based on the current step
        user_data = user_sessions[sender]
        if user_data["step"] == "ask_name":
            # Save the user's name and ask for their location
            user_data["name"] = incoming_message
            user_data["step"] = "ask_location"
            twilio_response.message(f"Nice to meet you, {incoming_message}! Where are you from?")
        elif user_data["step"] == "ask_location":
            # Save the user's location and confirm
            user_data["location"] = incoming_message
            user_data["step"] = "show_menu"
            twilio_response.message(
                f"Got it, {user_data['name']} from {incoming_message}!\n\n"
                f"{MENU_OPTIONS}"
            )
        elif user_data["step"] == "show_menu":
            # Handle menu options
            if incoming_message in ["1", "2", "3", "4", "5", "7"]:
                # Respond with developmental phase message
                twilio_response.message(
                    "This feature is still in the developmental phase. "
                    "You can contact this number for further assistance: 1233455."
                )
            elif incoming_message == "6":
                # End the session with a farewell message
                twilio_response.message("Farewell! Come back anytime. 👋")
                # Clear the user's session
                user_sessions.pop(sender, None)
            else:
                # Handle invalid input
                twilio_response.message("Invalid option. Please choose a number from 1 to 7.")
        elif user_data["step"] == "completed":
            # Handle normal conversation
            if "thank you" in incoming_message:
                # Send the honey bee image and thank you message
                twilio_response.message("Thank you for choosing Areka Karmik Private Limited!")
                twilio_response.message().media(HONEY_BEE_IMAGE_URL)
            else:
                # Default chatbot response
                response = chatbot.get_response(incoming_message)
                twilio_response.message(str(response))
    else:
        # If the user hasn't started the conversation, prompt them to type 'start'
        twilio_response.message("Please type 'start' to begin the conversation.")

    return str(twilio_response)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
