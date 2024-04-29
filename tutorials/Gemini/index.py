import os
import time
import pyaudio
import speech_recognition as sr
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
from faster_whisper import WhisperModel
from constants import safety_settings, system_message

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

wake_word = 'sarah'
whisper_size = "base"
listening_for_wake_word = True
generation_config = genai.GenerationConfig(
    temperature=0.5,
    top_p=1,
    top_k=1,
    max_output_tokens=2048
)

open_ai = OpenAI(api_key=OPENAI_API_KEY)
whisper_model = WhisperModel(whisper_size, device='cpu', compute_type='int8')
speech = sr.Recognizer()
source = sr.Microphone()

# setup model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro-latest',
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat()
convo.send_message(system_message)


def speak(text):
    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
    stream_start = False

    with open_ai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            response_format='pcm',
            input=text,
    ) as resp:
        silence_threshold = 0.01
        for chunk in resp.iter_bytes(chunk_size=1024):
            if stream_start:
                player_stream.write(chunk)
            elif max(chunk) > silence_threshold:
                player_stream.write(chunk)
                stream_start = True


def wav_to_text(audio_path):
    segments, _ = whisper_model.transcribe(audio_path)
    text = ''.join(segment.text for segment in segments)
    return text


def listen_for_wake_word(audio):
    global listening_for_wake_word
    wake_audio_path = 'wake_detect.wav'
    with open(wake_audio_path, 'wb') as f:
        f.write(audio.get_wav_data())

    text_input = wav_to_text(wake_audio_path)

    if wake_word in text_input.lower().strip():
        print("Wake word detected. Please speak now.")
        listening_for_wake_word = False


def prompt_gpt(audio):
    global listening_for_wake_word
    try:
        prompt_audio_path = 'prompt.wav'
        with open(prompt_audio_path, 'wb') as f:
            f.write(audio.get_wav_data())

        prompt_text = wav_to_text(prompt_audio_path)

        if len(prompt_text.strip()) == 0:
            print('Empty prompt. Speak again.')
            listening_for_wake_word = True
        else:
            print('User:' + prompt_text)
            convo.send_message(prompt_text)
            output = convo.last.text

            print('Gemini: ', output)
            speak(output)

            print('\n Say', wake_word, 'to wake me up. \n')
            listening_for_wake_word = True
    except Exception as e:
        print('Prompt error: ', e)


def callback(recognizer, audio):
    global listening_for_wake_word

    if listening_for_wake_word:
        listen_for_wake_word(audio)
    else:
        prompt_gpt(audio)


def start_listening():
    with source as s:
        speech.adjust_for_ambient_noise(s, duration=2)

    print('\n Say', wake_word, 'to wake me up. \n')

    speech.listen_in_background(source, callback)

    while True:
        time.sleep(0.5)


if __name__ == '__main__':
    start_listening()
