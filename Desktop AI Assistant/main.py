import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime
from plyer import notification
import os
import wikipedia
import pywhatkit as pwk
from openai_client import send_request
from credentials import password, mobile_num, mails ,sender_mail

# Initializing Text-to-Speech engine
engine = pyttsx3.init()
voice = engine.getProperty('voices')
engine.setProperty('rate', 200)
engine.setProperty('voice', voice[0].id)


def speak(command):
    """Function to speak a command."""
    engine.say(command)
    engine.runAndWait()


def take_command():
    """Function to capture voice input from the user."""
    query = ""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except sr.UnknownValueError:
        speak("I couldn't understand. Please repeat.")
    except sr.RequestError as e:
        speak("Network error. Please check your connection.")
        print(f"Error: {e}")
    return query.lower()


def search_wikipedia(request):
    """Search Wikipedia and provide results."""
    try:
        request = request.replace("jarvis ", "").replace("search wikipedia about", "").strip()
        results = wikipedia.summary(request, sentences=2)
        speak("According to Wikipedia")
        print(results)
        speak(results)
    except wikipedia.exceptions.DisambiguationError as e:
        speak("The query is too broad. Here are some options:")
        for option in e.options[:5]:
            print(option)
            speak(option)
        speak("Please choose a more specific query.")
    except wikipedia.exceptions.PageError:
        speak("No page found for the given query.")
    except Exception as e:
        speak("An error occurred while fetching information.")
        print(f"Error: {e}")


def notify_tasks():
    """Notify the user of tasks from the to-do list."""
    try:
        if not os.path.exists("todo.txt"):
            speak("The 'todo.txt' file does not exist. Please create it and add tasks.")
            return
        with open("todo.txt", "r") as f:
            tasks = f.read().strip()
        if not tasks:
            speak("No tasks to notify.")
            return
        notification.notify(
            title="Tasks Remaining",
            message=tasks,
            timeout=10
        )
        speak("Tasks notified successfully.")
    except Exception as e:
        speak("An error occurred while notifying tasks.")
        print(f"Error: {e}")


def send_whatsapp_message(request):
    """Send a WhatsApp message."""
    try:
        name = request.replace("send whatsapp message to", "").strip()
        mob_no = mobile_num.get(name)
        if not mob_no:
            speak("I couldn't find the contact. Please check the name.")
            return
        speak("What is the message?")
        message = take_command()
        pwk.sendwhatmsg_instantly(mob_no, message, wait_time=10, tab_close=True, close_time=5)
        speak("Message sent successfully.")
    except Exception as e:
        speak("An error occurred while sending the message.")
        print(f"Error: {e}")


def send_mail(request):
    """Send an email."""
    try:
        name = request.replace("send mail to", "").strip()
        mail_id = mails.get(name)
        if not mail_id:
            speak("I couldn't find the contact. Please check the name.")
            return
        speak("What is the subject?")
        subject = take_command()
        speak("What is the message?")
        message = take_command()
        pwk.send_mail(sender_mail, password , subject, message, mail_id)
        speak("Mail sent successfully.")
    except Exception as e:
        speak("An error occurred while sending the mail.")
        print(f"Error: {e}")


def handle_tasks(request):
    """Handle task-related requests."""
    if "new task" in request:
        speak("What is the task?")
        new_task = take_command()
        if new_task:
            with open("todo.txt", "a") as f:
                f.write(new_task + "\n")
            speak("Task added successfully.")
    elif "read all tasks" in request:
        if not os.path.exists("todo.txt") or os.path.getsize("todo.txt") == 0:
            speak("No tasks found.")
            return
        with open("todo.txt", "r") as f:
            tasks = f.readlines()
            speak("Here are your tasks:")
            for task in tasks:
                speak(task.strip())
    elif "reset the list" in request:
        if os.path.exists("todo.txt"):
            os.remove("todo.txt")
        speak("All tasks have been deleted.")
    elif "notify the task" in request:
        notify_tasks()


def main_process():
    """Main process loop for the virtual assistant."""
    jarvis_chat = []
    while True:
        request = take_command()
        if "hello" in request:
            speak("Hello! How may I assist you?")
        elif "tell me the time" in request:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {current_time}")
        elif "tell date" in request:
            current_date = datetime.datetime.now().strftime("%d %B %Y")
            speak(f"Today's date is {current_date}")
        elif "play music" in request:
            song = random.randint(1, 5)
            urls = [
                "https://youtu.be/ekr2nIex040?si=YQAwEuMueCoCZoW1",
                "https://youtu.be/Wj7lL6eDOqc?si=kJv_Mdm3iIzouInN",
                "https://youtu.be/1qmPNot9NJs?si=tI2k23alhhfPibgv",
                "https://youtu.be/Zam-KYu8AvA?si=yi6NkkApANFMT9VY",
                "https://youtu.be/yJg-Y5byMMw?si=YCdew6FpG2FQp30J",
            ]
            speak(f"Playing song {song}")
            webbrowser.open(urls[song - 1])
        elif "wikipedia" in request:
            search_wikipedia(request)
        elif "send whatsapp" in request:
            send_whatsapp_message(request)
        elif "send mail" in request:
            send_mail(request)
        elif "task" in request:
            handle_tasks(request)
        elif "ask gpt" in request:
            jarvis_chat.clear()
            question = request.replace("jarvis", "").replace("ask ai", "").strip()
            jarvis_chat.append({"role": "user", "content": question})
            response = send_request(jarvis_chat)
            speak(response)
        elif "exit" in request or "shutdown" in request:
            print("Goodbye! Have a great day.")
            speak("Goodbye! Have a great day.")
            break
        else:
            jarvis_chat.append({"role": "user", "content": request})
            response = send_request(jarvis_chat)
            jarvis_chat.append({"role": "assistant", "content": response})
            speak(response)


# Run the virtual assistant
if __name__ == "__main__":
    main_process()
