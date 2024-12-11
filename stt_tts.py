import os
import azure.cognitiveservices.speech as speechsdk
import requests
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SPEECH_REGION = os.getenv("SPEECH_REGION")
SPEECH_KEY = os.getenv("SPEECH_KEY")

# Function to recognize speech from an audio file(English) and translate to Korean
def recognize_from_microphone(audio_file):
    # Speech translation configuration
    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_translation_config.speech_recognition_language="en-US" # Input language

    to_language ="ko" # Target translation language
    speech_translation_config.add_target_language(to_language)

    # Configure audio input settings
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
    translation_recognizer = speechsdk.translation.TranslationRecognizer(translation_config=speech_translation_config, audio_config=audio_config)

    # Perform recognition and translation
    result = translation_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.TranslatedSpeech:
        return result.text, result.translations[to_language]
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

# Function to perform speech-to-text (STT) using Azure REST API
def request_stt(file_path):
    endpoint = f"https://{SPEECH_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=ko-KR&format=detailed"
    headers = {'Ocp-Apim-Subscription-Key': SPEECH_KEY, 'Content-Type': 'audio/wav'}
    with open(file_path, "rb") as audio:
        audio_data = audio.read()
     
    # Send POST request to Azure STT service
    response = requests.post(endpoint, headers=headers, data=audio_data)
    if response.status_code == 200:
        response_json = response.json()
        is_succeed = response_json["RecognitionStatus"] == "Success"
        if is_succeed:
            response_text = response_json["DisplayText"]
        else:
            response_text = ""
        return response_text # Return recognized text
    else:
        return ""


# Developed but passed due to the need to purchase new resources.   
def request_stt_fast(file_path):
    # Fast STT implementation
    pass  

# Function to perform text-to-speech (TTS) using Azure REST API 
def request_tts(text):
    endpoint = f"https://{SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        'Ocp-Apim-Subscription-Key': SPEECH_KEY,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3'
    }
    payload = f"<speak version='1.0' xml:lang='ko-KR'><voice xml:lang='en-US' xml:gender='Female' name='ko-KR-SunHiNeural'>{text}</voice></speak>"
    response = requests.post(endpoint, headers=headers, data=payload)
    if response.status_code == 200:
        with open("response_audio.wav", "wb") as audio_file:
            audio_file.write(response.content) # Save audio response to a file
        return "response_audio.wav" # Return the name of the audio file
    return "" 

# Function to handle audio file processing and return recognized text
def change_audio(file_path, radio):
    if file_path:
        # Determine which STT method to use based on the radio button selection
        if radio == "Fast Text Conversion":
            response_text = request_stt_fast(file_path=file_path)
        else:
            response_text = request_stt(file_path=file_path)
        return response_text
    else:
        return ""

# Function to handle TTS for a given text
def click_tts_send(text):
        audio_file_name = request_tts(text)
        return audio_file_name