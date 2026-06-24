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
    "В нашем штате более 5 000 сотрудников по всей стране. "
    "Ежедневно мы выполняем тысячи доставок — от небольших посылок до крупногабаритных грузов.\n\n"
    "<b>Почему выбирают нас:</b>\n"
    "• Стабильные выплаты каждую неделю без задержек\n"
    "• Гибкий график — сам выбираешь смены\n"
    "• Официальное оформление с первого дня\n"
    "• Собственный транспорт компании для тех, у кого нет своего\n"
    "• Поддержка и обучение на старте — выходишь на работу уже через день"
)

HOW_TO_START = (
    "<b>Как начать работу в ТрансРФ</b>\n\n"
    "<b>Шаг 1 — Отклик</b>\n"
    "Оставьте заявку прямо в боте. Это займёт 2 минуты.\n\n"
    "<b>Шаг 2 — Оформление</b>\n"
    "Официальное трудоустройство с первого дня. "
    "Никаких серых схем — только белая зарплата.\n\n"
    "<b>Шаг 3 — Инструктаж</b>\n"
    "Короткое обучение. Занимает несколько часов.\n\n"
    "<b>Шаг 4 — Первый рабочий день</b>\n"
    "Уже на следующий день приступаешь к работе и начинаешь зарабатывать.\n\n"
    "💰 Первая выплата — через 7 дней после начала работы."
)

FAQ = (
    "<b>Частые вопросы</b>\n\n"
    "<b>Нужен ли опыт?</b>\n"
    "Нет. Мы обучаем всех с нуля.\n\n"
    "<b>Как происходят выплаты?</b>\n"
    "Каждую неделю на карту. Без задержек и серых схем.\n\n"
    "<b>Можно ли выбирать смены?</b>\n"
    "Да. Вы сами выбираете удобные дни и время.\n\n"
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

CATEGORIES = {
    "cat_courier": "🚴 Вакансии курьером",
    "cat_warehouse": "📦 Вакансии на складе",
    "cat_office": "🏢 Вакансии в офисе",
}

VACANCIES = {
    # Курьеры
    "v1": {
        "cat": "cat_courier",
        "icon": "🚶",
        "title": "Пеший курьер",
        "salary": "3 500–6 000 ₽ за смену",
        "schedule": "Гибкий, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Доставка заказов пешком в пределах района\n• Приём и передача посылок получателю\n• Подтверждение доставки через приложение",
        "requirements": "• Без опыта — обучаем\n• Смартфон с навигацией\n• Ответственность и пунктуальность",
        "conditions": "• 3 500–6 000 ₽ за смену\n• Выплаты каждую неделю\n• Гибкий выбор смен\n• Официальное оформление с первого дня",
    },
    "v2": {
        "cat": "cat_courier",
        "icon": "🚴",
        "title": "Курьер на велосипеде / самокате",
        "salary": "4 000–7 000 ₽ за смену",
        "schedule": "Гибкий, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Доставка заказов на велосипеде или самокате\n• Работа по оптимизированным маршрутам\n• Подтверждение доставки через приложение",
        "requirements": "• Велосипед или самокат — свой или компании\n• Уверенное вождение в городе\n• Смартфон с навигацией",
        "conditions": "• 4 000–7 000 ₽ за смену, в пиковые дни выше\n• Выплаты каждую неделю\n• Гибкий выбор смен\n• Официальное оформление с первого дня",
    },
    "v3": {
        "cat": "cat_courier",
        "icon": "🚗",
        "title": "Курьер на автомобиле",
        "salary": "5 000–9 000 ₽ за смену",
        "schedule": "Гибкий, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Доставка заказов на автомобиле по нескольким точкам\n• Работа по оптимизированным маршрутам\n• Подтверждение доставки через приложение",
        "requirements": "• Водительское удостоверение кат. B\n• Опыт вождения в городе от 1 года\n• Смартфон с навигацией",
        "conditions": "• 5 000–9 000 ₽ за смену\n• Свой транспорт с компенсацией топлива или авто компании\n• Выплаты каждую неделю\n• Официальное оформление с первого дня",
    },
    "v4": {
        "cat": "cat_courier",
        "icon": "🏍",
        "title": "Курьер на мотоцикле",
        "salary": "5 500–9 500 ₽ за смену",
        "schedule": "Гибкий, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Быстрая доставка заказов на мотоцикле\n• Работа по приоритетным маршрутам\n• Подтверждение доставки через приложение",
        "requirements": "• Водительское удостоверение кат. A\n• Опыт езды в городе от 1 года\n• Смартфон с навигацией",
        "conditions": "• 5 500–9 500 ₽ за смену\n• Компенсация топлива\n• Выплаты каждую неделю\n• Официальное оформление с первого дня",
    },
    # Склад
    "v5": {
        "cat": "cat_warehouse",
        "icon": "📦",
        "title": "Сортировщик посылок",
        "salary": "2 800–4 500 ₽ за смену",
        "schedule": "Сменный график, смены 8–12 часов",
        "location": "Вся Россия",
        "duties": "• Сортировка входящих и исходящих посылок\n• Сканирование и маркировка отправлений\n• Контроль сохранности грузов",
        "requirements": "• Без опыта — обучаем\n• Внимательность и аккуратность\n• Готовность к физическому труду",
        "conditions": "• 2 800–4 500 ₽ за смену\n• Выплаты каждую неделю\n• Сменный график\n• Официальное оформление с первого дня",
    },
    "v6": {
        "cat": "cat_warehouse",
        "icon": "🏭",
        "title": "Комплектовщик заказов",
        "salary": "3 000–5 000 ₽ за смену",
        "schedule": "Сменный график, смены 8–12 часов",
        "location": "Вся Россия",
        "duties": "• Сборка и комплектация заказов по накладным\n• Упаковка отправлений\n• Размещение товаров на складе",
        "requirements": "• Без опыта — обучаем\n• Внимательность, аккуратность\n• Готовность к физическому труду",
        "conditions": "• 3 000–5 000 ₽ за смену\n• Выплаты каждую неделю\n• Сменный график\n• Официальное оформление с первого дня",
    },
    "v7": {
        "cat": "cat_warehouse",
        "icon": "🔧",
        "title": "Механик / техник по обслуживанию транспорта",
        "salary": "4 000–7 000 ₽ за смену",
        "schedule": "Сменный график, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Техническое обслуживание транспортных средств компании\n• Диагностика и устранение неисправностей\n• Ведение журнала технического состояния",
        "requirements": "• Опыт работы механиком от 1 года\n• Знание устройства автомобилей и мотоциклов\n• Ответственность и аккуратность",
        "conditions": "• 4 000–7 000 ₽ за смену\n• Выплаты каждую неделю\n• Стабильный график\n• Официальное оформление с первого дня",
    },
    "v8": {
        "cat": "cat_warehouse",
        "icon": "📋",
        "title": "Кладовщик",
        "salary": "3 200–5 500 ₽ за смену",
        "schedule": "Сменный график, смены 8–12 часов",
        "location": "Вся Россия",
        "duties": "• Приём, хранение и выдача товарно-материальных ценностей\n• Ведение складского учёта\n• Контроль остатков и инвентаризация",
        "requirements": "• Опыт работы кладовщиком приветствуется\n• Знание складских программ (1С, Excel)\n• Внимательность, ответственность",
        "conditions": "• 3 200–5 500 ₽ за смену\n• Выплаты каждую неделю\n• Сменный график\n• Официальное оформление с первого дня",
    },
    # Офис
    "v9": {
        "cat": "cat_office",
        "icon": "📞",
        "title": "Диспетчер службы доставки",
        "salary": "3 500–6 000 ₽ за смену",
        "schedule": "Сменный график, смены 8–12 часов",
        "location": "Вся Россия",
        "duties": "• Координация работы курьеров и распределение маршрутов\n• Контроль сроков доставки\n• Решение оперативных вопросов с клиентами и курьерами",
        "requirements": "• Опыт работы диспетчером или оператором приветствуется\n• Стрессоустойчивость, многозадачность\n• Уверенное владение ПК",
        "conditions": "• 3 500–6 000 ₽ за смену\n• Выплаты каждую неделю\n• Сменный график\n• Официальное оформление с первого дня",
    },
    "v10": {
        "cat": "cat_office",
        "icon": "🗂",
        "title": "Оператор колл-центра",
        "salary": "3 000–5 000 ₽ за смену",
        "schedule": "Гибкий, смены 8–10 часов",
        "location": "Вся Россия",
        "duties": "• Приём и обработка входящих обращений клиентов\n• Консультация по статусу заказов и условиям доставки\n• Фиксация обращений в CRM-системе",
        "requirements": "• Грамотная речь, вежливость\n• Уверенное владение ПК\n• Без опыта — обучаем",
        "conditions": "• 3 000–5 000 ₽ за смену\n• Выплаты каждую неделю\n• Гибкий график\n• Официальное оформление с первого дня",
    },
    "v11": {
        "cat": "cat_office",
        "icon": "📊",
        "title": "Менеджер по работе с партнёрами",
        "salary": "4 500–8 000 ₽ за смену",
        "schedule": "Стандартный, 5/2",
        "location": "Вся Россия",
        "duties": "• Развитие и поддержка отношений с партнёрами и клиентами\n• Заключение и сопровождение договоров\n• Мониторинг выполнения условий сотрудничества",
        "requirements": "• Опыт в продажах или работе с клиентами от 1 года\n• Коммуникабельность, нацеленность на результат\n• Уверенное владение ПК",
        "conditions": "• 4 500–8 000 ₽ за смену + бонусы\n• Выплаты каждую неделю\n• График 5/2\n• Официальное оформление с первого дня",
    },
}

QUIZ_QUESTIONS = [
    {
        "text": "Шаг 1 из 3\n\n<b>Укажите ваш возраст:</b>",
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
        "text": "Шаг 2 из 3\n\n<b>Есть ли у вас опыт работы?</b>",
        "key": "experience",
        "options": [
            ("Да, есть опыт", "да"),
            ("Нет, первый раз", "нет"),
        ]
    },
    {
        "text": "Шаг 3 из 3\n\n<b>Когда готовы приступить к работе?</b>",
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
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚴 Вакансии курьером", callback_data="cat_courier")],
        [InlineKeyboardButton("📦 Вакансии на складе", callback_data="cat_warehouse")],
        [InlineKeyboardButton("🏢 Вакансии в офисе", callback_data="cat_office")],
        [InlineKeyboardButton("🏢 О компании", callback_data="about"),
         InlineKeyboardButton("📍 Города", callback_data="cities")],
        [InlineKeyboardButton("🚀 Как начать работу", callback_data="how_to_start")],
        [InlineKeyboardButton("❓ Частые вопросы", callback_data="faq")],
    ])


def category_keyboard(cat_id):
    buttons = [
        [InlineKeyboardButton(f"{v['icon']} {v['title']}", callback_data=k)]
        for k, v in VACANCIES.items() if v["cat"] == cat_id
    ]
    buttons.append([InlineKeyboardButton("← Назад", callback_data="back")])
    return InlineKeyboardMarkup(buttons)


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
        "Более 5 000 сотрудников по всей России.\n\n"
        "Выберите направление:",
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
            f"Актуальные вакансии <b>{COMPANY_NAME}</b>. Выберите направление:",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )
        return

    # Категорії
    if data in CATEGORIES:
        await query.edit_message_text(
            f"<b>{CATEGORIES[data]}</b>\n\nВыберите вакансию:",
            parse_mode="HTML",
            reply_markup=category_keyboard(data)
        )
        return

    # Вибір вакансії
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
            "Ответьте на 3 быстрых вопроса, и мы свяжемся с вами в течение 15 минут 👇\n\n"
            + QUIZ_QUESTIONS[0]["text"],
            parse_mode="HTML",
            reply_markup=quiz_keyboard(data, 0)
        )
        return

    # Квіз
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

        # Квіз завершено — відправляємо адміну
        vac = VACANCIES[vac_id]
        answers = ctx.user_data["answers"]
        user = query.from_user
        username = f"@{user.username}" if user.username else "нет username"

        admin_message = (
            f"📋 <b>Новая заявка — {COMPANY_NAME}</b>\n\n"
            f"👤 Имя: {user.full_name or '—'}\n"
            f"🔗 Username: {username}\n"
            f"🆔 ID: <code>{user.id}</code>\n\n"
            f"💼 Вакансия: {vac['icon']} {vac['title']}\n"
            f"📅 Возраст: {answers.get('age', '—')}\n"
            f"💼 Опыт работы: {answers.get('experience', '—')}\n"
            f"⏰ Готов приступить: {answers.get('start', '—')}"
        )

        await query.get_bot().send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="HTML"
        )

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
