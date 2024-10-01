from app.services.db_service import db, User, Preference, TravelDestination
from app.utils.whatsapp_utils import generate_response, process_text_for_whatsapp, get_text_message_input, send_message



def save_user_info(wa_id, name, age, gender, state, travel_style):
    user = User.query.get(wa_id)
    if user is None:
        user = User(phone_number=wa_id, name=name, age=age, gender=gender, state=state, travel_style=travel_style)
        db.session.add(user)
    else:
        user.name = name
        user.age = age
        user.gender = gender
        user.state = state
        user.travel_style = travel_style
    db.session.commit()

def save_user_preference(wa_id, destination_name, style, tags):
    user = User.query.get(wa_id)
    if user is None:
        return  # Handle error: user not found

    destination = TravelDestination.query.filter_by(destination_name=destination_name).first()
    if destination is None:
        destination = TravelDestination(destination_name=destination_name, location="Unknown", style=style, tags=tags)
        db.session.add(destination)
        db.session.flush()  # This will assign an ID to the new destination

    preference = Preference.query.filter_by(user_id=wa_id, destination_id=destination.destination_id).first()
    if preference is None:
        preference = Preference(user_id=wa_id, destination_id=destination.destination_id, style=style, tags=tags)
        db.session.add(preference)
    else:
        preference.style = style
        preference.tags = tags

    db.session.commit()

# Modify your process_whatsapp_message function
def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # Generate response using OpenAI
    response = generate_response(message_body, wa_id, name)
    
    # Process the response to extract user information and preferences
    user_info, preferences = extract_user_data(response)
    
    # Save user information
    if user_info:
        save_user_info(wa_id, name, user_info.get('age'), user_info.get('gender'), 
                       user_info.get('state'), user_info.get('travel_style'))
    
    # Save user preferences
    if preferences:
        for pref in preferences:
            save_user_preference(wa_id, pref['destination'], pref['style'], pref['tags'])

    # Process the response for WhatsApp formatting
    response = process_text_for_whatsapp(response)

    # Send the message
    data = get_text_message_input(wa_id, response)
    send_message(data)

def extract_user_data(response):
    # Implement logic to extract user information and preferences from the AI response
    # This is a placeholder implementation. You'll need to adjust this based on your AI's output format.
    user_info = {}
    preferences = []
    
    # Example parsing (adjust according to your AI's output structure):
    lines = response.split('\n')
    for line in lines:
        if line.startswith("User Info:"):
            # Parse user info
            info = line.split(':')[1].strip().split(',')
            for item in info:
                key, value = item.split('=')
                user_info[key.strip()] = value.strip()
        elif line.startswith("Preference:"):
            # Parse preference
            pref = line.split(':')[1].strip().split(',')
            preference = {}
            for item in pref:
                key, value = item.split('=')
                preference[key.strip()] = value.strip()
            preferences.append(preference)
    
    return user_info, preferences