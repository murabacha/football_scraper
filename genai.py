from google import genai
import time
import requests
import json
import telebot

BOT_TOKEN = '8550258583:AAE1RiO1VATBXlkRF0GbNVRPHk639xkdfyQ'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_telegram_message(message):
    bot.reply_to(message, "hey am ankibot ! sebd me a topic and i will generate flashcards for you !")
def time_genai(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time} seconds")
        return result
    return wrapper

def create_anki_deck(subject):
    url = "http://localhost:8765"
    payload = {
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": subject
        }
    }
    try:
        response = requests.post(url, json=payload).json()
        if response.get("error"):
            print(f"  Note on Deck: {response['error']}")
        else:
            print(f" Deck '{subject}' is ready (ID: {response['result']})")
    except requests.exceptions.ConnectionError:
        print(" Error: Anki is not open. Please start Anki first.")
        exit() # Stop the script if Anki isn't open
def add_card_to_anki(front_text, back_text,subject):
    # This URL is where AnkiConnect listens
    url = "http://localhost:8765"
    
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": subject,
                "modelName": "Basic",
                "fields": {
                    "Front": front_text,
                    "Back": back_text
                },
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck"
                },
                "tags": ["automated_import", "gemini_api"]
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload).json()
        if response.get("error"):
            print(f" Error adding card: {response['error']}")
        else:
            print(f"✅ Card added! (ID: {response['result']})")
    except requests.exceptions.ConnectionError:
        print("  Make sure Anki is OPEN and AnkiConnect is installed!")
        
def trigger_anki_sync():
    url = "http://localhost:8765"
    payload = {
        "action": "sync",
        "version": 6
    }
    try:
        response = requests.post(url, json=payload).json()
        if response.get("error"):
            print(f" Error during sync: {response['error']}")
        else:
            print(" Anki sync triggered successfully!")
    except requests.exceptions.ConnectionError:
        print("  Make sure Anki is OPEN and AnkiConnect is installed!")
        
@bot.message_handler(func=lambda message: True)
@time_genai
def genai_prompt( message):
    count = 0
    user_id = message.from_user.id
    subject = message.text
    API_KEY = 'AIzaSyCyH_zzvvj2dfQufiWdZkX_QMVkG5T_5u8'
    bot.reply_to(message, f" Generating flashcards for '{subject}'. Please wait...")
    print(f'received request from user {user_id} for subject: {subject}')
    client  = genai.Client(api_key=API_KEY)
    models ={
        'better':'gemini-2.5-flash-lite',
    }
    response = client.models.generate_content(
        model = models['better'],


        contents = f"""
        You are an expert Kenyan High School examiner (KCSE standard). Create 30 revision flashcards for '{subject}'.

        OUTPUT FORMAT Rules (Strictly follow for Anki Import):
        1.  **Structure:** Output ONLY the raw questions. One flashcard per line.
        2.  **Separator:** Use the **Pipe character '|'** to separate Question and Answer.
            * Format: `Question | Answer`
        3.  **Mermaid Diagrams (CRITICAL):**
            * Wrap code in: <div class="mermaid"> ... </div>
            * Write code on a **SINGLE LINE**.
            * **Use Semicolons (;)** to separate steps.
            * **MUST USE QUOTES:** Enclose ALL node text in double quotes to prevent syntax errors with brackets.
            * CORRECT: `graph TD; A["Calcium (Ca)"]-->B["Oxide (O)"];`
            * WRONG: `graph TD; A[Calcium (Ca)]-->B[Oxide (O)];`
            * Do NOT use the pipe character '|' inside the diagram text.
            * feel free to create more that one diagram if needed.
        4.  **Math:** Use LaTeX \\( ... \\) for formulas.

        CONTENT Rules:
        1.  **Calculations:** 50% of questions should involve calculations if applicable.
        2.  **Difficulty:** Mix of Hard, Medium, Easy.
        3.  **Syllabus:** Strictly KCSE syllabus.
        """
    )
    response = response.text
    response = response.splitlines()
    subject = subject.replace(' ','_')
            
    create_anki_deck(subject)
    for line in response:
        if '|' in line:
            front, back = line.split('|', 1)
            add_card_to_anki(front.strip(), back.strip(),subject)
            bot.send_message(user_id, f"✅ Added flashcard:\nQ: {front.strip()}")
            count += 1
    bot.reply_to(message, f"✅ Generated and added {count} flashcards to Anki deck '{subject}'.")
    trigger_anki_sync()
    bot.send_message(user_id, f"✅ Generated and added {count} flashcards to Anki deck '{subject}'.")
            
    
print('bot running...')
bot.infinity_polling()
