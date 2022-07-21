import sqlite3 as sq


def sql_start():
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    if base:
        print("База данных подключена")
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS good(
        row_id INTEGER PRIMARY KEY, 
        article TEXT UNIQUE, 
        catalog_level1 TEXT, 
        catalog_level2 TEXT, 
        catalog_level3 TEXT, 
        name TEXT, 
        description TEXT, 
        photo1 TEXT, 
        photo2 TEXT, 
        price REAL, 
        date_add TEXT, 
        user_id INTEGER)''')
    base.commit()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS orders(
        row_id INTEGER PRIMARY KEY, 
        order_id TEXT UNIQUE, 
        article TEXT, size TEXT, 
        user_id INTEGER, 
        user_email TEXT, 
        user_phone TEXT, 
        user_address TEXT, 
        order_date TEXT, 
        order_value REAL, 
        order_status TEXT)''')
    base.commit()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS warehouse(
        row_id INTEGER PRIMARY KEY, 
        article TEXT, 
        size TEXT, 
        quantity INTEGER, 
        history TEXT)''')
    base.commit()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS clients(
        row_id INTEGER PRIMARY KEY, 
        first_name TEXT, 
        tg_id INTEGER, 
        phone TEXT, 
        e_mail TEXT, 
        address TEXT)''')
    base.commit()
    cur.execute(
        '''CREATE VIEW IF NOT EXISTS clientgoods 
        AS SELECT 
        good.row_id, 
        good.article, 
        good.catalog_level1, 
        good.catalog_level2, 
        good.catalog_level3, 
        good.name, 
        good.description, 
        good.photo1, 
        good.photo2, 
        good.price, 
        warehouse."size", 
        warehouse.quantity 
        FROM good, warehouse 
        WHERE good.article = warehouse.article 
        AND warehouse.quantity >= 1''')
    base.commit()
    backup = sq.connect('Bot_catalog_backup.db')
    with backup:
        base.backup(backup, pages=1)
    print(f'Бэкап базы готов'
          f'\nЕсли испортили базу, то остановите бота, НЕ ЗАПУСКАЙТЕ ПОВТОРНО'
          f'\nПереименуйте "Bot_catalog_backup.db" в "Bot_catalog_database.db" и снова можете запускать бота')
    base.close()
    backup.close()
