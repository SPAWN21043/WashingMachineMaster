from aiogram import types


def inline_button_row_2(buttons):
    kb_profile = types.InlineKeyboardMarkup(row_width=2)
    kb_profile.add(*buttons)
    return kb_profile


def inline_button_row_3(buttons):
    kb_profile = types.InlineKeyboardMarkup(row_width=3)
    kb_profile.add(*buttons)
    return kb_profile
