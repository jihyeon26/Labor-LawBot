import os
import requests
from dotenv import load_dotenv
import os
import re
from stt_tts import request_tts

load_dotenv()

# Load environment variables
GPT_ENDPOINT = os.getenv("GPT_ENDPOINT")
GPT_API_KEY = os.getenv("GPT_API_KEY")
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
AI_SEARCH_KEY = os.getenv("AI_SEARCH_KEY")
AI_SEARCH_INDEX = os.getenv("AI_SEARCH_INDEX")
AI_SEARCH_SEMANTIC = os.getenv("AI_SEARCH_SEMANTIC")

# Function to extract a limited number of message history for GPT request
def get_history_messages(histories):
    history_list = list()

    history_length = 5  # Define maximum number of message pairs to keep
    history_index = 0

    # Iterate through the history of messages
    for history in histories:
        
        if history_index >= history_length:
            break
        # Separate user and assistant messages
        message1 = history[0]
        message2 = history[1]
        
        # Add the messages to the list in a structured format
        history_list.append({
            "role": "assistant",
            "content": message1
        })
        history_list.append({
            "role": "assistant",
            "content": message2               
        })
        
        history_index += 1
        
    return history_list

# Function to request GPT for a response
def request_gpt(prompt, history_list):
    headers = {"Content-Type": "application/json", "api-key": GPT_API_KEY}
    message_list = list()
    
    # System role message to instruct GPT
    message_list.append({
        "role": "system",
        "content": "You're a labor law expert, please answer with case law references and add the relevant case number below your answer."       
    })
    # Add message history to the payload
    message_list.extend(history_list)
    # Add the user prompt to the payload
    message_list.append({
        "role": "user",
        "content":prompt
    })
    # Define the payload with GPT settings and Azure Search configuration
    payload = {
        "messages": message_list,
        "temperature": 0.09,
        "top_p": 0.4,
        "max_tokens": 800,
        "data_sources": [
        {
            "type": "azure_search",
            "parameters": {
                "endpoint": AI_SEARCH_ENDPOINT,
                "semantic_configuration": AI_SEARCH_SEMANTIC,
                "query_type": "semantic",
                "strictness": 5,
                "top_n_documents": 5,
                "key": AI_SEARCH_KEY,
                "indexName": AI_SEARCH_INDEX
            }
        }
        ]
    }
    
    response = requests.post(GPT_ENDPOINT, headers=headers, json=payload)
    
    if response.status_code == 200:
        response_json = response.json()
        content = response_json["choices"][0]["message"]["content"]
        
        # Check if there are any citations in the response
        if response_json["choices"][0]["message"]["context"]:
            citations = response_json["choices"][0]["message"]["context"]["citations"]
            formatted_citation_list = list()
            i = 0
            for c in citations:
                i += 1
                temp = f"<details><summary>Citation{i}</summary><ul>{c['content']}</ul></details>"
                formatted_citation_list.append(temp)
                
        else:
            formatted_citation_list = list() # No citations
            
        return content, "".join(formatted_citation_list) # Return response content and formatted citations
    else:
        return f"{response.status_code}, {response.text}", ""

# Function to handle user prompt submission
def click_send(prompt, histories):
    # Retrieve message history for the GPT request
    history_list = get_history_messages(histories=histories)
    # Send the prompt and history to GPT and get the response
    response_text, citation_html = request_gpt(prompt, history_list)
    histories.append((prompt, response_text))
    return histories, "", citation_html

# Function to generate an audio response for the chatbot
def change_chatbot(histories):
        # Extract the last response from the chatbot history
        #[(prompt, assistant)]
        assistant_text = histories[-1][1]
        
        # Remove special characters and retain only letters, numbers, and spaces
        pattern = r'[^가-힣a-zA-Z0-9\s]'
        formmated_response_text = re.sub(pattern, '', assistant_text)
        
        # Generate an audio file using TTS for the formatted text
        audio_file_name = request_tts(formmated_response_text)
        return audio_file_name