import speech_recognition as sr
from twilio.rest import Client
import os

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def listen_for_help(user_phone):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        if "help me" in text.lower():
            client.messages.create(
                body="Emergency! Help needed. Location: XYZ",
                from_=TWILIO_PHONE,
                to=user_phone
            )
            return "SOS Alert Sent!"
    except:
        return "Could not recognize."
