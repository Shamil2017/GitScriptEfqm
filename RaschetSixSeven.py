#!/usr/bin/env python
# coding: utf-8

# In[60]:


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


# In[61]:


import pyodbc 
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import math
    


# In[62]:


#scaleEgeVip = [
#    (109.32, 80.000000),  # Если значение больше 109.32%, то 80 баллов
#    (100.79, 65.000000),  # Если значение в диапазоне 100.79% – 109.32%, то 65 баллов
#    (98.91, 50.000000),  # Если значение в диапазоне 98.91% – 100.79%, то 50 баллов
#    (94.49, 50.000000),  # Если значение в диапазоне 94.49% – 98.91%, то 50 баллов
#    (91.31, 43.333333),  # Если значение в диапазоне 91.31% – 94.49%, то 43.333333333333336 баллов
#    (90.09, 36.666667),  # Если значение в диапазоне 90.09% – 91.31%, то 36.66666666666667 баллов
#    (88.38, 30.000000),  # Если значение в диапазоне 88.38% – 90.09%, то 30 баллов
#    (87.02, 23.333333),  # Если значение в диапазоне 87.02% – 88.38%, то 23.333333333333336 баллов
#    (85.44, 16.666667),  # Если значение в диапазоне 85.44% – 87.02%, то 16.666666666666668 баллов
#    (0, 10)        # Если значение меньше или равно 85.44%, то 10 баллов
#]

scaleEgeVip = [
    (109.32, 80.000000),  # Если значение больше 109.32%, то 80.0 баллов
    (100.79, 65.000000),  # Если значение в диапазоне 100.79% – 109.32%, то 65.0 баллов
    (98.91, 50.000000),  # Если значение в диапазоне 98.91% – 100.79%, то 50.0 баллов
    (94.49, 50.000000),  # Если значение в диапазоне 94.49% – 98.91%, то 50.0 баллов
    (91.31, 50.000000),  # Если значение в диапазоне 91.31% – 94.49%, то 50.0 баллов
    (90.09, 50.000000),  # Если значение в диапазоне 90.09% – 91.31%, то 50.0 баллов
    (88.38, 50.000000),  # Если значение в диапазоне 88.38% – 90.09%, то 50.0 баллов
    (87.02, 50.000000),  # Если значение в диапазоне 87.02% – 88.38%, то 50.0 баллов
    (85.44, 50.000000),  # Если значение в диапазоне 85.44% – 87.02%, то 50.0 баллов
    (0, 10)        # Если значение меньше или равно 85.44%, то 10 баллов
]

scaleTrudoustroistvoVip = [
    (100, 60),  # Если значение равно 100%, то 80 баллов
    (99, 50),   # Если значение 99%, то 75 баллов
    (97, 45),   # Если значение 97%, то 65 баллов
    (91, 40),   # Если значение 96%, то 60 баллов
]



scaleRidVip = [
    (537.83, 80),  # Если значение больше 537.83%, то 80 баллов
    (326.38, 75),  # Если значение в диапазоне 326.38% – 537.83%, то 75 баллов
    (236.58, 70),  # Если значение в диапазоне 236.58% – 326.38%, то 70 баллов
    (200.00, 65),  # Если значение в диапазоне 200.00% – 236.58%, то 65 баллов
    (150.00, 60),  # Если значение в диапазоне 150.00% – 200.00%, то 60 баллов
    (130.80, 55),  # Если значение в диапазоне 130.80% – 150.00%, то 55 баллов
    (100.00, 50),  # Если значение в диапазоне 100.00% – 130.80%, то 50 баллов
    (90.47, 50),  # Если значение в диапазоне 90.47% – 100.00%, то 50 баллов
    (61.88, 30),  # Если значение в диапазоне 61.88% – 90.47%, то 30 баллов
    (0, 10)        # Если значение меньше или равно 61.88%, то 10 баллов
]

scalePublNauchMaterialVip = [
    (1013.32, 80.000000),  # Если значение больше 1013.32%, то 80.0 баллов
    (582.90, 74.000000),  # Если значение в диапазоне 582.90% – 1013.32%, то 74.0 баллов
    (344.15, 68.000000),  # Если значение в диапазоне 344.15% – 582.90%, то 68.0 баллов
    (259.29, 62.000000),  # Если значение в диапазоне 259.29% – 344.15%, то 62.0 баллов
    (200.00, 56.000000),  # Если значение в диапазоне 200.00% – 259.29%, то 56.0 баллов
    (100.00, 50.000000),  # Если значение в диапазоне 100.00% – 200.00%, то 50.0 баллов
    (75.00, 50.000000),  # Если значение в диапазоне 75.00% – 100.00%, то 50.0 баллов
    (50.00, 36.666667),  # Если значение в диапазоне 50.00% – 75.00%, то 36.66666666666667 баллов
    (28.75, 23.333333),  # Если значение в диапазоне 28.75% – 50.00%, то 23.333333333333336 баллов
    (0, 10)        # Если значение меньше или равно 28.75%, то 10 баллов
]

scaleAkadMobVip = [
    (366.67, 80.000000),  # Если значение больше 366.67%, то 80.0 баллов
    (239.65, 70.000000),  # Если значение в диапазоне 239.65% – 366.67%, то 70.0 баллов
    (133.33, 60.000000),  # Если значение в диапазоне 133.33% – 239.65%, то 60.0 баллов
    (100.00, 50.000000),  # Если значение в диапазоне 100.00% – 133.33%, то 50.0 баллов
    (85.05, 50.000000),  # Если значение в диапазоне 85.05% – 100.00%, то 50.0 баллов
    (66.67, 36.666667),  # Если значение в диапазоне 66.67% – 85.05%, то 36.66666666666667 баллов
    (33.33, 23.333333),  # Если значение в диапазоне 33.33% – 66.67%, то 23.333333333333336 баллов
    (0, 10)        # Если значение меньше или равно 33.33%, то 10 баллов
]



scaleDolInostrVip = [
    (162.46, 80.000000),  # Если значение больше 162.46%, то 80.0 баллов
    (139.12, 72.500000),  # Если значение в диапазоне 139.12% – 162.46%, то 72.5 баллов
    (115.81, 65.000000),  # Если значение в диапазоне 115.81% – 139.12%, то 65.0 баллов
    (102.69, 57.500000),  # Если значение в диапазоне 102.69% – 115.81%, то 57.5 баллов
    (89.01, 50.000000),  # Если значение в диапазоне 89.01% – 102.69%, то 50.0 баллов
    (78.89, 50.000000),  # Если значение в диапазоне 78.89% – 89.01%, то 50.0 баллов
    (68.08, 40.000000),  # Если значение в диапазоне 68.08% – 78.89%, то 40.0 баллов
    (64.28, 30.000000),  # Если значение в диапазоне 64.28% – 68.08%, то 30.0 баллов
    (40.47, 20.000000),  # Если значение в диапазоне 40.47% – 64.28%, то 20.0 баллов
    (0, 10)        # Если значение меньше или равно 40.47%, то 10 баллов
]


scaleDolMagVip = [
    (141.12, 80),  # Если значение больше 141.12%, то 80 баллов
    (127.49, 75),  # Если значение в диапазоне 127.49% – 141.12%, то 75 баллов
    (124.42, 70),  # Если значение в диапазоне 124.42% – 127.49%, то 70 баллов
    (117.56, 65),  # Если значение в диапазоне 117.56% – 124.42%, то 65 баллов
    (111.62, 60),  # Если значение в диапазоне 111.62% – 117.56%, то 60 баллов
    (105.49, 55),  # Если значение в диапазоне 105.49% – 111.62%, то 55 баллов
    (98.05, 50),  # Если значение в диапазоне 98.05% – 105.49%, то 50 баллов
    (92.67, 50),  # Если значение в диапазоне 92.67% – 98.05%, то 50 баллов
    (89.09, 30),  # Если значение в диапазоне 89.09% – 92.67%, то 30 баллов
    (0, 10)        # Если значение меньше или равно 89.09%, то 10 баллов
]

scaleDolOstepenennykhVip = [
    (108.54, 80.000000),  # Если значение больше 100.54%, то 80.0 баллов
    (96.23, 50.000000),  # Если значение в диапазоне 96.23% – 100.54%, то 50.0 баллов
    (91.03, 50.000000),  # Если значение в диапазоне 91.03% – 96.23%, то 50.0 баллов
    (85.80, 44.285714),  # Если значение в диапазоне 85.80% – 91.03%, то 44.285714285714285 баллов
    (80.73, 38.571429),  # Если значение в диапазоне 80.73% – 85.80%, то 38.57142857142857 баллов
    (75.55, 32.857143),  # Если значение в диапазоне 75.55% – 80.73%, то 32.85714285714286 баллов
    (73.23, 27.142857),  # Если значение в диапазоне 73.23% – 75.55%, то 27.142857142857142 баллов
    (68.94, 21.428571),  # Если значение в диапазоне 68.94% – 73.23%, то 21.42857142857143 баллов
    (58.12, 15.714286),  # Если значение в диапазоне 58.12% – 68.94%, то 15.714285714285715 баллов
    (0, 10)        # Если значение меньше или равно 58.12%, то 10 баллов
]

scaleDolPPS200Vip = [
    (108.43, 80.000000),  # Если значение больше 108.43%, то 80.0 баллов
    (100.00, 50.000000),  # Если значение в диапазоне 100.00% – 108.43%, то 50.0 баллов
    (87.67, 50.000000),  # Если значение в диапазоне 87.67% – 100.00%, то 50.0 баллов
    (78.85, 44.285714),  # Если значение в диапазоне 78.85% – 87.67%, то 44.285714285714285 баллов
    (76.28, 38.571429),  # Если значение в диапазоне 76.28% – 78.85%, то 38.57142857142857 баллов
    (70.55, 32.857143),  # Если значение в диапазоне 70.55% – 76.28%, то 32.85714285714286 баллов
    (65.63, 27.142857),  # Если значение в диапазоне 65.63% – 70.55%, то 27.142857142857142 баллов
    (61.16, 21.428571),  # Если значение в диапазоне 61.16% – 65.63%, то 21.42857142857143 баллов
    (50.09, 15.714286),  # Если значение в диапазоне 50.09% – 61.16%, то 15.714285714285715 баллов
    (0, 10)        # Если значение меньше или равно 50.09%, то 10 баллов
]

scaleDolStorMagVip = [
    (197.83, 80.000000),  # Если значение больше 197.83%, то 80.0 баллов
    (120.48, 74.000000),  # Если значение в диапазоне 120.48% – 197.83%, то 74.0 баллов
    (112.35, 68.000000),  # Если значение в диапазоне 112.35% – 120.48%, то 68.0 баллов
    (106.61, 62.000000),  # Если значение в диапазоне 106.61% – 112.35%, то 62.0 баллов
    (102.72, 56.000000),  # Если значение в диапазоне 102.72% – 106.61%, то 56.0 баллов
    (94.83, 50.000000),  # Если значение в диапазоне 94.83% – 102.72%, то 50.0 баллов
    (77.23, 50.000000),  # Если значение в диапазоне 77.23% – 94.83%, то 50.0 баллов
    (70.69, 36.666667),  # Если значение в диапазоне 70.69% – 77.23%, то 36.66666666666667 баллов
    (50.56, 23.333333),  # Если значение в диапазоне 50.56% – 70.69%, то 23.333333333333336 баллов
    (0, 10)        # Если значение меньше или равно 50.56%, то 10 баллов
]


scaleDolCelevikovVip = [
    (197.83, 80.000000),  # Если значение больше 197.83%, то 80.0 баллов
    (120.48, 74.000000),  # Если значение в диапазоне 120.48% – 197.83%, то 74.0 баллов
    (112.35, 68.000000),  # Если значение в диапазоне 112.35% – 120.48%, то 68.0 баллов
    (106.61, 62.000000),  # Если значение в диапазоне 106.61% – 112.35%, то 62.0 баллов
    (102.72, 56.000000),  # Если значение в диапазоне 102.72% – 106.61%, то 56.0 баллов
    (94.83, 50.000000),  # Если значение в диапазоне 94.83% – 102.72%, то 50.0 баллов
    (77.23, 50.000000),  # Если значение в диапазоне 77.23% – 94.83%, то 50.0 баллов
    (70.69, 36.666667),  # Если значение в диапазоне 70.69% – 77.23%, то 36.66666666666667 баллов
    (50.56, 23.333333),  # Если значение в диапазоне 50.56% – 70.69%, то 23.333333333333336 баллов
    (0, 10)        # Если значение меньше или равно 50.56%, то 10 баллов
]

scaleZashchityVip = [
    (168.30, 80.000000),  # Если значение больше 168.30%, то 80.0 баллов
    (146.51, 72.500000),  # Если значение в диапазоне 146.51% – 168.30%, то 72.5 баллов
    (136.51, 65.000000),  # Если значение в диапазоне 136.51% – 146.51%, то 65.0 баллов
    (118.85, 57.500000),  # Если значение в диапазоне 118.85% – 136.51%, то 57.5 баллов
    (100.00, 50.000000),  # Если значение в диапазоне 100.00% – 118.85%, то 50.0 баллов
    (87.47, 50.000000),  # Если значение в диапазоне 87.47% – 100.00%, то 50.0 баллов
    (77.14, 40.000000),  # Если значение в диапазоне 77.14% – 87.47%, то 40.0 баллов
    (69.15, 30.000000),  # Если значение в диапазоне 69.15% – 77.14%, то 30.0 баллов
    (59.43, 20.000000),  # Если значение в диапазоне 59.43% – 69.15%, то 20.0 баллов
    (0, 10)        # Если значение меньше или равно 59.43%, то 10 баллов
]


scaleDolPPS200Vip = [
    (168.30, 80.000000),  # Если значение больше 168.30%, то 80.0 баллов
    (146.51, 72.500000),  # Если значение в диапазоне 146.51% – 168.30%, то 72.5 баллов
    (136.51, 65.000000),  # Если значение в диапазоне 136.51% – 146.51%, то 65.0 баллов
    (118.85, 57.500000),  # Если значение в диапазоне 118.85% – 136.51%, то 57.5 баллов
    (100.00, 50.000000),  # Если значение в диапазоне 100.00% – 118.85%, то 50.0 баллов
    (87.47, 50.000000),  # Если значение в диапазоне 87.47% – 100.00%, то 50.0 баллов
    (77.14, 40.000000),  # Если значение в диапазоне 77.14% – 87.47%, то 40.0 баллов
    (69.15, 30.000000),  # Если значение в диапазоне 69.15% – 77.14%, то 30.0 баллов
    (59.43, 20.000000),  # Если значение в диапазоне 59.43% – 69.15%, то 20.0 баллов
    (0, 10)        # Если значение меньше или равно 59.43%, то 10 баллов
]

scaleZayavAktivVip = [
    (211.33, 80),  # Если значение больше 211.33%, то 80 баллов
    (136.00, 70),  # Если значение в диапазоне 136.00% – 211.33%, то 70 баллов
    (120.00, 60),  # Если значение в диапазоне 120.00% – 136.00%, то 60 баллов
    (100.00, 50),  # Если значение в диапазоне 100.00% – 120.00%, то 50 баллов
    (75.00, 42),  # Если значение в диапазоне 75.00% – 100.00%, то 42 баллов
    (72.86, 34),  # Если значение в диапазоне 72.86% – 75.00%, то 34 баллов
    (50.00, 26),  # Если значение в диапазоне 50.00% – 72.86%, то 26 баллов
    (38.67, 18),  # Если значение в диапазоне 38.67% – 50.00%, то 18 баллов
    (0, 10)        # Если значение меньше или равно 38.67%, то 10 баллов
]

scaleInnovaciiVip = [
    (200.00, 80),  # Если значение больше 200.00%, то 80 баллов
    (150.00, 70),  # Если значение в диапазоне 150.00% – 200.00%, то 70 баллов
    (133.33, 60),  # Если значение в диапазоне 133.33% – 150.00%, то 60 баллов
    (100.00, 50),  # Если значение в диапазоне 100.00% – 133.33%, то 50 баллов
    (87.47, 50),  # Если значение в диапазоне 87.47% – 100.00%, то 50 баллов
    (66.67, 40),  # Если значение в диапазоне 66.67% – 87.47%, то 40 баллов
    (50.00, 30),  # Если значение в диапазоне 50.00% – 66.67%, то 30 баллов
    (33.33, 20),  # Если значение в диапазоне 33.33% – 50.00%, то 20 баллов
    (0, 10)        # Если значение меньше или равно 33.33%, то 10 баллов
]



scaleKolInostrPrepodVip = [
    (632.48, 80.000000),  # Если значение больше 632.48%, то 80.0 баллов
    (500.00, 76.666667),  # Если значение в диапазоне 500.00% – 632.48%, то 76.66666666666667 баллов
    (447.22, 73.333333),  # Если значение в диапазоне 447.22% – 500.00%, то 73.33333333333334 баллов
    (400.00, 70.000000),  # Если значение в диапазоне 400.00% – 447.22%, то 70.0 баллов
    (346.42, 66.666667),  # Если значение в диапазоне 346.42% – 400.00%, то 66.66666666666667 баллов
    (300.00, 63.333333),  # Если значение в диапазоне 300.00% – 346.42%, то 63.333333333333336 баллов
    (244.97, 60.000000),  # Если значение в диапазоне 244.97% – 300.00%, то 60.0 баллов
    (200.00, 56.666667),  # Если значение в диапазоне 200.00% – 244.97%, то 56.666666666666664 баллов
    (141.48, 53.333333),  # Если значение в диапазоне 141.48% – 200.00%, то 53.333333333333336 баллов
    (0, 10)        # Если значение меньше или равно 141.48%, то 10 баллов
]


scaleKolPublikVip = [
    (143.64, 80),  # Если значение больше 143.64%, то 80 баллов
    (119.66, 70),  # Если значение в диапазоне 119.66% – 143.64%, то 70 баллов
    (106.16, 60),  # Если значение в диапазоне 106.16% – 119.66%, то 60 баллов
    (91.74, 50),  # Если значение в диапазоне 91.74% – 106.16%, то 50 баллов
    (81.94, 50),  # Если значение в диапазоне 81.94% – 91.74%, то 50 баллов
    (76.49, 42),  # Если значение в диапазоне 76.49% – 81.94%, то 42 баллов
    (67.94, 34),  # Если значение в диапазоне 67.94% – 76.49%, то 34 баллов
    (61.23, 26),  # Если значение в диапазоне 61.23% – 67.94%, то 26 баллов
    (55.94, 18),  # Если значение в диапазоне 55.94% – 61.23%, то 18 баллов
    (0, 10)        # Если значение меньше или равно 55.94%, то 10 баллов
]

scaleObemNIOKRVip = [
    (281.73, 80.000000),  # Если значение больше 281.73%, то 80.0 баллов
    (181.08, 72.500000),  # Если значение в диапазоне 181.08% – 281.73%, то 72.5 баллов
    (131.28, 65.000000),  # Если значение в диапазоне 131.28% – 181.08%, то 65.0 баллов
    (112.83, 57.500000),  # Если значение в диапазоне 112.83% – 131.28%, то 57.5 баллов
    (83.61, 50.000000),  # Если значение в диапазоне 83.61% – 112.83%, то 50.0 баллов
    (74.05, 50.000000),  # Если значение в диапазоне 74.05% – 83.61%, то 50.0 баллов
    (59.25, 40.000000),  # Если значение в диапазоне 59.25% – 74.05%, то 40.0 баллов
    (34.00, 30.000000),  # Если значение в диапазоне 34.00% – 59.25%, то 30.0 баллов
    (13.31, 20.000000),  # Если значение в диапазоне 13.31% – 34.00%, то 20.0 баллов
    (0, 10)        # Если значение меньше или равно 13.31%, то 10 баллов
]




scaleObemPOUVip = [
    (142.36, 80.000000),  # Если значение больше 142.36%, то 80.0 баллов
    (124.13, 72.500000),  # Если значение в диапазоне 124.13% – 142.36%, то 72.5 баллов
    (117.00, 65.000000),  # Если значение в диапазоне 117.00% – 124.13%, то 65.0 баллов
    (107.26, 57.500000),  # Если значение в диапазоне 107.26% – 117.00%, то 57.5 баллов
    (91.20, 50.000000),  # Если значение в диапазоне 91.20% – 107.26%, то 50.0 баллов
    (77.58, 50.000000),  # Если значение в диапазоне 77.58% – 91.20%, то 50.0 баллов
    (70.72, 40.000000),  # Если значение в диапазоне 70.72% – 77.58%, то 40.0 баллов
    (64.68, 30.000000),  # Если значение в диапазоне 64.68% – 70.72%, то 30.0 баллов
    (50.58, 20.000000),  # Если значение в диапазоне 50.58% – 64.68%, то 20.0 баллов
    (0, 10)        # Если значение меньше или равно 50.58%, то 10 баллов
]

scaleObemPOUVip = [
    (142.36, 80.000000),  # Если значение больше 142.36%, то 80.0 баллов
    (124.13, 72.500000),  # Если значение в диапазоне 124.13% – 142.36%, то 72.5 баллов
    (117.00, 65.000000),  # Если значение в диапазоне 117.00% – 124.13%, то 65.0 баллов
    (107.26, 57.500000),  # Если значение в диапазоне 107.26% – 117.00%, то 57.5 баллов
    (91.20, 50.000000),  # Если значение в диапазоне 91.20% – 107.26%, то 50.0 баллов
    (77.58, 50.000000),  # Если значение в диапазоне 77.58% – 91.20%, то 50.0 баллов
    (70.72, 50.000000),  # Если значение в диапазоне 70.72% – 77.58%, то 50.0 баллов
    (64.68, 36.666667),  # Если значение в диапазоне 64.68% – 70.72%, то 36.66666666666667 баллов
    (50.58, 23.333333),  # Если значение в диапазоне 50.58% – 64.68%, то 23.333333333333336 баллов
    (0, 10)        # Если значение меньше или равно 50.58%, то 10 баллов
]

scalePodgotovkaEnciklVip = [
    (0,0)
]



scaleDolMolNPRVip = [
    (173.15, 80),          # Если значение больше 173.15%, то 80 баллов
    (134.32, 72.5),        # Если значение в диапазоне 134.32% – 173.15%, то 72.5 баллов
    (119.05, 65),          # Если значение в диапазоне 119.05% – 134.32%, то 65 баллов
    (108.02, 57.5),        # Если значение в диапазоне 108.02% – 119.05%, то 57.5 баллов
    (99.21, 50),           # Если значение в диапазоне 99.21% – 108.02%, то 50 баллов
    (91.58, 50),           # Если значение в диапазоне 91.58% – 99.21%, то 50 баллов
    (66.15, 40),           # Если значение в диапазоне 66.15% – 91.58%, то 40 баллов
    (59.52, 30),           # Если значение в диапазоне 59.52% – 66.15%, то 30 баллов
    (49.16, 20),           # Если значение в диапазоне 49.16% – 59.52%, то 20 баллов
    (0, 10)                # Если значение меньше или равно 49.16%, то 10 баллов
]


# In[63]:


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


# In[64]:


def CalcBallCompare(E_kaf, E_univ, sigma):
    # Вычисляем баллы за сравнение B_срав по формуле
    B_compare = 50 + ((E_kaf - E_univ) / sigma) * 10
    print(f"CalcBallCompare called with value={E_kaf}, sred_C02={E_univ}, std_EGE={sigma}")
  
    # Применяем ограничения
    if B_compare > 80:
        B_compare = 80
    elif B_compare < 20:
        B_compare = 20
    
    return B_compare


# In[65]:


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


# In[66]:


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





# In[67]:


# Сохраняем DataFrame в CSV файл
#df.to_csv('dannie6.csv', index=False)

# Очищаем DataFrame
df = pd.DataFrame()

# Загружаем данные из CSV файла
df = pd.read_csv('dannie.csv')


# In[9]:


# Загрузка данных из CSV файла средних по университету
dfSred = pd.read_csv('sredneeUniver.csv', delimiter=';')

# Преобразование DataFrame в словарь
dictSred = dfSred.set_index('IndicatorCode')['SredneePoUniver'].to_dict()

print(dictSred)


# In[68]:


df


# In[69]:


columns_list = df.columns.tolist()
print(columns_list)


# In[72]:


# Фильтрация строк, где кафедра равна 'РТС'
filtered_df = df[df['kafedra'] == 'РТС']

# Вывод отфильтрованных данных
filtered_df.to_csv('filtered_data.csv', index=False, encoding='utf-8')


# In[ ]:





# In[10]:


# Преобразование значений в словаре dictSred, заменяя запятую на точку перед преобразованием в float
dictSred = {key: float(value.replace(',', '.')) for key, value in dictSred.items()}


# In[11]:


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


# In[12]:


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


# In[13]:


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


# In[14]:


print(list(df.columns))


# In[15]:


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




