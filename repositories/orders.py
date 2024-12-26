import psycopg2
from psycopg2.extras import RealDictCursor
from environment.settings import DB_CONFIG
from services.orders import print_check
import pandas as pd

def get_all_orders():
    query = "SELECT order_id, status FROM orders"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

def get_user_orders(user_id):
    query = """
        SELECT 
            order_id, 
            status, 
            total_price, 
            order_date
        FROM orders
        WHERE user_id = %s
        ORDER BY order_date DESC
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (user_id,))
            return cur.fetchall()

def get_order_items(order_id): #-> list[dict]:
    query = """
        SELECT 
            p.item_name,
            oi.quantity,
            p.price
        FROM order_items oi
        JOIN products p ON oi.item_id = p.item_id
        WHERE oi.order_id = %s
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (order_id,))
            return cur.fetchall()

def create_order(user_id, cart):
    query_insert_order = """
        INSERT INTO orders (user_id, total_price, order_date, status)
        VALUES (%s, %s, NOW(), 'Pending')
        RETURNING order_id
    """
    query_insert_order_items = """
        INSERT INTO order_items (order_id, item_id, quantity)
        VALUES (%s, %s, %s)
    """
    query_insert_order_data = """
        INSERT INTO order_data (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Рассчитываем общую стоимость заказа с учетом количества
                total_price = sum(
                    item_details["price"] * item_details["quantity"] for item_id, item_details in cart)

                # Вставляем запись о заказе
                cur.execute(query_insert_order, (user_id, total_price))
                order_id = cur.fetchone()[0]

                # Обновляем таблицу `order_items` и уменьшаем количество на складе
                for item_id, item_details in cart:
                    product_id = item_id
                    quantity = item_details["quantity"]

                    # Добавление в order_items
                    cur.execute(query_insert_order_items, (order_id, product_id, quantity))
                    cur.execute(query_insert_order_data, (user_id, product_id, quantity))

                # # Рассчитываем общую стоимость заказа
                # total_price = sum(item["price"] for item in cart)
                #
                # # Вставляем запись о заказе
                # cur.execute(query_insert_order, (user_id, total_price))
                # order_id = cur.fetchone()[0]
                #
                # # Обновляем таблицу `order_items` и уменьшаем количество на складе
                # for item in cart:
                #     product_id = item["item_id"]
                #     item_details = cart.get("item_id")
                #     quantity = item_details["quantity"] if item_details else 0
                #     # quantity = item["item_id"]["quantity"]  # В корзине учитывается каждое добавление как одна единица товара
                #
                #     # Добавление в order_items
                #     cur.execute(query_insert_order_items, (order_id, product_id, quantity))
                #     cur.execute(query_insert_order_data, (user_id, product_id, quantity))

                #print_check(order_id)

                # Подтверждаем транзакцию
                conn.commit()
                return order_id

    except Exception as e:
        conn.rollback()
        raise e

# def create_order(user_id, cart):
#     items_df = pd.read_csv('database/items.csv')
#     query_insert_order = """
#         INSERT INTO orders (user_id, total_price, order_date, status)
#         VALUES (%s, %s, NOW(), 'Pending')
#         RETURNING order_id;
#     """
#     query_insert_order_items = """
#         INSERT INTO order_items (order_id, item_id, quantity)
#         VALUES (%s, %s, %s);
#     """
#     query_update_order_data = """
#         UPDATE order_data
#         SET quantity = quantity + %s
#         WHERE user_id = %s AND product_id = %s;
#     """
#     query_insert_order_data = """
#         INSERT INTO order_data (user_id, product_id, quantity)
#         VALUES (%s, %s, %s);
#     """
#     query_check_user_orders = """
#         SELECT product_id
#         FROM order_data
#         WHERE user_id = %s;
#     """
#
#     try:
#         with psycopg2.connect(**DB_CONFIG) as conn:
#             with conn.cursor() as cur:
#                 total_price = sum(item_details["price"] * item_details["quantity"] for item_id, item_details in cart)
#                 cur.execute(query_insert_order, (user_id, total_price))
#                 order_id = cur.fetchone()[0]
#
#                 for item_id, item_details in cart:
#                     cur.execute(query_insert_order_items, (order_id, item_id, item_details["quantity"]))
#
#                 # Проверяем, есть ли у пользователя заказы
#                 cur.execute(query_check_user_orders, (user_id,))
#                 existing_product_ids = {row[0] for row in cur.fetchall()}
#                 print(existing_product_ids)
#
#                 item_ids = items_df['item_id'].tolist()
#                 for item_id in item_ids:
#                     for purchased_item_id, item_details in cart:
#                         #quantity = item_details["quantity"]# if (item_id, item_details) in cart else 0
#                         if purchased_item_id == item_id:
#                             quantity = item_details["quantity"]
#                             if item_id in existing_product_ids:
#                                 cur.execute(query_update_order_data, (quantity, user_id, item_id))
#                                 print(f"{item_id} added")
#                             else:
#                                 cur.execute(query_insert_order_data, (user_id, item_id, quantity))
#                                 print(f"{item_id} processed")
#
#
#                 conn.commit()
#                 return order_id
#     except Exception as e:
#         conn.rollback()
#         raise e
