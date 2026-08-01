import asyncio
import logging
import requests 
import random
import nest_asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

nest_asyncio.apply()

# ===== ТОКЕНЫ (ЗАМЕНИТЬ!) =====
BOT_TOKEN = "8903154909:AAFo9x5rL6EHEg7PlnOE9CUH8TLjpyomirM"
WEATHER_API_KEY = "31beafb00c591923a0add1efffafc909"


# ===== НАСТРОЙКА ЛОГИРОВАНИЯ =====
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ===== КЛАВИАТУРА =====
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🌡️ — погода"), KeyboardButton("🍃 — напоминание")],
        [KeyboardButton("📝 — заметки"), KeyboardButton("✅ — список задач")],
        [KeyboardButton("❓ — помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== ПОГОДА =====
def get_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            humidity = data['main']['humidity']
            return (f"Погода в городе {city}:\n"
                    f"🌡 температура: {temp}°C (ощущается как {feels_like}°C)\n"
                    f"☁️ {description.capitalize()}\n"
                    f"💨 ветер: {wind_speed} м/с\n"
                    f"💧 влажность: {humidity}%")
        else:
            return f"❌ ошибка: город '{city}' не найден или проблемы с API."
    except requests.exceptions.RequestException:
        return "❌ не удалось соединиться с сервером погоды. Попробуй позже."

# ===== ЦИТАТЫ (НАПОМИНАНИЯ) =====
def load_quotes():
    default_quotes = [
        "Все в твоих руках",
        "Кстати, есть люди, которые тебя искренне любят",
        "Кстати, ошибки — это часть роста",
        "Ты справляешься гораздо лучше, чем тебе кажется",
        "Твоя улыбка способна изменить чье-то утро",
        "Ты имеешь полное право на отдых без чувства вины",
        "Твой потенциал безграничен, просто начни",
        "Маленькие шаги тоже продвигают тебя вперед",
        "Этот сложный день закончится уже через несколько часов",
        "Ты — автор своей истории, пиши ее смелее",
        "Твое тело делает всё возможное, чтобы защитить тебя",
        "Ошибаться — это абсолютно естественно и нормально",
        "Позволь себе быть неидеальным человеком",
        "Ты заслуживаешь любви и уважения прямо сейчас",
        "Обними себя мысленно, ты большой молодец",
        "Твои чувства важны, не обесценивай их",
        "Окружай себя теми, с кем тепло на душе",
        "Ты — самый главный человек в своей жизни",
        "Заботиться о себе — это базовая необходимость, а не эгоизм",
        "Скажи себе сегодня искреннее спасибо",
        "Ты гораздо нужнее этому миру, чем думаешь",
        "Твоя доброта оставляет невидимый след в сердцах",
        "Побалуй себя сегодня какой-нибудь приятной мелочью",
        "Ты находишься в безопасности здесь и сейчас",
        "Твой внутренний ребенок точно гордится тобой",
        "Твоя ценность никогда не зависит от чужого мнения",
        "Ошибка — это лишь доказательство того, что ты пытаешься",
        "Неудачный опыт делает тебя намного мудрее",
        "Падать не страшно, главное — находить силы подниматься",
        "Твое прошлое никак не определяет твое будущее",
        "Каждый шаг назад — это лишь подготовка к мощному разбегу",
        "Из любого, даже самого сложного тупика есть выход",
        "Ты учишься, адаптируешься и растешь каждый день",
        "Не суди свой день только по временным неудачам",
        "Опыт стоит абсолютно всех потраченных усилий",
        "Ты имеешь полное право передумать и изменить мнение",
        "Великие шедевры создаются через сотни черновиков",
        "Твои шрамы и штормы — это история твоей силы",
        "Исправлять свои ошибки — удел по-настоящему сильных",
        "Критика со стороны других говорит лишь о них самих",
        "Ты блестяще справлялся раньше, справишься и сейчас",
        "Каждая трудность делает твой характер только гибче",
        "Ты намного сильнее, чем тебе сейчас кажется",
        "Ты сам выбираешь, как реагировать на этот мир",
        "Ты можешь уверенно сказать «нет» без оправданий",
        "Твоя жизнь — это исключительно твои правила",
        "Измени фокус мыслей, и твоя реальность изменится",
        "Выход всегда на поверхности, просто осмотрись вокруг",
        "Великие дела всегда начинаются с одного простого решения",
        "Храбрость — это продолжать идти вопреки страху",
        "Твоя настойчивость обязательно принесет сладкие плоды",
        "Ты способен преодолеть любые текущие преграды",
        "Всегда доверяй своим внутренним силам и интуиции",
        "Твоя энергия определяет твой завтрашний успех",
        "Не жди идеального момента, сделай идеальным этот",
        "У тебя уже есть всё необходимое для уверенного старта",
        "Твоя воля способна двигать самые тяжелые горы",
        "Фокусируйся только на том, что ты можешь контролировать",
        "Просто сделай глубокий вдох и медленный выдох",
        "Замедлись на минуту и почувствуй текущий момент",
        "Твоя жизнь происходит прямо здесь и сейчас",
        "С легким сердцем отпусти то, что больше не служит тебе",
        "Тишина внутри гораздо важнее любого внешнего шума",
        "Сравнивай себя сегодняшнего только с собой прошлым",
        "Истинное счастье всегда прячется в простых мелочах",
        "Благодарность круто меняет фокус твоего восприятия",
        "Не беги слишком быстро, успевай наслаждаться путем",
        "Всему свое время, просто доверяй течению жизни",
        "Оставь ненужную тревогу о будущем за закрытой дверью",
        "Побудь в моменте и позволь себе никуда не спешить",
        "Твой внутренний покой — это твоя главная суперсила",
        "Мир вокруг тебя отражает твое внутреннее состояние",
        "Найди хотя бы один повод для радости прямо сейчас",
        "Умей вовремя остановиться и просто выпить чаю",
        "Природа вокруг тебя живет в своем идеальном ритме",
        "Твой загруженный разум заслуживает отдыха от мыслей",
        "Принимай этот день с благодарностью таким, какой он есть",
        "Осознанная простота в вещах дарует истинную свободу",
        "Лучший способ предсказать будущее — изобрести его",
        "Завтра обязательно будет новый день и новые шансы",
        "Самое лучшее и прекрасное еще точно впереди",
        "Твои заветные мечты стоят того, чтобы за них бороться",
        "Искренне верь в чудеса, они случаются каждый день",
        "Яркое солнце всегда выходит после самого сильного ливня",
        "Все твои усилия окупятся, просто никогда не сдавайся",
        "Этот огромный мир открывает двери перед теми, кто идет",
        "Ты на абсолютно правильном пути, продолжай движение",
        "Впереди тебя ждет невероятно много прекрасных открытий",
        "Твой внутренний свет способен разогнать любую тьму",
        "Каждый новый рассвет — это твой чистый лист бумаги",
        "Всегда верь в свои самые безумные и смелые задумки",
        "Твоя преданность любимому делу изменит твою жизнь",
        "Очень скоро ты будешь искренне гордиться этим периодом",
        "Капризная удача любит тех, кто упорно пытается",
        "Твоя маленькая искра способна зажечь огромное пламя",
        "Никогда не бойся смотреть далеко в свое будущее",
        "Всё вокруг складывается наилучшим для тебя образом",
        "Ты рожден для того, чтобы быть по-настоящему счастливым",
    ]
    try:
        with open("quotes.txt", "r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        if quotes:
            return quotes
        else:
            return default_quotes
    except FileNotFoundError:
        with open("quotes.txt", "w", encoding="utf-8") as f:
            for q in default_quotes:
                f.write(q + "\n")
        return default_quotes
    except Exception:
        return default_quotes

def get_random_quote():
    quotes = load_quotes()
    return random.choice(quotes)

# ===== ЗАМЕТКИ =====
def load_notes(user_id):
    filename = f"notes_{user_id}.txt"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []
    except Exception:
        return []

def save_notes(user_id, notes):
    filename = f"notes_{user_id}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for note in notes:
                f.write(note + "\n")
    except Exception:
        pass

def add_note(user_id, text):
    notes = load_notes(user_id)
    notes.append(text)
    save_notes(user_id, notes)

def get_notes_text(user_id):
    notes = load_notes(user_id)
    if not notes:
        return "📭 у вас пока нет заметок."
    result = "📋 ваши заметки:\n"
    for i, note in enumerate(notes, start=1):
        result += f"{i}. {note}\n"
    return result

# ===== ЗАДАЧИ =====
class Task:
    def __init__(self, title, description, is_done=False):
        self.title = title
        self.description = description
        self.is_done = is_done

    def to_string(self):
        status = "1" if self.is_done else "0"
        return f"{self.title}|{self.description}|{status}"

    @staticmethod
    def from_string(line):
        parts = line.strip().split("|")
        if len(parts) == 3:
            title, description, status = parts
            is_done = (status == "1")
            return Task(title, description, is_done)
        return None

def load_tasks(user_id):
    filename = f"tasks_{user_id}.txt"
    tasks = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                task = Task.from_string(line)
                if task:
                    tasks.append(task)
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return tasks

def save_tasks(user_id, tasks):
    filename = f"tasks_{user_id}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for task in tasks:
                f.write(task.to_string() + "\n")
    except Exception:
        pass

def add_task(user_id, title, description):
    tasks = load_tasks(user_id)
    tasks.append(Task(title, description))
    save_tasks(user_id, tasks)

def get_tasks_text(user_id):
    tasks = load_tasks(user_id)
    if not tasks:
        return "📭 задач пока нет."
    result = "📋 ваши задачи:\n"
    for i, task in enumerate(tasks, start=1):
        status = "✅" if task.is_done else "❌"
        result += f"{i}. {status} {task.title} — {task.description}\n"
    return result

def mark_task_done(user_id, task_index):
    tasks = load_tasks(user_id)
    if 1 <= task_index <= len(tasks):
        tasks[task_index - 1].is_done = True
        save_tasks(user_id, tasks)
        return True
    return False

# ===== ОБРАБОТЧИКИ =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 привет! Я Хэсси: бот-ассистент.\n"
        "я умею:\n"
        "🌤 показывать погоду\n"
        "🍃 поднимать настроение\n"
        "📝 хранить заметки\n"
        "✅ создавать список задач\n\n"
        "выбери действие в меню или используй команды:\n"
        "/start — показать это сообщение\n"
        "/help — помощь\n"
        "/quote — случайная цитата\n"
        "/addnote — добавить заметку\n"
        "/addtask — добавить задачу\n"
        "/tasks — показать задачи\n"
        "/done — отметить задачу выполненной",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 доступные команды:\n"
        "/start — приветствие и меню\n"
        "/help — это сообщение\n"
        "/quote — случайное напоминание\n"
        "/addnote — добавить заметку\n"
        "/addtask — добавить задачу\n"
        "/tasks — список задач\n"
        "/done — отметить задачу выполненной\n\n"
        "также ты можешь пользоваться кнопками меню.",
        reply_markup=get_main_keyboard()
    )

async def add_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ введите текст новой заметки:")
    context.user_data['awaiting_note'] = True

async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ введите название задачи:")
    context.user_data['awaiting_task_title'] = True

async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks_text = get_tasks_text(update.effective_user.id)
    await update.message.reply_text(tasks_text, reply_markup=get_main_keyboard())

async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔢 введите номер задачи, которую нужно отметить выполненной:")
    context.user_data['awaiting_done_number'] = True

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = get_random_quote()
    await update.message.reply_text(f"💡 {quote}", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # ---- ждём город для погоды ----
    if context.user_data.get('awaiting_city'):
        city = text
        context.user_data['awaiting_city'] = False
        weather_info = get_weather(city, WEATHER_API_KEY)
        await update.message.reply_text(weather_info, reply_markup=get_main_keyboard())
        return

    # ---- ждём текст заметки ----
    if context.user_data.get('awaiting_note'):
        note_text = text
        context.user_data['awaiting_note'] = False
        add_note(user_id, note_text)
        await update.message.reply_text("✅ заметка добавлена!", reply_markup=get_main_keyboard())
        return

    # ---- ждём название задачи (первый шаг) ----
    if context.user_data.get('awaiting_task_title'):
        context.user_data['awaiting_task_title'] = False
        context.user_data['task_title'] = text
        await update.message.reply_text("✏️ введите описание задачи:")
        context.user_data['awaiting_task_description'] = True
        return

    # ---- ждём описание задачи (второй шаг) ----
    if context.user_data.get('awaiting_task_description'):
        description = text
        context.user_data['awaiting_task_description'] = False
        title = context.user_data.pop('task_title', 'Без названия')
        add_task(user_id, title, description)
        await update.message.reply_text("✅ задача добавлена!", reply_markup=get_main_keyboard())
        return

    # ---- ждём номер задачи для отметки выполненной ----
    if context.user_data.get('awaiting_done_number'):
        context.user_data['awaiting_done_number'] = False
        try:
            num = int(text)
            if mark_task_done(user_id, num):
                await update.message.reply_text("✅ задача выполнена!", reply_markup=get_main_keyboard())
            else:
                await update.message.reply_text("❌ задача с таким номером не найдена.", reply_markup=get_main_keyboard())
        except ValueError:
            await update.message.reply_text("❌ введите число.", reply_markup=get_main_keyboard())
        return

    # ---- обработка кнопок меню (сравниваем без эмодзи и пробелов для упрощения) ----
    # нормализуем текст: убираем эмодзи и лишние пробелы
    clean_text = text.replace("🌡️", "").replace("🍃", "").replace("📝", "").replace("✅", "").replace("❓", "").replace("—", "").strip().lower()

    if clean_text == "погода":
        await update.message.reply_text("🌍 введите название города:")
        context.user_data['awaiting_city'] = True
    elif clean_text == "напоминание":
        quote = get_random_quote()
        await update.message.reply_text(f"💡 {quote}", reply_markup=get_main_keyboard())
    elif clean_text == "заметки":
        notes_text = get_notes_text(user_id)
        await update.message.reply_text(
            notes_text + "\n\nчтобы добавить заметку, используй команду /addnote",
            reply_markup=get_main_keyboard()
        )
    elif clean_text in ["список задач", "задачи"]:
        tasks_text = get_tasks_text(user_id)
        await update.message.reply_text(
            tasks_text + "\n\nкоманды для задач:\n/addtask — добавить задачу\n/done — отметить выполненной",
            reply_markup=get_main_keyboard()
        )
    elif clean_text == "помощь":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            f"я не знаю команду '{text}'. используй кнопки меню или команды (например, /help).",
            reply_markup=get_main_keyboard()
        )

# ===== ЗАПУСК БОТА =====
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("addnote", add_note_command))
    app.add_handler(CommandHandler("addtask", add_task_command))
    app.add_handler(CommandHandler("tasks", tasks_command))
    app.add_handler(CommandHandler("done", done_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 бот запущен...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    # держим активным
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("бот остановлен.")
