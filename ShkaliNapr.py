#!/usr/bin/env python
# coding: utf-8

# In[3]:


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
#- #Ц18	Подготовка энциклопедии/справочника
#- #Ц20	Руководство работами студентов и аспирантов – победителей олимпиад (конкурсов, выставок)
#Ц21	Участие в научно-технических и творческих выставках (учитывается только участие с экспонатами)
##Ц22	Членство в научно-технических или учебно-методических и редакционных советах, редколлегиях
#Ц23	Членство в программных и организационных комитетах конференций и олимпиад
#Ц24	Инновации
#Ц25	Доля ППС, СЗП которых по итогам календарного года составляет 200% и более от региональной
#Ц26	Доля общей численности НПР до 39 лет к общей численности НПР (по головам)
#Ц27	РИД


# In[5]:


import pyodbc 
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import math
import json
    


# In[7]:


server = 'KPI-MONITOR'
database = 'MEI2'
username = 'efqm'
password = 'mpeiR@dar'
current_date = datetime.datetime.now().date()


# In[9]:


def sorted_column_to_string(df, column_name):
    """
    Функция сортирует значения указанного столбца DataFrame по возрастанию
    и возвращает их в виде строки, разделенной точкой с запятой и пробелом.
    
    :param df: DataFrame, содержащий данные
    :param column_name: Название столбца для сортировки и вывода
    :return: Строка отсортированных значений столбца
    """
    sorted_values = df[column_name].sort_values(ascending=True)  # Сортируем по возрастанию
    return "; ".join(map(str, sorted_values.tolist()))  # Преобразуем в строку


# In[11]:


def analyze_distribution(df, column_name):
    """
    Эта функция рассчитывает статистические показатели для указанного столбца в DataFrame.
    Она также определяет характер распределения и выявляет выбросы на основе распределения.

    Параметры:
        df (pd.DataFrame): DataFrame, содержащий данные.
        column_name (str): Название столбца для анализа.

    Возвращает:
        None: Печатает результаты построчно, каждая статистика выводится отдельно.
    """
    data = df[column_name].dropna()  # Убираем NaN значения для корректного расчета
    
    # Рассчитываем базовые статистические показатели
    minimum = data.min()
    maximum = data.max()
    median = data.median()
    
    # Квартильные значения
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1  # Межквартильный размах
    
    # Определение выбросов (значения выше 105% считаются выбросами)
    outliers = data[data > 105]
    
    # Определение типа скошенности
    skewness_type = "правостороннее скошенное распределение" if data.mean() < data.max() else "приблизительно симметричное"
    
    # Печать результатов построчно
    print("Минимум:", minimum)
    print("Максимум:", maximum)
    print("Медиана (Q2):", median)
    print("Q1 (25-й перцентиль):", q1)
    print("Q3 (75-й перцентиль):", q3)
    print("Межквартильный размах (IQR):", iqr)
    print("Тип скошенности:", skewness_type)
    print("Выбросы:", ', '.join(map(str, outliers.tolist())) if not outliers.empty else "Нет выбросов")


# In[13]:


def build_scale_quartiles(percentages, num_sections=4, min_score=50, max_score=80):
    """
    Функция для построения шкалы присвоения баллов на основе квартильного или перцентильного разделения данных.

    :param percentages: список процентных значений выполнения плана
    :param num_sections: количество секций для разделения (по умолчанию 4 для квартилей)
    :param min_score: минимальный балл (по умолчанию 50)
    :param max_score: максимальный балл (по умолчанию 80)
    :return: DataFrame с диапазонами процентов и соответствующими баллами
    """
    df_unique = list(set(percentages.tolist()))
  

   
    # Преобразуем список в numpy array, отфильтровав только числовые значения
    data = np.array([float(value) for value in df_unique if isinstance(value, (int, float, str)) and str(value).replace('.', '', 1).isdigit()])
    data_sorted = np.sort(data)

    # Вычисляем перцентили для разделения на секции
    percentiles = np.linspace(0, 100, num_sections + 1)
    percentile_values = np.percentile(data_sorted, percentiles)

    # Создаем диапазоны на основе перцентилей
    ranges = []
    for i in range(len(percentile_values) - 1):
        lower = percentile_values[i]
        upper = percentile_values[i + 1]
        if i == 0:
            range_str = f"≤ {upper:.2f}%"
        elif i == len(percentile_values) - 2:
            range_str = f"> {lower:.2f}%"
        else:
            range_str = f"{lower:.2f}% – {upper:.2f}%"
        ranges.append((lower, upper, range_str))

    # Присваиваем баллы каждому диапазону
    num_ranges = len(ranges)
    scores = np.linspace(min_score, max_score, num_ranges)

    # Создаем DataFrame для шкалы
    scale_df = pd.DataFrame({
        'Напряженность': [r[2] for r in ranges],
        'Баллы': scores.astype(int)
    })

    return scale_df


# In[15]:


def build_scale(percentages, num_grades=10, min_score=10, max_score=100, scale_type='linear'):
    """
    Функция для построения шкалы присвоения баллов на основе распределения данных и заданных критериев,
    с удалением одинаковых интервалов.

    :param percentages: список процентных значений выполнения плана
    :param num_grades: количество градаций шкалы (по умолчанию 10)
    :param min_score: минимальный балл (по умолчанию 10)
    :param max_score: максимальный балл (по умолчанию 100)
    :param scale_type: тип масштабирования ('linear' или 'log')
    :return: DataFrame с диапазонами процентов и соответствующими баллами
    """
    df_unique = list(set(percentages.tolist()))
  

    # Преобразуем список в numpy array
    data = np.array(df_unique)

    # Проверяем максимальное значение
    max_percent = max(data)

    # Обрабатываем данные в зависимости от выбранного масштабирования
    if scale_type == 'log':
        data = np.log(data + 1)  # Логарифмическое масштабирование
    elif scale_type != 'linear':
        raise ValueError("scale_type должен быть 'linear' или 'log'")

    # Сортируем данные
    data_sorted = np.sort(data)

    # Разделяем данные на перцентили
    percentiles = np.linspace(0, 100, num_grades + 1)  # Делим на num_grades диапазонов
    bins = np.percentile(data_sorted, percentiles)

    # Создаем диапазоны процентов
    ranges = []
    scores = []
    for i in range(len(bins) - 1):
        lower = bins[i]
        upper = bins[i + 1]

        # Преобразуем границы обратно, если использовали логарифмическое масштабирование
        if scale_type == 'log':
            lower_display = np.exp(lower) - 1
            upper_display = np.exp(upper) - 1
        else:
            lower_display = lower
            upper_display = upper

        if i == 0:
            range_str = f"≤ {upper_display:.2f}%"
        elif i == len(bins) - 2:
            range_str = f"> {lower_display:.2f}%"
        else:
            range_str = f"{lower_display:.2f}% – {upper_display:.2f}%"

        # Пропускаем повторяющиеся диапазоны
        #if ranges and ranges[-1][1] == upper_display:
        #    continue

        ranges.append((lower_display, upper_display, range_str))

        # Присваиваем баллы
        if upper <= 100:  # Невыполнение плана (до 100%)
            score = min_score + (50 - min_score) * (upper / 100)
        else:  # От 100% равномерное распределение
            relative_position = (upper - 100) / (max_percent - 100)
            score = 50 + (max_score - 50) * relative_position

        scores.append(round(score))  # Округляем до целого

    # Создаем DataFrame для шкалы
    scale_df = pd.DataFrame({
        'Напряженность': [r[2] for r in ranges],
        'Баллы': scores
    })

    return scale_df


# In[17]:


def format_scale(scale_df, scale_name):
    """
    Генерирует отформатированный список на основе DataFrame с указанием имени переменной.

    Args:
        scale_df (pd.DataFrame): DataFrame с диапазонами и баллами.
        scale_name (str): Имя переменной для итогового списка.

    Returns:
        str: Отформатированный список в виде строки.
    """
    formatted_scale = []
    ranges = scale_df['Напряженность']
    scores = scale_df['Баллы']
    
    # Смещаем баллы на одну позицию
    shifted_scores = list(scores[1:]) + [scores.iloc[-1]]  # Последнее значение дублируется для крайних случаев
    
    for i in range(len(ranges)):
        range_str = ranges[i]
        score = shifted_scores[i]  # Используем сдвинутый список
        
        # Извлекаем диапазоны из строк формата "x% – y%" или "> x%"
        if " – " in range_str:
            lower, upper = map(lambda x: float(x.strip('%')), range_str.split(" – "))
            if lower != upper:  # Пропускаем одинаковые нижнюю и верхнюю границы
                formatted_scale.append((upper, score))
        elif "> " in range_str:
            lower = float(range_str.split("> ")[1].strip('%'))
            formatted_scale.append((lower, score))  # Больше, чем нижняя граница
        elif "≤ " in range_str:
            upper = float(range_str.split("≤ ")[1].strip('%'))
            formatted_scale.append((upper, score))  # Меньше или равно верхней границе

    # Удаляем дубликаты значений с одинаковой границей и сортируем
    filtered_scale = []
    for i, (threshold, score) in enumerate(formatted_scale):
        if i == 0 or threshold != formatted_scale[i - 1][0]:
            filtered_scale.append((threshold, score))
    
    filtered_scale.sort(reverse=True, key=lambda x: x[0])  # Сортируем по границе убывания

    # Форматируем вывод с использованием имени переменной
    formatted_output = f"{scale_name} = [\n"
    for i, (threshold, score) in enumerate(filtered_scale):
        score = round(score)  # Округление до целого
        if i == 0:
            formatted_output += f"    ({threshold}, {score}),  # Если значение больше {threshold}%, то {score} баллов\n"
        else:
            formatted_output += f"    ({threshold}, {score}),  # Если значение в диапазоне {threshold}% – {filtered_scale[i-1][0]}%, то {score} баллов\n"
    
    # Добавляем последнее значение
    formatted_output += f"    (0, 10)        # Если значение меньше или равно {filtered_scale[-1][0]}%, то 10 баллов\n"
    formatted_output += "]"
    return formatted_output


# In[19]:


def adjust_scores(scale_df, min_score=10, max_score=80):
    """
    Корректировка баллов в DataFrame: строго один интервал с 100% получает 50 баллов,
    остальные распределяются равномерно ниже и выше.
    
    :param scale_df: DataFrame с диапазонами процентов и баллами
    :param min_score: Минимальный балл для значений до 100%
    :param max_score: Максимальный балл для значений выше 100%
    :return: DataFrame с откорректированными баллами
    """
    def extract_upper_bound(range_str):
        """
        Извлекает верхнюю границу диапазона из строки формата:
        '≤ 50.00%', '50.00% – 100.00%', '> 100.00%'
        """
        if '≤' in range_str:
            return float(range_str.split('≤')[1].strip('% '))
        elif '>' in range_str:
            return float(range_str.split('>')[1].strip('% '))
        else:  # Формат 'x% – y%'
            return float(range_str.split('–')[1].strip('% '))

    def extract_lower_bound(range_str):
        """
        Извлекает нижнюю границу диапазона из строки формата:
        '≤ 50.00%', '50.00% – 100.00%', '> 100.00%'
        """
        if '≤' in range_str or '>' in range_str:
            return 0  # Для первых и последних интервалов
        else:
            return float(range_str.split('–')[0].strip('% '))

    # Извлекаем границы диапазонов
    scale_df['lower_bound'] = scale_df['Напряженность'].apply(extract_lower_bound)
    scale_df['upper_bound'] = scale_df['Напряженность'].apply(extract_upper_bound)

    # Определяем минимальный интервал, содержащий 100%
    containing_100 = scale_df[(scale_df['lower_bound'] <= 1) & (scale_df['upper_bound'] >= 1)].index
    if containing_100.empty:
        raise ValueError("Не удалось найти интервал, содержащий 1")
    containing_100_index = containing_100.min()  # Берем минимальный индекс

    # Деление на интервалы выше и ниже 100%
    below_100_indices = scale_df.loc[:containing_100_index].index
    above_100_indices = scale_df.loc[containing_100_index + 1:].index

    # Генерация равномерных баллов для интервалов ниже 100%
    if len(below_100_indices) > 1:
        below_100_scores = np.linspace(min_score, 50, len(below_100_indices)).tolist()
    else:
        below_100_scores = [50]

    # Генерация равномерных баллов для интервалов выше 100%
    if len(above_100_indices) > 0:
        above_100_scores = np.linspace(50 + (max_score - 50) / len(above_100_indices), max_score, len(above_100_indices)).tolist()
    else:
        above_100_scores = []

    # Обновляем баллы в DataFrame
    scale_df.loc[below_100_indices, 'Баллы'] = below_100_scores
    scale_df.loc[containing_100_index, 'Баллы'] = 50  # Устанавливаем 50 баллов для 100%
    scale_df.loc[above_100_indices, 'Баллы'] = above_100_scores

    # Удаляем временные столбцы
    scale_df.drop(['lower_bound', 'upper_bound'], axis=1, inplace=True)

    return scale_df


# In[21]:


def plot_scores(scale_df):
    """
    Строит график зависимости баллов от процента выполнения плана.

    :param scale_df: DataFrame с колонками "Процент выполнения плана (%)" и "Баллы за выполнение"
    """
    # Преобразуем диапазоны процентов в значения для оси X
    x_values = []
    for percent_range in scale_df['Напряженность']:
        if '≤' in percent_range:
            x_values.append(float(percent_range.split('≤')[1].strip('% ')))
        elif '>' in percent_range:
            x_values.append(float(percent_range.split('>')[1].strip('% ')))
        else:
            bounds = percent_range.split('–')
            x_values.append((float(bounds[0].strip('% ')) + float(bounds[1].strip('% '))) / 2)

    # Строим график
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, scale_df['Баллы'], marker='o', linestyle='-', label='Баллы за выполнение')
    plt.title('Зависимость баллов от напряженности')
    plt.xlabel('Напряженность')
    plt.ylabel('Баллы')
    plt.grid(True)
    plt.legend()
    plt.show()


# In[23]:


def save_formatted_scale_to_file(formatted_scale_str, filename):
    """
    Сохраняет значение переменной formatted_scale в файл в формате JSON.

    :param formatted_scale_str: строка с определением переменной formatted_scale
    :param filename: имя файла для сохранения
    """
    # Извлекаем список из строки
    start_index = formatted_scale_str.index('[')
    end_index = formatted_scale_str.rindex(']')
    scale_list_str = formatted_scale_str[start_index:end_index + 1]

    # Преобразуем строку списка в Python-объект
    scale_list = eval(scale_list_str)

    # Сохраняем в файл
    with open(filename, "w") as file:
        json.dump(scale_list, file, indent=4)
    print(f"Файл {filename} успешно сохранён.")


def load_formatted_scale_from_file(filename):
    """
    Загружает значение scaleEgeNapr из файла и возвращает как список.

    :param filename: имя файла для загрузки
    :return: список с диапазонами и баллами
    """
    with open(filename, "r") as file:
        scale_list = json.load(file)
    return scale_list


# In[25]:


# Сохраняем DataFrame в CSV файл
#df.to_csv('dannie6.csv', index=False)

# Очищаем DataFrame
df = pd.DataFrame()

# Загружаем данные из CSV файла
df = pd.read_csv('dannie17_01_25.csv')
# Загрузка данных из CSV файла средних по университету
dfSred = pd.read_csv('sredneeUniver.csv', delimiter=';')
# Преобразование DataFrame в словарь
dictSred = dfSred.set_index('IndicatorCode')['SredneePoUniver'].to_dict()
# Преобразование значений в словаре dictSred, заменяя запятую на точку перед преобразованием в float
dictSred = {key: float(value.replace(',', '.')) for key, value in dictSred.items()}


# In[27]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['EGEFact'] >= 0.002]


# In[29]:


df_nonzero = df_nonzero.copy()
df_nonzero['EGENapr'] = df['EGEFact'] / dictSred['Ц02']


# In[31]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['EGENapr'], num_sections=10,min_score=10, max_score=80)
print("Шкала с использованием квартилей (10 секции):")
print("Напряженность; Баллы;") 
# Форматирование вывода
output = "\n".join(f"{row['Напряженность']}; {row['Баллы']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)


# In[33]:


adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleEgeNapr")
print(formatted_scale)


# In[35]:


save_formatted_scale_to_file(formatted_scale, "scaleEgeNapr.json")


# In[39]:


plot_scores(adjusted_scale_df)


# In[41]:


scaleEgeNapr = load_formatted_scale_from_file("scaleEgeNapr.json")
print("Загруженная переменная scaleEgeNapr:")
print(scaleEgeNapr)


# In[ ]:





# In[44]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['TrudoustroistvoFact'] >= 0.002]


# In[46]:


df_nonzero = df_nonzero.copy()
df_nonzero['TrudoustroistvoNapr'] = df_nonzero['TrudoustroistvoFact'] / dictSred['Ц07']


# In[48]:


df_nonzero['TrudoustroistvoNapr']


# In[50]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['TrudoustroistvoNapr'], num_sections=10,min_score=10, max_score=80)


# In[52]:


print("Шкала с использованием квартилей (10 секции):")
print("Напряженность; Баллы;") 
# Форматирование вывода
output = "\n".join(f"{row['Напряженность']}; {row['Баллы']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)


# In[54]:


adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleTrudoustroistvoNapr")
print(formatted_scale)


# In[56]:


save_formatted_scale_to_file(formatted_scale, "scaleTrudoustroistvoNapr.json")


# In[58]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['RIDFact'] >= 0.002]


# In[60]:


df_nonzero = df_nonzero.copy()
df_nonzero['RIDNapr'] = df_nonzero['RIDFact'] / dictSred['Ц27']


# In[62]:


analyze_distribution(df_nonzero, 'RIDNapr')


# In[64]:


#build_scale(percentages, num_grades=10, min_score=50, max_score=80, scale_type='linear')
scale_variant3 = build_scale(df_nonzero['RIDNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[66]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleRidNapr")
print(formatted_scale)


# In[68]:


save_formatted_scale_to_file(formatted_scale, "scaleRidNapr.json")


# In[70]:


plot_scores(adjusted_scale_df)



# In[72]:


result = sorted_column_to_string(df, 'PublNauchMaterialFact')
print(result)


# In[74]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['PublNauchMaterialFact'] >= 0.002]


# In[76]:


df_nonzero = df_nonzero.copy()
df_nonzero['PublNauchMaterialNapr'] = df_nonzero['PublNauchMaterialFact'] / dictSred['Ц17']


# In[78]:


analyze_distribution(df_nonzero, 'PublNauchMaterialNapr')


# In[80]:


scale_variant3 = build_scale(df_nonzero['PublNauchMaterialNapr'],num_grades=20, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scalePublNauchMaterialNapr")
print(formatted_scale)


# In[82]:


save_formatted_scale_to_file(formatted_scale, "scalePublNauchMaterialNapr.json")


# In[84]:


plot_scores(adjusted_scale_df)


# In[86]:


result = sorted_column_to_string(df, 'AkadMobFact')
print(result)


# In[88]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['AkadMobFact'] >= 0.002]


# In[90]:


df_nonzero = df_nonzero.copy()
df_nonzero['AkadMobNapr'] = df_nonzero['AkadMobFact'] / dictSred['Ц13']


# In[92]:


analyze_distribution(df_nonzero, 'AkadMobNapr')


# In[94]:


scale_variant3 = build_scale(df_nonzero['AkadMobNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[96]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleAkadMobNapr")
print(formatted_scale)


# In[98]:


save_formatted_scale_to_file(formatted_scale, "scaleAkadMobNapr.json")


# In[100]:


plot_scores(adjusted_scale_df)


# In[102]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['DolInostrFact'] >= 0.002]


# In[104]:


df_nonzero = df_nonzero.copy()
df_nonzero['DolInostrNapr'] = df_nonzero['DolInostrFact'] / dictSred['Ц11']


# In[106]:


analyze_distribution(df_nonzero, 'DolInostrNapr')


# In[108]:


scale_variant3 = build_scale(df_nonzero['DolInostrNapr'],num_grades=20, min_score=10, max_score=90, scale_type='log')


# In[110]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleDolInostrNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolInostrNapr.json")


# In[112]:


plot_scores(adjusted_scale_df)


# In[114]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['DolMagFact'] >= 0.002]


# In[116]:


df_nonzero = df_nonzero.copy()
df_nonzero['DolMagNapr'] = df_nonzero['DolMagFact'] / dictSred['Ц01']


# In[118]:


analyze_distribution(df_nonzero, 'DolMagNapr')


# In[120]:


scale_variant3 = build_scale(df_nonzero['DolMagNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[122]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleDolMagNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolMagNapr.json")


# In[124]:


plot_scores(adjusted_scale_df)


# In[126]:


df_nonzero = df[df['DolOstepenennykhFact'] >= 0.002]


# In[128]:


df_nonzero = df_nonzero.copy()
df_nonzero['DolOstepenennykhNapr'] = df_nonzero['DolOstepenennykhFact'] / dictSred['Ц06']


# In[130]:


analyze_distribution(df_nonzero, 'DolOstepenennykhNapr')


# In[132]:


#build_scale(percentages, num_grades=10, min_score=50, max_score=80, scale_type='linear')
scale_variant3 = build_scale(df_nonzero['DolOstepenennykhNapr'],num_grades=20, min_score=10, max_score=80, scale_type='log')


# In[134]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleDolOstepenennykhNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolOstepenennykhNapr.json")


# In[136]:


plot_scores(adjusted_scale_df)


# In[138]:


df_nonzero = df[df['DolPPS200Fact'] >= 0.002]


# In[140]:


df_nonzero = df_nonzero.copy()
df_nonzero['DolPPS200Napr'] = df_nonzero['DolPPS200Fact'] / dictSred['Ц25']


# In[142]:


df_nonzero['DolPPS200Napr']


# In[144]:


analyze_distribution(df_nonzero, 'DolPPS200Napr')


# In[146]:


scale_variant3 = build_scale(df_nonzero['DolPPS200Napr'],num_grades=20, min_score=10, max_score=80, scale_type='log')


# In[148]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleDolPPS200Napr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolPPS200Napr.json")


# In[150]:


plot_scores(adjusted_scale_df)


# In[152]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['DolStorMagFact'] >= 0.002]


# In[154]:


df_nonzero = df_nonzero.copy()
df_nonzero['DolStorMagNapr'] = df_nonzero['DolStorMagFact'] / dictSred['Ц03']


# In[156]:


analyze_distribution(df_nonzero, 'DolStorMagNapr')


# In[158]:


scale_variant3 = build_scale(df_nonzero['DolStorMagNapr'],num_grades=20, min_score=10, max_score=80, scale_type='log')


# In[160]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleDolStorMagNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolStorMagNapr.json")


# In[162]:


plot_scores(adjusted_scale_df)


# In[164]:


df_nonzero = df[df['DolCelevikovFact'] >= 0.002]


# In[166]:


df_nonzero = df_nonzero.copy()
df_nonzero['DolCelevikovNapr'] = df_nonzero['DolCelevikovFact'] / dictSred['Ц04']


# In[168]:


analyze_distribution(df_nonzero, 'DolCelevikovNapr')


# In[170]:


scale_variant3 = build_scale(df_nonzero['DolCelevikovNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[172]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleDolCelevikovNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolCelevikovNapr.json")


# In[174]:


plot_scores(adjusted_scale_df)


# In[ ]:





# In[176]:


df_nonzero = df[df['ZashchityFact'] >= 0.002]


# In[178]:


df_nonzero = df_nonzero.copy()
df_nonzero['ZashchityNapr'] = df['ZashchityFact'] / dictSred['Ц10']


# In[180]:


analyze_distribution(df_nonzero, 'ZashchityNapr')


# In[182]:


scale_variant3 = build_scale(df_nonzero['ZashchityNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[184]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleZashchityNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleZashchityNapr.json")


# In[186]:


plot_scores(adjusted_scale_df)


# In[188]:


result = sorted_column_to_string(df, 'ZayavAktivFact')


# In[190]:


print(result)
df_nonzero = df[df['ZayavAktivFact'] >= 0.002]


# In[192]:


df_nonzero = df_nonzero.copy()
df_nonzero['ZayavAktivNapr'] = df_nonzero['ZayavAktivFact'] / dictSred['Ц16']


# In[194]:


analyze_distribution(df_nonzero, 'ZayavAktivNapr')


# In[200]:


scale_variant3 = build_scale(df_nonzero['ZayavAktivNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[202]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleZayavAktivNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleZayavAktivNapr.json")


# In[204]:


plot_scores(adjusted_scale_df)


# In[206]:


df_nonzero = df[df['InnovaciiFact'] >= 0.002] 


# In[208]:


df_nonzero = df_nonzero.copy()
df_nonzero['InnovaciiNapr'] = df_nonzero['InnovaciiFact'] / dictSred['Ц24']


# In[210]:


analyze_distribution(df_nonzero, 'InnovaciiNapr')


# In[212]:


scale_variant3 = build_scale(df_nonzero['InnovaciiNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[214]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleInnovaciiNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleInnovaciiNapr.json")


# In[220]:


plot_scores(adjusted_scale_df)


# In[222]:


df_nonzero = df[df['KolInostrPrepodFact'] >= 0.002] 


# In[224]:


df_nonzero = df_nonzero.copy()
df_nonzero['KolInostrPrepodNapr'] = df['KolInostrPrepodFact'] / dictSred['Ц12']


# In[226]:


analyze_distribution(df_nonzero, 'KolInostrPrepodNapr')


# In[228]:


scale_variant3 = build_scale(df_nonzero['KolInostrPrepodNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[230]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleKolInostrPrepodNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleKolInostrPrepodNapr.json")


# In[232]:


plot_scores(adjusted_scale_df)


# In[234]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['KolPublikFact'] >= 0.002]


# In[236]:


df_nonzero = df_nonzero.copy()
df_nonzero['KolPublikNapr'] = df_nonzero['KolPublikFact'] / dictSred['Ц08']


# In[238]:


analyze_distribution(df_nonzero, 'KolPublikNapr')


# In[240]:


scale_variant3 = build_scale(df_nonzero['KolPublikNapr'],num_grades=20, min_score=10, max_score=90, scale_type='log')


# In[242]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleKolPublikNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleKolPublikNapr.json")


# In[244]:


plot_scores(adjusted_scale_df)


# In[246]:


df_nonzero = df[df['ObemNIOKRFact'] >= 0.002] 


# In[248]:


df_nonzero = df_nonzero.copy()
df_nonzero['ObemNIOKRNapr'] = df['ObemNIOKRFact'] / dictSred['Ц09']


# In[250]:


analyze_distribution(df_nonzero, 'ObemNIOKRNapr')


# In[252]:


scale_variant3 = build_scale(df_nonzero['ObemNIOKRNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[254]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleObemNIOKRNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleObemNIOKRNapr.json")


# In[256]:


plot_scores(adjusted_scale_df)


# In[258]:


df_nonzero = df[df['ObemPOUFact'] >= 0.002]


# In[260]:


df_nonzero = df_nonzero.copy()
df_nonzero['ObemPOUNapr'] = df['ObemPOUFact'] / dictSred['Ц05']


# In[262]:


analyze_distribution(df_nonzero, 'ObemPOUNapr')


# In[264]:


#build_scale(percentages, num_grades=10, min_score=50, max_score=80, scale_type='linear')
scale_variant3 = build_scale(df_nonzero['ObemPOUNapr'],num_grades=40, min_score=10, max_score=90, scale_type='log')


# In[266]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleObemPOUNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleObemPOUNapr.json")


# In[268]:


plot_scores(adjusted_scale_df)


# In[270]:


df_nonzero = df[df['DolMolNPRFact'] >= 0.002]


# In[272]:


df_nonzero = df_nonzero.copy()
df_nonzero['DolMolNPRNapr'] = df_nonzero['DolMolNPRFact'] / dictSred['Ц26']


# In[ ]:


dictSred


# In[275]:


dictSred['Ц26'] = df_nonzero['DolMolNPRNapr'].mean()  #Для проверки расчетов надо уточнить реальное значение


# In[ ]:


analyze_distribution(df_nonzero, 'DolMolNPRNapr')


# In[ ]:


scale_variant3 = build_scale(df_nonzero['DolMolNPRNapr'],num_grades=20, min_score=10, max_score=80, scale_type='log')


# In[ ]:


adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleDolMolNPRNapr")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolMolNPRNapr.json")


# In[ ]:


plot_scores(adjusted_scale_df)


# In[ ]:


df['PodgotovkaEnciklVip']


# In[ ]:




