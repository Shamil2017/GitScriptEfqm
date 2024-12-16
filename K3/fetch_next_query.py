import json
import os
import pyperclip

# Файлы конфигурации

CONFIG_FILE = "C:/efqm/K3/question_config.json"
INPUT_FILE = "C:/efqm/K3/input09_12_24.json"
PASSPORT_FILE = "C:/efqm/K3/example.txt"
department_name = "МиПЭУ"  # Название кафедры
option_file = "C:/efqm/K3/option.txt"

    

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
                        "page_id": page['page'],
                        "question_id": question['question_id'],
                        "question_description": question['question_description'],
                        "options": question['options']
                    })
    return results
    
# Функция для подготовки запроса
def prepare_request(question_description, options):
    """
    Формирует текст запроса для ассистента, включая паспорт кафедры.
    """
    # Читаем содержимое файла паспорта кафедры
    with open(PASSPORT_FILE, "r", encoding="utf-8") as file:
        passport_content = file.read().strip()
    
    # Формируем запрос
    request = (
        f"Паспорт кафедры:\n{passport_content}\n\n"
        f"Есть такой вопрос анкеты, который заполняет заведующий кафедры:\n{question_description}\n\n"
        "Варианты ответов и баллы\n"
    )
    # Открываем файл в режиме записи
    with open(option_file, "w", encoding="utf-8") as file:
        # Цикл для обработки данных
        for idx, option in enumerate(options, start=1):
            # Формируем строку для записи
            file.write(f"{option['option_id']}\n")
            # Формируем строку запроса (для примера)
            request += f"{idx}. {option['option_name']} - {option['answer']}\n"
    
    
    request += (
        "\nИсходя из паспорта кафедры и проставленных баллов, "
        "найди несоответствия баллов по каждому варианту ответов. Внимательно проанализируй паспорт кафедры и строго давай ответы на основе паспорта кафедры. Учитывай план выполнения показателей если они непосредственно связаны с вопросом или вариантом ответа\n"
        "По каждому варианту ответов заведующий кафедры выставляет баллы от 0 до 10:\n"
        "0 - не поддерживается, 10 - максимально активно поддерживается.\n"
        "Нет свидетельств или если нет данных, то строго ставь оценку – 0-1\n"
        "Отдельные свидетельства продемонстрированы в ограниченном виде, то строго ставь оценку – 2-3\n"
        "План почти выполнен / выполнен / немного перевыполнен, если средние или нормальные достижения, то ставь оценку – 4-6\n"
        "Получены отличные результаты / значительно лучше запланированных – 7-8\n"
        "Лучшие результаты в стране или мире / примеры лучшей практики – 9-10\n"
        "Дай ответ на русском языке строго в формате JSON, содержащий следующие поля и ничего кроме этого формата не выводи. Строго только результат в формате JSON:\n"
        "1. 'Вариант ответа' - текст варианта ответа.\n"
        "2. 'Проставленный балл' - исходный балл из анкеты.\n"
        "3. 'Предложенный балл' - балл, основанный на данных из паспорта кафедры.\n"
        "4. 'Обоснование краткое' - краткий комментарий.\n"
        "5. 'Обоснование подробное' - развернутый анализ.\n"
        "6. 'Несоответствие' - 0, если существенных несоответствий нет, или 1, если есть.\n"
       
    )
    
    return request

if __name__ == "__main__":
   

    # Загружаем индекс текущего вопроса из файла конфигурации
    if not os.path.exists(CONFIG_FILE):
        config = {"current_question_index": 0}
        with open(CONFIG_FILE, "w") as file:
            json.dump({"current_question_index": 0}, file)
        print(f"Файл {CONFIG_FILE} создан с начальной конфигурацией.")
    else:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)

    current_index = config.get("current_question_index", 0)

    # Загружаем данные вопросов из JSON файла
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    # Извлекаем вопросы для указанной кафедры
    questions = extract_questions_for_department(data, department_name)
    
    # Проверка, есть ли еще не обработанные вопросы
    if current_index >= len(questions):
        print("Все вопросы обработаны.")
        exit()

    # Берем текущий вопрос
    question = questions[current_index]
    question_description = question["question_description"]
    options = question["options"]

    # Готовим запрос
    request_text = prepare_request(question_description, options)
    
    print(request_text)

    # Копируем запрос в буфер обмена
    pyperclip.copy(request_text)
    print(f"Запрос для вопроса {current_index + 1} скопирован в буфер обмена.")

    # Обновляем индекс текущего вопроса и сохраняем в конфигурацию
    config["current_question_index"] += 1
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)
