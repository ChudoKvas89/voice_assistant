import os
import subprocess
import speech_recognition as sr
import pyttsx3
from transformers import AutoModelForCausalLM, AutoTokenizer

# Инициализация модели Qwen 0.5B
model_name = "Qwen/Qwen1.5-0.5B-Chat"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Инициализация голосового движка
engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    """Озвучивание текста"""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Запись голоса с микрофона с обработкой ошибок"""
    try:
        with sr.Microphone() as source:
            print("Слушаю... (скажите 'стоп' для выхода)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        
        text = recognizer.recognize_google(audio, language="ru-RU")
        print(f"Распознано: {text}")
        return text
    
    except sr.UnknownValueError:
        print("Речь не распознана")
        return ""
    except sr.RequestError:
        print("Ошибка сервиса распознавания")
        return ""
    except sr.WaitTimeoutError:
        print("Время ожидания истекло")
        return ""
    except Exception as e:
        print(f"Ошибка микрофона: {e}")
        return ""

def execute_command(command):
    """Выполнение системных команд"""
    command = command.lower()
    try:
        if "открой сайт" in command:
            url = command.split("открой сайт")[-1].strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            subprocess.Popen(f"start chrome {url}", shell=True)
            return f"Открываю сайт {url}"
        
        elif "создай файл" in command:
            filename = command.split("создай файл")[-1].strip()
            with open(filename, 'w') as f:
                f.write("")
            return f"Файл {filename} создан"
        
        elif "выключи компьютер" in command:
            os.system("shutdown /s /t 1")
            return "Выключаю компьютер..."
        
        elif "открой калькулятор" in command:
            subprocess.Popen("calc.exe", shell=True)
            return "Открываю калькулятор"
            
        else:
            return None  # Не распознана как команда
    
    except Exception as e:
        return f"Ошибка выполнения: {e}"

def main():
    speak("Ассистент готов к работе")
    print("Говорите 'стоп' для выхода")
    
    while True:
        # Выбор режима ввода
        print("\nВыберите режим:")
        print("1 - Голосовой ввод")
        print("2 - Текстовый ввод")
        print("0 - Выход")
        
        mode = input("Ваш выбор: ")
        
        if mode == "0":
            speak("Завершаю работу")
            break
            
        elif mode == "1":
            print("\n=== Голосовой режим ===")
            while True:
                user_input = listen()
                if not user_input:
                    continue
                
                if user_input.lower() == "стоп":
                    speak("Завершаю работу")
                    break
                
                # Генерация ответа
                inputs = tokenizer(user_input, return_tensors="pt")
                outputs = model.generate(**inputs, max_new_tokens=50)
                ai_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(f"AI: {ai_response}")
                speak(ai_response)  # Озвучивание ответа модели
                
                # Попытка выполнить команду
                action_result = execute_command(ai_response)
                if action_result:
                    print("Действие:", action_result)
                    speak(action_result)
                    
        elif mode == "2":
            print("\n=== Текстовый режим ===")
            user_input = input("Вы: ")
            
        else:
            print("Некорректный выбор")
            continue
            
        if user_input.lower() == "стоп":
            speak("Завершаю работу")
            break

if __name__ == "__main__":
    main()