^!y:: ; Ctrl + Alt + Y
; Запускаем Python-скрипт
Run, "C:\efqm\K6\openai-env\Scripts\python.exe" "C:\efqm\K6\process_response.py"
; Ждем завершения выполнения и обновления буфера обмена
Sleep, 1000 ; Задержка 1 секунда
return
