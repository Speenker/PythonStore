import streamlit as st
from repositories.recommendations import get_top_items, get_top_items_by_category
from repositories.categories import get_all_categories
from ml.recommendation_person import get_recommendations
from ml.recommendation_person_2 import get_personal_recommendations

def show_recommendations_page():
    st.title("Рекомендации")

    # Получение топ-8 самых популярных товаров
    st.header("Топ-8 самых популярных товаров")
    top_items = get_top_items(limit=8)
    if not top_items:
        st.warning("Нет данных о популярных товарах.")
    else:
        for item in top_items:
            st.write(f"- **{item['item_name']}** — {item['price']:.2f} RUB")

    st.divider()

    # Выбор категории и отображение товаров
    st.header("Топ по категории")
    categories = get_all_categories()

    if not categories:
        st.warning("Категории отсутствуют.")
    else:
        category_options = {category['item_category_name']: category['item_category_id'] for category in categories}
        selected_category_name = st.selectbox("Выберите категорию:", options=category_options.keys())

        # if "show_category_button_clicked" not in st.session_state:
        #     st.session_state.show_category_button_clicked = False

        if f"show_category_items" not in st.session_state:
            st.session_state[f"show_category_items"] = False

        if st.button(
                "Показать топ товаров этой категории",
                key=f"btn_show_category_items"
        ):
            st.session_state[f"show_category_items"] = not st.session_state[f"show_category_items"]

        # if st.button("Показать топ товаров этой категории"):
        #     st.session_state.show_category_button_clicked = True

        if st.session_state[f"show_category_items"]:
            category_id = category_options[selected_category_name]
            category_items = get_top_items_by_category(category_id, limit=10)

            if not category_items:
                st.warning("Нет данных для выбранной категории.")
            else:
                st.subheader(f"Топ товаров для категории '{selected_category_name}'")
                for item in category_items:
                    st.write(f"- **{item['item_name']}** — {item['price']:.2f} RUB")

    st.divider()

    st.header("Персональные рекомендации")

    # if f"show_recs" not in st.session_state:
    #     st.session_state[f"show_recs"] = False
    #
    # if st.button(
    #         "Подобрать товары",
    #         key=f"btn_show_recs"
    # ):
    #     st.session_state[f"show_recs"] = not st.session_state[f"show_recs"]

    if st.button("Подобрать товары"):
        personal_recs = get_recommendations(st.session_state.user["user_id"].item())
        #personal_recs = get_personal_recommendations(st.session_state.user["user_id"].item())
        if not personal_recs:
            st.warning("Нет данных о популярных товарах.")
        else:
            for item in personal_recs:
                st.write(f"- **{item['item_name']}** — {item['price']:.2f} RUB")