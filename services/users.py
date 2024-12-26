from pandas import DataFrame
import repositories.users
from repositories.users import get_user_by_email
from repositories.users import update_user


def get_users() -> DataFrame:
    users = repositories.users.get_users()
    result = DataFrame(users)
    result = result[["user_id", "email"]]
    return result


def update_balance(email, amount):
    # Получение текущего пользователя по email
    user_list = get_user_by_email(email)
    if not user_list:
        raise ValueError("Пользователь с таким email не найден.")

    user = user_list[0]
    current_balance = user["balance"]
    new_balance = current_balance + amount

    # Обновление баланса в базе данных
    update_user(email, new_balance)
    return new_balance

print("Receiving users")
print(get_users())