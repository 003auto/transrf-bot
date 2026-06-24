import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВИТИ_ТОКЕН")
ADMIN_ID = 7831988668

COMPANY_NAME = "ТрансРФ"

COMPANY_ABOUT = (
    "<b>О компании ТрансРФ</b>\n\n"
    "ТрансРФ — федеральная курьерская служба с многолетней историей. "
    "Мы начинали с нескольких городов, а сегодня работаем во всех крупных городах России: "
    "Москва, Санкт-Петербург, Екатеринбург, Новосибирск, Казань, Краснодар, "
    "Нижний Новгород и десятки региональных центров.\n\n"
    "В нашем штате более 5 000 курьеров по всей стране. "
    "Ежедневно мы выполняем тысячи доставок — от небольших посылок до крупногабаритных грузов.\n\n"
    "<b>Почему выбирают нас:</b>\n"
    "• Стабильные выплаты каждую неделю без задержек\n"
    "• Гибкий график — сам выбираешь смены\n"
    "• Официальное оформление с первого дня\n"
    "• Собственный транспорт компании для тех, у кого нет своего\n"
    "• Поддержка и обучение на старте — выходишь на маршрут уже через день"
)

HOW_TO_START = (
    "<b>Как начать работу в ТрансРФ</b>\n\n"
    "<b>Шаг 1 — Отклик</b>\n"
    "Оставьте заявку прямо в боте. Это займёт 2 минуты.\n\n"
    "<b>Шаг 2 — Оформление</b>\n"
    "Официальное трудоустройство с первого дня. "
    "Никаких серых схем — только белая зарплата.\n\n"
    "<b>Шаг 3 — Инструктаж</b>\n"
    "Короткое обучение работе с приложением и маршрутами. "
    "Занимает несколько часов.\n\n"
    "<b>Шаг 4 — Первая смена</b>\n"
    "Уже на следующий день выходишь на маршрут и начинаешь зарабатывать.\n\n"
    "💰 Первая выплата — через 7 дней после начала работы."
)

FAQ = (
    "<b>Частые вопросы</b>\n\n"
    "<b>Нужен ли опыт?</b>\n"
    "Нет. Мы обучаем всех с нуля. Главное — ответственность и смартфон.\n\n"
    "<b>Как происходят выплаты?</b>\n"
    "Каждую неделю на карту. Без задержек и серых схем.\n\n"
    "<b>Можно ли выбирать смены?</b>\n"
    "Да. Вы сами выбираете удобные дни и время через приложение.\n\n"
    "<b>Нужен ли свой транспорт?</b>\n"
    "Для пешего курьера — нет. Для авто/вело — можно использовать транспорт компании.\n\n"
    "<b>Есть ли официальное оформление?</b>\n"
    "Да, с первого рабочего дня. Трудовой договор, все отчисления.\n\n"
    "<b>В каких городах есть работа?</b>\n"
    "Москва, Санкт-Петербург, Екатеринбург, Новосибирск, Казань, Краснодар, "
    "Нижний Новгород, Самара, Ростов-на-Дону, Уфа, Пермь, Воронеж и другие города России."
)

CITIES = (
    "<b>Города присутствия ТрансРФ</b>\n\n"
    "<b>Центральный федеральный округ:</b>\n"
    "Москва, Воронеж, Тула, Рязань, Ярославль\n\n"
    "<b>Северо-Западный:</b>\n"
    "Санкт-Петербург, Калининград, Мурманск, Архангельск\n\n"
    "<b>Приволжский:</b>\n"
    "Нижний Новгород, Казань, Самара, Уфа, Пермь, Саратов\n\n"
    "<b>Уральский:</b>\n"
    "Екатеринбург, Челябинск, Тюмень\n\n"
    "<b>Сибирский:</b>\n"
    "Новосибирск, Омск, Красноярск, Иркутск\n\n"
    "<b>Южный:</b>\n"
    "Краснодар, Ростов-на-Дону, Волгоград\n\n"
    "Не нашли свой город? Уточните у HR — список постоянно расширяется."
)

VACANCIES = {
    "v1": {
        "icon": "🚶",
        "title": "Пеший курьер",
        "salary": "3 500–6 000 ₽ за смену",
        "schedule": "Гибкий, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Доставка заказов пешком в пределах района\n• Приём и передача посылок получателю\n• Подтверждение доставки через приложение",
        "requirements": "• Без опыта — обучаем\n• Смартфон с навигацией\n• Ответственность и пунктуальность",
        "conditions": "• 3 500–6 000 ₽ за смену\n• Выплаты каждую неделю\n• Гибкий выбор смен\n• Оформление с первого дня",
    },
    "v2": {
        "icon": "🚴",
        "title": "Курьер на велосипеде / самокате / СИМ",
        "salary": "4 500–8 000 ₽ за смену",
        "schedule": "Гибкий, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Доставка заказов на личном или корпоративном транспорте\n• Работа по оптимизированным маршрутам\n• Подтверждение доставки через приложение",
        "requirements": "• Велосипед, самокат или СИМ — свой или компании\n• Уверенное вождение в городе\n• Смартфон с навигацией",
        "conditions": "• 4 500–8 000 ₽ за смену, в пиковые дни выше\n• Выплаты каждую неделю\n• Гибкий выбор смен\n• Оформление с первого дня",
    },
    "v3": {
        "icon": "🚗",
        "title": "Курьер на авто / мото",
        "salary": "5 000–9 000 ₽ за смену",
        "schedule": "Гибкий, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Доставка заказов на автомобиле или мотоцикле\n• Работа по маршрутам с несколькими точками\n• Подтверждение доставки через приложение",
        "requirements": "• Водительское удостоверение кат. B (авто) или A (мото)\n• Опыт вождения в городе\n• Смартфон с навигацией",
        "conditions": "• 5 000–9 000 ₽ за смену, при высокой загрузке больше\n• Свой транспорт с компенсацией топлива или транспорт компании\n• Выплаты каждую неделю\n• Оформление с первого дня",
    },
}

QUIZ_QUESTIONS = [
    {
        "text": "Шаг 1 из 4\n\n<b>Укажите ваш возраст:</b>",
        "key": "age",
        "options": [
            ("До 18 лет", "до 18"),
            ("18–25 лет", "18–25"),
            ("26–35 лет", "26–35"),
            ("36–45 лет", "36–45"),
            ("45+ лет", "45+"),
        ]
    },
    {
        "text": "Шаг 2 из 4\n\n<b>Есть ли у вас смартфон с навигацией?</b>",
        "key": "smartphone",
        "options": [
            ("Да", "да"),
            ("Нет", "нет"),
        ]
    },
    {
        "text": "Шаг 3 из 4\n\n<b>Вы работали курьером раньше?</b>",
        "key": "experience",
        "options": [
            ("Да, есть опыт", "да"),
            ("Нет, первый раз", "нет"),
        ]
    },
    {
        "text": "Шаг 4 из 4\n\n<b>Когда готовы приступить к работе?</b>",
        "key": "start",
        "options": [
            ("Готов прямо сейчас", "сейчас"),
            ("Через неделю", "через неделю"),
            ("В течение месяца", "в течение месяца"),
        ]
    },
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"{v['icon']} {v['title']}", callback_data=k)]
         for k, v in VACANCIES.items()] +
        [
            [InlineKeyboardButton("🏢 О компании", callback_data="about"),
             InlineKeyboardButton("📍 Города", callback_data="cities")],
            [InlineKeyboardButton("🚀 Как начать работу", callback_data="how_to_start")],
            [InlineKeyboardButton("❓ Частые вопросы", callback_data="faq")],
        ]
    )


def quiz_keyboard(vac_id, question_index):
    question = QUIZ_QUESTIONS[question_index]
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"quiz_{vac_id}_{question_index}_{value}")]
        for label, value in question["options"]
    ]
    return InlineKeyboardMarkup(buttons)


def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("← Все вакансии", callback_data="back")]
    ])


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ctx.user_data.clear()
    await update.message.reply_text(
        f"Здравствуйте, {user.first_name}! 👋\n\n"
        f"Вы обратились в HR-отдел компании <b>{COMPANY_NAME}</b>.\n\n"
        "Федеральная курьерская служба.\n"
        "Более 5 000 курьеров по всей России.\n\n"
        "Выберите интересующую вакансию или узнайте подробнее о работе у нас:",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "about":
        await query.edit_message_text(COMPANY_ABOUT, parse_mode="HTML", reply_markup=back_keyboard())
        return

    if data == "how_to_start":
        await query.edit_message_text(HOW_TO_START, parse_mode="HTML", reply_markup=back_keyboard())
        return

    if data == "faq":
        await query.edit_message_text(FAQ, parse_mode="HTML", reply_markup=back_keyboard())
        return

    if data == "cities":
        await query.edit_message_text(CITIES, parse_mode="HTML", reply_markup=back_keyboard())
        return

    if data == "back":
        ctx.user_data.clear()
        await query.edit_message_text(
            f"Актуальные вакансии <b>{COMPANY_NAME}</b>. Выберите интересующую:",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )
        return

    # Выбор вакансии — карточка + первый вопрос
    if data in VACANCIES:
        vac = VACANCIES[data]
        ctx.user_data["vac_id"] = data
        ctx.user_data["answers"] = {}
        await query.edit_message_text(
            f"{vac['icon']} <b>{vac['title']}</b>\n"
            f"💰 {vac['salary']}  |  📍 {vac['location']}  |  🕐 {vac['schedule']}\n\n"
            f"<b>Обязанности:</b>\n{vac['duties']}\n\n"
            f"<b>Требования:</b>\n{vac['requirements']}\n\n"
            f"<b>Условия:</b>\n{vac['conditions']}\n\n"
            "—\n\n"
            "Ответьте на 4 быстрых вопроса, и мы свяжемся с вами в течение 15 минут 👇\n\n"
            + QUIZ_QUESTIONS[0]["text"],
            parse_mode="HTML",
            reply_markup=quiz_keyboard(data, 0)
        )
        return

    # Ответы на вопросы квиза
    if data.startswith("quiz_"):
        parts = data.split("_", 3)
        _, vac_id, q_idx_str, answer = parts
        q_idx = int(q_idx_str)

        if "answers" not in ctx.user_data:
            ctx.user_data["answers"] = {}

        ctx.user_data["answers"][QUIZ_QUESTIONS[q_idx]["key"]] = answer
        ctx.user_data["vac_id"] = vac_id

        next_q = q_idx + 1

        if next_q < len(QUIZ_QUESTIONS):
            await query.edit_message_text(
                QUIZ_QUESTIONS[next_q]["text"],
                parse_mode="HTML",
                reply_markup=quiz_keyboard(vac_id, next_q)
            )
            return

        # Квиз завершён — отправляем заявку админу
        vac = VACANCIES[vac_id]
        answers = ctx.user_data["answers"]
        user = query.from_user

        username = f"@{user.username}" if user.username else "нет username"
        full_name = user.full_name or "—"

        admin_message = (
            f"📋 <b>Новая заявка — {COMPANY_NAME}</b>\n\n"
            f"👤 Имя: {full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 ID: <code>{user.id}</code>\n\n"
            f"💼 Вакансия: {vac['icon']} {vac['title']}\n"
            f"📅 Возраст: {answers.get('age', '—')}\n"
            f"📱 Смартфон с навигацией: {answers.get('smartphone', '—')}\n"
            f"🚴 Опыт курьера: {answers.get('experience', '—')}\n"
            f"⏰ Готов приступить: {answers.get('start', '—')}"
        )

        await query.get_bot().send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="HTML"
        )

        # Сообщение пользователю
        await query.edit_message_text(
            "✅ <b>Заявка принята!</b>\n\n"
            f"Вы откликнулись на вакансию: <b>{vac['icon']} {vac['title']}</b>\n\n"
            "Наш HR-менеджер свяжется с вами в течение 15 минут.\n\n"
            "Ожидайте сообщения в Telegram 📲",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← На главную", callback_data="back")]
            ])
        )
        return


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle))
    logger.info("Бот запущено")
    app.run_polling()


if __name__ == "__main__":
    main()
