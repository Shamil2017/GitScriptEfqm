^!r:: ; Ctrl + Alt + R
; Запускаем Python-скрипт
Run, "C:\efqm\K4\openai-env\Scripts\python.exe" "C:\efqm\K4\process_response.py"
; Ждем завершения выполнения и обновления буфера обмена
Sleep, 1000 ; Задержка 1 секунда
return
