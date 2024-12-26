-- Тип для прав пользователей
CREATE TYPE user_role AS ENUM ('user', 'admin');

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