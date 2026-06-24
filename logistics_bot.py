import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import quote
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВИТИ_ТОКЕН")
HR_USERNAME = "transrf_hr"

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
    "Напишите нашему HR-менеджеру. Это займёт 2 минуты.\n\n"
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


def vacancy_keyboard(vac_id):
    text = quote("Привет! Хочу узнать подробнее о вакансии", safe="")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ Написать HR", url=f"https://t.me/{HR_USERNAME}?text={text}")],
        [InlineKeyboardButton("← Все вакансии", callback_data="back")],
    ])


def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("← Все вакансии", callback_data="back")]
    ])


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
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

    if query.data == "about":
        await query.edit_message_text(
            COMPANY_ABOUT,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
        return

    if query.data == "how_to_start":
        await query.edit_message_text(
            HOW_TO_START,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
        return

    if query.data == "faq":
        await query.edit_message_text(
            FAQ,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
        return

    if query.data == "cities":
        await query.edit_message_text(
            CITIES,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
        return

    if query.data == "back":
        await query.edit_message_text(
            f"Актуальные вакансии <b>{COMPANY_NAME}</b>. Выберите интересующую:",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )
        return

    vac = VACANCIES.get(query.data)
    if not vac:
        return

    await query.edit_message_text(
        f"{vac['icon']} <b>{vac['title']}</b>\n"
        f"💰 {vac['salary']}  |  📍 {vac['location']}  |  🕐 {vac['schedule']}\n\n"
        f"<b>Обязанности:</b>\n{vac['duties']}\n\n"
        f"<b>Требования:</b>\n{vac['requirements']}\n\n"
        f"<b>Условия:</b>\n{vac['conditions']}\n\n"
        "Остались вопросы или хотите откликнуться? Напишите нашему HR-менеджеру 👇",
        parse_mode="HTML",
        reply_markup=vacancy_keyboard(query.data)
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle))
    logger.info("Бот запущено")
    app.run_polling()


if __name__ == "__main__":
    main()
