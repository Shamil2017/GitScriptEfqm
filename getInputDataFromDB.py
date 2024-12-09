import pyodbc
import json
from datetime import datetime

# Функция для получения списка кафедр
def get_kafedra_list(server, database, username, password):
    kafedra_list = []
    sql_query = "SELECT DISTINCT [SubdivisionShortName] FROM [dbo].[EFQM_InputData_FULL]"

    try:
        conn = pyodbc.connect(f'DRIVER=SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        for row in rows:
            kafedra_list.append(row[0])
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error while fetching kafedra list:", e)
    
    return kafedra_list

# Функция для получения данных для каждой кафедры
def get_kafedra_data(server, database, username, password, kafedra):
    sql_query = f"""
        SELECT page, page_id, question_description, question_id, option_id,  option_name, answer
        FROM [dbo].[EFQM_SurveyAnswers]
        WHERE [SubdivisionShortName] = ?
    """
    kafedra_data = []
    
    try:
        conn = pyodbc.connect(f'DRIVER=SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
        cursor.execute(sql_query, (kafedra,))
        rows = cursor.fetchall()
        
        for row in rows:
            kafedra_data.append({
                "page": row[0],
                "page_id": row[1],
                "question_description": row[2],
                "question_id": row[3],
                "option_id": row[4],
                "option_name": row[5],
                "answer": row[6]
            })
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error while fetching data for kafedra '{kafedra}':", e)
    
    return kafedra_data


    
# Функция для преобразования данных в иерархический JSON формат
def transform_to_hierarchical_format(kafedra_name, kafedra_data):
    hierarchical_data = []
    
    kafedra_entry = {
        "SubdivisionShortName": kafedra_name,
        "pages": []
    }
    
    pages = {}
    for item in kafedra_data:
        page = item["page"]
        page_id = item["page_id"]
        question_description = item["question_description"]
        question_id = item["question_id"]
        option_id = item["option_id"]
        option_name = item["option_name"]
        answer = item["answer"]
        
        if page not in pages:
            pages[page] = {
                "page_id": page_id,
                "questions": {}
            }
        
        if question_id not in pages[page]["questions"]:
            pages[page]["questions"][question_id] = {
                "question_description": question_description,
                "question_id": question_id,
                "options": []
            }
        
        pages[page]["questions"][question_id]["options"].append({
            "option_id":option_id,
            "option_name": option_name,
            "answer": answer
        })
    
    for page_name, page_content in pages.items():
        page_data = {
            "page": page_name,
            "page_id": page_content["page_id"],
            "questions": list(page_content["questions"].values())
        }
        kafedra_entry["pages"].append(page_data)
    
    hierarchical_data.append(kafedra_entry)
    
    return hierarchical_data


# Основная программа
def main():
    server = 'KPI-MONITOR'
    database = 'MEI2'
    username = 'efqm'
    password = 'mpeiR@dar'
    
    

    # Получаем список кафедр
    kafedra_list = get_kafedra_list(server, database, username, password)

    # Создаём итоговый JSON
    result = []

    for kafedra in kafedra_list:
        kafedra_data = get_kafedra_data(server, database, username, password, kafedra)
        hierarchical_data = transform_to_hierarchical_format(kafedra, kafedra_data)
        result.append(hierarchical_data)

    # Сохраняем в JSON файл
    current_date = datetime.now().strftime("%d_%m_%y")
    filename = f"input{current_date}.json"
    
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)

    print(f"Данные успешно сохранены в файл: {filename}")

# Запуск основной программы
if __name__ == "__main__":
    main()


