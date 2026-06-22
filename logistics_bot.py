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

COMPANY_NAME = "КурьерПро"
COMPANY_DESC = "Сервис курьерской доставки. Работаем по всему городу, выплаты каждую неделю."

VACANCIES = {
    "v1": {
        "title": "Пеший курьер",
        "salary": "3 500–6 000 ₽ за смену", "schedule": "Гибкий, смены 8–10 часов", "location": "Москва",
        "duties": "• Доставка заказов пешком в пределах района\n• Приём и передача посылок по маршруту\n• Подтверждение доставки через приложение",
        "requirements": "• Без опыта — обучаем\n• Смартфон с навигацией\n• Ответственность и пунктуальность",
        "conditions": "• 3 500–6 000 ₽ за смену 8–10 часов\n• Выплаты каждую неделю\n• Гибкий выбор смен через приложение\n• Оформление с первого дня",
    },
    "v2": {
        "title": "Велокурьер / электровелосипед",
        "salary": "4 500–8 000 ₽ за смену", "schedule": "Гибкий, смены 8–10 часов", "location": "Москва",
        "duties": "• Доставка заказов на велосипеде или электровелосипеде\n• Работа по оптимизированным маршрутам\n• Подтверждение доставки через приложение",
        "requirements": "• Свой велосипед или электровелосипед\n• Умение уверенно ездить в городе\n• Смартфон с навигацией",
        "conditions": "• 4 500–8 000 ₽ за смену, в пиковые дни выше\n• Выплаты каждую неделю\n• Гибкий выбор смен\n• Оформление с первого дня",
    },
    "v3": {
        "title": "Автокурьер",
        "salary": "5 000–9 000 ₽ за смену", "schedule": "Гибкий, смены 8–10 часов", "location": "Москва",
        "duties": "• Доставка заказов на личном автомобиле\n• Работа по маршрутам с несколькими точками\n• Подтверждение доставки через приложение",
        "requirements": "• Личный автомобиль и водительское удостоверение кат. B\n• Опыт вождения в городе\n• Смартфон с навигацией",
        "conditions": "• 5 000–9 000 ₽ за смену, при высокой загрузке больше\n• Компенсация топлива\n• Выплаты каждую неделю\n• Оформление с первого дня",
    },
}

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
    icons = {"v1": "🚶", "v2": "🚴", "v3": "🚗"}
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{icons.get(k,'📦')} {v['title']}", callback_data=k)]
        for k, v in VACANCIES.items()
    ] + [[InlineKeyboardButton("ℹ️ О компании", callback_data="about")]])


def vacancy_action_keyboard(vac_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Откликнуться", callback_data=f"apply_{vac_id}")],
        [InlineKeyboardButton("← Все вакансии", callback_data="back")],
    ])


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
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
            "• Официальное оформление с первого дня\n"
            "• Выплаты каждую неделю без задержек\n"
            "• Гибкий выбор смен через приложение\n"
            "• Работа по всему городу",
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
        "emp_full": "Полная занятость",
        "emp_shift": "Сменный график",
        "emp_part": "Подработка / частичная",
    }
    ctx.user_data["employment"] = emp_map.get(query.data, "—")
    vac_id = ctx.user_data.get("selected_vacancy", "")
    if vac_id == "v2":
        await query.edit_message_text(
            "🚴 Есть ли у вас свой велосипед или электровелосипед?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Да, велосипед", callback_data="exp_bike")],
                [InlineKeyboardButton("Да, электровелосипед", callback_data="exp_ebike")],
                [InlineKeyboardButton("Нет", callback_data="exp_none")],
            ])
        )
    else:
        await query.edit_message_text(
            "Есть ли у вас опыт работы курьером?\n\n"
            "Напишите коротко: например «есть, 6 месяцев» или «нет, готов начать»"
        )
    return ASK_EXPERIENCE


async def got_relocation(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Not used for couriers — kept for compatibility
    query = update.callback_query
    await query.answer()
    ctx.user_data["relocation"] = "—"
    await query.edit_message_text(
        "Есть ли у вас опыт работы курьером?\n\n"
        "Напишите коротко: например «есть, 6 месяцев» или «нет, готов начать»"
    )
    return ASK_EXPERIENCE


async def got_experience(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Handle both callback (bike selection) and text message
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        bike_map = {"exp_bike": "Велосипед", "exp_ebike": "Электровелосипед", "exp_none": "Нет своего транспорта"}
        ctx.user_data["experience"] = bike_map.get(query.data, "—")
        await query.edit_message_text(
            "📞 Укажите ваш номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX"
        )
        return ASK_PHONE
    else:
        ctx.user_data["experience"] = update.message.text
        vac_id = ctx.user_data.get("selected_vacancy", "")
        if vac_id == "v3":
            await update.message.reply_text(
                "🚗 Есть ли у вас водительское удостоверение кат. B?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Да, кат. B", callback_data="lic_B")],
                    [InlineKeyboardButton("B+C", callback_data="lic_BC")],
                    [InlineKeyboardButton("Нет прав", callback_data="lic_none")],
                ])
            )
            return ASK_LICENSE
        else:
            ctx.user_data["license"] = "Не требуется"
            await update.message.reply_text(
                "📞 Укажите ваш номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX"
            )
            return ASK_PHONE


async def got_license(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    license_map = {
        "lic_B": "B", "lic_BC": "B+C", "lic_none": "Нет"
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
        f"📦 Вакансия: {vac.get('title', vac_id)}\n"
        f"📍 Город: {ctx.user_data.get('city', '—')}\n"
        f"🎂 Возраст: {ctx.user_data.get('age', '—')}\n"
        f"💼 Занятость: {ctx.user_data.get('employment', '—')}\n"
        f"📋 Опыт / транспорт: {ctx.user_data.get('experience', '—')}\n"
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
        "Чтобы вернуться в меню — нажмите /start"
    )
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("Хорошо. Если захотите вернуться — напишите /start")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
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
            ASK_EXPERIENCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_experience),
                CallbackQueryHandler(got_experience, pattern="^exp_"),
            ],
            ASK_LICENSE:    [CallbackQueryHandler(got_license, pattern="^lic_")],
            ASK_PHONE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, got_phone)],
            ASK_CALL_TIME:  [CallbackQueryHandler(got_call_time, pattern="^time_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    logger.info("Бот запущено")
    app.run_polling()


if __name__ == "__main__":
    main()
