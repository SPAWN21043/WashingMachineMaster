from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from data_base.sqlite_db import category_async_read, manuf_async_read


kb_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
buttons = ['Каталог', 'Корзина', 'Мой_заказ', 'Помощь']
kb_keyboard.add(*buttons)


kb_creat = ReplyKeyboardMarkup(resize_keyboard=True)
buttons7 = ['Каталог', 'Корзина', 'Оформить', 'Мой_заказ', 'Помощь']
kb_creat.add(*buttons7)


async def cat_return_read():
    req_cat = await category_async_read()
    if req_cat is not None:

        buttons2 = []
        for key, val in req_cat:

            g = ["text", "callback_data"]
            r = dict.fromkeys(g, val)
            r.update({'callback_data': 'Cat|'+str(key)})
            buttons2.append(r)

        ikw_kb = types.InlineKeyboardMarkup(row_width=2)
        ikw_kb.add(*buttons2)
        return ikw_kb
    else:
        return None


async def manuf_return_read(category):

    manuf = await manuf_async_read()

    if manuf is not None:

        buttons_key = []
        for w, v in manuf:

            back_test = ["text", "callback_data"]
            s = dict.fromkeys(back_test, v)
            s.update({'callback_data': f'Man|{category}|'+str(w)})
            buttons_key.append(s)

        ikw_kb = types.InlineKeyboardMarkup(row_width=3)
        ikw_kb.add(*buttons_key)
        return ikw_kb
    else:
        return None


async def create_basket_product(user, quantity, id_product, price):
    buttons3 = [
        types.InlineKeyboardButton(text="Добавить", callback_data=f"Добавить|{user}|{quantity}|{id_product}|{price}"),
        types.InlineKeyboardButton(text="Назад", callback_data="Назад"),
    ]
    kb_basket = types.InlineKeyboardMarkup(row_width=2)
    kb_basket.add(*buttons3)

    return kb_basket


async def index_create(user, id_basket, name_product, id_product):
    button_index = [
        types.InlineKeyboardButton(f'Увеличить на 1', callback_data=f'Увел|{user}|{id_basket}|{id_product}'),
        types.InlineKeyboardButton(f'Уменьшить на 1', callback_data=f'Умен|{user}|{id_basket}|{id_product}'),
        types.InlineKeyboardButton(f'Удалить {name_product}', callback_data=f'Убрать|{user}|{id_basket}|{id_product}')
    ]

    kb_index = types.InlineKeyboardMarkup(row_width=2)
    kb_index.add(*button_index)

    return kb_index


async def cancel_user_order(user, order):
    buttons3 = [
        types.InlineKeyboardButton(text="Отменить заказ", callback_data=f"CUO|{user}|{order}"),

    ]
    kb_basket = types.InlineKeyboardMarkup(row_width=1)
    kb_basket.add(*buttons3)

    return kb_basket
