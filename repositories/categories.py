import psycopg2
import psycopg2.extras
from environment.settings import DB_CONFIG

# Получение всех категорий
def get_all_categories():
    query = "SELECT item_category_id, item_category_name FROM categories"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()