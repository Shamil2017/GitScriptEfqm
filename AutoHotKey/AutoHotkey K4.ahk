^!4:: ; Ctrl + Alt + 4
;Run, "C:\Program Files\Google\Chrome\Application\chrome.exe" https://chat.openai.com ; Launch ChatGPT
;Sleep, 5000 ; Wait 9 seconds for browser to load
;Send, +{Esc} ; Focus input field
;Sleep, 500 ; Short pause

; Trigger Python to fetch the next query and copy it to clipboard
Run, "C:\efqm\K4\openai-env\Scripts\python.exe" "C:\efqm\K4\fetch_next_query.py"
Sleep, 2000 ; Wait for query to load in clipboard

;Send, ^v ; Paste the query into ChatGPT
;Sleep, 500 ; Short pause
;Send, {Enter} ; Send the query

return


