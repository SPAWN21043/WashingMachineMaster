from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configurations import dp, bot
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from data_base.sqlite_db import read_admin, sql_add_command, category_async_read, sql_delete_command, manuf_async_read
from data_base.sqlite_db import sql_add_manuf, sql_delete_manuf, sql_add_product, read_product, sql_delete_product
from data_base.sqlite_db import sql_add_pri, sql_add_admin, sql_add_stock, read_admin_orders, delete_order_admin
from data_base.sqlite_db import search_admin_orders, search_product_cancel, up_stock_product
from keyboard.kb_admin import kb_admin_keyboard, a_cat_return_read, a_manuf_return_read, delete_product_category
from keyboard.kb_admin import delete_product_manufacturing, update_product_category, update_product_manufacturing
from keyboard.kb_admin import price_update_admin, update_manuf_admin, orders_read_admin
from keyboard.kb_user import kb_keyboard
from configurations import chief
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


class CategoryFSM(StatesGroup):
    name_cat = State()


class ManufFSM(StatesGroup):
    name_manuf = State()


class ProductFSM(StatesGroup):
    category_id = State()
    manufacturer_id = State()
    img = State()
    name_product = State()
    description = State()
    in_stock = State()
    code = State()
    condition_p = State()
    price = State()


class UpdatePriceFSM(StatesGroup):
    id_product = State()
    price = State()


class CreateAdminFSM(StatesGroup):
    id_admin = State()


class UpdateQtyFSM(StatesGroup):
    id_product = State()
    in_stock = State()


@dp.message_handler(commands=['admin_m'])
async def make_changes_command(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        await bot.send_message(message.from_user.id, 'Что хозяин надо???', reply_markup=kb_admin_keyboard)
        await message.delete()
    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.message_handler(state="*", commands='Отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply("Отменено", reply_markup=kb_admin_keyboard)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена.', show_alert=True)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('m_del '))
async def del_manuf_run(callback_query: types.CallbackQuery):
    await sql_delete_manuf(callback_query.data.replace('m_del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("m_del ", "")} удалена.', show_alert=True)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('P_del '))
async def del_product_run(callback_query: types.CallbackQuery):
    await sql_delete_product(callback_query.data.replace('P_del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("P_del ", "")} удалена.', show_alert=True)


@dp.message_handler(Text(equals="Все категории"))
async def cat_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        key_admin = await category_async_read()

        if key_admin is not None:
            await message.answer('Все категории в базе')
            for key in key_admin:

                await bot.send_message(message.from_user.id, f'Категория: {key[1]}')
                await bot.send_message(message.from_user.id, text='⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                       add(InlineKeyboardButton(f'Удалить {key[1]}', callback_data=f'del {key[0]}')))

        else:
            text = "В базе нет категорий создайте их"
            await message.answer(text)

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.message_handler(Text(equals="Создать категорию"), state=None)
async def create_cat_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        await CategoryFSM.name_cat.set()
        await message.reply('Введите название категории')

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.message_handler(state=CategoryFSM.name_cat)
async def creat_category(message: types.Message, state: FSMContext):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        async with state.proxy() as data:
            data['name_manuf'] = message.text

        await sql_add_command(state)
        await state.finish()
        await message.reply("Категория создана")


@dp.message_handler(Text(equals="Все производители"))
async def manuf_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        key_admin = await manuf_async_read()

        if key_admin is not None:
            await message.answer('Все производители в базе')
            for key in key_admin:

                await bot.send_message(message.from_user.id, f'Категория: {key[1]}')
                await bot.send_message(message.from_user.id, text='⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                       add(InlineKeyboardButton(f'Удалить {key[1]}', callback_data=f'm_del {key[0]}')))

        else:
            text = "В базе нет производителей создайте их"
            await message.answer(text)

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.message_handler(Text(equals="Создать производителя"), state=None)
async def create_manuf_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        await ManufFSM.name_manuf.set()
        await message.reply('Введите название производителя')

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.message_handler(state=ManufFSM.name_manuf)
async def creat_manuf(message: types.Message, state: FSMContext):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        async with state.proxy() as data:
            data['name_cat'] = message.text

        await sql_add_manuf(state)
        await state.finish()
        await message.reply("Производитель создан")

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.message_handler(Text(equals="Добавить товар"))
async def admin_catalog_menu(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        text = "Выберите категорию"
        await message.answer(text, reply_markup=await a_cat_return_read())
        await message.delete()

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('ACat|'))
async def admin_manuf_menu(call: types.CallbackQuery):
    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        categ = call.data.split('|')[1]
        text = "Выберите производителя"
        await call.message.answer(text, reply_markup=await a_manuf_return_read(categ))
        await call.message.delete()

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('AMan|'), state=None)
async def admin_img_load(call: types.CallbackQuery):
    categ = call.data.split('|')[1]
    manuf = call.data.split('|')[2]

    await ProductFSM.category_id.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(category_id=categ)
    await ProductFSM.manufacturer_id.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(manufacturer_id=manuf)
    await call.message.reply('Загрузите фото')
    await ProductFSM.img.set()


@dp.message_handler(content_types=['photo'], state=ProductFSM.img)
async def load_photo(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['img'] = message.photo[0].file_id
    await ProductFSM.next()
    await message.reply('Теперь введите название')


@dp.message_handler(state=ProductFSM.name_product)
async def load_name(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['name_product'] = message.text
    await ProductFSM.next()
    await message.reply('Введите описание')


@dp.message_handler(state=ProductFSM.description)
async def load_description(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['description'] = message.text
    await ProductFSM.next()
    await message.reply('Введите количество в наличии')


@dp.message_handler(state=ProductFSM.in_stock)
async def load_stock(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['in_stock'] = message.text
    await ProductFSM.next()
    await message.reply('Введите артикул')


@dp.message_handler(state=ProductFSM.code)
async def load_code(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['code'] = message.text
    await ProductFSM.next()
    await message.reply('Введите состояние')


@dp.message_handler(state=ProductFSM.condition_p)
async def load_cond(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['condition_p'] = message.text
    await ProductFSM.next()
    await message.reply('Введите стоимость')


@dp.message_handler(state=ProductFSM.price)
async def load_price(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['price'] = float(message.text)

    await sql_add_product(state)
    await state.finish()
    await message.reply("Товар добавлен")


@dp.message_handler(Text(equals="Удалить товар"))
async def back_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        text = "Выберите категорию для удаления товара"
        await message.answer(text, reply_markup=await delete_product_category())
        await message.delete()

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('DPCat|'))
async def admin_manuf_menu(call: types.CallbackQuery):
    categ = call.data.split('|')[1]

    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        text = "Выберите производителя для удаления товара"
        await call.message.answer(text, reply_markup=await delete_product_manufacturing(categ))
        await call.message.delete()

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('MDP|'))
async def admin_dep_menu(call: types.CallbackQuery):
    categ = call.data.split('|')[1]
    manufacturer = call.data.split('|')[2]

    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        product = await read_product(categ, manufacturer)

        if product is not None:
            await call.message.answer('Все товары в базе для удаления')
            for key in product:

                await call.message.answer_photo(key[3], f'Название: {key[4]}')
                await bot.send_message(call.from_user.id, text='⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                       add(InlineKeyboardButton(f'Удалить {key[4]}', callback_data=f'P_del {key[0]}')))

        else:
            text = "В базе нет товаров в данной категории создайте их"
            await call.message.answer(text)

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.message_handler(Text(equals="Обновить цену"))
async def update_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        text = "Выберите категорию для обновления цены"
        await message.answer(text, reply_markup=await update_product_category())
        await message.delete()

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('UpCat|'))
async def update_manuf_menu(call: types.CallbackQuery):
    categ = call.data.split('|')[1]

    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        text = "Выберите производителя для обновления цены"
        await call.message.answer(text, reply_markup=await update_product_manufacturing(categ))
        await call.message.delete()

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('UpMan|'))
async def update_dep_menu(call: types.CallbackQuery):
    categ = call.data.split('|')[1]
    manufacturer = call.data.split('|')[2]

    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        product = await read_product(categ, manufacturer)

        if product is not None:
            await call.message.answer('Все товары в базе для удаления')
            for key in product:

                await call.message.answer_photo(key[3], f'Название: {key[4]}')
                await bot.send_message(call.from_user.id, text='⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                       add(InlineKeyboardButton(f'Обновить цену {key[4]}', callback_data=f'UpPrice {key[0]}')))

        else:
            text = "В базе нет товаров в данной категории создайте их"
            await call.message.answer(text)

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('UpPrice '), state=None)
async def update_update_run(callback_query: types.CallbackQuery):
    id_products = callback_query.data.replace('UpPrice ', '')

    await UpdatePriceFSM.id_product.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(id_product=id_products)
    await callback_query.message.reply('Введите новую стоимость')
    await UpdatePriceFSM.price.set()


@dp.message_handler(state=UpdatePriceFSM.price)
async def update_price(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        id_prod = data['id_product']
        data.clear()
        data['price'] = float(message.text)
        data['id_product'] = id_prod

    await sql_add_pri(state)
    await state.finish()
    await message.reply("Цена изменена")


@dp.message_handler(Text(equals="Добавить админа"), state=None)
async def create_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        await CreateAdminFSM.id_admin.set()
        await message.reply('Введите id администратора')

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.message_handler(state=CreateAdminFSM.id_admin)
async def load_admin(message: types.Message, state: FSMContext):

    async with state.proxy() as data:

        data['id_admin'] = message.text

    await sql_add_admin(state)
    await state.finish()
    await message.reply("Админ добавлен")


@dp.message_handler(Text(equals="Обновить количество"))
async def test_update_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        text = "Выберите категорию для обновления наличия"
        await message.answer(text, reply_markup=await price_update_admin())
        await message.delete()

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('CPUA|'))
async def test_manuf_menu(call: types.CallbackQuery):
    categ = call.data.split('|')[1]

    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        text = "Выберите производителя для обновления наличия"
        await call.message.answer(text, reply_markup=await update_manuf_admin(categ))
        await call.message.delete()

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('UMAD|'))
async def test_test_admin(call: types.CallbackQuery):
    categ = call.data.split('|')[1]
    manufacture = call.data.split('|')[2]

    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        product = await read_product(categ, manufacture)

        if product is not None:
            await call.message.answer('Все товары в базе для обновления количества')
            for key in product:
                await call.message.answer_photo(key[3], f'Название: {key[4]}')
                await bot.send_message(call.from_user.id, text='⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                       add(
                    InlineKeyboardButton(f'Обновить количество {key[4]}', callback_data=f'UpQt {key[0]}')))

        else:
            text = "В базе нет товаров в данной категории создайте их"
            await call.message.answer(text)

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('UpQt '), state=None)
async def test_update_run(callback_query: types.CallbackQuery):
    id_products = callback_query.data.replace('UpQt ', '')

    await UpdateQtyFSM.id_product.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(id_product=id_products)
    await callback_query.message.reply('Введите новое количество')
    await UpdateQtyFSM.in_stock.set()


@dp.message_handler(state=UpdateQtyFSM.in_stock)
async def test_update_stock(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        id_prod = data['id_product']
        data.clear()
        data['in_stock'] = float(message.text)
        data['id_product'] = id_prod

    await sql_add_stock(state)
    await state.finish()
    await message.reply("Количество изменено")


@dp.message_handler(Text(equals="Заказы"))
async def order_user_admin(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id
    order = await read_admin_orders()

    if current_user == admin_list or chief:
        if order is None:
            text = "Нет заказов"
            await message.answer(text, reply_markup=kb_keyboard)
            await message.delete()
        else:
            for index in order:
                text = f'Заказ номер: {index[0]}.\n{index[2]}'
                print(text)
                await message.answer(text, reply_markup=await orders_read_admin(index[1], index[0]))

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('СonfA|'))
async def conf_order_admin(call: types.CallbackQuery):
    user = call.data.split('|')[1]
    order = call.data.split('|')[2]

    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        text = "Заказ выполнен"
        await call.answer(text, show_alert=True)
        await delete_order_admin(order)
        await call.message.delete()
        await bot.send_message(user, "Ваш заказ выполнен")

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('Cancel|'))
async def cancel_order_admin(call: types.CallbackQuery):
    user = call.data.split('|')[1]
    order = call.data.split('|')[2]

    admin_list = await read_admin()
    current_user = call.from_user.id

    if current_user == admin_list or chief:
        user_order = await search_admin_orders(order)
        spare = user_order[2].split('\n')[1]
        name = spare.split(',')[0]
        tew = await search_product_cancel(name)

        pr = spare.split(',')[1]
        qt = pr.split(' ')[3]

        new_qt = int(tew[1])+int(qt)

        id_product = tew[0]

        await up_stock_product(new_qt, id_product)
        text = f"Заказ {user_order[0]} отменен"
        await call.answer(text, show_alert=True)
        await delete_order_admin(order)
        await call.message.delete()
        await bot.send_message(user, f"Ваш заказ {user_order[0]} отменен")

    else:
        await bot.send_message(call.from_user.id, 'Нет такой команды')
        await call.message.delete()


@dp.message_handler(Text(equals="Вернуться"))
async def back_client(message: types.Message):
    admin_list = await read_admin()
    current_user = message.from_user.id

    if current_user == admin_list or chief:
        text = "Вы вернулись в клиентский раздел"
        await message.answer(text, reply_markup=kb_keyboard)
        await message.delete()

    else:
        await bot.send_message(message.from_user.id, 'Нет такой команды')
        await message.delete()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['admin_m'])
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(del_callback_run, commands=['del '])
    dp.register_message_handler(del_manuf_run, commands=['m_del '])
    dp.register_message_handler(del_product_run, commands=['P_del '])
    dp.register_message_handler(cat_admin, commands=['Все категории'])
    dp.register_message_handler(create_cat_admin, commands=['Создать категорию'], state=None)
    dp.register_message_handler(creat_category, state=CategoryFSM.name_cat)
    dp.register_message_handler(cat_admin, commands=['Все производители'])
    dp.register_message_handler(create_manuf_admin, commands=['Создать производителя'], state=None)
    dp.register_message_handler(creat_manuf, state=CategoryFSM.name_cat)
    dp.register_message_handler(admin_catalog_menu, commands=['Добавить товар'])
    dp.register_message_handler(admin_manuf_menu, commands=['ACat|'])
    dp.register_message_handler(admin_img_load, commands=['AMan|'], state=None)
    dp.register_message_handler(load_photo, content_types=['photo'], state=ProductFSM.img)
    dp.register_message_handler(load_name, state=ProductFSM.name_product)
    dp.register_message_handler(load_description, state=ProductFSM.description)
    dp.register_message_handler(load_stock, state=ProductFSM.in_stock)
    dp.register_message_handler(load_code, state=ProductFSM.code)
    dp.register_message_handler(load_cond, state=ProductFSM.condition_p)
    dp.register_message_handler(load_price, state=ProductFSM.price)
    dp.register_message_handler(back_admin, commands=['Удалить товар'])
    dp.register_message_handler(admin_manuf_menu, commands=['DPCat|'])
    dp.register_message_handler(admin_dep_menu, commands=['MDP|'])
    dp.register_message_handler(update_admin, commands=['Обновить цену'])
    dp.register_message_handler(update_manuf_menu, commands=['UpCat|'])
    dp.register_message_handler(update_dep_menu, commands=['UpMan|'])
    dp.register_message_handler(update_update_run, commands=['UpPrice '], state=None)
    dp.register_message_handler(update_price, state=UpdatePriceFSM.price)
    dp.register_message_handler(create_admin, commands=['Добавить админа'], state=None)
    dp.register_message_handler(load_admin, state=CreateAdminFSM.id_admin)
    dp.register_message_handler(test_update_admin, commands=['Обновить количество'])
    dp.register_message_handler(test_manuf_menu, commands=['CPUA|'])
    dp.register_message_handler(test_test_admin, commands=['UMAD|'])
    dp.register_message_handler(test_update_run, commands=['UpQt '], state=None)
    dp.register_message_handler(test_update_stock, state=UpdateQtyFSM.in_stock)
    dp.register_message_handler(order_user_admin, commands=['Заказы'])
    dp.register_message_handler(conf_order_admin, commands=['СonfA|'])
    dp.register_message_handler(cancel_order_admin, commands=['Cancel|'])
    dp.register_message_handler(back_client, commands=['Вернуться'])

