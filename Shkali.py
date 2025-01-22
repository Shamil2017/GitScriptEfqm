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


# In[21]:


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


# Вспомогательная функция построения графика исходных данных для которых мы строим шкалы
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


# In[27]:


def plot_point_main(df, column_name):
    result = sorted_column_to_string(df, column_name)
    result = [float(x.strip()) for x in result.split(";")]
    data_sorted = np.sort(result)
    plot_point_distribution(data_sorted)


# In[29]:


# Сохраняем DataFrame в CSV файл
#df.to_csv('dannie6.csv', index=False)

# Очищаем DataFrame
df = pd.DataFrame()

# Загружаем данные из CSV файла
df = pd.read_csv('dannie17_01_25.csv')


# In[31]:


df


# In[33]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['EGEVip'] >= 0.002]


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


# In[39]:


# Начало расчета


# In[41]:


adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleEgeVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleEgeVip.json")


# In[43]:


plot_scores(adjusted_scale_df)


# In[ ]:


fields = df.columns.tolist()
print(fields)


# In[ ]:


#trudProcVip


# In[45]:


df_nonzero = df[df['TrudoustroistvoVip'] >= 0.002]


# In[46]:


analyze_distribution(df_nonzero, 'TrudoustroistvoVip')


# In[49]:


result = sorted_column_to_string(df_nonzero, 'TrudoustroistvoVip')
print(result)


# In[51]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['TrudoustroistvoVip'], num_sections=10,min_score=10, max_score=80)
print("Шкала с использованием квартилей (10 секции):")
print("Процент выполнения плана (%); Баллы за выполнение;") 
# Форматирование вывода
output = "\n".join(f"{row['Процент выполнения плана (%)']}; {row['Баллы за выполнение']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)



# In[53]:


adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=80)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleTrudoustroistvoVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleTrudoustroistvoVip.json")


# In[61]:


#ridProcVip


# In[63]:


df_nonzero = df[df['RIDVip'] >= 0.002]


# In[65]:


plot_point_main(df_nonzero, 'RIDVip')


# In[67]:


analyze_distribution(df_nonzero, 'RIDVip')


# In[191]:


#build_scale(percentages, num_grades=10, min_score=50, max_score=80, scale_type='linear')
scale_variant3 = build_scale(df_nonzero['RIDVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df,"scaleRidVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleRidVip.json")


# In[193]:


plot_scores(adjusted_scale_df)


# In[73]:


#PublNauchMaterialVip


# In[75]:


result = sorted_column_to_string(df, 'PublNauchMaterialVip')
print(result)


# In[77]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
df_nonzero = df[df['PublNauchMaterialVip'] >= 0.002]


# In[79]:


plot_point_main(df_nonzero, 'PublNauchMaterialVip')


# In[81]:


analyze_distribution(df_nonzero, 'PublNauchMaterialVip')


# In[195]:


scale_variant3 = build_scale(df_nonzero['PublNauchMaterialVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scalePublNauchMaterialVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scalePublNauchMaterialVip.json")


# In[197]:


plot_scores(adjusted_scale_df)


# In[87]:


AkadMob


# In[89]:


# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact

result = sorted_column_to_string(df, 'AkadMobVip')
print(result)
df_nonzero = df[df['AkadMobVip'] >= 0.002]
plot_point_main(df_nonzero, 'AkadMobVip')


# In[91]:


analyze_distribution(df_nonzero, 'AkadMobVip')


# In[93]:


scale_variant3 = build_scale(df_nonzero['AkadMobVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[199]:


scale_variant3 = build_scale(df_nonzero['AkadMobVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleAkadMobVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleAkadMobVip.json")


# In[201]:


plot_scores(adjusted_scale_df)


# In[203]:


# DolInostrVip
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolInostrVip')
print(result)
df_nonzero = df[df['DolInostrVip'] >= 0.002]
plot_point_main(df_nonzero, 'DolInostrVip')


# In[205]:


analyze_distribution(df_nonzero, 'DolInostrVip')


# In[207]:


scale_variant3 = build_scale(df_nonzero['DolInostrVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[211]:


scale_variant3 = build_scale(df_nonzero['DolInostrVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolInostrVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolInostrVip.json")


# In[213]:


plot_scores(adjusted_scale_df)


# In[217]:


#DolMag
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolMagVip')
print(result)
df_nonzero = df[df['DolMagVip'] >= 0.002]
plot_point_main(df_nonzero, 'DolMagVip')


# In[221]:


analyze_distribution(df_nonzero, 'DolMagVip')


# In[223]:


scale_variant3 = build_scale(df_nonzero['DolMagVip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[225]:


scale_variant3 = build_scale(df_nonzero['DolMagVip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolMagVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolMagVip.json")


# In[117]:


plot_scores(adjusted_scale_df)


# In[227]:


#DolOstepenennykh
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolOstepenennykhVip')
print(result)
df_nonzero = df[df['DolOstepenennykhVip'] >= 0.002]
plot_point_main(df_nonzero, 'DolOstepenennykhVip')


# In[229]:


analyze_distribution(df_nonzero, 'DolOstepenennykhVip')


# In[231]:


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
save_formatted_scale_to_file(formatted_scale, "scaleDolOstepenennykhVip.json")


# In[233]:


plot_scores(adjusted_scale_df)


# In[235]:


#DolPPS200
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolPPS200Vip')
print(result)
df_nonzero = df[df['DolPPS200Vip'] >= 0.002]
plot_point_main(df_nonzero, 'DolPPS200Vip')


# In[237]:


analyze_distribution(df_nonzero, 'DolPPS200Vip')


# In[239]:


scale_variant3 = build_scale(df_nonzero['DolPPS200Vip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[241]:


scale_variant3 = build_scale(df_nonzero['DolPPS200Vip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolPPS200Vip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolPPS200Vip.json")


# In[243]:


plot_scores(adjusted_scale_df)


# In[245]:


#DolStorMag
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolStorMagVip')
print(result)
df_nonzero = df[df['DolStorMagVip'] >= 0.002]
plot_point_main(df_nonzero, 'DolStorMagVip')


# In[247]:


analyze_distribution(df_nonzero, 'DolStorMagVip')


# In[249]:


scale_variant3 = build_scale(df_nonzero['DolStorMagVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[253]:


scale_variant3 = build_scale(df_nonzero['DolStorMagVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolStorMagVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolStorMagVip.json")


# In[257]:


plot_scores(adjusted_scale_df)


# In[259]:


#DolCelevikov
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'DolCelevikovVip')
print(result)
df_nonzero = df[df['DolCelevikovVip'] >= 0.002]
plot_point_main(df_nonzero, 'DolCelevikovVip')


# In[261]:


analyze_distribution(df_nonzero, 'DolCelevikovVip')


# In[263]:


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
save_formatted_scale_to_file(formatted_scale, "scaleDolCelevikovVip.json")


# In[265]:


plot_scores(adjusted_scale_df)


# In[267]:


#Zashchity
# Отфильтровать DataFrame, оставив только ненулевые значения в столбце sredFact
result = sorted_column_to_string(df, 'ZashchityVip')
print(result)
df_nonzero = df[df['ZashchityVip'] >= 0.002]
plot_point_main(df_nonzero, 'ZashchityVip')


# In[269]:


analyze_distribution(df_nonzero, 'ZashchityVip')


# In[271]:


kol_inostr_prepod_vip = df_nonzero['ZashchityVip'].tolist()
kol_inostr_prepod_vip_unique = list(set(kol_inostr_prepod_vip))


# In[273]:


scale_variant3 = build_scale(df_nonzero['ZashchityVip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[275]:


scale_variant3 = build_scale(df_nonzero['ZashchityVip'],num_grades=20, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleZashchityVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleZashchityVip.json")


# In[277]:


plot_scores(adjusted_scale_df)


# In[279]:


#DolPPS200
result = sorted_column_to_string(df, 'DolPPS200Vip')
print(result)
df_nonzero = df[df['DolPPS200Vip'] >= 0.002]
plot_point_main(df_nonzero, 'DolPPS200Vip')


# In[281]:


analyze_distribution(df_nonzero, 'DolPPS200Vip')


# In[283]:


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
save_formatted_scale_to_file(formatted_scale, "scaleDolPPS200Vip.json")


# In[285]:


plot_scores(adjusted_scale_df)


# In[287]:


#ZayavAktiv
result = sorted_column_to_string(df, 'ZayavAktivVip')
print(result)
df_nonzero = df[df['ZayavAktivVip'] >= 0.002]
plot_point_main(df_nonzero, 'ZayavAktivVip')


# In[289]:


analyze_distribution(df_nonzero, 'ZayavAktivVip')


# In[291]:


# Пример использования функции с вариантом №1 и 4 секциями (квартилями)
scale_variant1_quartiles = build_scale_quartiles(df_nonzero['ZayavAktivVip'], num_sections=20,min_score=10, max_score=90)
print("Шкала с использованием квартилей (10 секции):")
print("Процент выполнения плана (%); Баллы за выполнение;") 
# Форматирование вывода
output = "\n".join(f"{row['Процент выполнения плана (%)']}; {row['Баллы за выполнение']};" for _, row in scale_variant1_quartiles.iterrows())
print(output)


# In[293]:


adjusted_scale_df = adjust_scores(scale_variant1_quartiles, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleZayavAktivVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleZayavAktivVip.json")


# In[295]:


plot_scores(adjusted_scale_df)


# In[297]:


#Innovacii
result = sorted_column_to_string(df, 'InnovaciiVip')
print(result)
df_nonzero = df[df['InnovaciiVip'] >= 0.002]
plot_point_main(df_nonzero, 'InnovaciiVip')


# In[299]:


analyze_distribution(df_nonzero, 'InnovaciiVip')


# In[301]:


scale_variant3 = build_scale(df_nonzero['InnovaciiVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[303]:


scale_variant3 = build_scale(df_nonzero['InnovaciiVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleInnovaciiVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleInnovaciiVip.json")


# In[305]:


plot_scores(adjusted_scale_df)


# In[307]:


#KolInostrPrepod
result = sorted_column_to_string(df, 'KolInostrPrepodVip')
print(result)
df_nonzero = df[df['KolInostrPrepodVip'] >= 0.002]
plot_point_main(df_nonzero, 'KolInostrPrepodVip')


# In[309]:


analyze_distribution(df_nonzero, 'KolInostrPrepodVip')


# In[311]:


kol_inostr_prepod_vip = df_nonzero['KolInostrPrepodVip'].tolist()
kol_inostr_prepod_vip_unique = list(set(kol_inostr_prepod_vip))


# In[313]:


print(kol_inostr_prepod_vip_unique)


# In[ ]:


scale_variant3 = build_scale(df_nonzero['KolInostrPrepodVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[319]:


scale_variant3 = build_scale(df_nonzero['KolInostrPrepodVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleKolInostrPrepodVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleKolInostrPrepodVip.json")


# In[321]:


plot_scores(adjusted_scale_df)


# In[323]:


#KolPublik
result = sorted_column_to_string(df, 'KolPublikVip')
print(result)
df_nonzero = df[df['KolPublikVip'] >= 0.002]
plot_point_main(df_nonzero, 'KolPublikVip')


# In[325]:


analyze_distribution(df_nonzero, 'KolPublikVip')


# In[327]:


scale_variant3 = build_scale(df_nonzero['KolPublikVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[333]:


scale_variant3 = build_scale(df_nonzero['KolPublikVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleKolPublikVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleKolPublikVip.json")


# In[335]:


plot_scores(adjusted_scale_df)


# In[337]:


#ObemNIOKR
result = sorted_column_to_string(df, 'ObemNIOKRVip')
print(result)
df_nonzero = df[df['ObemNIOKRVip'] >= 0.002]
plot_point_main(df_nonzero, 'ObemNIOKRVip')


# In[349]:


analyze_distribution(df_nonzero, 'ObemNIOKRVip')


# In[351]:


scale_variant3 = build_scale(df_nonzero['ObemNIOKRVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[353]:


scale_variant3 = build_scale(df_nonzero['ObemNIOKRVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleObemNIOKRVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleObemNIOKRVip.json")


# In[355]:


plot_scores(adjusted_scale_df)


# In[ ]:





# In[ ]:


#PodgotovkaEncikl
result = sorted_column_to_string(df, 'PodgotovkaEnciklVip')
print(result)
df_nonzero = df[df['PodgotovkaEnciklVip'] >= 0.002]
plot_point_main(df_nonzero, 'PodgotovkaEnciklVip')


# In[ ]:





# In[357]:


#ObemPOU
result = sorted_column_to_string(df, 'ObemPOUVip')
print(result)
df_nonzero = df[df['ObemPOUVip'] >= 0.002]
plot_point_main(df_nonzero, 'ObemPOUVip')


# In[359]:


analyze_distribution(df_nonzero, 'ObemPOUVip')


# In[361]:


scale_variant3 = build_scale(df_nonzero['ObemPOUVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[363]:


scale_variant3 = build_scale(df_nonzero['ObemPOUVip'],num_grades=40, min_score=10, max_score=90, scale_type='linear')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleObemPOUVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleObemPOUVip.json")


# In[365]:


plot_scores(adjusted_scale_df)


# In[367]:


#PodgotovkaEncikl
result = sorted_column_to_string(df, 'DolMolNPRVip')
print(result)
df_nonzero = df[df['DolMolNPRVip'] >= 0.002]
plot_point_main(df_nonzero, 'DolMolNPRVip')


# In[369]:


analyze_distribution(df_nonzero, 'DolMolNPRVip')


# In[ ]:


scale_variant3 = build_scale(df_nonzero['DolMolNPRVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
print(scale_variant3)


# In[ ]:





# In[376]:


scale_variant3 = build_scale(df_nonzero['DolMolNPRVip'],num_grades=40, min_score=10, max_score=90, scale_type='log')
adjusted_scale_df = adjust_scores(scale_variant3, min_score=10, max_score=90)
print(adjusted_scale_df)
formatted_scale = format_scale(adjusted_scale_df, "scaleDolMolNPRVip")
print(formatted_scale)
save_formatted_scale_to_file(formatted_scale, "scaleDolMolNPRVip.json")


# In[378]:


plot_scores(adjusted_scale_df)


# In[380]:


pwd


# In[ ]:




