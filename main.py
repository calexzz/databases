import sqlite3
import pandas as pd
from datetime import datetime

file_path = 'data.xls'

trade_df = pd.read_excel(file_path, sheet_name="Движение товаров")
product_df = pd.read_excel(file_path, sheet_name="Товар")
shop_df = pd.read_excel(file_path, sheet_name="Магазин")

trade_df['Дата'] = pd.to_datetime(trade_df['Дата']).dt.strftime('%Y-%m-%d')

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

trade_df.to_sql('trade', conn, index=False)
product_df.to_sql('product', conn, index=False)
shop_df.to_sql('shop', conn, index=False)

cursor.execute("""
    SELECT SUM(t."Количество упаковок, шт" * p."Цена за упаковку")
    FROM trade t 
    JOIN product p ON t."Артикул" = p."Артикул"
    JOIN shop s ON t."ID магазина" = s."ID магазина"
    WHERE p."Наименование товара" LIKE '%Говядина%'
        AND s."Район" LIKE '%Центральный%'
        AND t."Тип операции" = 'Поступление'
        AND t."Дата" BETWEEN '2024-10-10' AND '2024-10-15'
""")

result = cursor.fetchone()[0]
print(result)

conn.close()