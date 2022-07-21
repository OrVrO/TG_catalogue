import sqlite3 as sq


async def sql_show_menu1():
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute("""SELECT catalog_level1 from good GROUP BY catalog_level1""").fetchall()
    cur.close()
    return result


async def sql_show_menu2(level1):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(f"""SELECT catalog_level2 from good WHERE catalog_level1 = (?) GROUP BY catalog_level2""",
                         (level1,)).fetchall()
    cur.close()
    return result


async def sql_show_menu3(level1, level2):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT catalog_level3 from good WHERE catalog_level1 = '{level1}' AND catalog_level2 = '{level2}' GROUP BY catalog_level3""").fetchall()
    cur.close()
    return result


async def sql_show_item(level1, level3):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from good WHERE catalog_level1 = '{level1}' AND catalog_level3 = '{level3}'""").fetchall()
    cur.close()
    return result


async def sql_find_article_good(article):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from good WHERE article = '{article}'""").fetchone()
    cur.close()
    return result


async def sql_find_article_warehouse(article):
    base = sq.connect('Bot_catalog_database.db')
    cur = base.cursor()
    result = cur.execute(
        f"""SELECT * from warehouse WHERE article = '{article}'""").fetchall()
    cur.close()
    return result
