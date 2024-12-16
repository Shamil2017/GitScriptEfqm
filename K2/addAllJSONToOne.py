import os
import json
from datetime import datetime

# Константы
INPUT_FOLDER = "results"
SUBDIVISION_NAME = "ДИТ"  # Константа для фильтрации по имени подразделения
OUTPUT_FILE = f"out_{datetime.now().strftime('%d_%m_%Y')}_{SUBDIVISION_NAME}.json"  # Использование SUBDIVISION_NAME в имени файла

# Структура для хранения данных
final_data = {
    SUBDIVISION_NAME: {
        "pages": []
    }
}

# Функция для объединения вопросов
def merge_questions(existing_questions, new_questions):
    questions_dict = {q['question_id']: q for q in existing_questions}
    for question in new_questions:
        if question['question_id'] in questions_dict:
            continue
        questions_dict[question['question_id']] = question
    return list(questions_dict.values())

# Сканируем папку и обрабатываем каждый JSON-файл
for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".json"):
        file_path = os.path.join(INPUT_FOLDER, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                
                # Если файл содержит список, обрабатываем каждый элемент
                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and entry.get("Subdisidion_shortname") == SUBDIVISION_NAME:
                            for answer in entry.get("Answers", []):
                                for page in answer.get("pages", []):
                                    page_id = page.get("page_id")
                                    page_name = page.get("page")
                                    # Проверяем, существует ли уже эта страница по page_id и page
                                    existing_page = next(
                                        (p for p in final_data[SUBDIVISION_NAME]["pages"] if p["page_id"] == page_id and p["page"] == page_name),
                                        None
                                    )
                                    if existing_page:
                                        # Объединяем вопросы для существующей страницы
                                        existing_page["questions"] = merge_questions(existing_page["questions"], page["questions"])
                                    else:
                                        # Добавляем новую страницу
                                        final_data[SUBDIVISION_NAME]["pages"].append(page)
                elif isinstance(data, dict) and data.get("Subdisidion_shortname") == SUBDIVISION_NAME:
                    for answer in data.get("Answers", []):
                        for page in answer.get("pages", []):
                            page_id = page.get("page_id")
                            page_name = page.get("page")
                            # Проверяем, существует ли уже эта страница по page_id и page
                            existing_page = next(
                                (p for p in final_data[SUBDIVISION_NAME]["pages"] if p["page_id"] == page_id and p["page"] == page_name),
                                None
                            )
                            if existing_page:
                                # Объединяем вопросы для существующей страницы
                                existing_page["questions"] = merge_questions(existing_page["questions"], page["questions"])
                            else:
                                # Добавляем новую страницу
                                final_data[SUBDIVISION_NAME]["pages"].append(page)
                else:
                    print(f"Необработанный формат данных в файле {filename}")
            except Exception as e:
                print(f"Ошибка обработки файла {filename}: {e}")

# Сохраняем результат в выходной файл
with open(OUTPUT_FILE, "w", encoding="utf-8") as output:
    json.dump(final_data, output, ensure_ascii=False, indent=4)

print(f"Объединенные данные сохранены в файл {OUTPUT_FILE}")
