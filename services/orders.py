from pandas import DataFrame
import repositories.orders
import os

def print_check(order_id):
    order = repositories.orders.get_order_items(order_id)
    result = DataFrame(order)
    result = result[["item_name", "price", "quantity"]]

    # Получаем абсолютный путь к текущему файлу (get_order_items.py)
    current_file_path = os.path.abspath(__file__)

    # Получаем путь к директории services
    services_dir = os.path.dirname(current_file_path)

    # Переходим на уровень выше от services
    parent_dir = os.path.dirname(services_dir)

    # Создаем путь к директории чеков
    checks_dir = os.path.join(parent_dir, "checks")

    # Создаем директорию, если её нет
    os.makedirs(checks_dir, exist_ok=True)

    # Формируем имя файла
    filename = os.path.join(checks_dir, f"order_{order_id}.txt")

    # Выводим в консоль
    print(f"Order N{order_id}")
    print(result)

    # Выводим в файл
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Order N{order_id}\n")
        f.write(result.to_string(index=False))


def get_order_items(order_id):
    order = repositories.orders.get_order_items(order_id)
    result = DataFrame(order)
    result = result[["item_name" ,"price", "quantity"]]
    print(f"Order N{order_id}")
    print(result)
    return order
