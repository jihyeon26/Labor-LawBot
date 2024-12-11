import os
import gradio as gr
from dotenv import load_dotenv
from stt_tts import recognize_from_microphone, request_stt, request_stt_fast, request_tts
from gpt import click_send, change_chatbot
from stt_tts import change_audio

# Load environment variables
load_dotenv()

### Web UI ###
with gr.Blocks(css="styles.css") as demo:
    # Header Section
    with gr.Row():
        # Logo Section
        with gr.Column(scale=1, min_width=60):
            gr.Image(value="logo_n.png", show_label=False, show_download_button=False, show_fullscreen_button=False, elem_id="logo")
        # Title Section
        with gr.Column(scale=9):
            gr.Markdown("""
            # Labor LawBot  
            **Trusted AI labor law case search service**
            """, elem_id="title")
    # Description Section
    with gr.Column():
        gr.HTML("""
        <div class="description-box">
            <p><strong>How to use Labor LawBot:</strong></p>
            <ul>
                <li>Enter a labor law case law question in the question field (e.g., tell me a wrongful termination case).</li>
                <li>In the translation tab, record your voice in English, and it will be translated into Korean and sent to the prompt window.</li>
                <li>You can check the case information in the citation area.</li>
                <li>AI can make mistakes. Use the information in the reference area to search for additional information.</li>
            </ul>
        </div>
        """)

    # Main Interaction Area
    with gr.Row():
        with gr.Column(scale=3):   
            # Chatbot, Citation area
            with gr.Row(elem_id="chatbot-container"):
                chatbot = gr.Chatbot(label="Chat history", elem_classes="chatbot")
                citation = gr.HTML(label="reference area", elem_classes="citation-box")
            # Input Box and Submit Button
            with gr.Row(elem_id="input-container"):
                input_openai_textbox = gr.Textbox(label="", elem_id="textbox", scale=7, placeholder="질문을 입력하세요...")
                send_button = gr.Button("Submit", elem_id="button", scale=1)
            
            chatbot_audio = gr.Audio(label='GPT', interactive=False, autoplay=True)

            # Connect the chatbot and button functionality
            input_openai_textbox.submit(fn=click_send, inputs=[input_openai_textbox, chatbot], outputs=[chatbot, input_openai_textbox, citation])
            send_button.click(fn=click_send, inputs=[input_openai_textbox, chatbot], outputs=[chatbot, input_openai_textbox, citation])
            chatbot.change(fn=change_chatbot, inputs=[chatbot], outputs=[chatbot_audio])

            
        # Speech-to-Text (STT) and Translation Tabs
        with gr.Column(scale=1):
            with gr.Column():
                # STT
                with gr.Tab("STT") as stt:
                    gr.Markdown("<h3>STT</h3>")    
                    input_mic = gr.Audio(label="Microphone input", type="filepath", sources="microphone", waveform_options=gr.WaveformOptions(
                        waveform_color="#00FFFF",
                        waveform_progress_color="#FF00FF",
                        skip_length=2,
                        show_controls=False
                    ))
                    
                    stt_type_radio = gr.Radio(["Fast Text Conversion", "Standard Text Conversion"], label="Conversion Type", info="Conversion speed", value="Standard Text Conversion")
                    
                    input_mic.change(fn=change_audio, inputs=[input_mic, stt_type_radio], outputs=[input_openai_textbox])
                
                # Translate    
                with gr.Tab("Translate") as translate:
                    gr.Markdown("<h3>Translate</h3>")
                    input_mic2 = gr.Audio(label="Mic input", type="filepath", sources="microphone", waveform_options=gr.WaveformOptions(
                        waveform_color="#00FFFF",
                        waveform_progress_color="#FF00FF",
                        skip_length=2,
                        show_controls=False
                    ))
                    input_translate_textbox = gr.Textbox(label="Input text", placeholder="Recognized text")

                    input_mic2.change(fn=recognize_from_microphone, inputs=input_mic2, outputs=[input_translate_textbox, input_openai_textbox])
                    
demo.launch()