import random

import pandas as pd
import numpy as np
import psycopg2
from environment.settings import DB_CONFIG

# Load item data from CSV
items_df = pd.read_csv('database/items.csv')
items = items_df['item_name'].tolist()
item_ids = items_df['item_id'].tolist()

# Generate random order data
np.random.seed(42)
user_ids = range(20, 101)
items_sample = random.sample(items, 5)
data = {user_id: np.random.randint(0, 10, len(items_sample)) for user_id in user_ids}
order_matrix = pd.DataFrame(data, index=items_sample).T

# Convert order matrix to long format for database insertion
order_data = []
for user_id, row in order_matrix.iterrows():
    for item_name, quantity in row.items():
        if quantity > 0:  # Only include orders with quantity > 0
            item_id = item_ids[items.index(item_name)]
            order_data.append((user_id, item_id, quantity))

# Insert data into the database
try:
    with psycopg2.connect(**DB_CONFIG) as conn:
        cur = conn.cursor()
        # Insert the generated data
        insert_query = """
            INSERT INTO order_data (user_id, product_id, quantity)
            VALUES (%s, %s, %s);
        """
        cur.executemany(insert_query, order_data)
        conn.commit()
        print("Data inserted successfully!")
except psycopg2.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
