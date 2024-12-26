import psycopg2
import psycopg2.extras
from environment.settings import DB_CONFIG

def predict_next_month_revenue():
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT SUM(mr.item_cnt_month * p.price)
                    FROM month_revenue mr
                    JOIN products p ON mr.item_id = p.item_id;
                """
                cur.execute(query)
                result = cur.fetchone()
                return result[0] if result else 0.0

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при выполнении запроса:", error)
        return None