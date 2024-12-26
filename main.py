import time

import streamlit
import pandas as pd

from pages.admin_panel import show_admin_panel
from pages.cart import show_cart_page
from pages.main_page import show_main_page
from pages.profile import show_profile_page
from pages.recommendations import show_recommendations_page
from services.auth import Authotize
import services.users
import services.regist
import repositories.admin
import pages

auth = Authotize()
users = services.users.get_users()
registr = services.regist.Registration()


def login():
    streamlit.title("Авторизация")
    streamlit.write("Введите почту и пароль:")

    email = streamlit.text_input("Почта")
    password = streamlit.text_input("Пароль", type="password")
    if streamlit.button("Войти"):
        if auth.auth(email, password):
            streamlit.session_state["authenticated"] = True
            streamlit.session_state["username"] = email
            streamlit.success(f"Добро пожаловать, {email}!")
            streamlit.session_state.user = repositories.users.get_user(email)
            # streamlit.session_state["email"] = email
            streamlit.session_state["admin"] = repositories.admin.get_admins(
                streamlit.session_state.user["user_id"].item())
            if streamlit.session_state["admin"]:
                print("You are logged as ADMIN")
            time.sleep(2.0)
            streamlit.rerun()
        else:
            streamlit.error("Неверная почта или пароль!")



def register():
    streamlit.title("Регистрация")
    streamlit.write("Введите почту")
    email = streamlit.text_input("Почта")
    streamlit.write("Введите пароль")
    password = streamlit.text_input("Пароль", type="password")
    streamlit.write("Подтвердите пароль")
    second_password = streamlit.text_input("Подтверждение пароля", type="password")

    if streamlit.button("Зарегистрироваться"):
        if (not (email) or not (password) or not (second_password)):
            streamlit.error("Введите требуемые значения!")
        else:
            if (password != second_password):
                streamlit.error("Пароли не совпадают!")
            else:
                if users["email"].isin([email]).any():
                    streamlit.error("Данная почта уже зарегистрирована!")
                else:
                    streamlit.success("Успешная регистрация")
                    streamlit.session_state["authenticated"] = True
                    # user = pd.DataFrame({"nickname" : nickname, "email" : email, "password" : password})
                    user_id = registr.registr(pd.DataFrame({"email": [email], "password": [password]}))
                    # user["user_id"] = user_id
                    user = pd.DataFrame({"user_id": [user_id], "email": [email], "password": [password]})
                    streamlit.session_state.user = user
                    streamlit.rerun()


def main():
    if not streamlit.session_state["authenticated"]:
        pg = streamlit.radio("Войдите или зарегистрируйтесь", ["Вход", "Регистрация", "Основная"])
        if pg == "Вход":
            login()
        elif pg == "Регистрация":
            register()
        elif pg == "Основная":
            show_main_page()

    else:
        # print(streamlit.session_state.user["user_id"].item())
        email = streamlit.session_state.user["email"].item()

        if streamlit.session_state["admin"]:
            page = streamlit.sidebar.radio(
                "Перейти к странице",
                ["Основная", "Профиль", "Корзина", "Рекомендации", "Панель Администратора"],
            )
            # email = streamlit.session_state["email"]

            if page == "Профиль":
                show_profile_page(email)

            elif page == "Корзина":
                show_cart_page(email)

            elif page == "Основная":
                show_main_page()

            elif page == "Рекомендации":
                show_recommendations_page()

            elif page == "Панель Администратора":
                show_admin_panel()

        else:
            page = streamlit.sidebar.radio(
                "Перейти к странице",
                ["Основная", "Профиль", "Корзина", "Рекомендации"],
            )

            if page == "Профиль":
                show_profile_page(email)

            elif page == "Корзина":
                show_cart_page(email)

            elif page == "Основная":
                show_main_page()

            elif page == "Рекомендации":
                show_recommendations_page()


if "authenticated" not in streamlit.session_state:
    streamlit.session_state["authenticated"] = False

if "admin" not in streamlit.session_state:
    streamlit.session_state["admin"] = False

if "user" not in streamlit.session_state:
    streamlit.session_state.user = pd.DataFrame(
        columns=["user_id", "email", "balance"]
    )

if __name__ == "__main__":
    main()