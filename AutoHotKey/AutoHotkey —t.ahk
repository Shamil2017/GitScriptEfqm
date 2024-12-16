^!t:: ; Ctrl + Alt + T
; Запускаем Python-скрипт
Run, "C:\efqm\K5\openai-env\Scripts\python.exe" "C:\efqm\K5\process_response.py"
; Ждем завершения выполнения и обновления буфера обмена
Sleep, 1000 ; Задержка 1 секунда
return
