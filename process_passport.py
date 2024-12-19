import pyperclip
import keyboard

def copy_to_clipboard(data):
    pyperclip.copy(data)

def read_and_copy_file(filename, batch_size=100):
    with open(filename, 'r', encoding='utf-8') as file:
        while True:
            # Чтение следующей порции строк
            lines = [file.readline().strip() for _ in range(batch_size)]
            lines = [line for line in lines if line]  # Удаляем пустые строки

            if not lines:
                break  # Если строки закончились, выходим из цикла

            # Копируем строки в буфер обмена
            copy_to_clipboard('\n'.join(lines))
            print(f'Копировано {len(lines)} строк в буфер обмена.')

            # Ожидание нажатия клавиши (например, пробел)
            print('Нажмите пробел для копирования следующих строк...')
            keyboard.wait('space')

if __name__ == "__main__":
    read_and_copy_file('example.txt')