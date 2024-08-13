import json
import requests
import os
from openai import OpenAI
from assistant_insturctions import assistant_instructions
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# Init OpenAI Client
client = OpenAI()


# Add lead to Airtable
def create_lead(name="", company_name="", phone="", email=""):
    # Define the path to the TXT file
    file_path = "leads.txt"

    # Create a lead entry as a string
    lead_entry = f"Name: {name}\nCompany: {company_name}\nPhone: {phone}\nEmail: {email}\n{'-' * 40}\n"

    # Write the lead entry to the TXT file, appending it to any existing entries
    with open(file_path, "a") as file:
        file.write(lead_entry)

    print("Lead saved to leads.txt successfully.")
    return {"status": "success"}


# Create or load assistant
def create_assistant(client):
    assistant_file_path = 'assistant.json'

    # If there is an assistant.json file already, then load that assistant
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # If no assistant.json is present, create a new assistant using the below specifications

        # To change the knowledge document, modifiy the file name below to match your document
        # If you want to add multiple files, paste this function into ChatGPT and ask for it to add support for multiple files
        file = client.files.create(file=open("knowledge.docx", "rb"),
                                   purpose='assistants')

        assistant = client.beta.assistants.create(
            # Getting assistant prompt from "prompts.py" file, edit on left panel if you want to change the prompt
            instructions=assistant_instructions,
            model="gpt-4-turbo",
            tools=[
                {
                    "type": "retrieval"  # This adds the knowledge base as a tool
                },
                {
                    "type": "function",  # This adds the lead capture as a tool
                    "function": {
                        "name": "create_lead",
                        "description":
                            "Capture lead details and save to Airtable.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the lead."
                                },
                                "phone": {
                                    "type": "string",
                                    "description": "Phone number of the lead."
                                },
                                "email": {
                                    "type": "string",
                                    "description": "Email of the lead."
                                },
                                "company_name": {
                                    "type": "string",
                                    "description": "CompanyName of the lead."
                                }
                            },
                            "required": ["name", "email", "company_name"]
                        }
                    }
                }
            ],
            file_ids=[file.id])

        # Create a new assistant.json file to load on future runs
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id