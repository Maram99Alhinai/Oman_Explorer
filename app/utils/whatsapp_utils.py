import logging
from flask import current_app, jsonify
import json
import requests
from app.services.openai_service import generate_response
import re
from app.utils.db_utils import save_user_info, save_user_preference



def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )
        response.raise_for_status()
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except requests.RequestException as e:
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    pattern = r"\【.*?\】"
    text = re.sub(pattern, "", text).strip()
    pattern = r"\*\*(.*?)\*\*"
    replacement = r"*\1*"
    whatsapp_style_text = re.sub(pattern, replacement, text)
    return whatsapp_style_text


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
    else:
        save_user_info(wa_id)
    
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


def is_valid_whatsapp_message(body):
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )