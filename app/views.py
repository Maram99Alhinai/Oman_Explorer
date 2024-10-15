import logging
import json
import threading
from flask import Blueprint, request, jsonify, current_app
from .decorators.security import signature_required
from .utils.whatsapp_utils import (process_whatsapp_message, is_valid_whatsapp_message)
import asyncio

webhook_blueprint = Blueprint("webhook", __name__)


def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.get_json()

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            asyncio.run_coroutine_threadsafe(process_whatsapp_message(body), asyncio.get_event_loop())
            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            return jsonify({"status": "error", "message": "Not a WhatsApp API event"}), 404
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400


def handle_message_async(body):
    """
    This function runs in a separate thread to process incoming WhatsApp messages asynchronously.
    """
    process_whatsapp_message(body)


@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    """
    Handles incoming POST requests from the WhatsApp API webhook.

    It processes the message asynchronously by spawning a new thread for message processing.
    This ensures that the response to WhatsApp is immediate while the message is processed in the background.

    Returns:
        response: A JSON response with status 200 to WhatsApp to acknowledge the receipt.
    """
    body = request.get_json()

    # Respond with 200 immediately, then process the message in a background thread
    thread = threading.Thread(target=handle_message_async, args=(body,))
    thread.start()

    return jsonify({"status": "ok"}), 200


# Required webhook verification for WhatsApp
def verify():
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()
