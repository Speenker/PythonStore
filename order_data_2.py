import random
import pandas as pd
import numpy as np
import psycopg2
from environment.settings import DB_CONFIG

# Load item data from CSV
items_df = pd.read_csv('database/items.csv')
items = items_df['item_name'].tolist()
item_ids = items_df['item_id'].tolist()

def get_random_items_around_center(items, center_index, num_samples):
    """Выбирает случайные товары из заданного диапазона."""
    max_index = len(items) -1
    indices = [i for i in random.sample(range(max(0, center_index - 1000), min(max_index, center_index + 1000)), num_samples)]
    return [items[i] for i in indices]

def generate_order_data(user_ids, items):
    """Генерирует данные о заказах для каждого пользователя."""
    order_data = []
    for user_id in user_ids:
        center_index = random.randrange(len(items) - 105)  # Генерация центрального индекса для каждого пользователя
        items_sample = get_random_items_around_center(items, center_index, 10)
        item_quantities = dict(zip(items_sample, np.random.randint(1, 11, len(items_sample)))) #количество от 1 до 10

        for item_name, quantity in item_quantities.items():
            item_id = item_ids[items.index(item_name)]
            order_data.append((user_id, item_id, quantity))
    return order_data

# User IDs
user_ids = range(20, 101)

# Generate order data
order_data = generate_order_data(user_ids, items)

# Insert data into the database
try:
    with psycopg2.connect(**DB_CONFIG) as conn:
        cur = conn.cursor()
        insert_query = """
            INSERT INTO order_data (user_id, product_id, quantity)
            VALUES (%s, %s, %s);
        """
        order_data_python_ints = [(user_id, int(product_id), int(quantity)) for user_id, product_id, quantity in
                                  order_data]
        cur.executemany(insert_query, order_data_python_ints)
        conn.commit()
        print("Data inserted successfully!")
except psycopg2.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
