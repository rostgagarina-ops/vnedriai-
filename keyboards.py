from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from config import Settings


def main_menu(settings: Settings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Заполнить анкету", callback_data="brief_start")],
            [
                InlineKeyboardButton(text="❓ Частые вопросы", callback_data="faq_menu"),
                InlineKeyboardButton(text="🎯 Что внедряем", callback_data="solutions"),
            ],
            [
                InlineKeyboardButton(text="📋 Как проходит аудит", callback_data="audit_flow"),
                InlineKeyboardButton(text="🌐 Сайт", url=settings.site_url),
            ],
            [
                InlineKeyboardButton(
                    text="💬 Написать основателю",
                    url=f"https://t.me/{settings.founder_username}",
                )
            ],
            [InlineKeyboardButton(text="📢 Наш канал", url=settings.channel_url)],
        ]
    )


def after_brief_menu(settings: Settings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=settings.channel_url)],
            [
                InlineKeyboardButton(
                    text="💬 Написать основателю",
                    url=f"https://t.me/{settings.founder_username}",
                )
            ],
            [InlineKeyboardButton(text="◀️ В главное меню", callback_data="main_menu")],
        ]
    )


def faq_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Что входит в аудит?", callback_data="faq:audit")],
            [InlineKeyboardButton(text="Сколько стоит?", callback_data="faq:price")],
            [InlineKeyboardButton(text="Как быстро запускаете?", callback_data="faq:timing")],
            [InlineKeyboardButton(text="Почему только онлайн-школы?", callback_data="faq:niche")],
            [InlineKeyboardButton(text="С чего начать?", callback_data="faq:first")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")],
        ]
    )


def pain_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"pain:{key}")]
        for key, label in {
            "expert": "👤 Эксперт не успевает",
            "support": "💬 Саппорт перегружен",
            "sales": "📉 Низкая конверсия",
            "onboarding": "🔄 Онбординг вручную",
            "churn": "📊 Высокий отвал",
            "content": "📝 Обновление контента",
        }.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def platform_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="GetCourse", callback_data="platform:getcourse")],
            [InlineKeyboardButton(text="Telegram + таблицы", callback_data="platform:telegram")],
            [InlineKeyboardButton(text="Другая LMS", callback_data="platform:other_lms")],
            [InlineKeyboardButton(text="Несколько инструментов", callback_data="platform:mixed")],
        ]
    )


def skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
