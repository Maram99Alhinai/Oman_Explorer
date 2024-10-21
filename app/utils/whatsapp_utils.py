import logging
from flask import current_app, jsonify
import json
import aiohttp
from app.services.openai_service import generate_response
import re
from collections import deque
import asyncio

# A deque to store recently processed message IDs
processed_messages = deque(maxlen=100)

async def log_http_response(response):
    logging.info(f"Status: {response.status}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    text = await response.text()
    logging.info(f"Body: {text}")

def get_text_message_input(recipient, text):
    return {
        "to": recipient,
        "text": text,
    }

async def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": data["to"],  # Correctly assigning the recipient
        "type": "text",    # Message type
        "text": {
            "body": data["text"],  # Correctly using 'body' for message content
        },
        "messaging_type": "RESPONSE",  # Specify the messaging type
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, timeout=10) as response:
                await log_http_response(response)
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            logging.error("Timeout occurred while sending message")
            return {"status": "error", "message": "Request timed out"}, 408
        except aiohttp.ClientError as e:
            logging.error(f"Request failed due to: {e}")
            return {"status": "error", "message": "Failed to send message"}, 500
        

def process_text_for_whatsapp(text):
    pattern = r"\【.*?\】"
    text = re.sub(pattern, "", text).strip()
    pattern = r"\*\*(.*?)\*\*"
    replacement = r"*\1*"
    whatsapp_style_text = re.sub(pattern, replacement, text)
    return whatsapp_style_text

async def process_whatsapp_message(body):
    message_id = body["entry"][0]["changes"][0]["value"]["messages"][0]["id"]

    if message_id in processed_messages:
        logging.info(f"Message {message_id} already processed. Skipping.")
        return

    processed_messages.append(message_id)

    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]

    if "location" in message:
        location = message["location"]
        message_body = f"""موقعي الحالي هو:
            خط العرض: {location['latitude']}
            خط الطول: {location['longitude']} """
    elif "text" in message:
        message_body = message["text"]["body"]
    else:
        message_body = "I can handle text messages and locations. Please send either of those."

    response = await generate_response(message_body, wa_id, name)
    response = process_text_for_whatsapp(response)

    data = get_text_message_input(wa_id, response)
    await send_message(data)

def is_valid_whatsapp_message(body):
    if not (body.get("object") and body.get("entry") and 
            body["entry"][0].get("changes") and 
            body["entry"][0]["changes"][0].get("value") and 
            body["entry"][0]["changes"][0]["value"].get("messages") and 
            body["entry"][0]["changes"][0]["value"]["messages"][0]):
        return False
        
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    return "text" in message or "location" in message