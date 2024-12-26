import pandas as pd
import numpy as np
from collections import defaultdict
import psycopg2
import psycopg2.extras
import streamlit

from environment.settings import DB_CONFIG
from repositories.products import get_all_products

def get_recommendations(user_id, top_n=6):
    # Загрузка данных из items.csv
    #items_df = pd.DataFrame(get_all_products())

    # Проверка, существуют ли данные о заказах в таблице order_data
    query_orders = """
        SELECT user_id, product_id, quantity
        FROM order_data;
    """

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query_orders)
            orders_data = cur.fetchall()

    if not orders_data:
        raise ValueError("Данные о заказах отсутствуют в таблице order_data.")

    orders_df = pd.DataFrame(orders_data)
    order_matrix = orders_df.pivot_table(index='user_id', columns='product_id', values='quantity', fill_value=0)

    if user_id not in order_matrix.index:
        streamlit.warning(f"Пользователь с ID {user_id} еще не сделал заказов.")
        # raise ValueError(f"Пользователь с ID {user_id} отсутствует в данных заказов.")
    else:
        user_orders = order_matrix.loc[user_id]

        # Находим все продукты, которые пользователь когда-либо покупал
        purchased_items = user_orders[user_orders > 0].index.tolist()

        # Словарь для хранения количества покупок других товаров
        recommendations = defaultdict(int)

        # Проходим по всем пользователям
        for other_user_id, row in order_matrix.iterrows():
            # Если пользователь покупал те же товары
            if any(row[item] > 0 for item in purchased_items):
                # Увеличиваем счетчик для каждого товара
                for item in row.index:
                    if item not in purchased_items:
                        recommendations[item] += row[item]

        # Сортируем товары по количеству покупок и возвращаем топ-N
        recommended_items = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        top_items = [item for item, _ in recommended_items[:top_n]]

        query = """
                SELECT item_id, item_name, price
                FROM products
                WHERE item_id = ANY(%s) AND price IS NOT NULL;
                """
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (top_items,))
                return cur.fetchall()
