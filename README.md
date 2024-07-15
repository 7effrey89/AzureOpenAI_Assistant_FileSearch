# AzureOpenAI_Assistant_FileSearch
 Code sample of how to use the File Search feature for Azure OpenAI Assistants.

There are two demos:

## Demo1:
Create a chat history and attach a file to a message for the assistant to use in answering the user's question.
    
## Demo2:
Asking the AI Assistant a simple question that will be answered by the assistant. A predefined knowledge base (vector object) is connected to the assistant to help answer the question.

## Getting Started: 
To get started simply uncomment one of the following lines to run a demo in the FileSearch.py

```
############################### Select Demo ###############################
# Uncomment one of the following lines to run a demo

thread = example1_chathistory_and_msgAttachment(client) #Demo1
#thread = example2_simpleMsg(client) #Demo2

############################### Select Demo ###############################
```


