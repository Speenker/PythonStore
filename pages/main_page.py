import streamlit as st
from repositories.products import get_all_products
from repositories.categories import get_all_categories

def show_main_page():
    st.title("Каталог товаров")

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