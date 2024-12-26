import psycopg2
import psycopg2.extras
from environment.settings import DB_CONFIG


# Получение всех продуктов
def get_all_products():
    query = "SELECT item_id, item_name, item_category_id, price FROM products WHERE price IS NOT NULL"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()