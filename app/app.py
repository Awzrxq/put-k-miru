import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'put_k_miru_db'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'supersecretpassword')
}


def get_db():
    return psycopg2.connect(**DB_CONFIG)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'put-k-miru-flask'})


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
        print('Ошибка при получении заявок:', e)
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
            '''INSERT INTO appointments (name, phone, service_type, message)
               VALUES (%s, %s, %s, %s) RETURNING *''',
            (name, phone, service_type, message)
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(result), 201
    except Exception as e:
        print('Ошибка при создании заявки:', e)
        return jsonify({'error': 'Ошибка при создании заявки'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
