-- Заполнение таблицы users
INSERT INTO
    users (password, email, balance, role)
VALUES
    ('admin', 'admin@admin.com', 5000.0, 'admin'),   -- Админ
    ('123', 'lev@lev.com', 2000.0, 'user'),
    ('aboba', 'aboba@aboba.com', 1000.0, 'user'),
    ('qwerty', 'obama@mypresident.ru', 0.0, 'user'),
    ('555', '5@5', 2000.0, 'user'),
    ('666', '6@6', 1000.0, 'user'),
    ('777', '7@7', 0.0, 'user'),
    ('888', '8@8', 2000.0, 'user'),
    ('999', '9@9', 1000.0, 'user'),
    ('10', '10@10', 0.0, 'user'),
    ('11', '11@11', 2000.0, 'user'),
    ('12', '12@12', 2000.0, 'user'),
    ('13', '13@13', 1000.0, 'admin');