from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from data_base.sqlite_db import category_async_read, manuf_async_read
from keyboard.functions import inline_button_row_2, inline_button_row_3


standard = ["text", "callback_data"]


kb_admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [
    'Все категории', 'Создать категорию', 'Все производители', 'Создать производителя',
    'Добавить товар', 'Удалить товар', 'Обновить цену', 'Обновить количество',
    'Заказы', 'Добавить админа', 'Отмена', 'Вернуться'
]
kb_admin_keyboard.add(*buttons)


async def a_cat_return_read():
    req_cat = await category_async_read()
    if req_cat is not None:

        buttons1 = []
        for key, val in req_cat:

            r = dict.fromkeys(standard, val)
            r.update({'callback_data': 'ACat|'+str(key)})
            buttons1.append(r)

        kb = inline_button_row_2(buttons1)

        return kb
    else:
        return None


async def a_manuf_return_read(categ):
    menu_admin_manuf = await manuf_async_read()

    if menu_admin_manuf is not None:

        buttons2 = []
        for w, tek in menu_admin_manuf:

            r = dict.fromkeys(standard, tek)
            r.update({'callback_data': f'AMan|{categ}|'+str(w)})
            buttons2.append(r)

        kb = inline_button_row_3(buttons2)

        return kb
    else:
        return None


async def delete_product_category():
    dpc = await category_async_read()

    if dpc is not None:

        buttons3 = []
        for i, v in dpc:

            create = dict.fromkeys(standard, v)
            create.update({'callback_data': f'DPCat|'+str(i)})
            buttons3.append(create)

        kb = inline_button_row_2(buttons3)

        return kb
    else:
        return None


async def delete_product_manufacturing(category):
    menu_admin_manuf = await manuf_async_read()

    if menu_admin_manuf is not None:

        buttons4 = []
        for w, tek in menu_admin_manuf:

            r = dict.fromkeys(standard, tek)
            r.update({'callback_data': f'MDP|{category}|'+str(w)})
            buttons4.append(r)

        kb = inline_button_row_3(buttons4)

        return kb
    else:
        return None


async def update_product_category():
    dpc = await category_async_read()

    if dpc is not None:

        buttons3 = []
        for i, v in dpc:

            create = dict.fromkeys(standard, v)
            create.update({'callback_data': f'UpCat|'+str(i)})
            buttons3.append(create)

        kb = inline_button_row_2(buttons3)

        return kb
    else:
        return None


async def update_product_manufacturing(category):
    menu_admin_manuf = await manuf_async_read()

    if menu_admin_manuf is not None:

        buttons4 = []
        for w, tek in menu_admin_manuf:

            r = dict.fromkeys(standard, tek)
            r.update({'callback_data': f'UpMan|{category}|'+str(w)})
            buttons4.append(r)

        kb = inline_button_row_3(buttons4)

        return kb
    else:
        return None


async def price_update_admin():
    req_cat = await category_async_read()
    if req_cat is not None:

        buttons1 = []
        for key, val in req_cat:

            r = dict.fromkeys(standard, val)
            r.update({'callback_data': 'CPUA|'+str(key)})
            buttons1.append(r)

        kb = inline_button_row_2(buttons1)

        return kb
    else:
        return None


async def update_manuf_admin(categ):
    menu_admin_manuf = await manuf_async_read()

    if menu_admin_manuf is not None:

        buttons2 = []
        for w, tek in menu_admin_manuf:

            r = dict.fromkeys(standard, tek)
            r.update({'callback_data': f'UMAD|{categ}|'+str(w)})
            buttons2.append(r)

        kb = inline_button_row_3(buttons2)

        return kb
    else:
        return None


async def orders_read_admin(user, id_order):
    buttons3 = [
        types.InlineKeyboardButton(text="Подтверждение", callback_data=f"СonfA|{user}|{id_order}"),
        types.InlineKeyboardButton(text="Отменен", callback_data=f"Cancel|{user}|{id_order}"),
    ]
    kb_basket = types.InlineKeyboardMarkup(row_width=2)
    kb_basket.add(*buttons3)

    return kb_basket
