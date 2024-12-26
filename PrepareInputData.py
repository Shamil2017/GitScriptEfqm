#!/usr/bin/env python
# coding: utf-8

# In[1]:


#IndicatorCode	IndicatorName
#Ц01	Доля магистров и аспирантов в общем контингенте 
#Ц02	Средний балл ЕГЭ
#Ц03	Доля сторонних магистров и аспирантов
#Ц04	Доля целевиков
#Ц05	Объем ПОУ на ставку НПР
#Ц06	Доля остепененных ППС
#Ц07	Трудоустройство
#Ц08	Количество публикаций в WoS и Scopus и журналов из перечня ВАК на ставку НПР
#Ц09	Объем НИОКР на ставку НПР
#Ц10	Защиты аспирантов в срок
#Ц11	Доля иностранных студентов
#Ц12	Количество иностранных преподавателей
#Ц13	Академическая мобильность студентов и аспирантов
#Ц16	Заявочная активность
#Ц17	Подготовленные к публикации тематические материалы  научно-просветительского характера для неспециализированных СМИ
#Ц18	Подготовка энциклопедии/справочника
#Ц20	Руководство работами студентов и аспирантов – победителей олимпиад (конкурсов, выставок)
#Ц21	Участие в научно-технических и творческих выставках (учитывается только участие с экспонатами)
##Ц22	Членство в научно-технических или учебно-методических и редакционных советах, редколлегиях
#Ц23	Членство в программных и организационных комитетах конференций и олимпиад
#Ц24	Инновации
#Ц25	Доля ППС, СЗП которых по итогам календарного года составляет 200% и более от региональной
#Ц26	Доля общей численности НПР до 39 лет к общей численности НПР (по головам)
#Ц27	РИД


# In[2]:


import pyodbc 
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import math
    


# In[3]:


server = 'KPI-MONITOR'
database = 'MEI2'
username = 'efqm'
password = 'mpeiR@dar'
current_date = datetime.datetime.now().date()


# In[4]:


def get_subdivision_info():
    # Create a connection to the database
    connection_string = f'DRIVER=SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
    connection = pyodbc.connect(connection_string)
    
    subdivision_dict = {}
    try:
        cursor = connection.cursor()
        # Execute the query to get SubdivisionShortName, SubdivisionCode, and SubdivisionName
        sub_query = "SELECT DISTINCT [SubdivisionShortName], [SubdivisionCode], [SubdivisionName] FROM [dbo].[EFQM_InputData_FULL]"
        results = cursor.execute(sub_query).fetchall()
        for result in results:
            subdivision_shortname = result[0]
            subdivision_code = result[1]
            subdivision_name = result[2]
            subdivision_dict[subdivision_shortname] = [subdivision_code, subdivision_name]
        return subdivision_dict
    except Exception as e:
        print("Error fetching subdivision info:", e)
    finally:
        cursor.close()
        connection.close()


# In[5]:


def get_kafedra_list(server, database, username, password):
    # Initialize an empty list to store the results
    kafedra_list = []

    # SQL query to select distinct values from the specified column
    sql_query = "SELECT DISTINCT [SubdivisionShortName] FROM [dbo].[EFQM_InputData_FULL]"

    try:
        # Connect to the SQL Server database
        conn = pyodbc.connect(f'DRIVER=SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute(sql_query)

        # Fetch all the rows and append them to the list
        rows = cursor.fetchall()
        for row in rows:
            kafedra_list.append(row[0])  # Assuming the column index is 0

        # Close the cursor and connection
        cursor.close()
        conn.close()

    except Exception as e:
        print("Error:", e)

    # Return the kafedra_list
    return kafedra_list


# In[6]:


def get_max_date():
    # Create a connection to the database
    connection_string = f'DRIVER=SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
    connection = pyodbc.connect(connection_string)
    
    try:
        cursor = connection.cursor()
        # Execute the query to get the maximum date
        date_query = "SELECT MAX(DateOper) FROM [MEI2].[dbo].[EFQM_InputData_FULL]"
        max_date = cursor.execute(date_query).fetchval()
        return max_date
    except Exception as e:
        print("Error fetching max date:", e)
    finally:
        cursor.close()
        connection.close()


# In[7]:


def get_row_by_args(arg1):
    try:
        # Connect to the SQL Server database
        conn = pyodbc.connect(f'DRIVER=SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()

        # Define the SQL query with parameters
        sql_query = """
            SELECT [factValue], 
              CASE 
                WHEN [planValue] = 0 THEN 0 
                ELSE [procentValue] 
              END AS [procentValue],
              [IndicatorCode]
       FROM [dbo].[EFQM_InputData_FULL]
       WHERE DateOper = '2023-12-31'
         AND [SubdivisionShortName] = ?
         AND [IndicatorCode] in (
           'Ц01', 'Ц02', 'Ц03', 'Ц04', 'Ц05', 'Ц06', 'Ц07', 'Ц08', 
           'Ц09', 'Ц10', 'Ц11', 'Ц12', 'Ц13', 'Ц16', 'Ц17', 'Ц18', 'Ц19',
           'Ц20', 'Ц21', 'Ц22', 'Ц23', 'Ц24', 'Ц25', 'Ц26', 'Ц27'
         )
       ORDER BY [IndicatorCode];
        """
         
        #WHERE DateOper = (SELECT MAX(DateOper) FROM [MEI2].[dbo].[EFQM_InputData_FULL])    
        # Execute the SQL query with its corresponding arguments
        cursor.execute(sql_query, (arg1))

        # Fetch the results
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print("Error:", e)
        return []


# In[8]:


kafedra_list = get_kafedra_list(server, database, username, password)


# In[9]:


kafedra_list[0]


# In[10]:


results = get_row_by_args('АСУТП')
results


# In[14]:


indicators_mapping = {
    "Ц01": "DolMag",
    "Ц02": "EGE",
    "Ц03": "DolStorMag",
    "Ц04": "DolCelevikov",
    "Ц05": "ObemPOU",
    "Ц06": "DolOstepenennykh",
    "Ц07": "Trudoustroistvo",
    "Ц08": "KolPublik",
    "Ц09": "ObemNIOKR",
    "Ц10": "Zashchity",
    "Ц11": "DolInostr",
    "Ц12": "KolInostrPrepod",
    "Ц13": "AkadMob",
    "Ц16": "ZayavAktiv",
    "Ц17": "PublNauchMaterial",
    "Ц18": "PodgotovkaEncikl",
    "Ц20": "RukovRaboty",
    "Ц21": "UchastieVystavki",
    "Ц22": "ChlenstvoSovetov",
    "Ц23": "ChlenstvoKomitetov",
    "Ц24": "Innovacii",
    "Ц25": "DolPPS200",
    "Ц26": "DolMolNPR",
    "Ц27": "RID"
}


# In[16]:


kafedra_list


# In[15]:


# Инициализация списка для хранения данных
data = []

for kafedra in kafedra_list:
    arg1 = kafedra
    results = get_row_by_args(arg1)

    # Инициализация переменных для всех индикаторов с нулевыми значениями
    DolMagFact, DolMagVip = 0, 0
    EGEFact, EGEVip = 0, 0
    DolStorMagFact, DolStorMagVip = 0, 0
    DolCelevikovFact, DolCelevikovVip = 0, 0
    ObemPOUFact, ObemPOUVip = 0, 0
    DolOstepenennykhFact, DolOstepenennykhVip = 0, 0
    TrudoustroistvoFact, TrudoustroistvoVip = 0, 0
    KolPublikFact, KolPublikVip = 0, 0
    ObemNIOKRFact, ObemNIOKRVip = 0, 0
    ZashchityFact, ZashchityVip = 0, 0
    DolInostrFact, DolInostrVip = 0, 0
    KolInostrPrepodFact, KolInostrPrepodVip = 0, 0
    AkadMobFact, AkadMobVip = 0, 0
    ZayavAktivFact, ZayavAktivVip = 0, 0
    PublNauchMaterialFact, PublNauchMaterialVip = 0, 0
    PodgotovkaEnciklFact, PodgotovkaEnciklVip = 0, 0
    RukovRabotyFact, RukovRabotyVip = 0, 0
    UchastieVystavkiFact, UchastieVystavkiVip = 0, 0
    ChlenstvoSovetovFact, ChlenstvoSovetovVip = 0, 0
    ChlenstvoKomitetovFact, ChlenstvoKomitetovVip = 0, 0
    InnovaciiFact, InnovaciiVip = 0, 0
    DolPPS200Fact, DolPPS200Vip = 0, 0
    DolMolNPRFact, DolMolNPRVip = 0, 0
    RIDFact, RIDVip = 0, 0

    # Обработка результатов вручную
    for result in results:
        indicator_code = result[2]  # Код индикатора, например 'Ц01'
        if indicator_code == "Ц01":
            DolMagFact, DolMagVip = result[0], result[1]
        elif indicator_code == "Ц02":
            EGEFact, EGEVip = result[0], result[1]
        elif indicator_code == "Ц03":
            DolStorMagFact, DolStorMagVip = result[0], result[1]
        elif indicator_code == "Ц04":
            DolCelevikovFact, DolCelevikovVip = result[0], result[1]
        elif indicator_code == "Ц05":
            ObemPOUFact, ObemPOUVip = result[0], result[1]
        elif indicator_code == "Ц06":
            DolOstepenennykhFact, DolOstepenennykhVip = result[0], result[1]
        elif indicator_code == "Ц07":
            TrudoustroistvoFact, TrudoustroistvoVip = result[0], result[1]
        elif indicator_code == "Ц08":
            KolPublikFact, KolPublikVip = result[0], result[1]
        elif indicator_code == "Ц09":
            ObemNIOKRFact, ObemNIOKRVip = result[0], result[1]
        elif indicator_code == "Ц10":
            ZashchityFact, ZashchityVip = result[0], result[1]
        elif indicator_code == "Ц11":
            DolInostrFact, DolInostrVip = result[0], result[1]
        elif indicator_code == "Ц12":
            KolInostrPrepodFact, KolInostrPrepodVip = result[0], result[1]
        elif indicator_code == "Ц13":
            AkadMobFact, AkadMobVip = result[0], result[1]
        elif indicator_code == "Ц16":
            ZayavAktivFact, ZayavAktivVip = result[0], result[1]
        elif indicator_code == "Ц17":
            PublNauchMaterialFact, PublNauchMaterialVip = result[0], result[1]
        elif indicator_code == "Ц18":
            PodgotovkaEnciklFact, PodgotovkaEnciklVip = result[0], result[1]
        elif indicator_code == "Ц20":
            RukovRabotyFact, RukovRabotyVip = result[0], result[1]
        elif indicator_code == "Ц21":
            UchastieVystavkiFact, UchastieVystavkiVip = result[0], result[1]
        elif indicator_code == "Ц22":
            ChlenstvoSovetovFact, ChlenstvoSovetovVip = result[0], result[1]
        elif indicator_code == "Ц23":
            ChlenstvoKomitetovFact, ChlenstvoKomitetovVip = result[0], result[1]
        elif indicator_code == "Ц24":
            InnovaciiFact, InnovaciiVip = result[0], result[1]
        elif indicator_code == "Ц25":
            DolPPS200Fact, DolPPS200Vip = result[0], result[1]
        elif indicator_code == "Ц26":
            DolMolNPRFact, DolMolNPRVip = result[0], result[1]
        elif indicator_code == "Ц27":
            RIDFact, RIDVip = result[0], result[1]

    # Добавляем данные в список
    data.append({
        'kafedra': kafedra,
        'DolMagFact': DolMagFact,
        'DolMagVip': DolMagVip,
        'EGEFact': EGEFact,
        'EGEVip': EGEVip,
        'DolStorMagFact': DolStorMagFact,
        'DolStorMagVip': DolStorMagVip,
        'DolCelevikovFact': DolCelevikovFact,
        'DolCelevikovVip': DolCelevikovVip,
        'ObemPOUFact': ObemPOUFact,
        'ObemPOUVip': ObemPOUVip,
        'DolOstepenennykhFact': DolOstepenennykhFact,
        'DolOstepenennykhVip': DolOstepenennykhVip,
        'TrudoustroistvoFact': TrudoustroistvoFact,
        'TrudoustroistvoVip': TrudoustroistvoVip,
        'KolPublikFact': KolPublikFact,
        'KolPublikVip': KolPublikVip,
        'ObemNIOKRFact': ObemNIOKRFact,
        'ObemNIOKRVip': ObemNIOKRVip,
        'ZashchityFact': ZashchityFact,
        'ZashchityVip': ZashchityVip,
        'DolInostrFact': DolInostrFact,
        'DolInostrVip': DolInostrVip,
        'KolInostrPrepodFact': KolInostrPrepodFact,
        'KolInostrPrepodVip': KolInostrPrepodVip,
        'AkadMobFact': AkadMobFact,
        'AkadMobVip': AkadMobVip,
        'ZayavAktivFact': ZayavAktivFact,
        'ZayavAktivVip': ZayavAktivVip,
        'PublNauchMaterialFact': PublNauchMaterialFact,
        'PublNauchMaterialVip': PublNauchMaterialVip,
        'PodgotovkaEnciklFact': PodgotovkaEnciklFact,
        'PodgotovkaEnciklVip': PodgotovkaEnciklVip,
        'RukovRabotyFact': RukovRabotyFact,
        'RukovRabotyVip': RukovRabotyVip,
        'UchastieVystavkiFact': UchastieVystavkiFact,
        'UchastieVystavkiVip': UchastieVystavkiVip,
        'ChlenstvoSovetovFact': ChlenstvoSovetovFact,
        'ChlenstvoSovetovVip': ChlenstvoSovetovVip,
        'ChlenstvoKomitetovFact': ChlenstvoKomitetovFact,
        'ChlenstvoKomitetovVip': ChlenstvoKomitetovVip,
        'InnovaciiFact': InnovaciiFact,
        'InnovaciiVip': InnovaciiVip,
        'DolPPS200Fact': DolPPS200Fact,
        'DolPPS200Vip': DolPPS200Vip,
        'DolMolNPRFact': DolMolNPRFact,
        'DolMolNPRVip': DolMolNPRVip,
        'RIDFact': RIDFact,
        'RIDVip': RIDVip
    })

# Создаем DataFrame из данных
df = pd.DataFrame(data)




# In[18]:


df


# In[19]:


# Сохраняем DataFrame в CSV файл
df.to_csv('dannie.csv', index=False)

# Очищаем DataFrame
#df = pd.DataFrame()

# Загружаем данные из CSV файла
#df = pd.read_csv('dannie6.csv')


# In[ ]:


# Извлекаем данные для паспортов 


# In[80]:


import pandas as pd

# Загружаем DataFrame (замените на ваш датасет)
# df = pd.read_csv('your_dataset.csv')

# Название кафедры
kafedra_name = "ЭЭС"

# Словарь для отображения названий полей и их описаний
field_descriptions = {
    "DolMagVip": "Доля магистров и аспирантов в общем контингенте",
    "EGEVip": "Средний балл ЕГЭ",
    "DolStorMagVip": "Доля сторонних магистров и аспирантов",
    "DolCelevikovVip": "Доля целевиков",
    "ObemPOUVip": "Объем ПОУ на ставку НПР",
    "DolOstepenennykhVip": "Доля остепененных ППС",
    "TrudoustroistvoVip": "Уровень трудоустройства выпускников",
    "KolPublikVip": "Количество публикаций в WoS, Scopus и ВАК",
    "ObemNIOKRVip": "Объем НИОКР на ставку НПР",
    "ZashchityVip": "Защиты аспирантов в срок",
    "DolInostrVip": "Доля иностранных студентов",
    "KolInostrPrepodVip": "Количество иностранных преподавателей",
    "AkadMobVip": "Академическая мобильность студентов и аспирантов",
    "ZayavAktivVip": "Заявочная активность",
    "PublNauchMaterialVip": "Подготовленные к публикации материалы",
    "PodgotovkaEnciklVip": "Подготовка энциклопедий или справочников",
    "RukovRabotyVip": "Руководство работами победителей олимпиад",
    "UchastieVystavkiVip": "Участие в научно-технических выставках",
    "ChlenstvoSovetovVip": "Членство в научных советах и редколлегиях",
    "ChlenstvoKomitetovVip": "Членство в комитетах конференций",
    "InnovaciiVip": "Инновации",
    "DolPPS200Vip": "Доля ППС с зарплатой ≥ 200% от региональной",
    "DolMolNPRVip": "Доля молодых НПР до 39 лет",
    "RIDVip": "Количество результатов интеллектуальной деятельности"
}

# Фильтруем строку по кафедре
filtered_row = df[df['kafedra'] == kafedra_name]

if not filtered_row.empty:
    # Проходим по всем столбцам, заканчивающимся на 'Vip'
    for column in df.columns:
        if column in field_descriptions:
            value = filtered_row[column].values[0]
            description = field_descriptions[column]
            print(f"{description}: {value:.3f} %")
else:
    print(f"Кафедра '{kafedra_name}' не найдена в данных.")


# In[ ]:





# In[ ]:




