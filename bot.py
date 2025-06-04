import os
import random
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import TelegramError
from recipes import RECIPES

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = '7601466273:AAGGx1fCt_c9JjS36GZiw2KOKg_NrkX1Xes'  # Direct token assignment

# Recipe categories
CATEGORIES = {
    "main": "Основные блюда",
    "soups": "Супы",
    "salads": "Салаты",
    "desserts": "Десерты"
}

# Difficulty levels
DIFFICULTY_LEVELS = {
    "easy": "Легкая",
    "medium": "Средняя",
    "hard": "Сложная"
}

# Time ranges
TIME_RANGES = {
    "15": "До 15 минут",
    "30": "15-30 минут",
    "60": "30-60 минут",
    "60+": "Более 60 минут"
}

def get_recipe_category(recipe):
    """Determine recipe category based on ingredients and name."""
    name = recipe["name"].lower()
    ingredients = [ing.lower() for ing in recipe["ingredients"]]
    
    if any(word in name for word in ["суп", "борщ", "бульон"]):
        return "soups"
    elif any(word in name for word in ["салат"]):
        return "salads"
    elif any(word in name for word in ["запеканка", "пирог", "торт", "кекс"]):
        return "desserts"
    else:
        return "main"

def get_cooking_time_minutes(cooking_time_str):
    """Convert cooking time string to minutes."""
    try:
        return int(cooking_time_str.split()[0])
    except (ValueError, IndexError):
        return 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Привет! Я бот с рецептами.\n\n"
        "Я могу:\n"
        "1. 🎲 Показать случайный рецепт (/random)\n"
        "2. 🔍 Найти рецепт по имеющимся продуктам (просто напишите список продуктов)\n"
        "3. 📑 Показать рецепты по категориям (/categories)\n"
        "4. ⏱ Найти рецепт по времени приготовления (/time)\n"
        "5. 📊 Найти рецепт по сложности (/difficulty)\n"
        "6. 🔥 Найти рецепт по калорийности (/calories)\n"
        "7. 📝 Показать список всех рецептов (/list)\n"
        "8. ❓ Показать справку (/help)\n\n"
        "Например: яйца, помидоры, лук"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    help_text = (
        "📚 Справка по командам:\n\n"
        "/start - Начать работу с ботом\n"
        "/random - Получить случайный рецепт\n"
        "/categories - Показать рецепты по категориям\n"
        "/time - Найти рецепт по времени приготовления\n"
        "/difficulty - Найти рецепт по сложности\n"
        "/calories - Найти рецепт по калорийности\n"
        "/list - Показать список всех рецептов\n"
        "/help - Показать эту справку\n\n"
        "Чтобы найти рецепт по продуктам, просто напишите список продуктов через запятую.\n"
        "Например: яйца, помидоры, лук"
    )
    await update.message.reply_text(help_text)

async def list_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of all recipes."""
    recipes_list = "📋 Список всех рецептов:\n\n"
    for i, recipe in enumerate(RECIPES, 1):
        category = CATEGORIES[get_recipe_category(recipe)]
        recipes_list += f"{i}. {recipe['name']} ({category})\n"
    
    await update.message.reply_text(recipes_list)

async def calories_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show calories filter options."""
    keyboard = [
        [InlineKeyboardButton("До 200 ккал", callback_data="cal_200")],
        [InlineKeyboardButton("200-300 ккал", callback_data="cal_300")],
        [InlineKeyboardButton("300-400 ккал", callback_data="cal_400")],
        [InlineKeyboardButton("Более 400 ккал", callback_data="cal_400+")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите максимальную калорийность:", reply_markup=reply_markup)

async def time_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show time filter options."""
    keyboard = [
        [InlineKeyboardButton(TIME_RANGES["15"], callback_data="time_15")],
        [InlineKeyboardButton(TIME_RANGES["30"], callback_data="time_30")],
        [InlineKeyboardButton(TIME_RANGES["60"], callback_data="time_60")],
        [InlineKeyboardButton(TIME_RANGES["60+"], callback_data="time_60+")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите максимальное время приготовления:", reply_markup=reply_markup)

async def difficulty_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show difficulty filter options."""
    keyboard = [
        [InlineKeyboardButton(DIFFICULTY_LEVELS["easy"], callback_data="diff_easy")],
        [InlineKeyboardButton(DIFFICULTY_LEVELS["medium"], callback_data="diff_medium")],
        [InlineKeyboardButton(DIFFICULTY_LEVELS["hard"], callback_data="diff_hard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите сложность рецепта:", reply_markup=reply_markup)

async def filter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle filter selection."""
    query = update.callback_query
    await query.answer()
    
    filter_type, value = query.data.split('_')
    
    if filter_type == 'time':
        max_time = int(value) if value != '60+' else float('inf')
        filtered_recipes = [
            r for r in RECIPES 
            if get_cooking_time_minutes(r['cooking_time']) <= max_time
        ]
    elif filter_type == 'diff':
        filtered_recipes = [
            r for r in RECIPES 
            if r['difficulty'].lower() == value
        ]
    elif filter_type == 'cal':
        max_calories = int(value) if value != '400+' else float('inf')
        filtered_recipes = [
            r for r in RECIPES 
            if int(r['calories'].split()[0]) <= max_calories
        ]
    else:
        return
    
    if filtered_recipes:
        recipe = random.choice(filtered_recipes)
        await send_recipe(update, recipe)
    else:
        await query.message.reply_text(
            "К сожалению, не найдено рецептов по выбранным критериям.\n"
            "Попробуйте другие параметры или используйте /random для случайного рецепта."
        )

async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recipe categories."""
    keyboard = [
        [InlineKeyboardButton(cat_name, callback_data=f"category_{cat_id}")]
        for cat_id, cat_name in CATEGORIES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите категорию рецептов:", reply_markup=reply_markup)

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection."""
    query = update.callback_query
    await query.answer()
    
    category = query.data.split("_")[1]
    category_recipes = [r for r in RECIPES if get_recipe_category(r) == category]
    
    if category_recipes:
        recipe = random.choice(category_recipes)
        await send_recipe(update, recipe)
    else:
        await query.message.reply_text("В этой категории пока нет рецептов.")

async def random_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random recipe."""
    recipe = random.choice(RECIPES)
    await send_recipe(update, recipe)

async def find_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Find recipes based on available ingredients."""
    user_ingredients = [ing.strip().lower() for ing in update.message.text.split(',')]
    
    matching_recipes = []
    for recipe in RECIPES:
        recipe_ingredients = [ing.lower() for ing in recipe['ingredients']]
        if any(ing in recipe_ingredients for ing in user_ingredients):
            matching_recipes.append(recipe)
    
    if matching_recipes:
        recipe = random.choice(matching_recipes)
        await send_recipe(update, recipe)
    else:
        await update.message.reply_text(
            "😕 К сожалению, я не нашел рецептов с указанными продуктами.\n"
            "Попробуйте другие ингредиенты или используйте /random для случайного рецепта."
        )

async def send_recipe(update: Update, recipe: dict):
    """Send a formatted recipe message."""
    try:
        category = CATEGORIES[get_recipe_category(recipe)]
        message = (
            f"🍳 {recipe['name']}\n"
            f"📌 Категория: {category}\n"
            f"⏱ Время приготовления: {recipe['cooking_time']}\n"
            f"📊 Сложность: {recipe['difficulty']}\n"
            f"🔥 Калории: {recipe['calories']}\n\n"
            f"📝 Ингредиенты:\n"
            f"{', '.join(recipe['ingredients'])}\n\n"
            f"📋 Инструкция:\n"
            f"{recipe['instructions']}"
        )
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message)
        else:
            await update.message.reply_text(message)
    except TelegramError as e:
        logger.error(f"Error sending recipe: {e}")
        error_message = "Извините, произошла ошибка при отправке рецепта. Пожалуйста, попробуйте еще раз."
        if update.callback_query:
            await update.callback_query.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    error_message = "Извините, произошла ошибка. Пожалуйста, попробуйте еще раз."
    if update and update.effective_message:
        await update.effective_message.reply_text(error_message)

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("random", random_recipe))
    application.add_handler(CommandHandler("categories", categories))
    application.add_handler(CommandHandler("time", time_filter))
    application.add_handler(CommandHandler("difficulty", difficulty_filter))
    application.add_handler(CommandHandler("calories", calories_filter))
    application.add_handler(CommandHandler("list", list_recipes))
    application.add_handler(CallbackQueryHandler(category_callback, pattern="^category_"))
    application.add_handler(CallbackQueryHandler(filter_callback, pattern="^(time|diff|cal)_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, find_recipe))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 