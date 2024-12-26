import random
import pandas as pd
import numpy as np
import psycopg2
from environment.settings import DB_CONFIG

def fetch_order_data(db_config):
    """Retrieves order data from the database."""
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT user_id, product_id, quantity FROM order_data;")
                order_data = cur.fetchall()
        return order_data
    except psycopg2.Error as e:
        print(f"Database error in fetch_order_data: {e}")
        return None

def create_order_matrix(order_data, item_ids, items):
    """Creates the order matrix from order data."""
    try:
        order_df = pd.DataFrame(order_data, columns=['user_id', 'product_id', 'quantity'])
        order_df = order_df.astype({'user_id': 'int32', 'product_id': 'int32', 'quantity': 'int32'}) #Explicit type casting

        order_matrix = order_df.pivot_table(index='user_id', columns='product_id', values='quantity', fill_value=0)
        order_matrix = order_matrix.reindex(columns=item_ids, fill_value=0)
        order_matrix.columns = items
        return order_matrix
    except (KeyError, ValueError) as e:
        print(f"Error creating pivot_table: {e}. Check data in order_data.")
        return pd.DataFrame(columns=items, index=np.arange(1, 101)) # Return empty DataFrame on error

def configure_recommendations(user_id, order_matrix, item_ids, items, top_n=5):
    """Generates personalized recommendations."""
    try:
        user_orders = order_matrix.loc[user_id]
        purchased_items = user_orders[user_orders > 0].index.tolist()
        similar_users = order_matrix[order_matrix[purchased_items].sum(axis=1) > 0]
        product_sums = similar_users.sum().sort_values(ascending=False)

        for item in purchased_items:
            if item in product_sums:
                product_sums = product_sums.drop(item)

        top_head = product_sums.head(top_n).index.tolist()
        top_item_ids = [item_ids[items.index(item)] for item in top_head]

        query = """
            SELECT item_id, item_name, price
            FROM products
            WHERE item_id = ANY(%s) AND price IS NOT NULL;
        """
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (top_item_ids,))
                recommendations = cur.fetchall()
        return recommendations
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error processing recommendations: {e}")
        return []
    except psycopg2.Error as e:
        print(f"Database error in configure_recommendations: {e}")
        return []


def get_personal_recommendations(user_id):
    """Gets personalized recommendations for a user."""
    items_df = pd.read_csv('database/items.csv')
    items = items_df['item_name'].tolist()
    item_ids = items_df['item_id'].tolist()
    order_data = fetch_order_data(DB_CONFIG)
    if order_data is None:
        return [] #Handle database error in fetch_order_data

    order_matrix = create_order_matrix(order_data, item_ids, items)
    if order_matrix.empty:
        return [] #Handle error in create_order_matrix

    return configure_recommendations(user_id, order_matrix, item_ids, items)


# import psycopg2
# import psycopg2.extras
# import streamlit
# import pandas as pd
# import numpy as np
# import random
#
# from environment.settings import DB_CONFIG
# #
# # # Function to fetch order data from the database
# def fetch_order_data(db_config):
#     try:
#         with psycopg2.connect(**db_config) as conn:
#             with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
#                 cur.execute("SELECT user_id, product_id, quantity FROM order_data;")
#                 order_data = cur.fetchall()
#         #print(order_data)
#         return order_data
#     except psycopg2.Error as e:
#         print(f"Database error: {e}")
#         return None
#
# # Function to create the order matrix
# # def create_order_matrix(order_data, item_ids, items):
# #     if order_data is None:
# #         return None
# #
# #     order_df = pd.DataFrame(order_data)
# #     order_matrix = order_df.pivot_table(index='user_id', columns='product_id', values='quantity', fill_value=0)
# #     order_matrix = order_matrix.reindex(columns=item_ids, fill_value=0)
# #     order_matrix.columns = items
# #     return order_matrix
#
# def create_order_matrix(order_data, item_ids, items):
#
#     # if order_data.empty:
#     #     return pd.DataFrame(columns=items, index=np.arange(1, 101)) # Возвращаем пустую матрицу, если order_data пуста
#
#     # Создаем DataFrame из order_data, явно указывая типы данных
#     order_df = pd.DataFrame(order_data, columns=['user_id', 'product_id', 'quantity'])
#     order_df['user_id'] = order_df['user_id'].astype(int)
#     order_df['product_id'] = order_df['product_id'].astype(int)
#     order_df['quantity'] = order_df['quantity'].astype(int)
#
#
#     # Обрабатываем возможные ошибки при создании pivot_table
#     try:
#         order_matrix = order_df.pivot_table(index='user_id', columns='product_id', values='quantity', fill_value=0)
#     except KeyError as e:
#         print(f"Ошибка при создании pivot_table: {e}.  Проверьте данные в order_data.")
#         return pd.DataFrame(columns=items, index=np.arange(1, 101)) # Возвращаем пустую матрицу в случае ошибки
#
#     # Заполняем недостающие product_id нулями
#     order_matrix = order_matrix.reindex(columns=item_ids, fill_value=0)
#     order_matrix.columns = items
#     #print(order_matrix)
#     return order_matrix
#
#
# # Function to get personal recommendations
# def configure_recommendations(user_id, order_matrix, item_ids, items, top_n=15):
#     try:
#         # items_df = pd.read_csv('database/items.csv')
#         # items = items_df['item_name'].tolist()
#         # item_ids = items_df['item_id'].tolist()
#         # with psycopg2.connect(**DB_CONFIG) as conn:
#         #     with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
#         #         cur.execute("SELECT user_id, product_id, quantity FROM order_data;")
#         #         order_data = cur.fetchall()
#         #
#         # if order_data is None:
#         #     return None
#         #
#         # order_df = pd.DataFrame(order_data)
#         # order_matrix = order_df.pivot_table(index='user_id', columns='product_id', values='quantity', fill_value=0)
#         # order_matrix = order_matrix.reindex(columns=item_ids, fill_value=0)
#         # order_matrix.columns = items
#
#         # Get user orders
#         user_orders = order_matrix.loc[user_id]
#
#         # Find purchased items
#         purchased_items = user_orders[user_orders > 0].index.tolist()
#
#         # Find similar users
#         similar_users = order_matrix[order_matrix[purchased_items].sum(axis=1) > 0]
#         product_sums = similar_users.sum().sort_values(ascending=False)
#
#         # Exclude purchased items
#         for item in purchased_items:
#             if item in product_sums:
#                 product_sums = product_sums.drop(item)
#
#         # Get top N recommendations
#         top_head = product_sums.head(top_n).index.tolist()
#         #random_top_items = random.sample(list(top_head), 5)# product_sums.head(top_n).index.tolist()
#         top_item_ids = [item_ids[items.index(item)] for item in top_head]
#
#         # Fetch product details from the database
#         query = """
#         SELECT item_id, item_name, price
#         FROM products
#         WHERE item_id = ANY(%s) AND price IS NOT NULL;
#         """
#         with psycopg2.connect(**DB_CONFIG) as conn:
#             with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
#                 cur.execute(query, (top_item_ids,))
#                 recommendations = cur.fetchall()
#         return recommendations
#
#     except (KeyError, IndexError) as e:
#         print(f"Error processing recommendations: {e}")
#         return []
#     except psycopg2.Error as e:
#         print(f"Database error: {e}")
#         return []
#
# def get_personal_recommendations(user_id):
#     items_df = pd.read_csv('database/items.csv')
#     items = items_df['item_name'].tolist()
#     item_ids = items_df['item_id'].tolist()
#     # Fetch order data from the database
#     order_data = fetch_order_data(DB_CONFIG)
#     # print(order_data)
#     # Create the order matrix
#     order_matrix = create_order_matrix(order_data, item_ids, items)
#
#     return configure_recommendations(user_id, order_matrix, item_ids, items)
#
#




#
# import pandas as pd
# import numpy as np
# import psycopg2
# import psycopg2.extras
# import streamlit
#
# from environment.settings import DB_CONFIG
#
# # Загрузка данных из items.csv
# items_df = pd.read_csv('database/items.csv')
# items = items_df['item_name'].tolist()
# item_ids = items_df['item_id'].tolist()
#
# # Генерация случайных данных
# np.random.seed(42)
# user_ids = range(1, 101)
# #data = {user_id: np.random.randint(0, 10, len(items)) for user_id in user_ids}
# data = fetch_order_data(DB_CONFIG)
# # Создание DataFrame
# order_matrix = pd.DataFrame(data, index=items).T
#
#
# # Функция для получения персональных рекомендаций
# def get_personal_recommendations(user_id, top_n=10):
#     # Получаем заказы пользователя
#     user_orders = order_matrix.loc[user_id]
#
#     # Находим товары, которые пользователь заказывал
#     purchased_items = user_orders[user_orders > 0].index.tolist()
#
#     # Суммируем заказы по другим пользователям
#     similar_users = order_matrix[order_matrix[purchased_items].sum(axis=1) > 0]
#     product_sums = similar_users.sum().sort_values(ascending=False)
#
#     # Исключаем уже купленные товары
#     for item in purchased_items:
#         if item in product_sums:
#             product_sums = product_sums.drop(item)
#
#     # Получаем топ-N рекомендаций
#     top_items = product_sums.head(top_n).index.tolist()
#     top_item_ids = [item_ids[items.index(item)] for item in top_items]
#
#     query = """
#             SELECT item_id, item_name, price
#             FROM products
#             WHERE item_id = ANY(%s) AND price IS NOT NULL;
#             """
#     with psycopg2.connect(**DB_CONFIG) as conn:
#         with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
#             cur.execute(query, (top_item_ids,))
#             return cur.fetchall()
    # Получаем ID и имена товаров
    #
    # return top_item_ids, top_items