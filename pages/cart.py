import time

import streamlit as st

import services.orders
from repositories.users import get_user_by_email
from repositories.orders import create_order
from services.users import update_balance
from repositories.products import get_all_products
from repositories.categories import get_all_categories
from services.orders import print_check

def show_cart_page(email):
    st.title("Покупки")

    # Получение данных о пользователе
    user_list = get_user_by_email(email)
    if not user_list:
        st.error("Пользователь не найден.")
        return

    user = user_list[0]

    # Получение списка категорий
    categories = get_all_categories()
    if not categories:
        st.warning("Нет доступных категорий.")
        return

    category_names = [category["item_category_name"] for category in categories]
    selected_category_name = st.selectbox("Выберите категорию", ["Все категории"] + category_names)

    # Получение списка продуктов, отфильтрованных по категории
    products = get_all_products()
    if selected_category_name != "Все категории":
        selected_category = next((c for c in categories if c["item_category_name"] == selected_category_name), None)
        if not selected_category:
            st.error("Ошибка при получении информации о категории.")
            return

        category_id = selected_category["item_category_id"]
        products = [p for p in products if p["item_category_id"] == category_id]

    if not products:
        st.warning("В этой категории пока нет товаров.")
        return

    # Поле поиска товара
    search_query = st.text_input("Поиск товара", placeholder="Название товара")
    if search_query:
        products = [p for p in products if search_query.lower() in p["item_name"].lower()]

    if not products:
        st.warning("Товары не найдены.")
        return

    # Выбор товара из выпадающего списка
    product_names = [product["item_name"] for product in products]
    selected_product_name = st.selectbox("Выберите товар", product_names)

    # Получение данных о выбранном продукте
    selected_product = next((p for p in products if p["item_name"] == selected_product_name), None)
    if not selected_product:
        st.error("Ошибка при получении информации о товаре.")
        return

    # Отображение основной информации
    st.write(f"### {selected_product['item_name']}")
    st.write(f"**Цена:** {selected_product['price']:.2f} RUB")

    # Инициализация корзины в session_state
    if "cart" not in st.session_state:
        st.session_state["cart"] = []

    # Создание выпадающего списка с товарами
    # product_options = [
    #     f"{product['item_name']} — {product['price']} $)"
    #     for product in products
    # ]
    # selected_product = st.selectbox("Выберите товар", product_options, key="product_select")
    # selected_product_id = next(
    #     (product["item_id"] for product in products if product["item_name"] in selected_product), None
    # )

    # Кнопка добавления товара в корзину
    if st.button("Добавить в корзину"):
        product = next((p for p in products if p["item_name"] == selected_product_name), None)

        st.session_state["cart"].append(product)
        st.success(f"Товар '{product['item_name']}' добавлен в корзину.")

    st.divider()

    # Отображение корзины
    st.write("### Корзина")
    if st.session_state["cart"]:
        total_price = sum(item["price"] for item in st.session_state["cart"])
        cart_items = {}

        for item in st.session_state["cart"]:
            if item["item_id"] in cart_items:
                cart_items[item["item_id"]]["quantity"] += 1
            else:
                cart_items[item["item_id"]] = {
                    "item_name": item["item_name"],
                    "price": item["price"],
                    "quantity": 1,
                }

        for product_id, details in cart_items.items():
            st.write(f"- {details['item_name']} ({details['quantity']} шт.) — {details['price'] * details['quantity']:.2f} RUB")

        st.write(f"**Общая сумма:** {total_price:.2f} RUB")

        # Кнопка формирования заказа
        if st.button("Сформировать заказ"):
            if user["balance"] >= total_price:
                # Обновление баланса пользователя
                update_balance(email, -total_price)

                # Добавление заказа в базу данных
                order_id = create_order(user["user_id"], cart_items.items()) #st.session_state["cart"])
                print_check(order_id)

                # Очистка корзины
                st.session_state["cart"] = []

                st.success("Заказ успешно оформлен!")
                # tmp = services.orders.get_order_items(order_id)
                time.sleep(2.0)
                st.rerun()
            else:
                st.error("Недостаточно средств на балансе.")

        # Кнопка для очистки корзины
        if st.button("Очистить корзину"):
            st.session_state["cart"] = []
            st.success("Корзина очищена!")
            time.sleep(1.5)
            st.rerun()
    else:
        st.write("Корзина пуста.")

