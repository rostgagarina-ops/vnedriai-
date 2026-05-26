import asyncio
import logging
from enum import StrEnum

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import Settings, get_settings
from database import init_db, save_brief, upsert_lead
from keyboards import (
    after_brief_menu,
    faq_menu,
    main_menu,
    pain_menu,
    platform_menu,
    remove_keyboard,
    skip_keyboard,
)
from texts import (
    AUDIT_FLOW,
    BRIEF_DONE,
    BRIEF_INTRO,
    BRIEF_Q2,
    BRIEF_Q3,
    BRIEF_Q4,
    BRIEF_Q5,
    FAQ_ITEMS,
    PAIN_LABELS,
    PLATFORM_LABELS,
    SOLUTIONS,
    START_MESSAGE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BriefForm(StatesGroup):
    project_link = State()
    request_text = State()
    main_pain = State()
    platform = State()
    scale = State()


class Cb(StrEnum):
    MAIN_MENU = "main_menu"
    BRIEF_START = "brief_start"
    FAQ_MENU = "faq_menu"
    SOLUTIONS = "solutions"
    AUDIT_FLOW = "audit_flow"


def user_contact(user) -> str:
    if user.username:
        return f"@{user.username}"
    return f'<a href="tg://user?id={user.id}">написать</a>'


def format_lead_alert(user, source: str, brief: dict | None = None) -> str:
    lines = [
        "🆕 <b>Новая заявка на аудит</b>",
        "",
        f"👤 {user.full_name}",
        f"🔗 {user_contact(user)}",
        f"🆔 <code>{user.id}</code>",
    ]
    if source:
        lines.append(f"📍 Источник: {source}")

    if brief:
        lines.extend(
            [
                "",
                "📝 <b>Анкета:</b>",
                f"• Проект: {brief.get('project_link', '—')}",
                f"• Запрос: {brief.get('request_text', '—')}",
                f"• Боль: {brief.get('main_pain', '—')}",
                f"• Платформа: {brief.get('platform', '—')}",
                f"• Масштаб: {brief.get('scale', '—')}",
            ]
        )
    else:
        lines.append("")
        lines.append("⏳ Анкета пока не заполнена")

    return "\n".join(lines)


async def notify_admin(bot: Bot, settings: Settings, text: str) -> None:
    try:
        await bot.send_message(settings.admin_id, text, parse_mode="HTML")
    except Exception:
        logger.exception("Не удалось отправить уведомление админу")


async def cmd_start(message: Message, state: FSMContext, bot: Bot, settings: Settings) -> None:
    await state.clear()

    source = ""
    if message.text and len(message.text.split()) > 1:
        source = message.text.split(maxsplit=1)[1]

    user = message.from_user
    upsert_lead(user.id, user.username, user.full_name, source)
    await state.update_data(source=source)

    await notify_admin(
        bot,
        settings,
        format_lead_alert(user, source or "прямой переход"),
    )

    await message.answer(START_MESSAGE, parse_mode="HTML", reply_markup=main_menu(settings))


async def show_main_menu(callback: CallbackQuery, settings: Settings) -> None:
    await callback.message.edit_text(
        "Выберите, что вас интересует:",
        reply_markup=main_menu(settings),
    )


async def cb_main_menu(callback: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    await state.clear()
    await callback.answer()
    await show_main_menu(callback, settings)


async def cb_faq_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(
        "❓ <b>Частые вопросы</b>\n\nВыберите тему:",
        parse_mode="HTML",
        reply_markup=faq_menu(),
    )


async def cb_faq_item(callback: CallbackQuery) -> None:
    key = callback.data.split(":", 1)[1]
    text = FAQ_ITEMS.get(key, "Ответ не найден.")
    await callback.answer()
    await callback.message.edit_text(
        text + "\n\n<i>Остались вопросы — напишите основателю или заполните анкету.</i>",
        parse_mode="HTML",
        reply_markup=faq_menu(),
    )


def back_menu(extra: list | None = None) -> InlineKeyboardMarkup:
    rows = extra or []
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data=Cb.MAIN_MENU)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def cb_solutions(callback: CallbackQuery, settings: Settings) -> None:
    await callback.answer()
    await callback.message.edit_text(
        SOLUTIONS,
        parse_mode="HTML",
        reply_markup=back_menu(
            [[InlineKeyboardButton(text="📝 Заполнить анкету", callback_data=Cb.BRIEF_START)]]
        ),
    )


async def cb_audit_flow(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(
        AUDIT_FLOW,
        parse_mode="HTML",
        reply_markup=back_menu(
            [[InlineKeyboardButton(text="📝 Заполнить анкету", callback_data=Cb.BRIEF_START)]]
        ),
    )


async def cb_brief_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(BriefForm.project_link)
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(BRIEF_INTRO, parse_mode="HTML")


async def brief_project_link(message: Message, state: FSMContext) -> None:
    link = message.text.strip()
    if len(link) < 3:
        await message.answer("Пришлите ссылку или название проекта текстом.")
        return
    await state.update_data(project_link=link)
    await state.set_state(BriefForm.request_text)
    await message.answer(BRIEF_Q2, parse_mode="HTML")


async def brief_request_text(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if len(text) < 10:
        await message.answer("Напишите чуть подробнее — хотя бы 1–2 предложения.")
        return
    await state.update_data(request_text=text)
    await state.set_state(BriefForm.main_pain)
    await message.answer(BRIEF_Q3, parse_mode="HTML", reply_markup=pain_menu())


async def cb_pain(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(":", 1)[1]
    label = PAIN_LABELS.get(key, key)
    await state.update_data(main_pain=label)
    await state.set_state(BriefForm.platform)
    await callback.answer()
    await callback.message.edit_text(BRIEF_Q4, parse_mode="HTML", reply_markup=platform_menu())


async def cb_platform(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(":", 1)[1]
    label = PLATFORM_LABELS.get(key, key)
    await state.update_data(platform=label)
    await state.set_state(BriefForm.scale)
    await callback.answer()
    await callback.message.edit_text(BRIEF_Q5, parse_mode="HTML")
    await callback.message.answer("Можно написать текстом или нажать «Пропустить».", reply_markup=skip_keyboard())


async def brief_scale(message: Message, state: FSMContext, bot: Bot, settings: Settings) -> None:
    scale = message.text.strip()
    if scale.lower() == "пропустить":
        scale = "не указано"
    await finish_brief(message, state, bot, settings, scale)


async def finish_brief(message: Message, state: FSMContext, bot: Bot, settings: Settings, scale: str) -> None:
    data = await state.get_data()
    data["scale"] = scale
    user = message.from_user

    save_brief(user.id, data)
    await notify_admin(
        bot,
        settings,
        format_lead_alert(user, data.get("source", ""), data),
    )

    await state.clear()
    await message.answer("Готово!", reply_markup=remove_keyboard())
    await message.answer(BRIEF_DONE, parse_mode="HTML", reply_markup=after_brief_menu(settings))


def setup_handlers(dp: Dispatcher, settings: Settings) -> None:
    @dp.message(CommandStart())
    async def _(message: Message, state: FSMContext, bot: Bot):
        await cmd_start(message, state, bot, settings)

    @dp.callback_query(F.data == Cb.MAIN_MENU)
    async def _(callback: CallbackQuery, state: FSMContext):
        await cb_main_menu(callback, state, settings)

    @dp.callback_query(F.data == Cb.FAQ_MENU)
    async def _(callback: CallbackQuery):
        await cb_faq_menu(callback)

    @dp.callback_query(F.data.startswith("faq:"))
    async def _(callback: CallbackQuery):
        await cb_faq_item(callback)

    @dp.callback_query(F.data == Cb.SOLUTIONS)
    async def _(callback: CallbackQuery):
        await cb_solutions(callback, settings)

    @dp.callback_query(F.data == Cb.AUDIT_FLOW)
    async def _(callback: CallbackQuery):
        await cb_audit_flow(callback)

    @dp.callback_query(F.data == Cb.BRIEF_START)
    async def _(callback: CallbackQuery, state: FSMContext):
        await cb_brief_start(callback, state)

    @dp.callback_query(BriefForm.main_pain, F.data.startswith("pain:"))
    async def _(callback: CallbackQuery, state: FSMContext):
        await cb_pain(callback, state)

    @dp.callback_query(BriefForm.platform, F.data.startswith("platform:"))
    async def _(callback: CallbackQuery, state: FSMContext):
        await cb_platform(callback, state)

    @dp.message(BriefForm.project_link)
    async def _(message: Message, state: FSMContext):
        await brief_project_link(message, state)

    @dp.message(BriefForm.request_text)
    async def _(message: Message, state: FSMContext):
        await brief_request_text(message, state)

    @dp.message(BriefForm.scale)
    async def _(message: Message, state: FSMContext, bot: Bot):
        await brief_scale(message, state, bot, settings)

    @dp.message(Command("menu"))
    async def _(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu(settings))

    @dp.message(F.text)
    async def _(message: Message, state: FSMContext):
        if await state.get_state() is None:
            await message.answer(
                "Используйте кнопки меню или команду /menu.\n"
                "Если вопрос срочный — «Написать основателю» в меню.",
                reply_markup=main_menu(settings),
            )


async def main() -> None:
    settings = get_settings()
    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    setup_handlers(dp, settings)

    logger.info("Бот VnedriAI запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
