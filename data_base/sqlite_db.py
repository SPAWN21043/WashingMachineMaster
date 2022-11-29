import sqlite3 as sq


def sql_start():
    global base
    global cur

    base = sq.connect('base_master')
    cur = base.cursor()

    if base:
        print('Подключение к базе данных успешное!')

    # Создание таблиц

    cur.execute(
        # Таблица пользователя
        """
        CREATE TABLE IF NOT EXISTS profile(
        user_id INTEGER,
        user_name TEXT,
        last_name TEXT,
        first_name TEXT
        );
        """
    )
    base.commit()

    cur.execute(
        # Таблица категорий
        """
        CREATE TABLE IF NOT EXISTS category(
        id_cat INTEGER PRIMARY KEY AUTOINCREMENT,
        name_cat TEXT
        );
        """
    )
    base.commit()

    cur.execute(
        #
        """
        CREATE TABLE IF NOT EXISTS manufacturing(
        id_manuf INTEGER PRIMARY KEY AUTOINCREMENT,
        name_manuf TEXT
        );
        """
    )
    base.commit()

    cur.execute(
        # Таблица продукта
        """
        CREATE TABLE IF NOT EXISTS product(
        id_product INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        manufacturer_id INTEGER,
        img TEXT,
        name_product TEXT,
        description TEXT,
        in_stock INTEGER,
        code TEXT,
        condition_p TEXT,
        price INTEGER,
        FOREIGN KEY (category_id) REFERENCES category(id_cat),
        FOREIGN KEY (manufacturer_id) REFERENCES manufacturing(id_manuf)
        );
        """
    )
    base.commit()

    cur.execute(
        # Таблица корзины
        """
        CREATE TABLE IF NOT EXISTS basket(
        id_basket INTEGER PRIMARY KEY, 
        id_user INTEGER,
        quantity INTEGER,
        product_id INTEGER,
        price INTEGER
        );
        """
    )
    base.commit()

    cur.execute(
        # Таблица заказа
        """
        CREATE TABLE IF NOT EXISTS orders(
        id_order INTEGER PRIMARY KEY,
        id_user INTEGER,
        order_client TEXT,
        phone_client TEXT
        );
        """
    )
    base.commit()

    cur.execute(
        # Таблица Администраторов
        """
        CREATE TABLE IF NOT EXISTS admins(
        id_admin INTEGER
        );
        """
    )


async def search_product_cancel(name):
    pusto = []
    read_orders = cur.execute('SELECT id_product, in_stock FROM product WHERE name_product==?', (name,)).fetchone()
    if read_orders == pusto:
        return None
    else:
        return read_orders


async def delete_order_admin(id_order):
    cur.execute('DELETE FROM orders WHERE id_order==?', (id_order,))
    base.commit()


async def read_admin_orders():
    pusto = []
    read_orders = cur.execute('SELECT * FROM orders').fetchall()
    if read_orders == pusto:
        return None
    else:
        return read_orders


async def read_user_orders(id_user):
    pusto = []
    read_orders = cur.execute('SELECT * FROM orders WHERE id_user==?', (id_user,)).fetchall()
    if read_orders == pusto:
        return None
    else:
        return read_orders


async def search_admin_orders(id_order):
    pusto = []
    read_orders = cur.execute('SELECT * FROM orders WHERE id_order==?', (id_order,)).fetchone()
    if read_orders == pusto:
        return None
    else:
        return read_orders


async def delete_basket_user(id_user):
    cur.execute('DELETE FROM basket WHERE id_user==?', (id_user,))
    base.commit()


async def sql_add_orders(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO orders ('
                    'id_user, order_client, phone_client) VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_issue_basket(id_user):
    rows = cur.execute('SELECT * FROM basket WHERE id_user==?', (id_user,))
    issue_basket = []
    for row in rows:
        issue_basket.append({
            'qt': row[2],
            'product': row[3],
            'sum': row[4]
        })
    return issue_basket


async def search_price_product(product_id):
    return cur.execute('SELECT price FROM product WHERE id_product ==?', (product_id,)).fetchone()


async def search_qt_basket(id_user, product_id):
    return cur.execute('SELECT quantity FROM basket WHERE id_user ==? and product_id ==?', (id_user, product_id,)).fetchone()


async def delete_basket(id_basket, id_user):
    cur.execute('DELETE FROM basket WHERE id_basket == ? and id_user==?', (id_basket, id_user,))
    base.commit()


async def read_user_basket(user_id):
    pusto = []
    basket = cur.execute('SELECT * FROM basket WHERE id_user ==?', (user_id,)).fetchall()
    if basket == pusto:
        return None
    else:
        return basket


async def read_product_up(id_product):
    return cur.execute('SELECT in_stock FROM product WHERE id_product ==?', (id_product,)).fetchone()


async def read_product_name(id_product):
    return cur.execute('SELECT name_product FROM product WHERE id_product ==?', (id_product,)).fetchone()


async def up_stock_product(qt, id_product):
    cur.execute('UPDATE product SET in_stock=? WHERE id_product ==?', (qt, id_product,))
    base.commit()


async def up_basket_product(qt, total_price, id_basket, id_user):
    cur.execute('UPDATE basket SET quantity=?, price=? WHERE id_basket ==? and id_user ==?', (qt, total_price, id_basket, id_user,))
    base.commit()


async def add_product_basket(user_id, quantity, product, price):
    cur.execute('INSERT INTO basket (id_user, quantity, product_id, price) VALUES (?, ?, ?, ?)', (user_id, quantity, product, price,))
    base.commit()


async def search_basket(user_id, product):
    pusto = []
    prod_basket = cur.execute('SELECT * FROM basket WHERE id_user==? and product_id==?', (user_id, product,)).fetchall()
    if prod_basket == pusto:
        return None
    else:
        return prod_basket


async def read_product(cat, manuf):
    pusto = []
    cat_return = cur.execute('SELECT * FROM product WHERE category_id==? and manufacturer_id==?', (cat, manuf,)).fetchall()
    if cat_return == pusto:
        return None
    else:
        return cat_return


def user_read(id_user):
    return cur.execute('SELECT * FROM profile WHERE user_id=?', (id_user,))


async def user_create(user_id, user_name, last_name, first_name):
    cur.execute("INSERT INTO profile VALUES (?,?,?,?)", (user_id, user_name, last_name, first_name,))
    base.commit()


async def read_admin():
    return cur.execute('SELECT * FROM admins').fetchall()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO category (name_cat) VALUES (?)', tuple(data.values()))
        base.commit()


async def sql_add_manuf(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO manufacturing (name_manuf) VALUES (?)', tuple(data.values()))
        base.commit()


async def sql_add_product(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO product ('
                    'category_id, manufacturer_id, img, name_product, description,'
                    'in_stock, code, condition_p, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def category_async_read():
    pusto = []
    cat_return = cur.execute('SELECT * FROM category').fetchall()
    if cat_return == pusto:
        return None
    else:
        return cat_return


async def sql_delete_command(data):
    cur.execute('DELETE FROM category WHERE id_cat == ?', (data,))
    base.commit()


async def sql_delete_manuf(data):
    cur.execute('DELETE FROM manufacturing WHERE id_manuf == ?', (data,))
    base.commit()


async def sql_delete_product(data):
    cur.execute('DELETE FROM product WHERE id_product == ?', (data,))
    base.commit()


async def manuf_async_read():
    pusto = []
    cat_return = cur.execute('SELECT * FROM manufacturing').fetchall()
    if cat_return == pusto:
        return None
    else:
        return cat_return


async def sql_add_pri(state):
    async with state.proxy() as data:
        cur.execute('UPDATE product SET price=? WHERE id_product==?', tuple(data.values()))
        base.commit()


async def sql_add_stock(state):
    async with state.proxy() as data:
        cur.execute('UPDATE product SET in_stock=? WHERE id_product==?', tuple(data.values()))
        base.commit()


async def sql_add_admin(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO admins (id_admin) VALUES (?)', tuple(data.values()))
        base.commit()
