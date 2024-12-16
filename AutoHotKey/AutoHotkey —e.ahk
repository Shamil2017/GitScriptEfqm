^!e:: ; Ctrl + Alt + E
; Запускаем Python-скрипт
Run, "C:\efqm\K3\openai-env\Scripts\python.exe" "C:\efqm\K3\process_response.py"
; Ждем завершения выполнения и обновления буфера обмена
Sleep, 1000 ; Задержка 1 секунда
return
