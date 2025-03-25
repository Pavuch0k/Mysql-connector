from flask import Flask, render_template, jsonify, request
import mysql.connector
import json
import os
from datetime import datetime

app = Flask(__name__)


# Настройка логирования
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


# Конфигурация подключения к базе данных
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': '',
    'port': 3306,
    'table_prefix': ''
}


def load_db_config():
    """Загружает конфигурацию из файла"""
    global DB_CONFIG
    try:
        if os.path.exists('db_config.json'):
            log_message("Попытка загрузить конфигурацию из db_config.json")
            with open('db_config.json', 'r') as f:
                saved_config = json.load(f)
                DB_CONFIG.update(saved_config)
                log_message(f"Загружена конфигурация: {DB_CONFIG}")
    except Exception as e:
        log_message(f"Ошибка загрузки конфигурации: {e}")


load_db_config()


def get_db_connection():
    """Создает и возвращает соединение с базой данных с подробным логированием"""
    connection_config = DB_CONFIG.copy()
    table_prefix = connection_config.pop('table_prefix', '')

    log_message(f"Попытка подключения с параметрами: {connection_config}")

    try:
        conn = mysql.connector.connect(**connection_config)
        log_message("Подключение к базе данных успешно установлено")
        return conn
    except mysql.connector.Error as err:
        log_message(f"Ошибка подключения к базе данных: {err}")
        raise


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/directions')
def directions():
    return render_template('directions.html')


@app.route('/currencies')
def currencies():
    return render_template('currencies.html')


@app.route('/settings')
def settings():
    log_message("Отображение страницы настроек")
    return render_template('settings.html')


@app.route('/save-settings', methods=['POST'])
def save_settings():
    try:
        log_message("Начало обработки сохранения настроек")

        # Получаем данные из формы
        form_data = request.form
        host = form_data.get('host')
        database = form_data.get('database')
        user = form_data.get('user')
        password = form_data.get('password')
        table_prefix = form_data.get('table-prefix')

        log_message(f"Получены данные формы: host={host}, db={database}, user={user}, prefix={table_prefix}")

        # Проверка обязательных полей
        if not all([host, database, user]):
            msg = "Не заполнены обязательные поля"
            log_message(msg)
            return jsonify({"error": msg}), 400

        # Тестовое подключение
        test_config = {
            'host': host,
            'user': user,
            'password': password or '',
            'database': database,
            'port': 3306
        }

        log_message(f"Попытка тестового подключения с параметрами: {test_config}")

        try:
            test_conn = mysql.connector.connect(**test_config)
            test_conn.close()
            log_message("Тестовое подключение успешно")
        except mysql.connector.Error as err:
            error_msg = f"Ошибка подключения к базе данных: {err}"
            log_message(error_msg)
            return jsonify({"error": error_msg}), 400

        # Обновляем конфигурацию
        global DB_CONFIG
        DB_CONFIG = {
            'host': host,
            'user': user,
            'password': password or '',
            'database': database,
            'port': 3306,
            'table_prefix': table_prefix or ''
        }

        # Сохраняем настройки
        try:
            with open('db_config.json', 'w') as f:
                json.dump(DB_CONFIG, f)
            log_message("Настройки успешно сохранены в файл")
        except Exception as e:
            log_message(f"Ошибка сохранения настроек в файл: {e}")
            return jsonify({"error": str(e)}), 500

        return jsonify({
            "message": "Настройки успешно сохранены!",
            "config": {
                "host": host,
                "database": database,
                "user": user,
                "prefix": table_prefix
            }
        }), 200

    except Exception as e:
        log_message(f"Ошибка в save_settings: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/currencies', methods=['GET'])
def get_currencies():
    conn = None
    cursor = None
    try:
        log_message("Запрос списка валют")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        table_prefix = DB_CONFIG.get('table_prefix', '')
        table_name = f"{table_prefix}_currency" if table_prefix else "currency"

        log_message(f"Используется таблица: {table_name}")

        query = f"""
            SELECT id, psys_id, psys_title, currency_code_title, 
                   currency_decimal, currency_reserv, currency_status 
            FROM {table_name}
        """

        log_message(f"Выполняется запрос: {query}")
        cursor.execute(query)
        data = cursor.fetchall()

        log_message(f"Получено {len(data)} записей")
        return jsonify(data)

    except Exception as e:
        log_message(f"Ошибка в get_currencies: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/directions/<int:id>', methods=['PUT'])
def update_direction(id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Формируем имя таблицы с префиксом
        table_name = f"{DB_CONFIG['table_prefix']}_directions"

        updates = {}
        if 'direction_status' in data:
            status = data['direction_status']
            if status not in (0, 1):
                return jsonify({"error": "Недопустимое значение статуса"}), 400
            updates['direction_status'] = status

        fields = ['tech_name', 'new_parser', 'new_parser_actions_get']
        for field in fields:
            if field in data:
                updates[field] = data[field]

        if not updates:
            return jsonify({"error": "Нет полей для обновления"}), 400

        set_clause = ', '.join([f"{key} = %s" for key in updates.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        values = list(updates.values()) + [id]
        cursor.execute(query, values)
        conn.commit()

        return jsonify({"message": "Направление обновлено", "id": id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/directions', methods=['GET'])
def get_directions():
    conn = None
    cursor = None
    try:
        log_message("Запрос списка направлений")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        table_prefix = DB_CONFIG.get('table_prefix', '')
        directions_table = f"{table_prefix}_directions" if table_prefix else "directions"
        currency_table = f"{table_prefix}_currency" if table_prefix else "currency"

        log_message(f"Используются таблицы: {directions_table} и {currency_table}")

        query = f"""
        SELECT d.id, d.tech_name, c1.xml_value AS currency_give, c2.xml_value AS currency_get, 
               d.new_parser, d.new_parser_actions_get, d.direction_status 
        FROM {directions_table} d
        LEFT JOIN {currency_table} c1 ON d.currency_id_give = c1.id
        LEFT JOIN {currency_table} c2 ON d.currency_id_get = c2.id
        """

        log_message(f"Выполняется запрос: {query}")
        cursor.execute(query)
        data = cursor.fetchall()

        log_message(f"Получено {len(data)} записей направлений")
        return jsonify(data)

    except Exception as e:
        log_message(f"Ошибка в get_directions: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




@app.route('/api/currencies/<int:id>', methods=['PUT'])
def update_currency(id):
    try:
        data = request.get_json()
        updates = {}

        if 'currency_status' in data:
            status = data['currency_status']
            if status not in (0, 1):
                return jsonify({"error": "Недопустимое значение статуса"}), 400
            updates['currency_status'] = status

        allowed_fields = ['currency_code_title', 'currency_decimal']
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]

        if not updates:
            return jsonify({"error": "Нет полей для обновления"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Формируем имя таблицы с префиксом
        table_name = f"{DB_CONFIG['table_prefix']}_currency"

        set_clause = ', '.join([f"{key} = %s" for key in updates.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        values = list(updates.values()) + [id]

        cursor.execute(query, values)
        conn.commit()

        return jsonify({
            "message": "Валюта обновлена",
            "id": id,
            "updates": updates
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get-current-settings', methods=['GET'])
def get_current_settings():
    try:
        log_message("Запрос текущих настроек подключения")
        
        # Возвращаем текущую конфигурацию, исключая пароль из логов
        response_config = DB_CONFIG.copy()
        if 'password' in response_config:
            response_config['password'] = '*****' if response_config['password'] else ''
        
        log_message(f"Отправка текущих настроек: {response_config}")
        return jsonify(response_config), 200
    except Exception as e:
        log_message(f"Ошибка при получении настроек: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    log_message("Запуск приложения")
    app.run(debug=True, host='0.0.0.0')
