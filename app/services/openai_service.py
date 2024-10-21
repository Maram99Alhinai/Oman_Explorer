from openai import OpenAI, AsyncOpenAI
client = AsyncOpenAI()
import shelve
from dotenv import load_dotenv
import os
import asyncio
import logging

load_dotenv(override=True)
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))




# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("data/threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("data/threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


async def run_assistant(thread, name):
    assistant = await client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

    run = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while run.status != "completed":
        await asyncio.sleep(0.5)
        run = await client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = await client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message

async def generate_response(message_body, wa_id, name):
    thread = await get_or_create_thread(wa_id)
    await client.beta.threads.messages.create(thread_id=thread.id, role="user", content=message_body)
    new_message = await run_assistant(thread, name)
    return new_message

async def get_or_create_thread(wa_id):
    thread_id = check_if_thread_exists(wa_id)
    if thread_id is None:
        logging.info(f"Creating new thread for wa_id {wa_id}")
        thread = await client.beta.threads.create()
        store_thread(wa_id, thread.id)
    else:
        logging.info(f"Retrieving existing thread for wa_id {wa_id}")
        thread = await client.beta.threads.retrieve(thread_id)
    return thread
