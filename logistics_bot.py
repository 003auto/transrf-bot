import logging
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВИТИ_ТОКЕН")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID", "ВСТАВИТИ_CHAT_ID_МЕНЕДЖЕРА")

COMPANY_NAME = "ТрансРФ"
COMPANY_DESC = "Федеральная транспортная компания. Работаем с 2015 года, 12 региональных офисов."

VACANCIES = {
    "v1": {
        "title": "Специалист по сопровождению грузоперевозок",
        "salary": "от 65 000 ₽", "schedule": "5/2, гибкое начало дня", "location": "Москва",
        "duties": "• Организация и сопровождение процессов грузоперевозок\n• Работа с утверждёнными маршрутами\n• Контроль состояния груза на всех этапах",
        "requirements": "• Понимание устройства автомобиля\n• Грамотная устная и письменная речь\n• Стрессоустойчивость, ответственность",
        "conditions": "• Фиксированный оклад + прозрачная бонусная система\n• Официальное оформление с первого дня\n• Обучение и адаптация на старте\n• Стабильные выплаты без задержек",
    },
    "v2": {
        "title": "Координатор транспортных процессов",
        "salary": "от 70 000 ₽", "schedule": "5/2", "location": "Москва",
        "duties": "• Координация водителей и транспортных бригад\n• Согласование маршрутов и сроков доставки\n• Взаимодействие с клиентами по статусу заказов",
        "requirements": "• Опыт в логистике или транспорте от 6 месяцев\n• Умение работать в режиме многозадачности\n• Уверенный пользователь ПК",
        "conditions": "• Оклад + KPI-бонус\n• Официальное трудоустройство\n• Корпоративная связь\n• Карьерный рост внутри компании",
    },
    "v3": {
        "title": "Оператор транспортного отдела",
        "salary": "от 58 000 ₽", "schedule": "5/2 или 2/2 (на выбор)", "location": "Москва",
        "duties": "• Приём и обработка заявок на перевозку\n• Ведение реестра рейсов и документации\n• Коммуникация с водителями и клиентами",
        "requirements": "• Без опыта — обучаем\n• Внимательность, аккуратность\n• Желание развиваться в логистике",
        "conditions": "• Стабильный оклад\n• Полное обучение за счёт компании\n• Официальное оформление\n• Молодой дружный коллектив",
    },
}

# Флоу: місто → вік → зайнятість → переїзд → досвід → права → телефон → час дзвінка
(CHOOSING_VACANCY, VACANCY_DETAIL,
 ASK_CITY, ASK_AGE, ASK_EMPLOYMENT,
 ASK_RELOCATION, ASK_EXPERIENCE,
 ASK_LICENSE, ASK_PHONE, ASK_CALL_TIME) = range(10)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_valid_ru_phone(phone: str) -> bool:
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(r'^(\+7|8|7)\d{10}$', cleaned))


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


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Здравствуйте, {user.first_name}! 👋\n\n"
        f"Вы обратились в HR-отдел компании <b>{COMPANY_NAME}</b>.\n"
        f"{COMPANY_DESC}\n\n"
        "Ниже — наши актуальные вакансии. Выберите интересующую:",
        parse_mode="HTML", reply_markup=vacancies_keyboard()
    )
    return CHOOSING_VACANCY


async def show_vacancy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            f"<b>О компании {COMPANY_NAME}</b>\n\n{COMPANY_DESC}\n\n"
            "• Официальное трудоустройство по ТК РФ\n"
            "• Своевременная выплата заработной платы\n"
            "• Развитая система обучения и адаптации\n"
            "• Представительства в 12 городах России",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Все вакансии", callback_data="back")]])
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
    await query.edit_message_text(
        f"<b>{vac['title']}</b>\n"
        f"💰 {vac['salary']}  |  📍 {vac['location']}  |  🕐 {vac['schedule']}\n\n"
        f"<b>Обязанности:</b>\n{vac['duties']}\n\n"
        f"<b>Требования:</b>\n{vac['requirements']}\n\n"
        f"<b>Условия работы:</b>\n{vac['conditions']}",
        parse_mode="HTML",
        reply_markup=vacancy_action_keyboard(query.data)
    )
    return VACANCY_DETAIL


async def apply_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data["selected_vacancy"] = query.data.replace("apply_", "")
    await query.edit_message_text(
        "Отлично! Давайте познакомимся — это займёт меньше минуты.\n\n"
        "📍 В каком городе вы находитесь?"
    )
    return ASK_CITY


async def got_city(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["city"] = update.message.text
    await update.message.reply_text("Сколько вам лет?")
    return ASK_AGE


async def got_age(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    age_text = update.message.text.strip()
    if not age_text.isdigit() or not (16 <= int(age_text) <= 70):
        await update.message.reply_text("⚠️ Укажите возраст цифрами (например: 25)")
        return ASK_AGE
    ctx.user_data["age"] = age_text
    await update.message.reply_text(
        "Какой формат занятости вас интересует?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Полная занятость 5/2", callback_data="emp_full")],
            [InlineKeyboardButton("Сменный график 2/2", callback_data="emp_shift")],
            [InlineKeyboardButton("Подработка / частичная", callback_data="emp_part")],
        ])
    )
    return ASK_EMPLOYMENT


async def got_employment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    emp_map = {
        "emp_full": "Полная занятость 5/2",
        "emp_shift": "Сменный график 2/2",
        "emp_part": "Подработка / частичная",
    }
    ctx.user_data["employment"] = emp_map.get(query.data, "—")
    await query.edit_message_text(
        "Готовы ли вы к командировкам или работе в другом городе?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Да, готов", callback_data="rel_yes")],
            [InlineKeyboardButton("Только свой город", callback_data="rel_no")],
        ])
    )
    return ASK_RELOCATION


async def got_relocation(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data["relocation"] = "Да" if query.data == "rel_yes" else "Только свой город"
    await query.edit_message_text(
        "Есть ли у вас опыт работы в логистике или транспортной сфере?\n\n"
        "Напишите коротко: например «есть, 2 года» или «нет, готов обучаться»"
    )
    return ASK_EXPERIENCE


async def got_experience(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["experience"] = update.message.text
    await update.message.reply_text(
        "🚗 Есть ли у вас водительское удостоверение? Выберите категорию:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("B", callback_data="lic_B"),
             InlineKeyboardButton("C", callback_data="lic_C"),
             InlineKeyboardButton("D", callback_data="lic_D")],
            [InlineKeyboardButton("B+C", callback_data="lic_BC"),
             InlineKeyboardButton("C+E", callback_data="lic_CE")],
            [InlineKeyboardButton("Нет прав", callback_data="lic_none")],
        ])
    )
    return ASK_LICENSE


async def got_license(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    license_map = {
        "lic_B": "B", "lic_C": "C", "lic_D": "D",
        "lic_BC": "B+C", "lic_CE": "C+E", "lic_none": "Нет"
    }
    ctx.user_data["license"] = license_map.get(query.data, "—")
    await query.edit_message_text(
        "📞 Укажите ваш номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX"
    )
    return ASK_PHONE


async def got_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not is_valid_ru_phone(phone):
        await update.message.reply_text(
            "⚠️ Пожалуйста, укажите российский номер телефона.\n\n"
            "Формат: +7XXXXXXXXXX или 8XXXXXXXXXX"
        )
        return ASK_PHONE
    ctx.user_data["phone"] = phone
    await update.message.reply_text(
        "🕐 В какое время вам удобно принять звонок от HR-менеджера?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("9:00–12:00", callback_data="time_morning"),
             InlineKeyboardButton("12:00–15:00", callback_data="time_midday")],
            [InlineKeyboardButton("15:00–18:00", callback_data="time_evening"),
             InlineKeyboardButton("В любое время", callback_data="time_any")],
        ])
    )
    return ASK_CALL_TIME


async def got_call_time(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    time_map = {
        "time_morning": "9:00–12:00", "time_midday": "12:00–15:00",
        "time_evening": "15:00–18:00", "time_any": "В любое время",
    }
    ctx.user_data["call_time"] = time_map.get(query.data, "—")

    user = update.effective_user
    vac_id = ctx.user_data.get("selected_vacancy", "—")
    vac = VACANCIES.get(vac_id, {})

    manager_text = (
        f"📥 <b>Новая заявка</b>\n\n"
        f"👤 {user.full_name} (@{user.username or '—'})\n"
        f"🆔 ID: {user.id}\n\n"
        f"🚚 Вакансия: {vac.get('title', vac_id)}\n"
        f"📍 Город: {ctx.user_data.get('city', '—')}\n"
        f"🎂 Возраст: {ctx.user_data.get('age', '—')}\n"
        f"💼 Занятость: {ctx.user_data.get('employment', '—')}\n"
        f"✈️ Командировки: {ctx.user_data.get('relocation', '—')}\n"
        f"📋 Опыт: {ctx.user_data.get('experience', '—')}\n"
        f"🚗 Права: {ctx.user_data.get('license', '—')}\n"
        f"📞 Телефон: {ctx.user_data.get('phone', '—')}\n"
        f"🕐 Удобное время: {ctx.user_data.get('call_time', '—')}"
    )

    try:
        await ctx.bot.send_message(chat_id=MANAGER_CHAT_ID, text=manager_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Помилка відправки: {e}")

    await query.edit_message_text(
        "✅ Заявка принята!\n\n"
        "Наш HR-менеджер рассмотрит вашу кандидатуру и свяжется с вами "
        "в удобное для вас время (пн–пт, 9:00–18:00 МСК).\n\n"
        "Если возникнут вопросы — напишите /start для возврата в меню.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Посмотреть другие вакансии", callback_data="show_vacancies")]
        ])
    )
    return ConversationHandler.END


async def show_vacancies_after_end(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Актуальные вакансии компании. Выберите интересующую:",
        reply_markup=vacancies_keyboard()
    )


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо. Если захотите вернуться — напишите /start")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("cancel", cancel),
        ],
        states={
            CHOOSING_VACANCY: [CallbackQueryHandler(show_vacancy)],
            VACANCY_DETAIL: [
                CallbackQueryHandler(apply_start, pattern="^apply_"),
                CallbackQueryHandler(show_vacancy),
            ],
            ASK_CITY:       [MessageHandler(filters.TEXT & ~filters.COMMAND, got_city)],
            ASK_AGE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, got_age)],
            ASK_EMPLOYMENT: [CallbackQueryHandler(got_employment, pattern="^emp_")],
            ASK_RELOCATION: [CallbackQueryHandler(got_relocation, pattern="^rel_")],
            ASK_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_experience)],
            ASK_LICENSE:    [CallbackQueryHandler(got_license, pattern="^lic_")],
            ASK_PHONE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, got_phone)],
            ASK_CALL_TIME:  [CallbackQueryHandler(got_call_time, pattern="^time_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(show_vacancies_after_end, pattern="^show_vacancies$"))

    logger.info("Бот запущено")
    app.run_polling()


if __name__ == "__main__":
    main()
