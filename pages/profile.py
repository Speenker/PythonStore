import time
import streamlit as st
from services.users import update_balance
from repositories.users import get_user_by_email
from repositories.orders import get_user_orders, get_order_items

def show_profile_page(email):
    st.title("Ваш профиль")

    # Получение информации о текущем пользователе
    user_list = get_user_by_email(email)
    if not user_list:
        st.error("Пользователь не найден.")
        return

    # Берем первого (и единственного) пользователя из списка
    user = user_list[0]

    st.write(f"**Email:** {user['email']}")
    # st.write(f"**Баланс:** {user['balance']} $")
    st.write(f"**Баланс:** {user['balance']:.2f} RUB")

    # Форма для пополнения баланса
    st.write("### Пополнение баланса")
    add_balance = st.number_input("Введите сумму", min_value=0.0, step=10.0)

    if st.button("Пополнить баланс"):
        if add_balance > 0:
            new_balance = update_balance(user["email"], add_balance)
            st.success(f"Баланс успешно пополнен. Новый баланс: {new_balance}")
            time.sleep(2.0)
            st.rerun()
        else:
            st.warning("Введите положительную сумму!")

    st.divider()

    # Раздел для отображения заказов пользователя
    st.write("### Ваши заказы")
    user_orders = get_user_orders(user["user_id"])

    if not user_orders:
        st.info("Вы еще не сделали ни одного заказа.")
    else:
        # Формируем выпадающий список с заказами
        order_options = {f"Заказ #{order['order_id']} - {order['status']} ({order['order_date'].strftime("%Y-%m-%d %H:%M")})": order for order in user_orders}
        selected_order_name = st.selectbox("Выберите заказ для просмотра:", options=order_options.keys())
        selected_order = order_options[selected_order_name]

        if f"items" not in st.session_state:
            st.session_state[f"items"] = False

        if st.button(
                "Показать содержимое заказа",
                key=f"btn_items"
        ):
            st.session_state[f"items"] = not st.session_state[f"items"]

        if st.session_state[f"items"]:
            order_items = get_order_items(selected_order["order_id"])

            if not order_items:
                st.warning("Содержимое заказа отсутствует.")
            else:
                st.write(f"### Содержимое заказа #{selected_order['order_id']}")
                for item in order_items:
                    st.write(f"- **{item['item_name']}**: {item['quantity']} шт. — {item['price']:.2f} RUB")