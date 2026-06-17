"""
Логістичний HR-бот для TG Ads
Стек: python-telegram-bot v20+
Встановлення: pip install python-telegram-bot==20.7

Запуск: python logistics_bot.py
Env: BOT_TOKEN і MANAGER_CHAT_ID в .env або задай напряму нижче
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ─── CONFIG ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВИТИ_ТОКЕН")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID", "ВСТАВИТИ_CHAT_ID_МЕНЕДЖЕРА")

COMPANY_NAME = "ТрансГрупп"
COMPANY_DESC = "Федеральная транспортная компания. Работаем с 2015 года, 12 региональных офисов."

VACANCIES = {
    "v1": {
        "title": "Специалист по сопровождению грузоперевозок",
        "salary": "от 65 000 ₽",
        "schedule": "5/2, гибкое начало дня",
        "location": "Москва",
        "duties": (
            "• Организация и сопровождение процессов грузоперевозок\n"
            "• Работа с утверждёнными маршрутами\n"
            "• Контроль состояния груза на всех этапах"
        ),
        "requirements": (
            "• Понимание устройства автомобиля\n"
            "• Грамотная устная и письменная речь\n"
            "• Стрессоустойчивость, ответственность"
        ),
        "conditions": (
            "• Фиксированный оклад + прозрачная бонусная система\n"
            "• Официальное оформление с первого дня\n"
            "• Обучение и адаптация на старте\n"
            "• Стабильные выплаты без задержек"
        ),
    },
    "v2": {
        "title": "Координатор транспортных процессов",
        "salary": "от 70 000 ₽",
        "schedule": "5/2",
        "location": "Москва",
        "duties": (
            "• Координация водителей и транспортных бригад\n"
            "• Согласование маршрутов и сроков доставки\n"
            "• Взаимодействие с клиентами по статусу заказов"
        ),
        "requirements": (
            "• Опыт в логистике или транспорте от 6 месяцев\n"
            "• Умение работать в режиме многозадачности\n"
            "• Уверенный пользователь ПК"
        ),
        "conditions": (
            "• Оклад + KPI-бонус\n"
            "• Официальное трудоустройство\n"
            "• Корпоративная связь\n"
            "• Карьерный рост внутри компании"
        ),
    },
    "v3": {
        "title": "Оператор транспортного отдела",
        "salary": "от 58 000 ₽",
        "schedule": "5/2 или 2/2 (на выбор)",
        "location": "Москва",
        "duties": (
            "• Приём и обработка заявок на перевозку\n"
            "• Ведение реестра рейсов и документации\n"
            "• Коммуникация с водителями и клиентами"
        ),
        "requirements": (
            "• Без опыта — обучаем\n"
            "• Внимательность, аккуратность\n"
            "• Желание развиваться в логистике"
        ),
        "conditions": (
            "• Стабильный оклад\n"
            "• Полное обучение за счёт компании\n"
            "• Официальное оформление\n"
            "• Молодой дружный коллектив"
        ),
    },
}

# ─── STATES ────────────────────────────────────────────────────────────────────
CHOOSING_VACANCY, VACANCY_DETAIL, ASK_CITY, ASK_EXPERIENCE, ASK_PHONE = range(5)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── KEYBOARDS ─────────────────────────────────────────────────────────────────
def vacancies_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🚚 {v['title']}", callback_data=k)]
        for k, v in VACANCIES.items()
    ] + [[InlineKeyboardButton("ℹ️ О компании", callback_data="about")]])


def vacancy_action_keyboard(vac_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Откликнуться", callback_data=f"apply_{vac_id}")],
        [InlineKeyboardButton("← Все вакансии", callback_data="back")],
    ])


# ─── HANDLERS ──────────────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"Здравствуйте, {user.first_name}! 👋\n\n"
        f"Вы обратились в HR-отдел компании <b>{COMPANY_NAME}</b>.\n"
        f"{COMPANY_DESC}\n\n"
        "Ниже — наши актуальные вакансии. Выберите интересующую:"
    )
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=vacancies_keyboard()
    )
    return CHOOSING_VACANCY


async def show_vacancy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            f"<b>О компании {COMPANY_NAME}</b>\n\n"
            f"{COMPANY_DESC}\n\n"
            "• Официальное трудоустройство по ТК РФ\n"
            "• Своевременная выплата заработной платы\n"
            "• Развитая система обучения и адаптации\n"
            "• Представительства в 12 городах России\n\n"
            "Для возврата к вакансиям нажмите кнопку ниже.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Все вакансии", callback_data="back")]
            ])
        )
        return CHOOSING_VACANCY

    if query.data == "back":
        await query.edit_message_text(
            "Актуальные вакансии компании. Выберите интересующую:",
            reply_markup=vacancies_keyboard()
        )
        return CHOOSING_VACANCY

    vac = VACANCIES.get(query.data)
    if not vac:
        return CHOOSING_VACANCY

    ctx.user_data["selected_vacancy"] = query.data

    text = (
        f"<b>{vac['title']}</b>\n"
        f"💰 {vac['salary']}  |  📍 {vac['location']}  |  🕐 {vac['schedule']}\n\n"
        f"<b>Обязанности:</b>\n{vac['duties']}\n\n"
        f"<b>Требования:</b>\n{vac['requirements']}\n\n"
        f"<b>Условия работы:</b>\n{vac['conditions']}"
    )
    await query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=vacancy_action_keyboard(query.data)
    )
    return VACANCY_DETAIL


async def apply_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    vac_id = query.data.replace("apply_", "")
    ctx.user_data["selected_vacancy"] = vac_id

    await query.edit_message_text(
        "Отлично! Давайте познакомимся.\n\n"
        "📍 В каком городе вы находитесь?"
    )
    return ASK_CITY


async def got_city(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["city"] = update.message.text
    await update.message.reply_text(
        "Есть ли у вас опыт работы в логистике или транспортной сфере?\n\n"
        "Напишите коротко: например «есть, 2 года» или «нет, готов обучаться»"
    )
    return ASK_EXPERIENCE


async def got_experience(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["experience"] = update.message.text
    await update.message.reply_text(
        "Почти готово! 📞\n\n"
        "Укажите ваш номер телефона — наш HR-менеджер свяжется с вами в течение рабочего дня."
    )
    return ASK_PHONE


async def got_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["phone"] = update.message.text
    user = update.effective_user
    vac_id = ctx.user_data.get("selected_vacancy", "—")
    vac = VACANCIES.get(vac_id, {})

    # Повідомлення менеджеру
    manager_text = (
        f"📥 <b>Новая заявка</b>\n\n"
        f"👤 {user.full_name} (@{user.username or '—'})\n"
        f"🆔 ID: {user.id}\n\n"
        f"🚚 Вакансия: {vac.get('title', vac_id)}\n"
        f"📍 Город: {ctx.user_data.get('city', '—')}\n"
        f"💼 Опыт: {ctx.user_data.get('experience', '—')}\n"
        f"📞 Телефон: {ctx.user_data.get('phone', '—')}"
    )

    try:
        await ctx.bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=manager_text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не вдалось надіслати менеджеру: {e}")

    await update.message.reply_text(
        "✅ Заявка принята!\n\n"
        "Наш HR-менеджер рассмотрит вашу кандидатуру и свяжется с вами сегодня "
        "в рабочее время (пн–пт, 9:00–18:00 МСК).\n\n"
        "Если возникнут вопросы — напишите /start для возврата в меню.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Посмотреть другие вакансии", callback_data="restart")]
        ])
    )
    return ConversationHandler.END


async def restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Актуальные вакансии компании. Выберите интересующую:",
        reply_markup=vacancies_keyboard()
    )
    return CHOOSING_VACANCY


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо. Если захотите вернуться — напишите /start"
    )
    return ConversationHandler.END


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_VACANCY: [CallbackQueryHandler(show_vacancy)],
            VACANCY_DETAIL: [CallbackQueryHandler(show_vacancy)],
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_city)],
            ASK_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_experience)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_phone)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(restart, pattern="^restart$"),
        ],
    )

    app.add_handler(conv)
    logger.info("Бот запущено")
    app.run_polling()


if __name__ == "__main__":
    main()
