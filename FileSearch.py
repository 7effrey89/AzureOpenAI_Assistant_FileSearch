import os
import json
from openai import AzureOpenAI
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
import time

#-----------------------------Functions used in this script-----------------------------------
#Description: Drop all assistants, or those of a specific name e.g. "Demo Analyst Assistant"
def drop_assistants(client, assistant_name):
    #Show all assistants
    my_assistants = client.beta.assistants.list(
        order="desc",
        # limit="20",
    )
    # print(my_assistants.data)

    #delete all assistants that has name: "Demo Analyst Assistant"
    for assistant in my_assistants.data:
        if assistant.name == assistant_name:
            response = client.beta.assistants.delete(assistant.id)
            print("Assistant deleted:")
            print(response)

#Description: Drop all vector stores, or those of a specific name e.g. "specializedKnowledge"
def drop_vector_stores(client, vector_store_name):
    #delete all vector stores that has name: "specializedKnowledge"
    vector_stores = client.beta.vector_stores.list()
    # print(vector_stores)

    for vector_store in vector_stores.data:
        if vector_store.name == vector_store_name:
            response = client.beta.vector_stores.delete(vector_store.id)
            print("Vector Store deleted:")
            print(response)
        #else if the assistant_name is not provided, delete all vector stores
        elif vector_store_name == "":
            response = client.beta.vector_stores.delete(vector_store.id)
            print("Vector Store deleted:")
            print(response)

#-----------------------------Demoes-----------------------------------
#Demo1 Description: Create a chat history and attach a file to a message for the assistant to use in answering the user's question.
def example1_chathistory_and_msgAttachment(client):
    #Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Why is Donald Duck visiting Scrooge McDuck?"
            },
            {
                "role": "assistant",
                "content": "To have a short term reunification with his family during the Duckburg Fstival. "
            },
            {
                "role": "user",
                "content": "When is he coming?"
            ,
                # Attach the new file to the message.
                "attachments": [
                    { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
                ],
            }
        ]
    )
    return thread

#Demo2 Description: Asking the AI Assistant a simple question that will be answered by the assistant. 
# A predefined knowledge base (vector object) is connected to the assistant to help answer the question.
def example2_simpleMsg(client):
    #Crate a thread
    thread = client.beta.threads.create()

    # Add a user question to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="what are my benefits?" # Replace this with your prompt
    )
    return thread

#-----------------------------Let's go-----------------------------------
#-----------------------------Setting up Environment-----------------------------------
client = AzureOpenAI(
    api_key="<You-Azure-OpenAI-API-Key>",  # Replace this with your Azure OpenAI API key
    api_version="2024-05-01-preview",
    azure_endpoint = "https://<your-resourcename>.openai.azure.com/" # Replace this with your Azure OpenAI endpoint
    )

#Prepare the environment
drop_assistants(client, "Demo Analyst Assistant")
# drop_vector_stores(client, "specializedKnowledge")
drop_vector_stores(client, "")

#-----------------------------Create an assistant and vector store-----------------------------------
# # Create an assistant
assistant = client.beta.assistants.create(
  name="Demo Analyst Assistant",
  instructions="You are a helpful analyst. Use your knowledge base to answer questions to answer customer inquries.",
  model="gpt-4o",
  tools=[{"type": "file_search"}],
)

# # Create a vector store called "specializedKnowledge"
vector_store = client.beta.vector_stores.create(name="specializedKnowledge")
 
 # Construct the path relative to the current script's directory
script_dir = os.path.dirname(__file__)  # Directory of the script

# Ready the files for upload to OpenAI
file_paths = [
    os.path.join(script_dir, "mydirectory/PerksPlus.pdf"),
    os.path.join(script_dir, "mydirectory/JeffreyLaiDetails.txt")
]

file_streams = [open(path, "rb") for path in file_paths]
 
# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)
 
# # You can print the status and the file counts of the batch to see the result of this operation.
# print(file_batch.status)
# print(file_batch.file_counts)

#Update the assistant to use the new vector store
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

#----------------------------- run an assistant -----------------------------------

#Create a thread
# Upload the user provided file to OpenAI
attachment = os.path.join(script_dir, "mydirectory/Invitation letter - Donald.pdf")

message_file = client.files.create(
  file=open(attachment, "rb"), purpose="assistants"
)
 
# Create a thread for the conversation
############################### Select Demo ###############################
# Uncomment one of the following lines to run a demo

thread = example1_chathistory_and_msgAttachment(client) #Demo1
#thread = example2_simpleMsg(client) #Demo2

############################### Select Demo ###############################


# Run the thread
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)

# Looping until the run completes or fails
while run.status in ['queued', 'in_progress', 'cancelling']:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

if run.status == 'completed':
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  print('Message:')
  print(messages.data[0].content[0].text.value)

elif run.status == 'requires_action':
  # the assistant requires calling some functions
  # and submit the tool outputs back to the run
  pass
else:
  print(run.status)


