import sqlite3 as sq
from bot_create import admins


async def sql_add_goods(article, catalog_level1, catalog_level2, catalog_level3, name, description, photo1, photo2,
                        price, date_add, user_id):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    cur.execute(
        '''INSERT INTO good 
        (article, 
        catalog_level1, 
        catalog_level2, 
        catalog_level3, 
        name, 
        description, 
        photo1, 
        photo2, 
        price, 
        date_add, 
        user_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            article, catalog_level1, catalog_level2, catalog_level3, name, description, photo1, photo2, price,
            date_add,
            user_id))
    base.commit()
    print(f"Товар {article} добавлен в базу")
    cur.close()


async def sql_add_item_warehouse(article, size, quantity, date, user_id):
    history = f'{date};{user_id};{quantity}'
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from warehouse WHERE article = '{article}' AND size = '{size}'""").fetchone()
    if result:
        data = result[4]
        history_prev = data.split(',')[-1]
        history_new = f'{history_prev},{history}'
        cur.execute(
            f"""UPDATE warehouse SET (quantity, history) = (?, ?) WHERE article = '{article}' AND size = '{size}'""",
            (quantity, history_new,))
        base.commit()
    else:
        cur.execute(
            '''INSERT INTO warehouse (article, size, quantity, history) VALUES (?, ?, ?, ?)''',
            (article, size, quantity, history,))
        base.commit()
    print(f"Количество {article} размер {size} изменено на {quantity}")
    cur.close()


async def sql_delete_item(article):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * FROM good WHERE article = '{article}'""").fetchone()
    cur.execute(
        f"""DELETE FROM good WHERE article = '{article}'""")
    base.commit()
    cur.execute(
        f"""DELETE FROM warehouse WHERE article = '{article}'""")
    base.commit()
    cur.close()
    print(f"Товар {article} удалён из базы")
    return result


async def sql_edit_item(article, column, new_data, date, user_id):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    cur.execute(
        f"""UPDATE good SET ({column}, date_add, user_id) = (?, ?, ?) WHERE article = '{article}'""",
        (new_data, date, user_id,))
    base.commit()
    cur.close()
    print(f"Товар {article} изменён")


async def sql_order_cancel(order_id, user_id):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from orders WHERE order_id = '{order_id}'""").fetchone()
    if 'Подтверждён' in str(result[10]):
        if str(user_id) in admins:
            cur.execute(
                f"""DELETE FROM orders WHERE order_id = '{order_id}' """)
            base.commit()
            cur.execute(
                f"""UPDATE warehouse SET (quantity) = quantity+1 
                WHERE article = '{result[2]}' AND size = '{result[3]}'""")
            base.commit()
            cur.close()
            print(f"Заказ {order_id} отменён администратором")
            feedback = f'Заказ {order_id} отменён администратором.'
            return feedback, result
        else:
            feedback = f'Этот заказ можно отменить только через администратора!'
            cur.close()
            return feedback, result
    else:
        cur.execute(
            f"""DELETE FROM orders WHERE order_id = '{order_id}' """)
        base.commit()
        cur.execute(
            f"""UPDATE warehouse SET (quantity) = quantity+1 WHERE article = '{result[2]}' AND size = '{result[3]}'""")
        base.commit()
        cur.close()
        print(f"Заказ {order_id} отменён пользователем")
        feedback = f'Заказ {order_id} отменён.'
        return feedback, result


async def sql_order_approve(order_id, admin_id):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from orders WHERE order_id = '{order_id}'""").fetchone()
    if result:
        if str(admin_id) in admins:
            cur.execute(
                f"""UPDATE orders SET order_status = 'Подтверждён {admin_id}' WHERE order_id = '{order_id}' """)
            base.commit()
            cur.close()
            print(f"Заказ {order_id} подтверждён администратором")
        else:
            cur.close()
            print(f"Для подтверждения заказа нужны права администратора")
        return result


async def sql_order_ready(order_id, admin_id):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from orders WHERE order_id = '{order_id}'""").fetchone()
    if result:
        if str(admin_id) in admins:
            cur.execute(
                f"""UPDATE orders SET order_status = 'Исполнен {admin_id}' WHERE order_id = '{order_id}' """)
            base.commit()
            cur.close()
            print(f"Заказ {order_id} исполнен администратором")
        else:
            cur.close()
            print(f"Для подтверждения статуса нужны права администратора")
        return result


async def sql_list_orders(param):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    if param == "new":
        result = cur.execute(f"""SELECT * FROM orders 
        WHERE order_status ISNULL 
        ORDER BY user_phone""").fetchall()
        cur.close()
        return result
    elif param == "app":
        result = cur.execute(f"""SELECT * FROM orders 
        WHERE order_status 
        LIKE 'Подтверждён%' 
        ORDER BY user_phone""").fetchall()
        cur.close()
        return result
    elif param == "rdy":
        result = cur.execute(f"""SELECT * FROM orders 
        WHERE order_status LIKE 'Исполнен%' 
        ORDER BY user_phone""").fetchall()
        cur.close()
        return result


async def sql_find_order(order_id):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from orders WHERE order_id = '{order_id}'""").fetchone()
    cur.close()
    return result


async def sql_make_excel(table_name, column, param):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    column_name = [i[1] for i in cur.execute(f"""PRAGMA table_info("{table_name}")""").fetchall()]
    data = cur.execute(
        f"""SELECT * from {table_name} WHERE {column} LIKE '{param}%'""").fetchall()
    cur.close()
    return column_name, data
