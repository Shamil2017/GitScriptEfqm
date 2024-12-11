import json
import pyperclip
import os
from datetime import datetime
from typing import List, Dict


# Определяем директорию, где находится скрипт
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Абсолютные пути к файлам и папкам
CONFIG_FILE = os.path.join(BASE_DIR, "question_config.json")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "results")
INPUT_FILE = os.path.join(BASE_DIR, "input09_12_24.json")
department_name = "АСУТП"  # Название кафедры
option_file = os.path.join(BASE_DIR, "option.txt")

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
    results = []
    for entry_list in data:  # Iterate through the list of lists
        # Access the first element (dictionary) in the list
        entry = entry_list[0] if entry_list else {}  # Handle potential empty lists        
        if entry.get('SubdivisionShortName') == department_name:
            for page in entry['pages']:
                for question in page['questions']:
                    results.append({
                        "page": page['page'],
                        "page_id": page['page_id'],
                        "question_id": question['question_id'],
                        "question_description": question['question_description'],
                        "options": question['options']
                    })
    return results
    

    
# Функция преобразования result_structure в новый формат
def transform_result_structure(result_structure: Dict, response: str, question: Dict) -> List[Dict]:
    transformed = []
    subdivision = {
        "Subdisidion_shortname": result_structure["SubdivisionShortName"],
        "Answers": []
    }
    # Чтение option_id из файла option.txt
    if os.path.exists(option_file):
        with open(option_file, "r", encoding="utf-8") as file:
            option_ids = file.readlines()  # Считываем все строки в список
        #os.remove(option_file)  # Удаляем файл после чтения
    else:
        option_ids = []  # Если файл отсутствует, создаем пустой список
    
    # Указатель на текущий индекс option_id
    option_index = 0    
    
    for page in result_structure["pages"]:
        page_data = {
            "page_id": page["page_id"],
            "page": page["page"],
            "questions": []
        }
        
        for page_question in page["questions"]:
            question_data = {
                "question_id": page_question["question_id"],
                "question_description": page_question["question_description"],
                "options": []
            }
            # Convert 'response' string to a list of dictionaries
            response_data = json.loads(response)
            for result in response_data:
                # Получение option_id через функцию get_option_id
                print(question)
                print(result["Вариант ответа"])
                # Проверяем, есть ли ещё option_id в списке
                if option_index < len(option_ids):
                    option_id = option_ids[option_index].strip()  # Получаем текущий option_id и удаляем лишние пробелы
                    option_index += 1  # Увеличиваем индекс для следующего использования
                else:
                    option_id = "unknown"  # Если option_id закончились, устанавливаем значение по умолчанию

                option = {
                    "option_id": option_id,
                    "option_name": result["Вариант ответа"],
                    "zk_score": result["Проставленный балл"],
                    "gpt_score": result["Предложенный балл"],
                    "comment_short": result["Обоснование краткое"],
                    "comment_full": result["Обоснование подробное"]
                }
                question_data["options"].append(option)
            
            page_data["questions"].append(question_data)
        
        subdivision["Answers"].append({"pages": [page_data]})
    
    transformed.append(subdivision)
    return transformed
    
    
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
current_index = config["current_question_index"]-1
print("question")
question = questions[current_index]
print(question)

# Формируем структуру результата
result_structure = {
    "SubdivisionShortName": department_name,
    "pages": [
        {
            "page": question["page"],
            "page_id":question["page_id"],
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

# Преобразование данных
transformed_result = transform_result_structure(result_structure, response, question)

# Сохраняем результат
save_results_to_file(department_name, question["question_id"], transformed_result)

print("Response saved.")
# Очистка буфера обмена
pyperclip.copy("")  # Очищает буфер обмена
print("Clipboard cleared.")
