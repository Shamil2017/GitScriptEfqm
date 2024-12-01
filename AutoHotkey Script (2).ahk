^!c:: ; Комбинация клавиш Ctrl + Alt + C
Run, "C:\Program Files\Google\Chrome\Application\chrome.exe" https://chat.openai.com ; Запуск Chrome с ChatGPT
Sleep, 10000 ; Ожидание 10 секунд для загрузки браузера
Send, +{Esc} ; Нажатие Shift+Esc
Sleep, 500 ; Небольшая пауза для обработки нажатия
Send, Как лучше убрать мусор дома ; Ввод текста
Sleep, 2000 ; Пауза 2 секунды
Send, {Enter} ; Нажатие Enter
Sleep, 15000 ; Ждем 15 секунд
Send, ^+c ; Нажатие Ctrl+Shift+C
return

