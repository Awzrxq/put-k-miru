import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Безопасность: секретный ключ и настройки cookie
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-only-key-change-me')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 час

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'put_k_miru_db'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'supersecretpassword')
}


def get_db():
    return psycopg2.connect(**DB_CONFIG)


def send_email(data):
    server = os.getenv('MAIL_SERVER')
    port = int(os.getenv('MAIL_PORT', 465))
    user = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    recipient = os.getenv('MAIL_RECIPIENT')

    if not all([server, user, password, recipient]):
        print("Нет MAIL-настроек", flush=True)
        return

    body = "Новая заявка!\n"
    body += "Имя: " + str(data.get('name')) + "\n"
    body += "Телефон: " + str(data.get('phone')) + "\n"
    body += "Услуга: " + str(data.get('service_type') or '-') + "\n"
    body += "Сообщение: " + str(data.get('message') or '-')

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header("Новая заявка с сайта Путь к миру", 'utf-8')
    msg['From'] = user
    msg['To'] = recipient

    try:
        with smtplib.SMTP_SSL(server, port, timeout=20) as smtp:
            smtp.login(user, password)
            smtp.sendmail(user, [recipient], msg.as_string())
        print("Письмо отправлено на " + recipient, flush=True)
    except Exception as e:
        print("Ошибка: " + type(e).__name__ + ": " + str(e), flush=True)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM appointments ORDER BY created_at DESC')
        result = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        print('Ошибка: ' + str(e), flush=True)
        return jsonify({'error': 'Ошибка сервера'}), 500


@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    try:
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone')
        service_type = data.get('service_type', '')
        message = data.get('message', '')

        if not name or not phone:
            return jsonify({'error': 'Имя и телефон обязательны'}), 400

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            'INSERT INTO appointments (name, phone, service_type, message) VALUES (%s, %s, %s, %s) RETURNING *',
            (name, phone, service_type, message)
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        send_email(result)
        return jsonify(result), 201
    except Exception as e:
        print('Ошибка: ' + str(e), flush=True)
        return jsonify({'error': 'Ошибка'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
