import json
import os
from typing import List
from openai import OpenAI
import time

# Локальная конфигурация
CONFIG_PATH = 'config.json'

config = {
    "ASSISTANT_MODEL": "gpt-4o",
    "PROXY_API_KEY": "sk-zFbIsup4mbCWPGNsdH0Y9ITCHwGRmfT1",
    "vector_store_id": None,
    "assistant_id": None,
    "threads": {}
}

proxy_client = OpenAI(
    api_key=config['PROXY_API_KEY'],
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Проверяем наличие и загружаем конфигурацию из файла, если он существует
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as file:
        config.update(json.load(file))

# Сохраняем конфигурацию в файл
def save_config():
    with open(CONFIG_PATH, 'w') as file:
        json.dump(config, file)

# Функции для работы с ассистентом и базой знаний
def get_vector_store_id():
    if not config.get("vector_store_id"):
        new_store = proxy_client.beta.vector_stores.create()
        config["vector_store_id"] = new_store.id
        save_config()
    return config["vector_store_id"]

def create_assistant(name, instructions):
    assistant_id = get_assistant_id()
    if not assistant_id:
        new_assistant = proxy_client.beta.assistants.create(
            model=config["ASSISTANT_MODEL"],
            instructions=instructions,
            name=name,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [get_vector_store_id()]}},
        )
        config["assistant_id"] = new_assistant.id
        save_config()
    else:
        proxy_client.beta.assistants.update(assistant_id=assistant_id, instructions=instructions)

def get_assistant_id():
    return config.get("assistant_id")

def add_knowledge(filename, file):
    file_object = proxy_client.files.create(file=(filename, file), purpose="assistants")
    store_id = get_vector_store_id()
    proxy_client.beta.vector_stores.files.create(vector_store_id=store_id, file_id=file_object.id)

def reset_knowledge():
    store_id = get_vector_store_id()
    files = proxy_client.beta.vector_stores.files.list(vector_store_id=store_id)
    for file in files:
        proxy_client.beta.vector_stores.files.delete(vector_store_id=store_id, file_id=file.id)
        proxy_client.files.delete(file.id)

def delete_existing_assistant():
    assistant_id = get_assistant_id()
    if assistant_id:
        try:
            # Удаляем ассистента с текущим assistant_id
            proxy_client.beta.assistants.delete(assistant_id=assistant_id)
            print(f"Ассистент с ID {assistant_id} удалён.")
            
            # Удаляем assistant_id из конфигурации
            config["assistant_id"] = None
            save_config()
        except Exception as e:
            print(f"Ошибка при удалении ассистента: {e}")
    else:
        print("Ассистент не существует, удаление не требуется.")

def get_thread_id(chat_id: str):
    if "threads" not in config:
        config["threads"] = {}
    if chat_id not in config["threads"]:
        thread = proxy_client.beta.threads.create()
        config["threads"][chat_id] = thread.id
        save_config()
    return config["threads"][chat_id]

def list_knowledge_files():
    store_id = get_vector_store_id()
    files = proxy_client.beta.vector_stores.files.list(vector_store_id=store_id)
    print("Список файлов в базе знаний:")
    for file in files:
        print(f"ID: {file.id}, Имя файла: {file.filename}")
        
def process_message(chat_id: str, message: str) -> List[str]:
    assistant_id = get_assistant_id()
    thread_id = get_thread_id(chat_id)
    proxy_client.beta.threads.messages.create(thread_id=thread_id, content=message, role="user")
    run = proxy_client.beta.threads.runs.create_and_poll(thread_id=thread_id, assistant_id=assistant_id)
    answer = []
    if run.status == "completed":
        messages = proxy_client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id)
        for message in messages:
            if message.role == "assistant":
                for block in message.content:
                    if block.type == "text":
                        answer.append(block.text.value)
    return answer
    
def prepare_request(question, variants):
    """
    Формирует текст запроса для ассистента, объединяя вопрос и варианты ответов с баллами.
    """
    request = question + "\n\nВарианты ответов и баллы:\n"
    for idx, variant in enumerate(variants, start=1):
        request += f"{idx}. {variant['text']}\t{variant['score']}\n"
    request += (
        "\nИсходя из паспорта кафедры (загруженного документа) и проставленных баллов, "
        "найди несоответствия баллов по каждому варианту ответов. Внимательно проанализируй этот документ.\n"
        "По каждому варианту ответов заведующий кафедры выставляет баллы от 0 до 10:\n"
        "0 - не поддерживается, 10 - максимально активно поддерживается.\n"
        "Дай ответ на русском языке в формате JSON, содержащий следующие поля:\n"
        "1. 'Вариант ответа' - текст варианта ответа.\n"
        "2. 'Проставленный балл' - исходный балл из анкеты.\n"
        "3. 'Предложенный балл' - балл, основанный на данных из паспорта кафедры.\n"
        "4. 'Обоснование краткое' - краткий комментарий.\n"
        "5. 'Обоснование подробное' - развернутый анализ.\n"
        "6. 'Несоответствие' - 0, если существенных несоответствий нет, или 1, если есть.\n"
    )
    return request
    
if __name__ == '__main__':
    print("Инициализация процесса...")
    print("Проверка и удаление существующего ассистента...")
    delete_existing_assistant()
    time.sleep(10)  # Пауза 10 секунд
    
    # Пример использования функций
    print("Создание ассистента...")
    create_assistant(
        name="My Assistant",
        instructions="Вы помощник, который отвечает на вопросы и помогает решать задачи."
    )
    print("Ассистент создан!")
    time.sleep(10)  # Пауза 10 секунд
    
    print("Добавление документа в базу знаний...")
    # Имитируем добавление документа (укажите путь к реальному файлу)
    with open('example.txt', 'rb') as file:
        add_knowledge("example.txt", file)
    print("Документ добавлен!")
    time.sleep(10)  # Пауза 10 секунд
    
    # Формирование запроса
    # Переменная, хранящая вопрос
    question = "Есть такой вопрос анкеты, который заполняет заведующего кафедры: В чем заключается и какой степени реализуется лидерство кафедры в образовании?"
    variants = [
        {"text": "Довузовская подготовка", "score": 8},
        {"text": "Разработка и написание учебников, учебно-методической литературы", "score": 8},
        {"text": "Программы доп.проф.образования", "score": 4},
        {"text": "Развитие ПОУ", "score": 4},
        {"text": "Разработка новых ОП и стандартов", "score": 8},
        {"text": "Расширение профилей подготовки", "score": 4},
        {"text": "Международные образовательные программы (двойные дипломы и т.д.)", "score": 2},
    ]
    
    print("Формирование текста запроса...")
    request = prepare_request(question, variants)
    print(request)
    
    print("Отправка вопроса ассистенту...")
    try:
        responses = process_message(chat_id="12345", message=request)
        print("Ответ ассистента:")
        for response in responses:
            print(response)
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
    time.sleep(10)  # Пауза 10 секунд

    print("Сброс базы знаний...")
    reset_knowledge()
    print("База знаний сброшена!")
    time.sleep(10)  # Пауза 10 секунд

    print("Все операции завершены.")