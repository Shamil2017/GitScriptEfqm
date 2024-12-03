import json
import pyperclip
import os
from datetime import datetime

# Определяем директорию, где находится скрипт
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Абсолютные пути к файлам и папкам
CONFIG_FILE = os.path.join(BASE_DIR, "question_config.json")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "results")
INPUT_FILE = os.path.join(BASE_DIR, "input30_11_24.json")
department_name = "РТС"  # Название кафедры

# Убедимся, что папка для результатов существует
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def save_results_to_file(department, question_id, results):
    """
    Сохраняет результаты в файл JSON в папке OUTPUT_FOLDER.
    """
    filename = os.path.join(
        OUTPUT_FOLDER, f"out_{datetime.now().strftime('%d_%m_%y')}_{department}_{question_id}.json"
    )
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)
    print(f"Results saved to {filename}")

def extract_questions_for_department(data, department_name):
    """
    Извлекает вопросы, относящиеся к указанной кафедре.
    """
    results = []
    for entry in data:
        if entry['SubdivisionShortName'] == department_name:
            for page in entry['pages']:
                for question in page['questions']:
                    results.append({
                        "page": page['page'],
                        "question_id": question['question_id'],
                        "question_description": question['question_description'],
                        "options": question['options']
                    })
    return results

# Загрузка конфигурации
with open(CONFIG_FILE, "r") as file:
    config = json.load(file)

# Получаем текст ответа из буфера обмена
response = pyperclip.paste()

# Загружаем данные вопросов
with open(INPUT_FILE, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Извлекаем вопросы для кафедры
questions = extract_questions_for_department(data, department_name)

# Получаем текущий вопрос
current_index = config["current_question_index"]
question = questions[current_index]

# Формируем структуру результата
result_structure = {
    "SubdivisionShortName": department_name,
    "pages": [
        {
            "page": question["page"],
            "questions": [
                {
                    "question_id": question["question_id"],
                    "question_description": question["question_description"],
                    "results": response
                }
            ]
        }
    ]
}

# Сохраняем результат
save_results_to_file(department_name, question["question_id"], result_structure)

print("Response saved.")
# Очистка буфера обмена
pyperclip.copy("")  # Очищает буфер обмена
print("Clipboard cleared.")
