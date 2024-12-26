import psycopg2
import psycopg2.extras
from psycopg2 import extras
import numpy as np
from environment.settings import DB_CONFIG

num_records = 100
user_id_range = (1, 12)  # Пользователи от 1 до 11
product_id_range = (1, 22168)  # Продукты от 1 до 22167
quantity_range = (1, 5)  # Количество от 1 до 4


def reset_database():
    ddl_dml_script = """
    
    -- Удаление существующих таблиц
    DROP TABLE IF EXISTS order_items CASCADE;
    DROP TABLE IF EXISTS orders CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS manufacturers CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    DROP TABLE IF EXISTS reviews CASCADE;
   	DROP TABLE IF EXISTS categories CASCADE;
   	DROP TABLE IF EXISTS recommend_items CASCADE;
   	DROP TABLE IF EXISTS sales CASCADE;
   	DROP TABLE IF EXISTS order_data CASCADE;
   	DROP TABLE IF EXISTS month_revenue CASCADE;


    -- Создание новых таблиц
    
        -- Тип для прав пользователей
    --CREATE TYPE user_role AS ENUM ('user', 'admin');
    
    -- Таблица пользователей (users) с объединенными данными пользователей и админов
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        password TEXT NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        balance FLOAT DEFAULT 0,
        role user_role NOT NULL DEFAULT 'user'
    );
    
    -- Таблица производителей (manufacturers)
    CREATE TABLE IF NOT EXISTS manufacturers (
        shop_name VARCHAR(255) UNIQUE NOT NULL,
        shop_id SERIAL PRIMARY KEY
    );
   
      -- Создание таблицы categories
    CREATE TABLE IF NOT EXISTS categories (
        item_category_name VARCHAR(100) NOT NULL,
        item_category_id SERIAL PRIMARY KEY 
    );
    
    -- Таблица продуктов (products), объединенная с products_info
    CREATE TABLE IF NOT EXISTS products (
        item_name VARCHAR(255) NOT NULL,
        item_id SERIAL PRIMARY KEY,
        item_category_id INT REFERENCES categories(item_category_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS sales (
        date TEXT NOT NULL,
        date_block_num INT NOT NULL,
        shop_id INT REFERENCES manufacturers(shop_id) ON DELETE SET NULL,
        item_id INT REFERENCES products(item_id) ON DELETE SET NULL,
        item_price FLOAT NOT NULL,
        item_cnt_day FLOAT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS recommend_items (
        --rec_item_id SERIAL PRIMARY KEY,
        item_category_id INT REFERENCES categories(item_category_id) ON DELETE SET NULL,
        item_id INT REFERENCES products(item_id) ON DELETE SET NULL
    );
    
    CREATE TABLE IF NOT EXISTS recommend_items_by_category (
        item_category_id INT REFERENCES categories(item_category_id) ON DELETE SET NULL,
        item_id INT REFERENCES products(item_id) ON DELETE SET NULL
    );

    -- Таблица заказов (orders)
    CREATE TABLE IF NOT EXISTS orders (
        order_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
        total_price FLOAT NOT NULL,
        order_date TIMESTAMP NOT NULL,
        status VARCHAR(50) NOT NULL
    );
    
    -- Таблица с товарами в заказе
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id SERIAL PRIMARY KEY,
        order_id INT REFERENCES orders(order_id),
        item_id INT REFERENCES products(item_id),
        quantity INT NOT NULL
        --price DECIMAL NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS order_data (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS month_revenue (
        item_id INT NOT NULL,
        item_cnt_month FLOAT NOT NULL
    );
    
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
     """

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(ddl_dml_script)  # Выполнение DDL/DML скрипта
            #extras.execute_values(cur, insert_query, orders_list)  # Пакетная вставка
            conn.commit()

reset_database()
