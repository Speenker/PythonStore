import psycopg2
from psycopg2.extras import RealDictCursor
from environment.settings import DB_CONFIG

def get_top_items(limit=8):
    query = """
        SELECT p.item_name, p.price
        FROM recommend_items r
        JOIN products p ON r.item_id = p.item_id
        LIMIT %s
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (limit,))
            return cur.fetchall()

def get_top_items_by_category(category_id, limit=10):
    query = """
        SELECT p.item_name, p.price
        FROM recommend_items_by_category r
        JOIN products p ON r.item_id = p.item_id
        WHERE r.item_category_id = %s
        LIMIT %s
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (category_id, limit))
            return cur.fetchall()