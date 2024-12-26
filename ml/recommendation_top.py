import numpy as np
import pandas as pd

import os

# Загрузка данных
sales_data = pd.read_csv('../database/sales_train.csv')
items_data = pd.read_csv('../database/items.csv')
categories_data = pd.read_csv('../database/item_categories.csv')

# Объединение данных о продажах с данными о товарах
sales_items = sales_data.merge(items_data, on='item_id', how='left')

# Группировка данных по категориям и товарам, подсчет общего количества продаж
category_sales = sales_items.groupby(['item_category_id', 'item_id']).agg({'item_cnt_day': 'sum'}).reset_index()

# Сортировка по категориям и количеству продаж
category_sales = category_sales.sort_values(['item_category_id', 'item_cnt_day'], ascending=[True, False])

# Получение топ-10 товаров для каждой категории
top_10_items_per_category = category_sales.groupby('item_category_id').head(10)

# Сохранение топ-10 товаров для каждой категории в файл
top_10_items_per_category[['item_category_id', 'item_id']].to_csv('top_10_items_per_category.csv', index=False)

# Получение топ-8 товаров среди всех категорий
top_8_items = category_sales.sort_values('item_cnt_day', ascending=False).head(8)

# Сохранение топ-8 товаров в файл
top_8_items[['item_category_id', 'item_id']].to_csv('top_8_items.csv', index=False)

# Получение самого топового товара каждой категории
top_item_per_category = category_sales.groupby('item_category_id').first().reset_index()

# Сохранение самого топового товара каждой категории в файл
top_item_per_category[['item_category_id', 'item_id']].to_csv('top_item_per_category.csv', index=False)

