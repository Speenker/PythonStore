import psycopg2
import psycopg2.extras
from environment.settings import DB_CONFIG

def get_admins(admin_id) -> bool:
    query = """SELECT user_id FROM users WHERE user_id = %(admin_id)s AND role = 'admin'"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"admin_id": admin_id})
            return (cur.fetchone() != None)

def update_order_status(order_id, new_status):
    query = "UPDATE orders SET status = %s WHERE order_id = %s"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (new_status, order_id))
            conn.commit()