import sqlite3 as sq


async def sql_show_item_client(level1, level3):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT row_id, article, catalog_level1, catalog_level2, catalog_level3, name, description, photo1, photo2, price FROM clientgoods WHERE catalog_level1 = '{level1}' AND catalog_level3 = '{level3}' GROUP BY article""").fetchall()
    cur.close()
    return result

async def sql_show_orders_client(user_id):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from orders WHERE user_id = '{user_id}' AND order_status ISNULL OR order_status LIKE 'Подтверждён%'""").fetchall()
    cur.close()
    return result


async def sql_add_order(article, user_id, order_date, order_value, user_email, user_phone, user_address, size):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute('''SELECT COUNT(*) from orders''').fetchone()
    order_id = f'{result[0]}{str(order_date)[14:16]}{str(order_date)[17:19]}{str(user_id)[:4]}'
    result2 = cur.execute(f"""SELECT quantity FROM warehouse WHERE article = '{article}'""").fetchone()
    if result2[0] >= 1:
        cur.execute(
            '''INSERT INTO orders (order_id, article, user_id, order_date, order_value, user_email, user_phone, user_address, size) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (order_id, article, user_id, order_date, order_value, user_email, user_phone, user_address, size,))
        base.commit()
        cur.execute(
            f"""UPDATE warehouse SET (quantity) = quantity-1 WHERE article = '{article}' AND size = '{size}'""")
        base.commit()
        print(f"Заказ {order_id} добавлен в базу")
        cur.close()
        return order_id


async def sql_search1(column):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT {column} FROM clientgoods GROUP BY {column} ORDER BY {column}""").fetchall()
    cur.close()
    return result


async def sql_search2(column1, column2, param):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT {column1} FROM clientgoods WHERE {column2} = '{param}' GROUP BY {column1} ORDER BY {column1}""").fetchall()
    cur.close()
    return result


async def sql_search3(column1, column2, column3, param1, param2):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT {column1} FROM clientgoods WHERE {column2} = '{param1}' AND {column3} = '{param2}' GROUP BY {column1} ORDER BY {column1}""").fetchall()
    cur.close()
    return result


async def sql_search_item(catalog_level1, catalog_level2, size):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT row_id, article, catalog_level1, catalog_level2, catalog_level3, name, description, photo1, photo2, price FROM clientgoods WHERE catalog_level1 = '{catalog_level1}' AND catalog_level2 = '{catalog_level2}' AND size = '{size}' GROUP BY article ORDER BY catalog_level3""").fetchall()
    cur.close()
    return result


async def sql_add_client(first_name, tg_id, phone, e_mail, address):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    cur.execute(
        '''INSERT INTO clients (first_name, tg_id, phone, e_mail, address) VALUES (?, ?, ?, ?, ?)''',
        (first_name, tg_id, phone, e_mail, address,))
    base.commit()
    cur.close()


async def sql_search_client(user_id):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * FROM clients WHERE tg_id = '{user_id}'""").fetchone()
    cur.close()
    return result
