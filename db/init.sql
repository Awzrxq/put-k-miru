CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    service_type VARCHAR(100),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO appointments (name, phone, service_type, message) 
VALUES ('Тестовый Клиент', '+79990000000', 'Индивидуальная консультация', 'Хочу записаться на прием');
