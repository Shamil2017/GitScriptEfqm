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


server = 'KPI-MONITOR'
database = 'MEI2'
username = 'efqm'
password = 'mpeiR@dar'
current_date = datetime.datetime.now().date()


# In[7]:


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


# In[9]:


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



# In[11]:


def build_scaleOld(percentages, num_grades=10, min_score=50, max_score=80, scale_type='linear'):
    """
    Функция для построения шкалы присвоения баллов на основе распределения данных.

    :param percentages: список процентных значений выполнения плана
    :param num_grades: количество градаций шкалы (по умолчанию 10)
    :param min_score: минимальный балл (по умолчанию 50)
    :param max_score: максимальный балл (по умолчанию 80)
    :param scale_type: тип масштабирования ('linear' или 'log')
    :return: DataFrame с диапазонами процентов и соответствующими баллами
    """
    # Преобразуем список в numpy array
    data = np.array(percentages)

    # Обрабатываем данные в зависимости от выбранного масштабирования
    if scale_type == 'log':
        # Добавляем небольшое число, чтобы избежать логарифма от нуля
        data = np.log(data + 1)
    elif scale_type != 'linear':
        raise ValueError("scale_type должен быть 'linear' или 'log'")

    # Сортируем данные
    data_sorted = np.sort(data)

    # Вычисляем перцентили для разделения на градации
    percentiles = np.linspace(0, 100, num_grades + 1)
    bins = np.percentile(data_sorted, percentiles)

    # Создаем диапазоны процентов
    ranges = []
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
        ranges.append((lower_display, upper_display, range_str))

    # Присваиваем баллы каждому диапазону
    scores = np.linspace(min_score, max_score, num_grades)

    # Создаем DataFrame для шкалы
    scale_df = pd.DataFrame({
        'Процент выполнения плана (%)': [r[2] for r in ranges],
        'Баллы за выполнение': scores.astype(int)
    })

    return scale_df



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
        'Процент выполнения плана (%)': [r[2] for r in ranges],
        'Баллы за выполнение': scores.astype(int)
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
        'Процент выполнения плана (%)': [r[2] for r in ranges],
        'Баллы за выполнение': scores
    })

    return scale_df


# In[17]:


def format_scale0(scale_df, scale_name):
    """
    Генерирует отформатированный список на основе DataFrame с указанием имени переменной.

    Args:
        scale_df (pd.DataFrame): DataFrame с диапазонами и баллами.
        scale_name (str): Имя переменной для итогового списка.

    Returns:
        str: Отформатированный список в виде строки.
    """
    formatted_scale = []
    ranges = scale_df['Процент выполнения плана (%)']
    scores = scale_df['Баллы за выполнение']
    
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
        if i == 0:
            formatted_output += f"    ({threshold:.2f}, {int(score) if score.is_integer() else score:.6f}),  # Если значение больше {threshold:.2f}%, то {int(score) if score.is_integer() else score} баллов\n"
        else:
            formatted_output += f"    ({threshold:.2f}, {int(score) if score.is_integer() else score:.6f}),  # Если значение в диапазоне {threshold:.2f}% – {filtered_scale[i-1][0]:.2f}%, то {int(score) if score.is_integer() else score} баллов\n"
    
    # Добавляем последнее значение
    formatted_output += f"    (0, 10)        # Если значение меньше или равно {filtered_scale[-1][0]:.2f}%, то 10 баллов\n"
    formatted_output += "]"
    return formatted_output



# In[19]:


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
    ranges = scale_df['Процент выполнения плана (%)']
    scores = scale_df['Баллы за выполнение']
    
    # Смещаем баллы на одну позицию
    shifted_scores = list(scores[1:]) + [scores.iloc[-1]]  # Последнее значение дублируется для крайних случаев
    
    for i in range(len(ranges)):
        range_str = ranges[i]
        score = shifted_scores[i]  # Используем сдвинутый список
        
        # Извлекаем диапазоны из строк формата "x% – y%" или "> x%"
        if " – " in range_str:
            lower, upper = map(lambda x: float(x.strip('%')), range_str.split(" – "))
            if lower != upper:  # Пропускаем одинаковые нижнюю и верхнюю границы
                formatted_scale.append((round(upper), score))
        elif "> " in range_str:
            lower = float(range_str.split("> ")[1].strip('%'))
            formatted_scale.append((round(lower), score))  # Больше, чем нижняя граница
        elif "≤ " in range_str:
            upper = float(range_str.split("≤ ")[1].strip('%'))
            formatted_scale.append((round(upper), score))  # Меньше или равно верхней границе

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


# In[21]:


def adjust_scores0(scale_df, min_score=10, max_score=80):
    """
    Функция для корректировки баллов в DataFrame, созданном build_scale.

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

    # Извлекаем верхние границы диапазонов
    upper_bounds = scale_df['Процент выполнения плана (%)'].apply(extract_upper_bound)

    # Определяем диапазоны ниже и выше 100%
    below_100_indices = upper_bounds <= 100
    above_100_indices = upper_bounds > 100

    # Количество диапазонов ниже и выше 100%
    below_100_count = below_100_indices.sum()
    above_100_count = above_100_indices.sum()

    # Генерация равномерных баллов
    below_100_scores = np.linspace(min_score, 50, below_100_count) if below_100_count > 0 else []
    above_100_scores = np.linspace(50, max_score, above_100_count) if above_100_count > 0 else []

    # Обновляем баллы в DataFrame
    scale_df.loc[below_100_indices, 'Баллы за выполнение'] = below_100_scores
    scale_df.loc[above_100_indices, 'Баллы за выполнение'] = above_100_scores

    return scale_df


# In[23]:


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
    scale_df['lower_bound'] = scale_df['Процент выполнения плана (%)'].apply(extract_lower_bound)
    scale_df['upper_bound'] = scale_df['Процент выполнения плана (%)'].apply(extract_upper_bound)

    # Определяем минимальный интервал, содержащий 100%
    containing_100 = scale_df[(scale_df['lower_bound'] <= 100) & (scale_df['upper_bound'] >= 100)].index
    if containing_100.empty:
        raise ValueError("Не удалось найти интервал, содержащий 100%")
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
    scale_df.loc[below_100_indices, 'Баллы за выполнение'] = below_100_scores
    scale_df.loc[containing_100_index, 'Баллы за выполнение'] = 50  # Устанавливаем 50 баллов для 100%
    scale_df.loc[above_100_indices, 'Баллы за выполнение'] = above_100_scores

    # Удаляем временные столбцы
    scale_df.drop(['lower_bound', 'upper_bound'], axis=1, inplace=True)

    return scale_df


# In[25]:


def plot_scores(scale_df):
    """
    Строит график зависимости баллов от процента выполнения плана.

    :param scale_df: DataFrame с колонками "Процент выполнения плана (%)" и "Баллы за выполнение"
    """
    # Преобразуем диапазоны процентов в значения для оси X
    x_values = []
    for percent_range in scale_df['Процент выполнения плана (%)']:
        if '≤' in percent_range:
            x_values.append(float(percent_range.split('≤')[1].strip('% ')))
        elif '>' in percent_range:
            x_values.append(float(percent_range.split('>')[1].strip('% ')))
        else:
            bounds = percent_range.split('–')
            x_values.append((float(bounds[0].strip('% ')) + float(bounds[1].strip('% '))) / 2)

    # Строим график
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, scale_df['Баллы за выполнение'], marker='o', linestyle='-', label='Баллы за выполнение')
    plt.title('Зависимость баллов от процента выполнения плана')
    plt.xlabel('Процент выполнения плана (%)')
    plt.ylabel('Баллы за выполнение')
    plt.grid(True)
    plt.legend()
    plt.show()


# In[27]:


# Сохраняем DataFrame в CSV файл
#df.to_csv('dannie6.csv', index=False)

# Очищаем DataFrame
df = pd.DataFrame()

# Загружаем данные из CSV файла
df = pd.read_csv('dannie24.csv')


# In[29]:


df


# In[31]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['EGEVip'] >= 0.002]


# In[ ]:





# In[ ]:





# In[33]:


#sredProcVip


# In[35]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['EGEVip'], num_sections=10,min_score=10, max_score=80)
print("Шкала с использованием квартилей (10 секции):")
print("Процент выполнения плана (%); Баллы за выполнение;") 
# Форматирование вывода
output = "\n".join(f"{row['Процент выполнения плана (%)']}; {row['Баллы за выполнение']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)




# In[37]:


scale_variant1_quartiles


# In[ ]:





# In[40]:


# Начало расчета


# In[42]:


adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleEgeVip")
print(formatted_scale)


# In[44]:


plot_scores(adjusted_scale_df)


# In[132]:


fields = df.columns.tolist()
print(fields)


# In[ ]:





# In[46]:


#trudProcVip


# In[48]:


df_nonzero = df[df['TrudoustroistvoVip'] >= 0.002]


# In[50]:


analyze_distribution(df_nonzero, 'TrudoustroistvoVip')


# In[52]:


result = sorted_column_to_string(df_nonzero, 'TrudoustroistvoVip')
print(result)


# In[54]:


#ridProcVip


# In[56]:


df_nonzero = df[df['RIDVip'] >= 0.002]


# In[58]:


result = sorted_column_to_string(df_nonzero, 'RIDVip')
print(result)


# In[60]:


# Function to plot the distribution
# Function to plot the point distribution
# Function to plot the point distribution as a line chart
def plot_point_distribution(data):
    plt.figure(figsize=(10, 6))

    # Generate indices for data
    indices = range(1, len(data) + 1)

    # Plot line chart
    plt.plot(indices, data, '-o', label='Значения', markersize=5)

    # Add title and labels
    plt.title("Зависимость значений от индекса", fontsize=16)
    plt.xlabel("Индекс", fontsize=14)
    plt.ylabel("Значение", fontsize=14)

    # Add legend
    plt.legend()

    # Grid for better readability
    plt.grid(axis='both', linestyle='--', alpha=0.7)

    # Show plot
    plt.show()


# In[245]:


result = [float(x.strip()) for x in result.split(";")]


# In[247]:


data_sorted = np.sort(result)


# In[249]:


plot_point_distribution(data_sorted)


# In[211]:


# Min, mid, and max values
min_value = min(data_sorted)
max_value = max(data_sorted)
mid_value = 100  # Value corresponding to 50 points

# Functions to calculate scores

def calculate_log_scores(data, min_value, max_value):
    scores = []
    log_min = np.log(min_value)
    log_max = np.log(max_value)
    for value in data:
        log_value = np.log(value)
        score = 10 + (log_value - log_min) / (log_max - log_min) * (100 - 10)
        scores.append(score)
    return scores

def calculate_exp_scores(data, min_value, max_value):
    scores = []
    for value in data:
        exp_value = np.exp(value - min_value)
        exp_min = np.exp(min_value - min_value)
        exp_max = np.exp(max_value - min_value)
        score = 10 + (exp_value - exp_min) / (exp_max - exp_min) * (100 - 10)
        scores.append(score)
    return scores

def calculate_quad_scores(data, min_value, max_value):
    scores = []
    for value in data:
        quad_value = (value - min_value) ** 2
        quad_max = (max_value - min_value) ** 2
        score = 10 + quad_value / quad_max * (100 - 10)
        scores.append(score)
    return scores

# Calculate scores for each method
log_scores = calculate_log_scores(data_sorted, min_value, max_value)
exp_scores = calculate_exp_scores(data_sorted, min_value, max_value)
quad_scores = calculate_quad_scores(data_sorted, min_value, max_value)

# Function to plot the point distribution with scores
def plot_point_distribution_with_scores(data, log_scores, exp_scores, quad_scores):
    plt.figure(figsize=(12, 8))

    # Generate indices for data
    indices = range(1, len(data) + 1)

    # Plot the original data
    plt.plot(indices, data, '-o', label='Значения', markersize=5, color='blue')

    # Plot scores with different colors
    plt.scatter(indices, log_scores, label='Логарифмическая функция', color='green', alpha=0.7)
    plt.scatter(indices, exp_scores, label='Экспоненциальная функция', color='orange', alpha=0.7)
    plt.scatter(indices, quad_scores, label='Квадратичная функция', color='red', alpha=0.7)

    # Add title and labels
    plt.title("Зависимость значений и баллов от индекса", fontsize=16)
    plt.xlabel("Индекс", fontsize=14)
    plt.ylabel("Значение / Баллы", fontsize=14)

    # Add legend
    plt.legend()

    # Grid for better readability
    plt.grid(axis='both', linestyle='--', alpha=0.7)

    # Show plot
    plt.show()

# Call the function to plot
plot_point_distribution_with_scores(data_sorted, log_scores, exp_scores, quad_scores)


# In[213]:


plot_point_distribution(log_scores)


# In[ ]:





# In[62]:


analyze_distribution(df_nonzero, 'RIDVip')


# In[64]:


#build_scale(percentages, num_grades=10, min_score=50, max_score=80, scale_type='linear')
scale_variant3 = build_scale(df_nonzero['RIDVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleRidVip")
print(formatted_scale)


# In[66]:


plot_scores(adjusted_scale_df)


# In[265]:


#PublNauchMaterialVip


# In[68]:


result = sorted_column_to_string(df, 'PublNauchMaterialVip')
print(result)


# In[70]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['PublNauchMaterialVip'] >= 0.002]


# In[72]:


analyze_distribution(df_nonzero, 'PublNauchMaterialVip')


# In[74]:


scale_variant3 = build_scale(df_nonzero['PublNauchMaterialVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scalePublNauchMaterialVip")
print(formatted_scale)


# In[76]:


plot_scores(adjusted_scale_df)


# In[ ]:


AkadMob


# In[78]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact

result = sorted_column_to_string(df, 'AkadMobVip')
print(result)
df_nonzero = df[df['AkadMobVip'] >= 0.002]
analyze_distribution(df_nonzero, 'AkadMobVip')


# In[80]:


scale_variant3 = build_scale(df_nonzero['AkadMobVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[82]:


scale_variant3 = build_scale(df_nonzero['AkadMobVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleAkadMobVip")
print(formatted_scale)


# In[84]:


plot_scores(adjusted_scale_df)


# In[86]:


# DolInostrVip
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolInostrVip')
print(result)
df_nonzero = df[df['DolInostrVip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolInostrVip')


# In[90]:


scale_variant3 = build_scale(df_nonzero['DolInostrVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[92]:


scale_variant3 = build_scale(df_nonzero['DolInostrVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolInostrVip")
print(formatted_scale)


# In[94]:


plot_scores(adjusted_scale_df)


# In[96]:


#DolMag
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolMagVip')
print(result)
df_nonzero = df[df['DolMagVip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolMagVip')


# In[104]:


scale_variant3 = build_scale(df_nonzero['DolMagVip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[106]:


scale_variant3 = build_scale(df_nonzero['DolMagVip'],num_grades=10, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolMagVip")
print(formatted_scale)


# In[108]:


#DolOstepenennykh
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolOstepenennykhVip')
print(result)
df_nonzero = df[df['DolOstepenennykhVip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolOstepenennykhVip')


# In[116]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['DolOstepenennykhVip'], num_sections=20,min_score=10, max_score=90)
print("Шкала с использованием квартилей (10 секции):")
print("Процент выполнения плана (%); Баллы за выполнение;") 
# Форматирование вывода
output = "\n".join(f"{row['Процент выполнения плана (%)']}; {row['Баллы за выполнение']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)
adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolOstepenennykhVip")
print(formatted_scale)


# In[118]:


plot_scores(adjusted_scale_df)


# In[122]:


#DolPPS200
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolPPS200Vip')
print(result)
df_nonzero = df[df['DolPPS200Vip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolPPS200Vip')


# In[126]:


scale_variant3 = build_scale(df_nonzero['DolPPS200Vip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[130]:


scale_variant3 = build_scale(df_nonzero['DolPPS200Vip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolPPS200Vip")
print(formatted_scale)


# In[132]:


plot_scores(adjusted_scale_df)


# In[173]:


#DolStorMag
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolStorMagVip')
print(result)
df_nonzero = df[df['DolStorMagVip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolStorMagVip')


# In[134]:


scale_variant3 = build_scale(df_nonzero['DolStorMagVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[136]:


scale_variant3 = build_scale(df_nonzero['DolStorMagVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolStorMagVip")
print(formatted_scale)


# In[138]:


plot_scores(adjusted_scale_df)


# In[140]:


#DolCelevikov
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolCelevikovVip')
print(result)
df_nonzero = df[df['DolCelevikovVip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolCelevikovVip')


# In[142]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['DolCelevikovVip'], num_sections=20,min_score=10, max_score=90)

print("Шкала с использованием квартилей (10 секции):")
print("Процент выполнения плана (%); Баллы за выполнение;") 
# Форматирование вывода
output = "\n".join(f"{row['Процент выполнения плана (%)']}; {row['Баллы за выполнение']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)
adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolCelevikovVip")
print(formatted_scale)


# In[144]:


plot_scores(adjusted_scale_df)


# In[146]:


#Zashchity
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'ZashchityVip')
print(result)
df_nonzero = df[df['ZashchityVip'] >= 0.002]
analyze_distribution(df_nonzero, 'ZashchityVip')


# In[148]:


kol_inostr_prepod_vip = df_nonzero['ZashchityVip'].tolist()
kol_inostr_prepod_vip_unique = list(set(kol_inostr_prepod_vip))


# In[152]:


scale_variant3 = build_scale(df_nonzero['ZashchityVip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[154]:


scale_variant3 = build_scale(df_nonzero['ZashchityVip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleZashchityVip")
print(formatted_scale)


# In[156]:


plot_scores(adjusted_scale_df)


# In[158]:


#DolPPS200
result = sorted_column_to_string(df, 'DolPPS200Vip')
print(result)
df_nonzero = df[df['DolPPS200Vip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolPPS200Vip')


# In[160]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['DolPPS200Vip'], num_sections=20,min_score=10, max_score=90)
print("Шкала с использованием квартилей (10 секции):")
print("Процент выполнения плана (%); Баллы за выполнение;") 
# Форматирование вывода
output = "\n".join(f"{row['Процент выполнения плана (%)']}; {row['Баллы за выполнение']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolPPS200Vip")
print(formatted_scale)


# In[162]:


plot_scores(adjusted_scale_df)


# In[164]:


#ZayavAktiv
result = sorted_column_to_string(df, 'ZayavAktivVip')
print(result)
df_nonzero = df[df['ZayavAktivVip'] >= 0.002]
analyze_distribution(df_nonzero, 'ZayavAktivVip')


# In[166]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['ZayavAktivVip'], num_sections=20,min_score=10, max_score=90)
print("Шкала с использованием квартилей (10 секции):")
print("Процент выполнения плана (%); Баллы за выполнение;") 
# Форматирование вывода
output = "\n".join(f"{row['Процент выполнения плана (%)']}; {row['Баллы за выполнение']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)


# In[168]:


adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleZayavAktivVip")
print(formatted_scale)


# In[170]:


plot_scores(adjusted_scale_df)


# In[172]:


#Innovacii
result = sorted_column_to_string(df, 'InnovaciiVip')
print(result)
df_nonzero = df[df['InnovaciiVip'] >= 0.002]
analyze_distribution(df_nonzero, 'InnovaciiVip')


# In[174]:


scale_variant3 = build_scale(df_nonzero['InnovaciiVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[180]:


scale_variant3 = build_scale(df_nonzero['InnovaciiVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleInnovaciiVip")
print(formatted_scale)


# In[182]:


plot_scores(adjusted_scale_df)


# In[184]:


#KolInostrPrepod
result = sorted_column_to_string(df, 'KolInostrPrepodVip')
print(result)
df_nonzero = df[df['KolInostrPrepodVip'] >= 0.002]

analyze_distribution(df_nonzero, 'KolInostrPrepodVip')


# In[186]:


kol_inostr_prepod_vip = df_nonzero['KolInostrPrepodVip'].tolist()
kol_inostr_prepod_vip_unique = list(set(kol_inostr_prepod_vip))


# In[188]:


print(kol_inostr_prepod_vip_unique)


# In[190]:


scale_variant3 = build_scale(df_nonzero['KolInostrPrepodVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[192]:


scale_variant3 = build_scale(df_nonzero['KolInostrPrepodVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleKolInostrPrepodVip")
print(formatted_scale)


# In[194]:


plot_scores(adjusted_scale_df)


# In[196]:


#KolPublik
result = sorted_column_to_string(df, 'KolPublikVip')
print(result)
df_nonzero = df[df['KolPublikVip'] >= 0.002]
analyze_distribution(df_nonzero, 'KolPublikVip')


# In[198]:


scale_variant3 = build_scale(df_nonzero['KolPublikVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[200]:


scale_variant3 = build_scale(df_nonzero['KolPublikVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleKolPublikVip")
print(formatted_scale)


# In[202]:


plot_scores(adjusted_scale_df)


# In[204]:


#ObemNIOKR
result = sorted_column_to_string(df, 'ObemNIOKRVip')
print(result)
df_nonzero = df[df['ObemNIOKRVip'] >= 0.002]
analyze_distribution(df_nonzero, 'ObemNIOKRVip')


# In[206]:


scale_variant3 = build_scale(df_nonzero['ObemNIOKRVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[208]:


scale_variant3 = build_scale(df_nonzero['ObemNIOKRVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleObemNIOKRVip")
print(formatted_scale)


# In[210]:


plot_scores(adjusted_scale_df)


# In[212]:


#ObemPOU
result = sorted_column_to_string(df, 'ObemPOUVip')
print(result)
df_nonzero = df[df['ObemPOUVip'] >= 0.002]
analyze_distribution(df_nonzero, 'ObemPOUVip')


# In[214]:


scale_variant3 = build_scale(df_nonzero['ObemPOUVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[216]:


scale_variant3 = build_scale(df_nonzero['ObemPOUVip'],num_grades=40, min_score=10, max_score=100, scale_type='linear')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleObemPOUVip")
print(formatted_scale)


# In[218]:


plot_scores(adjusted_scale_df)


# In[220]:


#PodgotovkaEncikl
result = sorted_column_to_string(df, 'DolMolNPRVip')
print(result)
df_nonzero = df[df['DolMolNPRVip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolMolNPRVip')


# In[222]:


scale_variant3 = build_scale(df_nonzero['DolMolNPRVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
print(scale_variant3)


# In[ ]:





# In[224]:


df_nonzero = df[df['DolMolNPRVip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolMolNPRVip')


# In[226]:


scale_variant3 = build_scale(df_nonzero['DolMolNPRVip'],num_grades=40, min_score=10, max_score=100, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=100)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolMolNPRVip")
print(formatted_scale)


# In[228]:


plot_scores(adjusted_scale_df)


# In[ ]:


df_nonzero = df[df['DolMolNPRVip'] >= 0.002]
analyze_distribution(df_nonzero, 'DolMolNPRVip')


# In[251]:


df['PodgotovkaEnciklVip']


# In[ ]:




