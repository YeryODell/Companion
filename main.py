from pygame import mixer
from time import sleep

import asyncio
import edge_tts
import ollama
import os
import pyttsx3
import speech_recognition as sr
import subprocess


VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "voice.mp3"
r = sr.Recognizer()


def SpeakText(command):
    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


async def genAudio(text):
    """Main function"""
    communicate = edge_tts.Communicate(text, VOICE)
    with open(OUTPUT_FILE, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])

    mixer.init()
    mixer.music.load("voice.mp3")
    mixer.music.play()
    while mixer.music.get_busy():
        sleep(1)
    mixer.music.unload()


async def main():
    user_content = ""
    client = ollama.AsyncClient()
    messages = []
    print("Samantha: Hello")
    await genAudio("Hello")

    while user_content != "I'll talk to you later":

        try:
            print("<>")
            # use the microphone as source for input.
            with sr.Microphone() as source2:

                # wait for a second to let the recognizer
                # adjust the energy threshold based on
                # the surrounding noise level
                r.adjust_for_ambient_noise(source2, duration=0.2)

                # listens for the user's input
                audio2 = r.listen(source2)

                # Using google to recognize audio
                user_content = r.recognize_google(audio2)
                print("Me: ", user_content)


        except sr.RequestError as e:
            # print("Could not request results; {0}".format(e))
            print("Samantha: I didn't catch that. Can you please say it again?")
            await genAudio("I didn't catch that. Can you please say it again?")
            continue

        except sr.UnknownValueError:
            # print("unknown error occurred")
            print("Samantha: I'm hearing extra noise, so it may be difficult to hear you. Can you please try again?")
            await genAudio("I'm hearing extra noise, so it may be difficult to hear you. Can you please try again?")
            continue

        messages.append(
            {
                'role': 'user',
                'content': user_content
            }
        )

        message = {'role': 'assistant', 'content': ''}
        async for response in await client.chat(model='samantha-mistral:latest', messages=messages, stream=True):
            # print(response)
            if response['done']:
                messages.append(message)
                print("Samantha: ", message['content'])
                await genAudio(message['content'])

            content = response['message']['content']
            message['content'] += content


try:
    asyncio.run(main())
except (KeyboardInterrupt, EOFError):
    ...
