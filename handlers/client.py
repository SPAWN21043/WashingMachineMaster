from aiogram import types, Dispatcher
from configurations import dp, bot
from aiogram.dispatcher.filters import Text
from data_base.sqlite_db import user_read, user_create, read_product, search_basket, add_product_basket, \
    search_admin_orders, search_product_cancel, delete_order_admin
from data_base.sqlite_db import up_basket_product, up_stock_product, read_product_up, read_user_basket, read_admin
from data_base.sqlite_db import read_product_name, delete_basket, search_qt_basket, search_price_product
from data_base.sqlite_db import sql_issue_basket, sql_add_orders, delete_basket_user, read_user_orders
from keyboard.kb_user import kb_keyboard, cat_return_read, manuf_return_read, create_basket_product, index_create
from keyboard.kb_user import kb_creat, cancel_user_order
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


class PhoneFSM(StatesGroup):
    id_user = State()
    order_client = State()
    phone_client = State()


@dp.message_handler(commands=['start'])
async def start_sent(message: types.Message):

    user_id = message.from_user.id
    user_name = message.from_user.username
    last_name = message.from_user.last_name
    first_name = message.from_user.first_name
    text = 'Приветствую. Для понимания как работает бот нажмите или введите: Помощь'
    try:
        await bot.send_message(message.from_user.id, text, reply_markup=kb_keyboard)
        await message.delete()
    except:
        await message.reply('Для дальнейшей работы перейдите в личные сообщения к боту:\n '
                            'http://t.me/WashingMachineMasterBot')

    info = user_read(user_id)

    if info.fetchone() is None:

        await user_create(user_id, user_name, last_name, first_name)


@dp.message_handler(Text(equals="Каталог"))
async def catalog_menu(message: types.Message):
    text = "Каталог"
    await message.answer(text, reply_markup=await cat_return_read())
    await message.answer("Выберите категорию", reply_markup=kb_keyboard)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('Cat|'))
async def manuf_menu(call: types.CallbackQuery):
    categ = call.data.split('|')[1]
    text = "Выберите производителя"
    await call.message.answer(text, reply_markup=await manuf_return_read(categ))
    await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('Man|'))
async def user_product_return(call: types.CallbackQuery):
    id_user = call.from_user.id
    quantity = 1
    categ = call.data.split('|')[1]
    manufacturing = call.data.split('|')[2]

    product_user = await read_product(categ, manufacturing)

    if product_user is not None:
        await call.message.answer('Все товары данного производителя')
        for index in product_user:
            await call.message.answer_photo(
                index[3], f'Наименование: {index[4]}\nОписание: {index[5]}\nВ наличии: {index[6]}\n'
                          f'Артикул: {index[7]}\nСостояние: {index[8]}\nСтоимость: {index[9]} руб.',
                reply_markup=await create_basket_product(id_user, quantity, index[0], index[9])
            )
    else:
        text = "У нас нет товаров данного производителя"
        await call.message.answer(text)
        await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('Добавить|'))
async def tov_add(call: types.CallbackQuery):
    user_id = call.data.split('|')[1]
    quantity = call.data.split('|')[2]
    product = call.data.split('|')[3]
    price = call.data.split('|')[4]

    product_user = await search_basket(user_id, product)
    in_stock = await read_product_up(product)

    if product_user is None:
        new_stock = in_stock[0] - 1
        await add_product_basket(user_id, quantity, product, price)
        await up_stock_product(new_stock, product)
        await call.answer('Товар добавлен в корзину', show_alert=True)
    else:
        if in_stock[0] == 0:
            await call.answer('На складе больше нет товара', show_alert=True)
        else:
            current_product = product_user[0]
            new_price = int(current_product[4])+int(price)
            new_quantity = int(current_product[2])+int(quantity)
            new_stock = in_stock[0] - 1

            await up_basket_product(new_quantity, new_price, current_product[0], current_product[1])
            await up_stock_product(new_stock, current_product[3])
            await call.answer('Вы увеличили количество в корзине', show_alert=True)


@dp.callback_query_handler(text='Назад')
async def back_user_menu(call: types.CallbackQuery):
    text = "Каталог"
    await call.message.answer(text, reply_markup=await cat_return_read())
    await call.message.delete()
    await call.answer()


@dp.message_handler(Text(equals="Помощь"))
async def help_user(message: types.Message):
    text = f"Зайдите в каталог, выберите категорию, выберите производителя, выберите товар.\n" \
           f"Нажмите кнопку добавить – нажатием на кнопку вы добавите товар в корзину.\n" \
           f"После наполнения корзины, зайдите в нее для редактирования и подтверждения товаров для бронирования.\n" \
           f"Введите номер телефона для связи с вами и мы вам перезвоним."
    await message.answer(text, reply_markup=kb_keyboard)
    await message.delete()


@dp.message_handler(Text(equals='Корзина'))
async def delete_item(message: types.Message):
    user = message.from_user.id
    read_basket = await read_user_basket(user)

    if read_basket is None:
        text = f'Вы не добавили товаров в корзину'
        await message.answer(text)
        await message.delete()
    else:
        for index in read_basket:
            id_product = index[3]
            name_product = await read_product_name(id_product)
            name = name_product[0]
            text = '⬆⬆⬆Проверьте позицию выше⬆⬆⬆'

            await bot.send_message(message.from_user.id, f'{name}, Количество: {index[2]}шт Цена: {index[4]}руб')
            await bot.send_message(message.from_user.id, text, reply_markup=await index_create(user, index[0], name, id_product))

        await message.answer("Для подтверждения нажмите оформить", reply_markup=kb_creat)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('Убрать|'))
async def del_order_callback_run(call: types.CallbackQuery):
    id_user = call.data.split('|')[1]
    id_basket = call.data.split('|')[2]
    id_product = call.data.split('|')[3]

    name_product = await read_product_name(id_product)
    name = name_product[0]
    stock = await read_product_up(id_product)
    return_stock = await search_basket(id_user, id_product)
    current_stock_user = return_stock[0]
    new_stock = int(stock[0]) + int(current_stock_user[2])

    await delete_basket(id_basket, id_user)
    await up_stock_product(new_stock, id_product)
    await call.answer(f'Товар: {name} был удален из корзины', show_alert=True)
    await call.message.answer('Нажмите на корзину для обновления')


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('Увел|'))
async def up_callback_run(call: types.CallbackQuery):

    id_user = call.data.split('|')[1]
    id_basket = call.data.split('|')[2]
    id_product = call.data.split('|')[3]

    qt = await search_qt_basket(id_user, id_product)
    price = await search_price_product(id_product)
    in_stock = await read_product_up(id_product)
    product_user = await search_basket(id_user, id_product)

    if in_stock[0] == 0:
        await call.answer('Больше не увеличить', show_alert=True)
    else:
        new_qt = int(qt[0])+1
        current_product = product_user[0]
        new_stock = in_stock[0] - 1
        new_price = int(current_product[4])+int(price[0])
        await up_basket_product(new_qt, new_price, id_basket, id_user)
        await up_stock_product(new_stock, id_product)
        update_qt = await search_qt_basket(id_user, id_product)
        await call.answer(f'Количество товара увеличено на 1.\n У вас {update_qt[0]} шт.', show_alert=True)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('Умен|'))
async def down_callback_run(call: types.CallbackQuery):

    user = call.data.split('|')[1]
    id_basket = call.data.split('|')[2]
    id_product = call.data.split('|')[3]

    qt = await search_qt_basket(user, id_product)
    price = await search_price_product(id_product)
    in_stock = await read_product_up(id_product)
    product_user = await search_basket(user, id_product)

    if qt[0] == 0:
        await call.answer('Удалите позицию, вы уменьшили до 0', show_alert=True)
    else:
        new_qt = int(qt[0])-1
        current_product = product_user[0]
        new_stock = in_stock[0] + 1
        new_price = int(current_product[4])-int(price[0])
        await up_basket_product(new_qt, new_price, id_basket, user)
        await up_stock_product(new_stock, id_product)
        update_qt = await search_qt_basket(user, id_product)
        await call.answer(f'Количество товара уменьшено на 1.\n У вас {update_qt[0]} шт.', show_alert=True)


@dp.message_handler(Text(equals="Оформить"), state=None)
async def issue(message: types.Message):
    user = message.from_user.id

    issue_bask = await sql_issue_basket(user)

    if not issue_bask:
        await message.reply("В корзине нет еще товаров", reply=False, reply_markup=kb_keyboard)
        return
    else:
        issue_bask_row = []
        for row in issue_bask:
            id_product = row['product']
            qt = row["qt"]
            sum_price = row["sum"]
            prod = await read_product_name(id_product)
            issue_bask_row.append(f'{prod[0]}, в количестве {qt} шт, стоимостью {sum_price} pуб.')
        answer_message = 'Вы заказали:\n' + '\n'.join(issue_bask_row)
        await message.reply(answer_message, reply=False)
        await PhoneFSM.id_user.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(id_user=user)
        await PhoneFSM.order_client.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(order_client=answer_message)
        await message.answer("Введите телефон для связи.")
        await PhoneFSM.phone_client.set()


@dp.message_handler(state=PhoneFSM.phone_client)
async def phone_load(message: types.Message, state: FSMContext):
    user = message.from_user.id
    async with state.proxy() as data:
        data['phone_client'] = message.text

    await sql_add_orders(state)
    await state.finish()
    await message.answer("Заявка создана", reply_markup=kb_keyboard)
    await delete_basket_user(user)
    orders = await read_user_orders(user)
    for index in orders:
        admin_list = await read_admin()
        for admin in admin_list:

            text = f'У вас новый заказ:\nНомер заказа: {index[0]}.\n{index[2]}\nТелефон для связи: {index[3]}'
            await bot.send_message(chat_id=admin[0], text=text)


@dp.message_handler(Text(equals='Мой_заказ'))
async def my_orders(message: types.Message):
    user = message.from_user.id

    orders = await read_user_orders(user)

    if orders is None:
        text = 'У вас нет заказов'
        await bot.send_message(message.from_user.id, text)
        await message.delete()
    else:

        for index in orders:
            text = f'Номер заказа: {index[0]}\n{index[2]}'
            await bot.send_message(user, text, reply_markup=await cancel_user_order(user, index[0]))
            await message.answer('Вы можете отменить заказ', reply_markup=kb_keyboard)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('CUO|'))
async def cancel_order_user(call: types.CallbackQuery):
    user = call.data.split('|')[1]
    order = call.data.split('|')[2]

    user_order = await search_admin_orders(order)
    admin = await read_admin()
    spare = user_order[2].split('\n')[1]
    name = spare.split(',')[0]
    tew = await search_product_cancel(name)

    pr = spare.split(',')[1]
    qt = pr.split(' ')[3]

    new_qt = int(tew[1]) + int(qt)

    id_product = tew[0]

    await up_stock_product(new_qt, id_product)
    text = f"Ваш заказ {user_order[0]} отменен"
    await call.answer(text, show_alert=True)
    await delete_order_admin(order)
    await call.message.delete()
    for ad in admin:
        await bot.send_message(chat_id=ad[0], text=f"Заказ {user_order[0]} отменен", reply_markup=kb_keyboard)


@dp.message_handler(Text(equals="private_id"))
async def id_profile(message: types.Message):
    id_private = message.from_user.id
    text = f'Ваш id: {id_private}'
    await bot.send_message(message.from_user.id, text)
    await message.delete()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_sent, commands=['start'])
    dp.register_message_handler(catalog_menu, commands=['Каталог'])
    dp.register_message_handler(manuf_menu, commands=['Cat|'])
    dp.register_message_handler(user_product_return, commands=['Man|'])
    dp.register_message_handler(tov_add, commands=['Добавить|'])
    dp.register_message_handler(back_user_menu, commands=['Назад'])
    dp.register_message_handler(help_user, commands=['Помощь'])
    dp.register_message_handler(delete_item, commands=['Корзина'])
    dp.register_message_handler(del_order_callback_run, commands=['Убрать|'])
    dp.register_message_handler(up_callback_run, commands=['Увел|'])
    dp.register_message_handler(down_callback_run, commands=['Умен|'])
    dp.register_message_handler(my_orders, commands=['Мой_заказ'])
    dp.register_message_handler(cancel_order_user, commands=['CUO|'])
    dp.register_message_handler(id_profile, commands=['private_id'])
