#!/bin/bash

# Установка Python 3 и pip, если их нет
if ! command -v python3 &> /dev/null; then
    echo "Python 3 не установлен. Устанавливаем..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv screen
fi

# Установка screen, если его нет
if ! command -v screen &> /dev/null; then
    echo "Установка screen..."
    sudo apt install -y screen
fi

# Создание виртуального окружения (если его нет)
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей из requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Установка зависимостей..."
    pip install -r requirements.txt
else
    echo "Файл requirements.txt не найден!"
    exit 1
fi

# Проверка наличия app.py
if [ ! -f "app.py" ]; then
    echo "Файл app.py не найден!"
    exit 1
fi

# Запуск Flask-приложения в screen-сессии
echo "Запуск Flask-приложения в screen..."
export FLASK_APP=app.py
export FLASK_ENV=development

# Создаем новую screen-сессию с именем "flask_app" и запускаем Flask
screen -dmS flask_app bash -c 'flask run --host=0.0.0.0; exec bash'

echo "Приложение запущено в фоновом режиме."
echo "Для подключения к сессии выполните: screen -r flask_app"
echo "Для отключения (без остановки): Ctrl+A затем D"#!/bin/bash

# Установка Python 3 и pip, если их нет
if ! command -v python3 &> /dev/null; then
    echo "Python 3 не установлен. Устанавливаем..."
    sudo apt update
#!/bin/bash

# Установка Python 3 и pip, если их нет
if ! command -v python3 &> /dev/null; then
    echo "Python 3 не установлен. Устанавливаем..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv screen
fi

# Установка screen, если его нет
if ! command -v screen &> /dev/null; then
    echo "Установка screen..."
    sudo apt install -y screen
fi

# Создание виртуального окружения (если его нет)
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей из requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Установка зависимостей..."
    pip install -r requirements.txt
else
    echo "Файл requirements.txt не найден!"
    exit 1
fi

# Проверка наличия app.py
if [ ! -f "app.py" ]; then
    echo "Файл app.py не найден!"
    exit 1
fi

# Запуск Flask-приложения в screen-сессии
echo "Запуск Flask-приложения в screen..."
export FLASK_APP=app.py
export FLASK_ENV=development

# Создаем новую screen-сессию с именем "flask_app" и запускаем Flask
screen -dmS flask_app bash -c 'flask run --host=0.0.0.0; exec bash'

echo "Приложение запущено в фоновом режиме."
echo "Для подключения к сессии выполните: screen -r flask_app"
echo "Для отключения (без остановки): Ctrl+A затем D"
