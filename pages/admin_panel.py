import time
import streamlit as st
from repositories.admin import update_order_status
from repositories.products import get_all_products
from repositories.orders import get_all_orders
from services.orders import get_order_items
from repositories.ml import predict_next_month_revenue

def show_admin_panel():
    st.title("Панель администратора 🧑‍💻")

    # Раздел для управления статусами заказов
    st.header("Управление статусами заказов")
    orders = get_all_orders()

    # Фильтрация заказов, исключая Completed
    pending_or_shipped_orders = [order for order in orders if order["status"] != "Completed"]

    if not pending_or_shipped_orders:
        st.warning("Нет заказов для обработки.")
    else:
        order_options = {f"Заказ #{order['order_id']} (Текущий статус: {order['status']})": order for order in
                         pending_or_shipped_orders}
        selected_order_name = st.selectbox("Выберите заказ для изменения статуса:", options=order_options.keys())
        selected_order = order_options[selected_order_name]

        new_status = st.selectbox(
            f"Изменить статус заказа #{selected_order['order_id']}:",
            options=["Pending", "Shipped", "Completed"],
            index=["Pending", "Shipped", "Completed"].index(selected_order["status"]),
            key=f"update_status_{selected_order['order_id']}"
        )

        if st.button("Обновить статус заказа"):
            update_order_status(selected_order["order_id"], new_status)
            st.success(f"Статус заказа #{selected_order['order_id']} обновлен на '{new_status}'.")
            time.sleep(1.5)
            st.rerun()

        if f"items_admin" not in st.session_state:
            st.session_state[f"items_admin"] = False

        if st.button(
                "Показать содержимое заказа",
                key=f"btn_items_admin"
        ):
            st.session_state[f"items_admin"] = not st.session_state[f"items_admin"]

        if st.session_state[f"items_admin"]:
            order_items = get_order_items(selected_order["order_id"])

            if not order_items:
                st.info("Заказ не содержит товаров.")
            else:
                st.write("### Содержимое заказа:")
                for item in order_items:
                    st.write(f"- **{item['item_name']}**: {item['quantity']} шт. — {item['price']:.2f} RUB")

    st.divider()

    st.header("Прогнозируемая выручка")
    month_revenue = predict_next_month_revenue()
    st.write(f"Выручка за следующий месяц: {month_revenue:.2f} RUB")