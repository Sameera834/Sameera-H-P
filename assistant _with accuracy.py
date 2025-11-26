import os
import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import subprocess
import pywhatkit
import psutil
import pyjokes
import sys
import platform
import socket
import random
import json
import keyboard
import requests
from bs4 import BeautifulSoup
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# File to persist assistant state like name
STATE_FILE = "assistant_state.json"

# Load or initialize assistant state
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"assistant_name": "Jarvis", "master_name": "Master"}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

state = load_state()
assistant_name = state.get("assistant_name", "Jarvis")
master_name = state.get("master_name", "Master")

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
engine.setProperty('rate', 170)  # Speech rate

# Metrics tracking
successful_tasks = 0
total_tasks = 0
is_awake = True  # Assistant state

# Initialize volume control
def get_volume_control():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

volume_control = get_volume_control()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_command(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        r.adjust_for_ambient_noise(source, duration=2)  # Adjust for ambient noise
        print("Listening for command...")
        try:
            audio = r.listen(source, timeout=timeout)  # Set a timeout for listening
            query = r.recognize_google(audio, language='en-in').lower()
            print(f"Heard: {query}")
            return query
        except sr.UnknownValueError:
            if is_awake:
                speak("Sorry, I didn't catch that. Please repeat.")
        except sr.RequestError:
            if is_awake:
                speak("Sorry, my speech service is down.")
        except sr.WaitTimeoutError:
            if is_awake:
                speak("Listening timed out. Please try again.")
    return "None"

def get_current_time():
    return datetime.datetime.now().strftime("%I:%M %p")

def get_current_date():
    return datetime.datetime.now().strftime("%B %d, %Y")

def open_youtube_search(query):
    speak(f"Playing {query} on YouTube.")
    pywhatkit.playonyt(query)

def open_website(url):
    speak(f"Opening the website: {url}.")
    webbrowser.open(url)

def summarize_search(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('h3')
    if results:
        main_content = results[0].get_text()
        speak(f"The main content of your search is: {main_content}")
    else:
        speak("I couldn't find any relevant information.")

def get_system_info():
    uname = platform.uname()
    sys_info = f"System: {uname.system}, Node Name: {uname.node}, Release: {uname.release}, Version: {uname.version}, Machine: {uname.machine}, Processor: {uname.processor}"
    return sys_info

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

def get_ip_address():
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
        return ip_address
    except:
        return "Could not fetch IP address"

def open_app(app_name):
    try:
        if sys.platform == "win32":
            if app_name == "calculator":
                subprocess.Popen('calc.exe')
            elif app_name == "notepad":
                subprocess.Popen('notepad.exe')
            elif app_name == "cmd":
                subprocess.Popen('cmd.exe')
            elif app_name == "paint":
                subprocess.Popen('mspaint.exe')
            elif app_name == "excel":
                subprocess.Popen('Excel.exe')
            elif app_name == "powerpoint":
                subprocess.Popen("PowerPoint.exe")
            elif app_name == "vscode":
                subprocess.Popen("Visual Studio Code.exe")
            elif app_name == "word":
                subprocess.Popen("Word.exe")
            elif app_name == "nfs":
                subprocess.Popen("Speed.exe")
            else:
                speak("Application not configured for Windows.")
        elif sys.platform == "darwin":
            if app_name == "calculator":
                subprocess.Popen(["open", "-a", "Calculator"])
            elif app_name == "textedit":
                subprocess.Popen(["open", "-a", "TextEdit"])
            else:
                speak("Application not configured for macOS.")
        else:
            speak("Unsupported operating system for app launching.")
    except Exception as e:
        speak(f"Failed to open {app_name}. Error: {str(e)}")

def close_app(app_name):
    try:
        if sys.platform == "win32":
            if app_name == "calculator":
                os.system(f'taskkill /im calc.exe /f')
            elif app_name == "notepad":
                os.system(f'taskkill /im notepad.exe /f')
            elif app_name == "cmd":
                os.system(f'taskkill /im cmd.exe /f')
            elif app_name == "paint":
                os.system(f'taskkill /im mspaint.exe /f')
            elif app_name == "excel":
                os.system(f'taskkill /im Excel.exe /f')
            elif app_name == "powerpoint":
                os.system(f'taskkill /im PowerPoint.exe /f')
            elif app_name == "vscode":
                os.system(f'taskkill /im "Visual Studio Code.exe" /f')
            elif app_name == "word":
                os.system(f'taskkill /im Word.exe /f')
            elif app_name == "nfs":
                os.system(f'taskkill /im Speed.exe /f')
        elif sys.platform == "darwin":
            os.system(f'pkill {app_name}')
        else:
            speak("Closing applications is not supported on this OS.")
    except Exception as e:
        speak(f"Failed to close {app_name}. Error: {str(e)}")

def shutdown_computer():
    try:
        if sys.platform == "win32":
            subprocess.call('shutdown /s /t 1', shell=True)
        elif sys.platform in ["darwin", "linux"]:
            subprocess.call('shutdown now', shell=True)
        else:
            speak("Shutdown command not supported on this OS.")
    except Exception as e:
        speak(f"Failed to shutdown. Error: {str(e)}")

def restart_computer():
    try:
        if sys.platform == "win32":
            subprocess.call('shutdown /r /t 1', shell=True)
        elif sys.platform in ["darwin", "linux"]:
            subprocess.call('reboot', shell=True)
        else:
            speak("Restart command not supported on this OS.")
    except Exception as e:
        speak(f"Failed to restart. Error: {str(e)}")

def battery_status():
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = battery.power_plugged
            status = "plugged in" if plugged else "not plugged in"
            return f"Battery is at {percent} percent and is currently {status}."
        else:
            return "No battery information available."
    else:
        return "Battery information not supported on this system."

def open_file(filepath):
    try:
        if os.path.exists(filepath):
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.call(["open", filepath])
            else:
                subprocess.call(["xdg-open", filepath])
        else:
            speak("File does not exist.")
    except Exception as e:
        speak(f"Failed to open file. {str(e)}")

def play_music():
    speak("Playing your playlist on YouTube.")
    pywhatkit.playonyt("Top trending music playlist")

def pause_music():
    speak("Pausing the music.")
    keyboard.press_and_release('space')  # Simulate space key to pause

def resume_music():
    speak("Resuming the music.")
    keyboard.press_and_release('space')  # Simulate space key to resume

def next_music():
    speak("Playing the next track.")
    # Implement next track functionality if using a specific music player API

def volume_up():
    current_volume = volume_control.GetMasterVolumeLevelScalar()
    if current_volume < 1.0:
        volume_control.SetMasterVolumeLevelScalar(current_volume + 0.1, None)  # Pass None as the second argument
        speak("Volume increased.")
    else:
        speak("Volume is already at maximum.")

def volume_down():
    current_volume = volume_control.GetMasterVolumeLevelScalar()
    if current_volume > 0.0:
        volume_control.SetMasterVolumeLevelScalar(current_volume - 0.1, None)  # Pass None as the second argument
        speak("Volume decreased.")
    else:
        speak("Volume is already at minimum.")

def mute():
    volume_control.SetMute(1, None)
    speak("Audio muted.")

def unmute():
    volume_control.SetMute(0, None)
    speak("Audio unmuted.")

def say_greeting():
    hour = datetime.datetime.now().hour
    greet = ""
    if 0 <= hour < 12:
        greet = "Good morning!"
    elif 12 <= hour < 18:
        greet = "Good afternoon!"
    else:
        greet = "Good evening!"
    speak(greet)

def respond_to_feeling(feeling):
    if feeling in ["bored", "i am bored", "feeling bored"]:
        speak("Let me play some videos to cheer you up.")
        pywhatkit.playonyt("funny videos")
    elif feeling in ["tired", "i am tired"]:
        speak("You should relax. Let me play some relaxing music for you.")
        pywhatkit.playonyt("relaxing music")
    elif feeling in ["sad", "i am sad"]:
        speak("I'm sorry you're feeling sad. Here's something to lighten up your mood.")
        pywhatkit.playonyt("uplifting songs")
    elif feeling in ["happy", "i am happy"]:
        speak("Great to hear that! Keep smiling.")
    else:
        speak("I am here to help you!")

def list_running_processes():
    procs = psutil.pids()
    proc_names = []
    try:
        for pid in procs[:10]:
            p = psutil.Process(pid)
            proc_names.append(p.name())
        speak("Here are some running processes on your computer:")
        speak(", ".join(proc_names))
    except:
        speak("Unable to retrieve running processes.")

def tell_about_me():
    speak(f"My name is {assistant_name}. I am your personal desktop assistant. I'm here to make your life easier!, and I was made by Hariharan, Krupa M C and Sameera Boss")

def exit_assistant():
    speak(f"Goodbye, {master_name}! Have a nice day master.")
    save_state({"assistant_name": assistant_name, "master_name": master_name})
    sys.exit()

def ask_change_name():
    global assistant_name
    speak(f"Do you want me to change my name from {assistant_name}? Please say yes or no. master")
    response = take_command(timeout=10)  # Increased timeout for better response
    if response in ["yes", "yeah", "yep", "sure"]:
        speak("Please tell me the new name you want me to have master.")
        new_name = take_command(timeout=10)  # Increased timeout for better response
        if new_name != "None" and new_name.strip() != "":
            old_name = assistant_name
            assistant_name = new_name.strip().split()[0].capitalize()
            speak(f"My name has been changed from {old_name} to {assistant_name}.")
            save_state({"assistant_name": assistant_name, "master_name": master_name})
            return
        else:
            speak("I didn't catch the name. I'll keep my current name.")
            return
    elif response in ["no", "nope", "nah"]:
        speak(f"Okay, I will keep the name {assistant_name}.")
        return
    speak("I didn't get your answer. I'll keep my current name.")

def process_command(query):
    global assistant_name, master_name, successful_tasks, total_tasks, is_awake
    lc_query = query.lower()
    total_tasks += 1  # Increment total tasks

    if "wake up" in lc_query:
        is_awake = True
        speak("master I am awake now. How can I assist you?")
        return

    if "sleep" in lc_query:
        is_awake = False
        speak("Going to sleep. You can wake me up by saying 'wake up'.")
        return

    if not is_awake:
        return  # If the assistant is asleep, ignore commands

    if any(phrase in lc_query for phrase in ["change your name to", "name yourself", "name the assistant", "change your name"]):
        possible_phrases = ["change your name to", "name yourself", "name the assistant", "change your name"]
        new_name = None
        for phrase in possible_phrases:
            if phrase in lc_query:
                new_name = lc_query.split(phrase)[-1].strip()
                break
        if new_name:
            new_name_formatted = new_name.split()[0].capitalize()
            old_name = assistant_name
            assistant_name = new_name_formatted
            responses = [
                f"My name has been changed from {old_name} to {assistant_name}.",
                f"You can call me {assistant_name} now.",
                f"I am now known as {assistant_name}.",
                f"From now on, I'm called {assistant_name}.",
                f"Alright, {assistant_name} at your service!"
            ]
            speak(random.choice(responses))
            save_state({"assistant_name": assistant_name, "master_name": master_name})
            successful_tasks += 1  # Increment successful tasks
        else:
            speak("Please tell me the new name you want me to have master")
        return

    if "google" in lc_query and not any(kw in lc_query for kw in ["open google", "open youtube"]):
        search_term = lc_query.replace("google", "", 1).strip()
        speak(f"Searching Google for {search_term}")
        summarize_search(search_term)
        successful_tasks += 1  # Increment successful tasks
        return

    if "what is your name" in lc_query or "your name" in lc_query:
        speak(f"My name is {assistant_name}.")
        successful_tasks += 1
    elif "time" in lc_query:
        speak(f"The time is {get_current_time()}")
        successful_tasks += 1
    elif "date" in lc_query:
        speak(f"Today is {get_current_date()}")
        successful_tasks += 1
    elif "open youtube" in lc_query:
        speak("Opening YouTube for you master.")
        open_website("https://www.youtube.com")
        successful_tasks += 1
    elif "open google" in lc_query:
        speak("Opening Google for you master.")
        open_website("https://www.google.com")
        successful_tasks += 1
    elif "open facebook" in lc_query:
        speak("Opening Facebook.= for you master.")
        open_website("https://www.facebook.com")
        successful_tasks += 1
    elif "open instagram" in lc_query:
        speak("Opening Instagram for you master.")
        open_website("https://www.instagram.com")
        successful_tasks += 1
    elif "search youtube for" in lc_query:
        search_term = lc_query.replace("search youtube for", "").strip()
        open_youtube_search(search_term)
        successful_tasks += 1
    elif "open calculator" in lc_query:
        speak("Opening calculator for you master.")
        open_app("calculator")
        successful_tasks += 1
    elif "open notepad" in lc_query:
        speak("Opening notepad for you master.")
        open_app("notepad")
        successful_tasks += 1
    elif "open cmd" in lc_query or "open command prompt" in lc_query:
        open_app("cmd")
        successful_tasks += 1
    elif "open paint" in lc_query or "open ms paint" in lc_query:
        open_app("paint")
        successful_tasks += 1
    elif "open excel" in lc_query or "open spreadsheet" in lc_query or "open ms excel" in lc_query:
        open_app("excel")
        successful_tasks += 1
    elif "open ppt" in lc_query or "open Powerpoint" in lc_query or "open ms powerpoint" in lc_query:
        open_app("powerpoint")
        successful_tasks += 1
    elif "open v s code" in lc_query or "open visual studio code" in lc_query:
        open_app("vscode")
        successful_tasks += 1
    elif "open word" in lc_query or "open ms word" in lc_query or "open document" in lc_query:
        open_app("word")
        successful_tasks += 1
    elif "open nfs" in lc_query or "open game" in lc_query or "open need for spped most wanted" in lc_query:
        open_app("nfs")
        successful_tasks += 1
    elif "close calculator" in lc_query:
        speak("closing calculator for you master.")
        close_app("calculator")
        successful_tasks += 1
    elif "close notepad" in lc_query:
        speak("closing notepad for you master.")
        close_app("notepad")
        successful_tasks += 1
    elif "close cmd" in lc_query or "close command prompt" in lc_query:
        close_app("cmd")
        successful_tasks += 1
    elif "close paint" in lc_query or "close ms paint" in lc_query:
        close_app("paint")
        successful_tasks += 1
    elif "close excel" in lc_query or "close spreadsheet" in lc_query or "close ms excel " in lc_query:
        close_app("excel")
        successful_tasks += 1
    elif "close ppt" in lc_query or "close Powerpoint" in lc_query or "close ms powerpoint" in lc_query:
        close_app("powerpoint")
        successful_tasks += 1
    elif "close v s code" in lc_query or "close visual studio code" in lc_query:
        close_app("vscode")
        successful_tasks += 1
    elif "close word" in lc_query or "close ms word" in lc_query or "close document" in lc_query:
        close_app("word")
        successful_tasks += 1
    elif "close nfs" in lc_query or "close game" in lc_query or "close need for spped most wanted" in lc_query:
        close_app("nfs")
        successful_tasks += 1
    elif "tell me a joke" in lc_query or "tell joke" in lc_query:
        tell_joke()
        successful_tasks += 1
    elif "system info" in lc_query or "system information" in lc_query:
        info = get_system_info()
        speak(info)
        successful_tasks += 1
    elif "ip address" in lc_query:
        ip = get_ip_address()
        speak(f"master Your IP address is {ip}")
        successful_tasks += 1
    elif "shutdown" in lc_query:
        speak("Shutting down the computer for you master.")
        shutdown_computer()
        successful_tasks += 1
    elif "restart" in lc_query:
        speak("Restarting the computer for you master.")
        restart_computer()
        successful_tasks += 1
    elif "battery status" in lc_query or "battery percentage" in lc_query:
        battery = battery_status()
        speak(battery)
        successful_tasks += 1
    elif "open file" in lc_query:
        parts = lc_query.split("open file")
        if len(parts) > 1:
            filepath = parts[1].strip()
            open_file(filepath)
            successful_tasks += 1
        else:
            speak("Please specify the file path.")
    elif "play music" in lc_query or "play songs" in lc_query:
        play_music()
        successful_tasks += 1
    elif "pause music" in lc_query:
        pause_music()
        successful_tasks += 1
    elif "resume music" in lc_query:
        resume_music()
        successful_tasks += 1
    elif "next music" in lc_query:
        next_music()
        successful_tasks += 1
    elif "volume up" in lc_query:
        volume_up()
        successful_tasks += 1
    elif "volume down" in lc_query:
        volume_down()
        successful_tasks += 1
    elif "mute" in lc_query:
        mute()
        successful_tasks += 1
    elif "unmute" in lc_query:
        unmute()
        successful_tasks += 1
    elif "hello" in lc_query or "hi" in lc_query or "greetings" in lc_query:
        say_greeting()
        successful_tasks += 1
    elif "who are you" in lc_query or "about yourself" in lc_query:
        tell_about_me()
        successful_tasks += 1
    elif lc_query in ["bored", "i am bored", "feeling bored", "tired", "i am tired", "sad", "i am sad", "happy", "i am happy"]:
        respond_to_feeling(lc_query)
        successful_tasks += 1
    elif "exit" in lc_query or "quit" in lc_query or "goodbye" in lc_query:
        exit_assistant()
    elif "list processes" in lc_query or "running processes" in lc_query:
        list_running_processes()
        successful_tasks += 1
    elif "weather" in lc_query:
        city = lc_query.split("in")[-1].strip() if "in" in lc_query else ""
        if city:
            speak(f"Searching for the current weather in {city} for you master.")
            open_website(f"https://www.google.com/search?q=current+weather+in+{city.replace(' ', '+')}")
            successful_tasks += 1
        else:
            speak("Please specify a city for the weather you want to search master.")
    elif "news" in lc_query:
        speak("Searching for the latest news for you master.")
        open_website("https://www.google.com/search?q=latest+news")
        successful_tasks += 1
    elif lc_query.startswith("google search"):
        search_term = lc_query.replace("google search", "").strip()
        if search_term:
            speak(f"Searching Google for {search_term}")
            summarize_search(search_term)
            successful_tasks += 1
        else:
            speak("Please tell me what you want to search on Google.")
    else:
        speak("I am sorry, I do not recognize this command.")

def calculate_accuracy():
    global successful_tasks, total_tasks
    accuracy = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    print(f"Overall Accuracy: {accuracy:.2f}%")

def setup_keyboard_shortcuts():
    keyboard.add_hotkey('ctrl+space', play_music)
    keyboard.add_hotkey('ctrl+p', pause_music)
    keyboard.add_hotkey('ctrl+r', resume_music)
    keyboard.add_hotkey('ctrl+up', volume_up)
    keyboard.add_hotkey('ctrl+down', volume_down)
    keyboard.add_hotkey('ctrl+m', mute)
    keyboard.add_hotkey('ctrl+u', unmute)

if __name__ == "__main__":
    setup_keyboard_shortcuts()
    speak(f"Hello {master_name}, I am your assistant {assistant_name}. How can I help you today master?")
    ask_change_name()
    
    while True:
        query = take_command()
        if query == "None":
            continue
        process_command(query)
        calculate_accuracy()