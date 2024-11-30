import os
import json
from datetime import datetime

# Указываем папку с JSON-файлами и выходной файл
input_folder = "JSON"
output_file = f"out_{datetime.now().strftime('%d_%m_%Y')}_РТС.json"

# Структура для хранения данных
final_data = {
    "РТС": {
        "pages": []
    }
}

# Функция для объединения вопросов
def merge_questions(existing_questions, new_questions):
    # Список для уникальных вопросов
    questions_dict = {q['question_id']: q for q in existing_questions}
    for question in new_questions:
        if question['question_id'] in questions_dict:
            continue
        questions_dict[question['question_id']] = question
    return list(questions_dict.values())

# Сканируем папку и обрабатываем каждый JSON-файл
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(input_folder, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if data.get("SubdivisionShortName") == "РТС":
                    for page in data.get("pages", []):
                        # Проверяем, существует ли уже эта страница
                        existing_page = next((p for p in final_data["РТС"]["pages"] if p["page"] == page["page"]), None)
                        if existing_page:
                            # Объединяем вопросы для существующей страницы
                            existing_page["questions"] = merge_questions(existing_page["questions"], page["questions"])
                        else:
                            # Добавляем новую страницу
                            final_data["РТС"]["pages"].append(page)
            except Exception as e:
                print(f"Ошибка обработки файла {filename}: {e}")

# Сохраняем результат в выходной файл
with open(output_file, "w", encoding="utf-8") as output:
    json.dump(final_data, output, ensure_ascii=False, indent=4)

print(f"Объединенные данные сохранены в файл {output_file}")
