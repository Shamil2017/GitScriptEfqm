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


# In[3]:


import pyodbc 
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import math
    


# In[5]:


def load_formatted_scale_from_file(filename):
    """
    Загружает значение scaleEgeNapr из файла и возвращает как список.

    :param filename: имя файла для загрузки
    :return: список с диапазонами и баллами
    """
    with open(filename, "r") as file:
        scale_list = json.load(file)
    return scale_list


# In[7]:


def format_and_print_scale(scale_list, scale_name="scaleEgeNapr"):
    """
    Форматирует и выводит список в виде читаемой переменной.
    
    :param scale_list: Список с диапазонами и баллами, например:
                       [[103, 80], [102, 65], [100, 50], [99, 44], [97, 39], [95, 33], [92, 27], [90, 21], [87, 16], [0, 10]]
    :param scale_name: Имя переменной для вывода.
    """
    formatted_output = f"{scale_name} = [\n"
    for i, (threshold, score) in enumerate(scale_list):
        if i == 0:
            formatted_output += f"    ({threshold}, {score}),  # Если значение больше {threshold}, то {score} баллов\n"
        elif i == len(scale_list) - 1:
            formatted_output += f"    ({threshold}, {score})        # Если значение меньше или равно {scale_list[i-1][0]}, то {score} баллов\n"
        else:
            formatted_output += f"    ({threshold}, {score}),  # Если значение в диапазоне {threshold} – {scale_list[i-1][0]}, то {score} баллов\n"
    formatted_output += "]"
    print(formatted_output)


# In[ ]:





# In[10]:


# загрузка шкал баллов за выполнение плана


# In[12]:


scaleEgeVip = load_formatted_scale_from_file("Shkali/scaleEgeVip.json")
scaleTrudoustroistvoVip = load_formatted_scale_from_file("Shkali/scaleTrudoustroistvoVip.json")
scaleRidVip = load_formatted_scale_from_file("Shkali/scaleRidVip.json")
scalePublNauchMaterialVip = load_formatted_scale_from_file("Shkali/scalePublNauchMaterialVip.json")
scaleAkadMobVip = load_formatted_scale_from_file("Shkali/scaleAkadMobVip.json")
scaleDolInostrVip = load_formatted_scale_from_file("Shkali/scaleDolInostrVip.json")
scaleDolMagVip = load_formatted_scale_from_file("Shkali/scaleDolMagVip.json")
scaleDolOstepenennykhVip = load_formatted_scale_from_file("Shkali/scaleDolOstepenennykhVip.json")
scaleDolPPS200Vip = load_formatted_scale_from_file("Shkali/scaleDolPPS200Vip.json")
scaleDolStorMagVip = load_formatted_scale_from_file("Shkali/scaleDolStorMagVip.json")
scaleDolCelevikovVip = load_formatted_scale_from_file("Shkali/scaleDolCelevikovVip.json")
scaleZashchityVip = load_formatted_scale_from_file("Shkali/scaleZashchityVip.json")
scaleZayavAktivVip = load_formatted_scale_from_file("Shkali/scaleZayavAktivVip.json")
scaleInnovaciiVip = load_formatted_scale_from_file("Shkali/scaleInnovaciiVip.json")
scaleKolInostrPrepodVip = load_formatted_scale_from_file("Shkali/scaleKolInostrPrepodVip.json")
scaleKolPublikVip = load_formatted_scale_from_file("Shkali/scaleKolPublikVip.json")
scaleObemNIOKRVip = load_formatted_scale_from_file("Shkali/scaleObemNIOKRVip.json")
scaleObemPOUVip = load_formatted_scale_from_file("Shkali/scaleObemPOUVip.json")
scaleDolMolNPRVip = load_formatted_scale_from_file("Shkali/scaleDolMolNPRVip.json")


# In[14]:


scaleEgeVip = [
    (109.32, 80.000000),  # Если значение больше 109.32%, то 80.0 баллов
    (100.79, 75.000000),  # Если значение в диапазоне 100.79% – 109.32%, то 65.0 баллов
    (98.91, 70.000000),  # Если значение в диапазоне 98.91% – 100.79%, то 50.0 баллов
    (94.49, 70.000000),  # Если значение в диапазоне 94.49% – 98.91%, то 50.0 баллов
    (91.31, 70.000000),  # Если значение в диапазоне 91.31% – 94.49%, то 50.0 баллов
    (90.09, 70.000000),  # Если значение в диапазоне 90.09% – 91.31%, то 50.0 баллов
    (88.38, 65.000000),  # Если значение в диапазоне 88.38% – 90.09%, то 50.0 баллов
    (87.02, 65.000000),  # Если значение в диапазоне 87.02% – 88.38%, то 50.0 баллов
    (85.44, 65.000000),  # Если значение в диапазоне 85.44% – 87.02%, то 50.0 баллов
    (50,    65.000000),  # Если значение в диапазоне 85.44% – 87.02%, то 50.0 баллов
    (0, 10)        # Если значение меньше или равно 85.44%, то 10 баллов
]


# In[ ]:





# In[17]:


# загрузка шкал напряженностей


# In[19]:


scaleEgeNapr = load_formatted_scale_from_file("Shkali/scaleEgeNapr.json")
scaleTrudoustroistvoNapr = load_formatted_scale_from_file("Shkali/scaleTrudoustroistvoNapr.json")
scaleRidNapr = load_formatted_scale_from_file("Shkali/scaleRidNapr.json")
scalePublNauchMaterialNapr = load_formatted_scale_from_file("Shkali/scalePublNauchMaterialNapr.json")
scaleAkadMobNapr = load_formatted_scale_from_file("Shkali/scaleAkadMobNapr.json")
scaleDolInostrNapr = load_formatted_scale_from_file("Shkali/scaleDolInostrNapr.json")
scaleDolMagNapr = load_formatted_scale_from_file("Shkali/scaleDolMagNapr.json")
scaleDolOstepenennykhNapr = load_formatted_scale_from_file("Shkali/scaleDolOstepenennykhNapr.json")
scaleDolPPS200Napr = load_formatted_scale_from_file("Shkali/scaleDolPPS200Napr.json")
scaleDolStorMagNapr = load_formatted_scale_from_file("Shkali/scaleDolStorMagNapr.json")
scaleDolCelevikovNapr = load_formatted_scale_from_file("Shkali/scaleDolCelevikovNapr.json")
scaleZashchityNapr = load_formatted_scale_from_file("Shkali/scaleZashchityNapr.json")
scaleZayavAktivNapr = load_formatted_scale_from_file("Shkali/scaleZayavAktivNapr.json")
scaleInnovaciiNapr = load_formatted_scale_from_file("Shkali/scaleInnovaciiNapr.json")
scaleKolInostrPrepodNapr = load_formatted_scale_from_file("Shkali/scaleKolInostrPrepodNapr.json")
scaleKolPublikNapr = load_formatted_scale_from_file("Shkali/scaleKolPublikNapr.json")
scaleObemNIOKRNapr = load_formatted_scale_from_file("Shkali/scaleObemNIOKRNapr.json")
scaleObemPOUNapr = load_formatted_scale_from_file("Shkali/scaleObemPOUNapr.json")
scaleDolMolNPRNapr = load_formatted_scale_from_file("Shkali/scaleDolMolNPRNapr.json")


# In[ ]:


# Список переменных и их имен
scales = [
    ("scaleEgeNapr", scaleEgeNapr),
    ("scaleTrudoustroistvoNapr", scaleTrudoustroistvoNapr),
    ("scaleRidNapr", scaleRidNapr),
    ("scalePublNauchMaterialNapr", scalePublNauchMaterialNapr),
    ("scaleAkadMobNapr", scaleAkadMobNapr),
    ("scaleDolInostrNapr", scaleDolInostrNapr),
    ("scaleDolMagNapr", scaleDolMagNapr),
    ("scaleDolOstepenennykhNapr", scaleDolOstepenennykhNapr),
    ("scaleDolPPS200Napr", scaleDolPPS200Napr),
    ("scaleDolStorMagNapr", scaleDolStorMagNapr),
    ("scaleDolCelevikovNapr", scaleDolCelevikovNapr),
    ("scaleZashchityNapr", scaleZashchityNapr),
    ("scaleZayavAktivNapr", scaleZayavAktivNapr),
    ("scaleInnovaciiNapr", scaleInnovaciiNapr),
    ("scaleKolInostrPrepodNapr", scaleKolInostrPrepodNapr),
    ("scaleKolPublikNapr", scaleKolPublikNapr),
    ("scaleObemNIOKRNapr", scaleObemNIOKRNapr),
    ("scaleObemPOUNapr", scaleObemPOUNapr),
    ("scaleDolMolNPRNapr", scaleDolMolNPRNapr)
]

# Вызываем функцию для каждой шкалы
for name, scale in scales:
    print(f"Форматированная шкала для {name}:")
    format_and_print_scale(scale, scale_name=name)
    print("\n")  # Пустая строка для разделения вывода


# In[21]:


# Список переменных и их имен
scales = [
    ("scaleEgeVip", scaleEgeVip),
    ("scaleTrudoustroistvoVip", scaleTrudoustroistvoVip),
    ("scaleRidVip", scaleRidVip),
    ("scalePublNauchMaterialVip", scalePublNauchMaterialVip),
    ("scaleAkadMobVip", scaleAkadMobVip),
    ("scaleDolInostrVip", scaleDolInostrVip),
    ("scaleDolMagVip", scaleDolMagVip),
    ("scaleDolOstepenennykhVip", scaleDolOstepenennykhVip),
    ("scaleDolPPS200Vip", scaleDolPPS200Vip),
    ("scaleDolStorMagVip", scaleDolStorMagVip),
    ("scaleDolCelevikovVip", scaleDolCelevikovVip),
    ("scaleZashchityVip", scaleZashchityVip),
    ("scaleZayavAktivVip", scaleZayavAktivVip),
    ("scaleInnovaciiVip", scaleInnovaciiVip),
    ("scaleKolInostrPrepodVip", scaleKolInostrPrepodVip),
    ("scaleKolPublikVip", scaleKolPublikVip),
    ("scaleObemNIOKRVip", scaleObemNIOKRVip),
    ("scaleObemPOUVip", scaleObemPOUVip),
    ("scaleDolMolNPRVip", scaleDolMolNPRVip)
]

# Вызываем функцию для каждой шкалы
for name, scale in scales:
    print(f"Форматированная шкала для {name}:")
    format_and_print_scale(scale, scale_name=name)
    print("\n")  # Пустая строка для разделения вывода


# In[27]:


# Функция для расчета баллов на основе шкалы
def CalcBallVipolnenia(value, scale):
    """
    value: float - значение выполнения плана
    scale: list of tuples - шкала в формате [(процент, баллы), ...]
    """
    for percent, score in scale:
        if value >= percent:
            return score
    # Если значение меньше минимального, возвращаем минимальный балл
    return scale[-1][1]

# Пример использования
#example_value = 93  # Значение выполнения плана
#score = CalcBallVipolnenia(example_value, scaleTrud)
#print(f"Баллы за выполнение: {score}")


# In[29]:


def CalcBallCompare(E_kaf, E_univ):
    
    """
    value: float - значение выполнения плана
    scale: list of tuples - шкала в формате [(процент, баллы), ...]
    """
    for percent, score in scale:
        if (E_kaf/E_univ) >= percent:
            return score
    # Если значение меньше минимального, возвращаем минимальный балл
    return scale[-1][1]


# In[31]:


def calculate_final_score(B_vyp, B_srav, w_vyp=0.6, w_srav=0.4):
    # Расчет итогового балла по формуле
    B_itog = w_vyp * B_vyp + w_srav * B_srav
    # Округление в большую сторону до числа, кратного 5
    B_itog = math.ceil(B_itog / 5) * 5
    # Применение ограничений
    if B_itog > 80:
        B_itog = 80
    elif B_itog < 20 and B_itog>0.01:
        B_itog = 20
    elif B_itog<=0.01:
        B_itog = 0
    
    return B_itog


# In[33]:


def get_sredBallFinal_values(df, kafedra_column, sredBallVipolnenia_column, sredBallCompare_column, sredBallFinal_column):
    # Обновленный список нужных кафедр в заданном порядке
    kafedry_list = [
        "ЭЭС", "РЗиАЭ", "ИТНО", "ЭППЭ", "Пром.эл.", "МЭП", "ТЭС", "ТЭВН", 
        "РМДиПМ", "ПТС", "ЭМЭЭА", "ИЭиОТ", "УИТ", "ТМ", "Физики", "ЭЭП", 
        "ГВИЭ", "ОФиЯС", "АЭС", "ТОЭ", "АСУТП", "И и К", "ПГТ", "РТС", 
        "ЭиН", "АЭП", "ХиЭЭ", "ВТ", "МиПЭУ", "ПМИИ", "ВМСС", "Эл.ст.", 
        "НТ", "ЭКАОиЭТ", "ТОТ", "МКМ", "ГГМ", "ДИТ", "ТМПУ", "РС и Л", 
        "ОРТ", "ФТЭМК", "Ин.яз", "БИТ", "ИТФ", "РТП и АС", "ЭГТС", "ФОРС", 
        "Светотех.", "ФПС", "Дизайн", "ВМ", "Ф и С"
    ]

    # Фильтрация DataFrame по списку кафедр
    filtered_df = df[df[kafedra_column].isin(kafedry_list)]

    # Сохранение результатов в нужном порядке
    result = []
    for kafedra in kafedry_list:
        # Находим строки, соответствующие конкретной кафедре
        row = filtered_df[filtered_df[kafedra_column] == kafedra]
        if not row.empty:
            # Извлекаем значения из нужных столбцов и приводим к целому числу
            vipolnenia = int(row.iloc[0][sredBallVipolnenia_column])
            compare = int(row.iloc[0][sredBallCompare_column])
            final = int(row.iloc[0][sredBallFinal_column])
            result.append(f"{kafedra}; {vipolnenia}; {compare}; {final}")
        else:
            # Если данных по кафедре нет, выводим "-"
            result.append(f"{kafedra}; - ; - ; -")

    return result


# In[ ]:





# In[35]:


# Сохраняем DataFrame в CSV файл
#df.to_csv('dannie6.csv', index=False)

# Очищаем DataFrame
df = pd.DataFrame()

# Загружаем данные из CSV файла
df = pd.read_csv('dannie.csv')


# In[37]:


# Загрузка данных из CSV файла средних по университету
dfSred = pd.read_csv('sredneeUniver.csv', delimiter=';')

# Преобразование DataFrame в словарь
dictSred = dfSred.set_index('IndicatorCode')['SredneePoUniver'].to_dict()

print(dictSred)


# In[39]:


df


# In[41]:


columns_list = df.columns.tolist()
print(columns_list)


# In[43]:


# Фильтрация строк, где кафедра равна 'РТС'
filtered_df = df[df['kafedra'] == 'РТС']

# Вывод отфильтрованных данных
filtered_df.to_csv('filtered_data.csv', index=False, encoding='utf-8')


# In[ ]:





# In[46]:


# Преобразование значений в словаре dictSred, заменяя запятую на точку перед преобразованием в float
dictSred = {key: float(value.replace(',', '.')) for key, value in dictSred.items()}


# In[33]:


def process_data(EGEFact, EGEVip, EGEFactVipolnenia, df, scaleEgeVip, 
                 EGEFactBallCompare, EGEFactFinal, sred_C02):
    
    # Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
    df_nonzero = df[df[EGEFact] >= 0.002]
    # Вычисляем стандартное отклонение для столбца 'sredFact'
    std_EGE = float(df_nonzero[EGEFact].std())
    
    # Если std_EGE - строка, заменяем запятую на точку
    std_EGE = float(std_EGE.replace(',', '.') if isinstance(std_EGE, str) else std_EGE)
    
    # Приведение значений в 'EGEFact' к float
    df[EGEFact] = pd.to_numeric(df[EGEFact], errors='coerce')
    
    # Приведение значений в 'EGEVip' к float
    df[EGEVip] = pd.to_numeric(df[EGEVip], errors='coerce')
    
    # Приведение значения sred_C02 к float с заменой запятой на точку
    if isinstance(sred_C02, str):
        sred_C02 = float(sred_C02.replace(',', '.'))
    else:
        sred_C02 = float(sred_C02)
    
    # Применяем функцию CalcBallVipolnenia для столбца EGEFactVipolnenia
    df[EGEFactVipolnenia] = df[EGEVip].apply(
        lambda x: CalcBallVipolnenia(x, scaleEgeVip) if x >= 0.002 else 0
    )
    
    # Применяем функцию CalcBallCompare для столбца EGEFactBallCompare
    df[EGEFactBallCompare] = df[EGEFact].apply(
        lambda x: CalcBallCompare(x, sred_C02, std_EGE) if x >= 0.002 else 0
    )
    
    # Применяем функцию calculate_final_score для столбца EGEFactFinal
    df[EGEFactFinal] = df.apply(
        lambda row: calculate_final_score(row[EGEFactVipolnenia], row[EGEFactBallCompare]),
        axis=1
    )
    
    return df


# In[35]:


def process_data0(EGEFact, EGEVip, EGEFactVipolnenia, df, scaleEgeVip, 
                    EGEFactBallCompare, EGEFactFinal, sred_C02):
    # Отфильтровать DataFrame, оставив только ненулевые значения в столбце EGEFact
    df_nonzero = df[df[EGEFact] >= 0.002]

    # Вычисляем стандартное отклонение для столбца 'EGEFact'
    std_EGE = float(df_nonzero[EGEFact].std())

    # Если std_EGE - строка, заменяем запятую на точку
    std_EGE = float(std_EGE.replace(',', '.') if isinstance(std_EGE, str) else std_EGE)

    # Приведение значений в 'EGEFact' и 'EGEVip' к float
    df[EGEFact] = pd.to_numeric(df[EGEFact], errors='coerce')
    df[EGEVip] = pd.to_numeric(df[EGEVip], errors='coerce')

    # Приведение значения sred_C02 к float с заменой запятой на точку
    sred_C02 = float(sred_C02.replace(',', '.')) if isinstance(sred_C02, str) else float(sred_C02)

    # Создаем новые столбцы с результатами
    new_columns = pd.DataFrame({
        EGEFactVipolnenia: df[EGEVip].apply(
            lambda x: CalcBallVipolnenia(x, scaleEgeVip) if x >= 0.002 else 0
        ),
        EGEFactBallCompare: df[EGEFact].apply(
            lambda x: CalcBallCompare(x, sred_C02, std_EGE) if x >= 0.002 else 0
        ),
        EGEFactFinal: df[EGEFactFinal].apply(
            lambda row: calculate_final_score(
                row.get(EGEFactVipolnenia, 0),
                row.get(EGEFactBallCompare, 0)
            ),
            axis=1
        )
    })

    # Объединяем новые столбцы с исходным DataFrame
    df = pd.concat([df, new_columns], axis=1)

    return df


# In[37]:


def calculate_krit6(row, columns):
    # Извлекаем ненулевые значения из указанных столбцов
    non_zero_values = [value for value in row[columns] if value > 0]
    
    # Если ненулевых значений нет, возвращаем 0
    if not non_zero_values:
        return 0
    
    # Вычисляем среднее ненулевых значений
    avg_value = sum(non_zero_values) / len(non_zero_values)
    
    # Округляем до ближайшего кратного 5
    return round(avg_value / 5) * 5


# In[39]:


print(list(df.columns))


# In[41]:


#По всем показателям


# In[16]:


# Для Доля магистров и аспирантов в общем контингенте
result_df = process_data(
    EGEFact='DolMagFact',
    EGEVip='DolMagVip',
    EGEFactVipolnenia='DolMagFactVipolnenia',
    df=df,
    scaleEgeVip=scaleDolMagVip,
    EGEFactBallCompare='DolMagFactBallCompare',
    EGEFactFinal='DolMagFactFinal',
    sred_C02=dictSred['Ц01']
)
result_df[['kafedra', 'DolMagFact', 'DolMagVip', 'DolMagFactVipolnenia', 'DolMagFactBallCompare', 'DolMagFactFinal']]


# In[17]:


print(list(result_df.columns))


# In[18]:


# Для Средний балл ЕГЭ
result_df = process_data(
    EGEFact='EGEFact',
    EGEVip='EGEVip',
    EGEFactVipolnenia='EGEFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleEgeVip,
    EGEFactBallCompare='EGEFactBallCompare',
    EGEFactFinal='EGEFactFinal',
    sred_C02=dictSred['Ц02']
)
result_df[['kafedra', 'EGEFact', 'EGEVip', 'EGEFactVipolnenia', 'EGEFactBallCompare', 'EGEFactFinal']]


# In[19]:


# Для Доля сторонних магистров и аспирантов
result_df = process_data(
    EGEFact='DolStorMagFact',
    EGEVip='DolStorMagVip',
    EGEFactVipolnenia='DolStorMagFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleDolStorMagVip,
    EGEFactBallCompare='DolStorMagFactBallCompare',
    EGEFactFinal='DolStorMagFactFinal',
    sred_C02=dictSred['Ц03']
)


# In[20]:


result_df[['kafedra', 'DolStorMagFact', 'DolStorMagVip', 'DolStorMagFactVipolnenia', 'DolStorMagFactBallCompare', 'DolStorMagFactFinal']]


# In[21]:


# Для Доля целевиков
result_df = process_data(
    EGEFact='DolCelevikovFact',
    EGEVip='DolCelevikovVip',
    EGEFactVipolnenia='DolCelevikovFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleDolCelevikovVip,
    EGEFactBallCompare='DolCelevikovFactBallCompare',
    EGEFactFinal='DolCelevikovFactFinal',
    sred_C02=dictSred['Ц04']
)
result_df[['kafedra', 'DolCelevikovFact', 'DolCelevikovVip', 'DolCelevikovFactVipolnenia', 'DolCelevikovFactBallCompare', 'DolCelevikovFactFinal']]


# In[57]:


# Применение функции с выводом результатов для проверки
result_df['debug_CalcBallCompare'] = result_df['ObemPOUFact'].apply(
    lambda x: CalcBallCompare(x, dictSred['Ц05'], result_df['ObemPOUFact'].std())
    if x >= 0.002 else 0
)


# In[52]:


result_df['ObemPOUFact'].std()


# In[53]:


dictSred['Ц05']


# In[58]:


result_df[['kafedra', 'ObemPOUFact', 'debug_CalcBallCompare']]


# In[22]:


# Для Объем ПОУ на ставку НПР
result_df = process_data(
    EGEFact='ObemPOUFact',
    EGEVip='ObemPOUVip',
    EGEFactVipolnenia='ObemPOUFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleObemPOUVip,
    EGEFactBallCompare='ObemPOUFactBallCompare',
    EGEFactFinal='ObemPOUFactFinal',
    sred_C02=dictSred['Ц05']
)
result_df[['kafedra', 'ObemPOUFact', 'ObemPOUVip', 'ObemPOUFactVipolnenia', 'ObemPOUFactBallCompare', 'ObemPOUFactFinal']]


# In[ ]:





# In[23]:


# Для Доля остепененных ППС
result_df = process_data(
    EGEFact='DolOstepenennykhFact',
    EGEVip='DolOstepenennykhVip',
    EGEFactVipolnenia='DolOstepenennykhFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleDolOstepenennykhVip,
    EGEFactBallCompare='DolOstepenennykhFactBallCompare',
    EGEFactFinal='DolOstepenennykhFactFinal',
    sred_C02=dictSred['Ц06']
)
result_df[['kafedra', 'DolOstepenennykhFact', 'DolOstepenennykhVip', 'DolOstepenennykhFactVipolnenia', 'DolOstepenennykhFactBallCompare', 'DolOstepenennykhFactFinal']]


# In[24]:


print(list(result_df.columns))


# In[25]:


# Для Трудоустройства
result_df = process_data(
    EGEFact='TrudoustroistvoFact',
    EGEVip='TrudoustroistvoVip',
    EGEFactVipolnenia='TrudoustroistvoFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleTrudoustroistvoVip,
    EGEFactBallCompare='TrudoustroistvoFactBallCompare',
    EGEFactFinal='TrudoustroistvoFactFinal',
    sred_C02=dictSred['Ц07']
)
result_df[['kafedra', 'TrudoustroistvoFact', 'TrudoustroistvoVip', 'TrudoustroistvoFactVipolnenia', 'TrudoustroistvoFactBallCompare', 'TrudoustroistvoFactFinal']]


# In[26]:


# Для Количество публикаций
result_df = process_data(
    EGEFact='KolPublikFact',
    EGEVip='KolPublikVip',
    EGEFactVipolnenia='KolPublikFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleKolPublikVip,
    EGEFactBallCompare='KolPublikFactBallCompare',
    EGEFactFinal='KolPublikFactFinal',
    sred_C02=dictSred['Ц08']
)
result_df[['kafedra', 'KolPublikFact', 'KolPublikVip', 'KolPublikFactVipolnenia', 'KolPublikFactBallCompare', 'KolPublikFactFinal']]


# In[27]:


# Для Объем НИОКР
result_df = process_data(
    EGEFact='ObemNIOKRFact',
    EGEVip='ObemNIOKRVip',
    EGEFactVipolnenia='ObemNIOKRFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleObemNIOKRVip,
    EGEFactBallCompare='ObemNIOKRFactBallCompare',
    EGEFactFinal='ObemNIOKRFactFinal',
    sred_C02=dictSred['Ц09']
)
result_df[['kafedra', 'ObemNIOKRFact', 'ObemNIOKRVip', 'ObemNIOKRFactVipolnenia', 'ObemNIOKRFactBallCompare', 'ObemNIOKRFactFinal']]


# In[28]:


# Для Защиты аспирантов в срок
result_df = process_data(
    EGEFact='ZashchityFact',
    EGEVip='ZashchityVip',
    EGEFactVipolnenia='ZashchityFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleZashchityVip,
    EGEFactBallCompare='ZashchityFactBallCompare',
    EGEFactFinal='ZashchityFactFinal',
    sred_C02=dictSred['Ц10']
)
result_df[['kafedra', 'ZashchityFact', 'ZashchityVip', 'ZashchityFactVipolnenia', 'ZashchityFactBallCompare', 'ZashchityFactFinal']]


# In[29]:


# Для Доля иностранных студентов
result_df = process_data(
    EGEFact='DolInostrFact',
    EGEVip='DolInostrVip',
    EGEFactVipolnenia='DolInostrFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleDolInostrVip,
    EGEFactBallCompare='DolInostrFactBallCompare',
    EGEFactFinal='DolInostrFactFinal',
    sred_C02=dictSred['Ц11']
)
result_df[['kafedra', 'DolInostrFact', 'DolInostrVip', 'DolInostrFactVipolnenia', 'DolInostrFactBallCompare', 'DolInostrFactFinal']]


# In[30]:


# Для Количество иностранных преподавателей
result_df = process_data(
    EGEFact='KolInostrPrepodFact',
    EGEVip='KolInostrPrepodVip',
    EGEFactVipolnenia='KolInostrPrepodFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleKolInostrPrepodVip,
    EGEFactBallCompare='KolInostrPrepodFactBallCompare',
    EGEFactFinal='KolInostrPrepodFactFinal',
    sred_C02=dictSred['Ц12']
)
result_df[['kafedra', 'KolInostrPrepodFact', 'KolInostrPrepodVip', 'KolInostrPrepodFactVipolnenia', 'KolInostrPrepodFactBallCompare', 'KolInostrPrepodFactFinal']]


# In[31]:


# Для Академическая мобильность студентов и аспирантов
result_df = process_data(
    EGEFact='AkadMobFact',
    EGEVip='AkadMobVip',
    EGEFactVipolnenia='AkadMobFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleAkadMobVip,
    EGEFactBallCompare='AkadMobFactBallCompare',
    EGEFactFinal='AkadMobFactFinal',
    sred_C02=dictSred['Ц13']
)
result_df[['kafedra', 'AkadMobFact', 'AkadMobVip', 'AkadMobFactVipolnenia', 'AkadMobFactBallCompare', 'AkadMobFactFinal']]


# In[32]:


# Для Заявочная активность
result_df = process_data(
    EGEFact='ZayavAktivFact',
    EGEVip='ZayavAktivVip',
    EGEFactVipolnenia='ZayavAktivFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleZayavAktivVip,
    EGEFactBallCompare='ZayavAktivFactBallCompare',
    EGEFactFinal='ZayavAktivFactFinal',
    sred_C02=dictSred['Ц16']
)
result_df[['kafedra', 'ZayavAktivFact', 'ZayavAktivVip', 'ZayavAktivFactVipolnenia', 'ZayavAktivFactBallCompare', 'ZayavAktivFactFinal']]


# In[ ]:





# In[ ]:





# In[33]:


# Для Подготовленные к публикации тематические материалы
result_df = process_data(
    EGEFact='PublNauchMaterialFact',
    EGEVip='PublNauchMaterialVip',
    EGEFactVipolnenia='PublNauchMaterialFactVipolnenia',
    df=result_df,
    scaleEgeVip=scalePublNauchMaterialVip,
    EGEFactBallCompare='PublNauchMaterialFactBallCompare',
    EGEFactFinal='PublNauchMaterialFactFinal',
    sred_C02=dictSred['Ц17']
)
result_df[['kafedra', 'PublNauchMaterialFact', 'PublNauchMaterialVip', 'PublNauchMaterialFactVipolnenia', 'PublNauchMaterialFactBallCompare', 'PublNauchMaterialFactFinal']]


# In[ ]:





# In[34]:


# Для Подготовка энциклопедии/справочника
result_df = process_data(
    EGEFact='PodgotovkaEnciklFact',
    EGEVip='PodgotovkaEnciklVip',
    EGEFactVipolnenia='PodgotovkaEnciklFactVipolnenia',
    df=result_df,
    scaleEgeVip=scalePodgotovkaEnciklVip,
    EGEFactBallCompare='PodgotovkaEnciklFactBallCompare',
    EGEFactFinal='PodgotovkaEnciklFactFinal',
    sred_C02=dictSred['Ц18']
)
result_df[['kafedra', 'PodgotovkaEnciklFact', 'PodgotovkaEnciklVip', 'PodgotovkaEnciklFactVipolnenia', 'PodgotovkaEnciklFactBallCompare', 'PodgotovkaEnciklFactFinal']]


# In[35]:


# Для Руководство работами студентов и аспирантов
result_df = process_data(
    EGEFact='RukovRabotyFact',
    EGEVip='RukovRabotyVip',
    EGEFactVipolnenia='RukovRabotyFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleEgeVip,
    EGEFactBallCompare='RukovRabotyFactBallCompare',
    EGEFactFinal='RukovRabotyFactFinal',
    sred_C02=dictSred['Ц20']
)
result_df[['kafedra', 'RukovRabotyFact', 'RukovRabotyVip', 'RukovRabotyFactVipolnenia', 'RukovRabotyFactBallCompare', 'RukovRabotyFactFinal']]


# In[36]:


# Для Инновации
result_df = process_data(
    EGEFact='InnovaciiFact',
    EGEVip='InnovaciiVip',
    EGEFactVipolnenia='InnovaciiFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleInnovaciiVip,
    EGEFactBallCompare='InnovaciiFactBallCompare',
    EGEFactFinal='InnovaciiFactFinal',
    sred_C02=dictSred['Ц24']
)
result_df[['kafedra', 'InnovaciiFact', 'InnovaciiVip', 'InnovaciiFactVipolnenia', 'InnovaciiFactBallCompare', 'InnovaciiFactFinal']]


# In[37]:


# Для Доля ППС, СЗП которых >= 200% от региональной
result_df = process_data(
    EGEFact='DolPPS200Fact',
    EGEVip='DolPPS200Vip',
    EGEFactVipolnenia='DolPPS200FactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleDolPPS200Vip,
    EGEFactBallCompare='DolPPS200FactBallCompare',
    EGEFactFinal='DolPPS200FactFinal',
    sred_C02=dictSred['Ц25']
)
result_df[['kafedra', 'DolPPS200Fact', 'DolPPS200Vip', 'DolPPS200FactVipolnenia', 'DolPPS200FactBallCompare', 'DolPPS200FactFinal']]


# In[51]:


# Для Доля общей численности НПР до 39 лет
result_df = process_data(
    EGEFact='DolMolNPRFact',
    EGEVip='DolMolNPRVip',
    EGEFactVipolnenia='DolMolNPRFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleDolMolNPRVip,
    EGEFactBallCompare='DolMolNPRFactBallCompare',
    EGEFactFinal='DolMolNPRFactFinal',
    sred_C02=dictSred['Ц26']
)
result_df[['kafedra', 'DolMolNPRFact', 'DolMolNPRVip', 'DolMolNPRFactVipolnenia', 'DolMolNPRFactBallCompare', 'DolMolNPRFactFinal']]


# In[39]:


# Для РИД
result_df = process_data(
    EGEFact='RIDFact',
    EGEVip='RIDVip',
    EGEFactVipolnenia='RIDFactVipolnenia',
    df=result_df,
    scaleEgeVip=scaleRidVip,
    EGEFactBallCompare='RIDFactBallCompare',
    EGEFactFinal='RIDFactFinal',
    sred_C02=dictSred['Ц27']
)
result_df[['kafedra', 'RIDFact', 'RIDVip', 'RIDFactVipolnenia', 'RIDFactBallCompare', 'RIDFactFinal']]


# In[40]:


print(result_df.columns.tolist())


# In[41]:


# Сохраняем DataFrame в CSV файл
result_df.to_csv('result.csv', index=False)


# In[42]:


# Очищаем DataFrame
result_dfNew = pd.DataFrame()

# Загружаем данные из CSV файла
result_dfNew = pd.read_csv('result.csv')


# In[43]:


#EGE + Trudoustroistvo + RID + PublNauchMaterial


# In[44]:


result_dfNew[['kafedra', 'EGEFactFinal','TrudoustroistvoFactFinal', 'RIDFactFinal','PublNauchMaterialFactFinal']]


# In[45]:


# Указываем столбцы для расчета
columns_to_average = ['EGEFactFinal', 'TrudoustroistvoFactFinal', 'RIDFactFinal', 'PublNauchMaterialFactFinal']

# Создаем новый столбец 'krit6'
result_dfNew['krit6'] = result_dfNew.apply(calculate_krit6, columns=columns_to_average, axis=1)


# In[46]:


result_dfNew[['kafedra', 'EGEFactFinal','TrudoustroistvoFactFinal', 'RIDFactFinal','PublNauchMaterialFactFinal','krit6']]


# In[47]:


print(result_dfNew.columns.tolist())


# In[48]:


result_dfNew[['kafedra', 'EGEFactFinal','TrudoustroistvoFactFinal', 'RIDFactFinal','PublNauchMaterialFactFinal','krit6']]


# In[49]:


print(list(result_dfNew.columns))


# In[50]:


columns_to_select = [
    'kafedra',    
    'AkadMobFactFinal',            # Академическая мобильность студентов и аспирантов, чел. (Ц13)
    'DolInostrFactFinal',          # Доля иностранных студентов (Ц11)
    'DolMagFactFinal',             # Доля магистров и аспирантов в общем контингенте, % (Ц01)
    'DolOstepenennykhFactFinal',   # Доля остепененных ППС, % (Ц06)
    'DolPPS200FactFinal',          # Доля ППС, СЗП (Ц25)
    'DolStorMagFactFinal',         # Доля сторонних магистров и аспирантов, % (Ц03)
    'DolCelevikovFactFinal',       # Доля целевиков, % (Ц04)
    'ZashchityFactFinal',          # Доля защит аспирантов в срок, % (Ц10)
    'DolMolNPRFactFinal',          # Доля ППС до 39 лет, % (Ц26)
    'ZayavAktivFactFinal',         # Заявочная активность, ед. (Ц16)
    'InnovaciiFactFinal',          # Инновации, ед. (Ц24)
    'KolInostrPrepodFactFinal',    # Количество иностранных преподавателей, чел. (Ц12)
    'KolPublikFactFinal',          # Количество публикаций в WoS (Ц08)
    'ObemNIOKRFactFinal',          # Объем НИОКР на ставку НПР, тыс. руб. (Ц09)
    'ObemPOUFactFinal'             # Объем ПОУ, тыс. руб. (Ц05)
]

# Вывод выбранных столбцов
selected_columns_df = result_dfNew[columns_to_select]


# In[ ]:


selected_columns_df


# In[53]:


#Критерий 7


# In[54]:


columns_for_krit7 = [
    'AkadMobFactFinal',            # Академическая мобильность студентов и аспирантов, чел. (Ц13)
    'DolInostrFactFinal',          # Доля иностранных студентов (Ц11)
    'DolMagFactFinal',             # Доля магистров и аспирантов в общем контингенте, % (Ц01)
    'DolOstepenennykhFactFinal',   # Доля остепененных ППС, % (Ц06)
    'DolPPS200FactFinal',          # Доля ППС, СЗП (Ц25)
    'DolStorMagFactFinal',         # Доля сторонних магистров и аспирантов, % (Ц03)
    'DolCelevikovFactFinal',       # Доля целевиков, % (Ц04)
    'ZashchityFactFinal',          # Доля защит аспирантов в срок, % (Ц10)
    'DolMolNPRFactFinal',           # Доля ППС до 39 лет, % (Ц26)
    'ZayavAktivFactFinal',         # Заявочная активность, ед. (Ц16)
    'InnovaciiFactFinal',          # Инновации, ед. (Ц24)
    'KolInostrPrepodFactFinal',    # Количество иностранных преподавателей, чел. (Ц12)
    'KolPublikFactFinal',          # Количество публикаций в WoS (Ц08)
    'ObemNIOKRFactFinal',          # Объем НИОКР на ставку НПР, тыс. руб. (Ц09)
    'ObemPOUFactFinal'             # Объем ПОУ на ставку НПР, тыс. руб Ц05
]

# Функция для расчета krit7
def calculate_krit7(row, columns):
    # Извлекаем ненулевые значения из указанных столбцов
    non_zero_values = [value for value in row[columns] if value > 0]
    
    # Если ненулевых значений нет, возвращаем 0
    if not non_zero_values:
        return 0
    
    # Вычисляем среднее ненулевых значений
    avg_value = sum(non_zero_values) / len(non_zero_values)
    
    # Округляем до ближайшего кратного 5
    return round(avg_value / 5) * 5

# Применяем функцию к DataFrame
result_dfNew['krit7'] = result_dfNew.apply(calculate_krit7, columns=columns_for_krit7, axis=1)


# In[55]:


result_dfNew[['kafedra'] + columns_for_krit7 + ['krit7']]


# In[56]:


print(list(result_dfNew.columns))


# In[57]:


# Сохраняем DataFrame в CSV файл
result_dfNew.to_csv('resultFinal.csv', index=False)


# In[58]:


get_ipython().system('pip install pandas openpyxl xlsxwriter')


# In[59]:


# Specify the filename and sheet name
output_file = "output2.xlsx"
sheet_name = "Sheet1"

# Save the DataFrame to an Excel file with UTF-8 encoding
result_dfNew.to_excel(output_file, index=False, sheet_name=sheet_name, engine="xlsxwriter")

print(f"DataFrame successfully saved to {output_file}")


# In[112]:


# Очищаем DataFrame
df2 = pd.DataFrame()

# Загружаем данные из CSV файла
df2 = pd.read_csv('dannie.csv')


# In[113]:


# Specify the filename and sheet name
output_file = "dannie.xlsx"
sheet_name = "Sheet1"

# Save the DataFrame to an Excel file with UTF-8 encoding
df2.to_excel(output_file, index=False, sheet_name=sheet_name, engine="xlsxwriter")

print(f"DataFrame successfully saved to {output_file}")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[111]:


result = get_sredBallFinal_values(df, 'kafedra', 'sredBallVipolnenia', 'sredBallCompare', 'sredBallFinal')
print("\n".join(result))


# In[ ]:




