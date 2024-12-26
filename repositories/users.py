import psycopg2
import psycopg2.extras
from environment.settings import DB_CONFIG
from pandas import DataFrame


def get_users() -> list[dict]:
    # print("Receiving users")
    query = "SELECT user_id, email FROM users;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()


def get_user(email) -> DataFrame:
    user = get_user_by_email(email)
    result = DataFrame(user)
    return result


def get_users_with_password() -> list[dict]:
    # print("Receiving users")
    query = "SELECT password, email FROM users;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()


def get_user_by_email(user_email) -> list[dict]:
    query = "SELECT user_id, email, balance FROM users WHERE email = %(email)s"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, {"email" : user_email})
            return cur.fetchall()


def update_user(user_email, new_balance) -> float:
    select_query = "SELECT balance FROM users WHERE email = %(email)s"
    update_query = "UPDATE users SET balance = %(new_balance)s WHERE email = %(email)s RETURNING balance"

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Обновляем баланс
            cur.execute(update_query, {"new_balance": new_balance, "email": user_email})
            updated_balance = cur.fetchone()["balance"]

    return updated_balance