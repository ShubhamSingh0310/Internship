import tkinter as tk
from tkinter import scrolledtext
from online_logic import get_online_response
from offline_logic import get_offline_response
import webbrowser
import os
import speech_recognition as sr
from PIL import Image, ImageTk
import threading
import time
import requests

mode = "offline"
current_theme = "dark"
WEATHER_API_KEY = "0e2d606fa6f79d97c161709e141ad70d"

def convert_currency(amount, from_currency, to_currency):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        response = requests.get(url)
        data = response.json()
        rate = data['rates'][to_currency.upper()]
        converted = amount * rate
        return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}"
    except Exception:
        return "Currency conversion failed."

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url)
        data = res.json()
        if data.get("cod") != 200:
            return "City not found."
        weather_desc = data['weather'][0]['description'].capitalize()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        return f"🌤 Weather in {city.title()}:\nDescription: {weather_desc}\nTemperature: {temp}°C\nHumidity: {humidity}%\nWind Speed: {wind} m/s"
    except:
        return "Weather fetch failed."

def toggle_mode():
    global mode
    if mode == "offline":
        mode = "online"
        status_label.config(text="Mode: Online", bg="#c5f2c7")
    else:
        mode = "offline"
        status_label.config(text="Mode: Offline", bg="#f2dede")

def toggle_theme():
    global current_theme
    if current_theme == "dark":
        root.config(bg="white")
        chat_area.config(bg="white", fg="black")
        frame.config(bg="white")
        button_frame.config(bg="white")
        suggestion_frame.config(bg="white")
        status_label.config(bg="lightgray", fg="black")
        current_theme = "light"
    else:
        root.config(bg="#121212")
        chat_area.config(bg="#1e1e1e", fg="white")
        frame.config(bg="#121212")
        button_frame.config(bg="#121212")
        suggestion_frame.config(bg="#121212")
        status_label.config(bg="#f2dede", fg="black")
        current_theme = "dark"

def open_booking():
    webbrowser.open("https://www.makemytrip.com")

def open_nearby_places():
    webbrowser.open("https://www.google.com/maps/search/places+near+me")

def insert_bot_response_animated(response):
    def type_response():
        chat_area.config(state='normal')
        chat_area.insert(tk.END, "Bot: ", 'bot')
        for char in response:
            chat_area.insert(tk.END, char, 'bot')
            chat_area.see(tk.END)
            chat_area.update()
            time.sleep(0.02)
        chat_area.insert(tk.END, "\n\n")
        chat_area.config(state='disabled')
    threading.Thread(target=type_response).start()

def set_suggestion_text(text):
    entry.delete("1.0", tk.END)
    entry.insert(tk.END, text)

def send_message():
    user_input = entry.get("1.0", tk.END).strip()
    if not user_input:
        return

    chat_area.config(state='normal')
    chat_area.insert(tk.END, f"You: {user_input}\n", 'user')
    chat_area.config(state='disabled')
    entry.delete("1.0", tk.END)

    def process_response():
        user_lower = user_input.lower()

        if "convert" in user_lower and "to" in user_lower:
            parts = user_lower.split()
            try:
                amount = float(parts[1])
                from_currency = parts[2]
                to_currency = parts[4]
                response = convert_currency(amount, from_currency, to_currency)
            except:
                response = "Please use format: convert 100 USD to INR"
        elif "weather in" in user_lower:
            city = user_lower.split("weather in")[-1].strip()
            response = get_weather(city)
        else:
            try:
                if mode == "online":
                    response = get_online_response(user_input)
                else:
                    response = get_offline_response(user_input)
            except:
                response = "Error fetching response. Please check your internet connection."

        insert_bot_response_animated(response)

    threading.Thread(target=process_response).start()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            entry.delete("1.0", tk.END)
            entry.insert(tk.END, user_input)
            send_message()
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError:
            print("Speech service error.")

root = tk.Tk()
root.title("YATRAMATE")
root.geometry("600x750")
root.config(bg="#121212")

status_label = tk.Label(root, text="Mode: Offline", bg="#f2dede", fg="black", font=("Helvetica", 10, "bold"))
status_label.pack(pady=5, fill=tk.X)

logo_img = Image.open("images/logo.png").resize((100, 100), Image.Resampling.LANCZOS)
logo_img = ImageTk.PhotoImage(logo_img)
logo_label = tk.Label(root, image=logo_img, bg="#121212")
logo_label.pack(pady=5)

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), bg="#1e1e1e", fg="white")
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.tag_config('user', foreground='cyan')
chat_area.tag_config('bot', foreground='white')
chat_area.config(state='disabled')

frame = tk.Frame(root, bg="#121212")
frame.pack(pady=10, fill=tk.X, padx=10)

entry = tk.Text(frame, font=("Arial", 12), height=3, bd=2, relief="solid", fg="white", bg="#1e1e1e", insertbackground="white")
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

# Icons
send_icon = Image.open("images/send_icon.png").resize((20, 20))
send_icon = ImageTk.PhotoImage(send_icon)

voice_icon = Image.open("images/voice_icon.png").resize((20, 20))
voice_icon = ImageTk.PhotoImage(voice_icon)

toggle_icon = Image.open("images/toggle_icon.png").resize((20, 20))
toggle_icon = ImageTk.PhotoImage(toggle_icon)

# Suggestion buttons
suggestion_frame = tk.Frame(root, bg="#121212")
suggestion_frame.pack(pady=5)

suggestions = ["Best hotels in Delhi", "Weather in Mumbai", "Convert 100 USD to INR", "Tourist spots in Assam"]
for text in suggestions:
    btn = tk.Button(suggestion_frame, text=text, font=("Arial", 9), command=lambda t=text: set_suggestion_text(t),
                    bg="#333", fg="white", padx=10, pady=2)
    btn.pack(side=tk.LEFT, padx=5)

# Button frame
button_frame = tk.Frame(root, bg="#121212")
button_frame.pack(pady=0)

send_button = tk.Button(button_frame, image=send_icon, bg="#4caf50", command=send_message)
send_button.grid(row=0, column=0, padx=10)

voice_button = tk.Button(button_frame, image=voice_icon, bg="#ff9800", command=listen)
voice_button.grid(row=0, column=1, padx=10)

toggle_button = tk.Button(button_frame, image=toggle_icon, bg="#2196f3", command=toggle_mode)
toggle_button.grid(row=0, column=2, padx=10)

switch_theme_button = tk.Button(button_frame, text="Theme", bg="#9c27b0", fg="white", command=toggle_theme)
switch_theme_button.grid(row=0, column=3, padx=10)

book_button = tk.Button(button_frame, text="Booking", bg="#e91e63", fg="white", command=open_booking)
book_button.grid(row=0, column=4, padx=10)

nearby_button = tk.Button(button_frame, text="Nearby", bg="#009688", fg="white", command=open_nearby_places)
nearby_button.grid(row=0, column=5, padx=10)

root.mainloop()