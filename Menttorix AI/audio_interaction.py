import os
import google.generativeai as genai
import pyaudio
import wave
import tempfile
import keyboard
import threading
import numpy as np
from google.oauth2 import service_account
from deepgram_speaker import DeepgramSpeaker
from dotenv import load_dotenv

load_dotenv()

# Set up Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# Create an instance of DeepgramSpeaker
speaker = DeepgramSpeaker(os.getenv('DEEPGRAM_API_KEY'))

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SILENCE_THRESHOLD = 500  # Adjust this value based on your microphone and environment
SILENCE_DURATION = 3  # Silence duration in seconds to stop recording

def is_silent(data_chunk):
    """Check if the audio chunk is silent."""
    return max(abs(np.frombuffer(data_chunk, dtype=np.int16))) < SILENCE_THRESHOLD

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("Recording... (Press 'q' to stop manually or stay silent for 3-5 seconds)")
    frames = []
    silent_chunks = 0
    stop_recording = False

    def check_stop_key():
        nonlocal stop_recording
        keyboard.wait('q')
        stop_recording = True

    # Start a thread to listen for the stop key
    stop_thread = threading.Thread(target=check_stop_key)
    stop_thread.start()

    while not stop_recording:
        data = stream.read(CHUNK)
        frames.append(data)
        if is_silent(data):
            silent_chunks += 1
            if silent_chunks > SILENCE_DURATION * (RATE / CHUNK):
                break
        else:
            silent_chunks = 0

    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    stop_thread.join(timeout=1)  # Ensure the thread is properly closed

    # Save the recorded audio to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        wf = wave.open(temp_audio_file.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    return temp_audio_file.name

def process_audio(audio_file_path, conversation_history):
    with open(audio_file_path, 'rb') as audio_file:
        audio_data = audio_file.read()
    
    system_message = """
    You are a friendly and knowledgeable student buddy AI called Menttorix. Your role is to assist students with their questions, 
    provide explanations, and offer encouragement. Use a supportive and patient tone, and try to explain concepts 
    in ways that are easy for students to understand. If a student seems confused, offer to explain things in a 
    different way. Always be positive and motivating in your responses and MAINTAIN A SHORT AND CONCISE RESPONSE.
    """
    
    prompt = f"""
    Please respond to the student's audio input, keeping in mind your role as a student buddy.
    Here's the conversation history:
    {conversation_history}
    
    Now, respond to the new audio input:
    """
    
    response = model.generate_content([
        system_message,
        prompt,
        {"mime_type": "audio/wav", "data": audio_data}
    ])
    return response.text

def main():
    print("Welcome to your Student Buddy AI!")
    print("Speak after pressing Enter. The recording will stop after 3-5 seconds of silence or when you press 'q'.")
    
    conversation_history = []
    
    while True:
        input("Press Enter to start recording...")
        audio_file_path = record_audio()
        
        print("Processing your input...")
        response = process_audio(audio_file_path, "\n".join(conversation_history))
        
        
        speaker.speak(response, "output_audio.wav")
        print("Student Buddy AI:", response)
        print("\n" + "-"*50 + "\n")
        
        # Add the response to the conversation history
        conversation_history.append(f"Student Buddy AI: {response}")
        
        # Limit the conversation history to the last 5 exchanges
        conversation_history = conversation_history[-5:]
        
        # Clean up the temporary audio file
        os.unlink(audio_file_path)
        
        if input("Do you want to continue? (y/n): ").lower() != 'y':
            break
    
    print("Thank you for using Student Buddy AI. Goodbye!")

if __name__ == "__main__":
    main()
