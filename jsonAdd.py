import os
import json

# Путь к папке с JSON файлами
json_folder = "JSON"
output_data = []

# Функция для обработки одного файла
def process_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        # Загружаем данные из JSON
        data = json.load(f)
        
        # Получаем название кафедры (первый ключ в файле)
        department_name = list(data.keys())[0]  # Название кафедры (например, "АСУТП")
        
        # Извлекаем данные кафедры
        department_data = data[department_name]
        
        # Добавляем данные кафедры в список output_data в нужном формате
        output_data.append({department_name: department_data})

# Обрабатываем все файлы в папке JSON
for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(json_folder, filename)
        process_json_file(file_path)

# Формируем итоговую структуру данных с ключом "data"
final_output = [{"data": output_data}]

# Сохраняем результат в новый файл output.json
output_file = 'output.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_output, f, ensure_ascii=False, indent=4)

print(f"Результат сохранен в {output_file}")
