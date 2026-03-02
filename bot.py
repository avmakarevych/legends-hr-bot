#!/usr/bin/env python3
"""
LegendsHR Bot v4.0
Telegram bot for collecting employee data → sends to Telegram channel
No database needed!
"""

import os
import logging
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

TOKEN = os.environ.get("BOT_TOKEN", "8522819299:AAF06NWPJPwi-T21_OT7Xc416tdiztHStVo")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003670705313"))

# States
(
    STATE_LANGUAGE,
    STATE_MENU,
    STATE_NAME,
    STATE_WALLET,
    STATE_TELEGRAM,
    STATE_CONFIRM,
) = range(6)

# Actions
ACT_REQUISITES = "requisites"
ACT_NEW_EMPLOYEE = "new_employee"
ACT_CHANGE_CONTACTS = "change_contacts"

# Languages
LANG_UK, LANG_RU, LANG_EN = "uk", "ru", "en"

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════════════════════════════════════════════

T = {
    LANG_UK: {
        "lang_prompt": "🌍 Оберіть мову:",
        "menu_title": "📋 *Головне меню*\n\nОберіть дію:",
        "btn_requisites": "💳 Змінити реквізити",
        "btn_new_employee": "👤 Новий співробітник", 
        "btn_change_contacts": "📞 Зміна контактів",
        "btn_back": "◀️ Назад",
        "btn_confirm": "✅ Підтвердити",
        "btn_cancel": "❌ Скасувати",
        "btn_restart": "🔄 Почати знову",
        "enter_name": "👤 Введіть *ім'я та прізвище*:",
        "enter_wallet": "💰 Введіть *TRC20 гаманець*:",
        "enter_telegram": "📱 Введіть *робочий телеграм*:",
        "confirm_title": "📝 *Перевірте дані:*\n",
        "confirm_action": "Дія",
        "confirm_name": "Ім'я",
        "confirm_wallet": "Гаманець",
        "confirm_telegram": "Телеграм",
        "saved": "✅ *Дані успішно збережено!*",
        "cancelled": "❌ Скасовано",
        "action_requisites": "Змінити реквізити",
        "action_new_employee": "Новий співробітник",
        "action_change_contacts": "Зміна контактів",
        "error": "⚠️ Щось пішло не так. Спробуйте /start",
    },
    LANG_RU: {
        "lang_prompt": "🌍 Выберите язык:",
        "menu_title": "📋 *Главное меню*\n\nВыберите действие:",
        "btn_requisites": "💳 Изменить реквизиты",
        "btn_new_employee": "👤 Новый сотрудник",
        "btn_change_contacts": "📞 Смена контактов",
        "btn_back": "◀️ Назад",
        "btn_confirm": "✅ Подтвердить",
        "btn_cancel": "❌ Отменить",
        "btn_restart": "🔄 Начать заново",
        "enter_name": "👤 Введите *имя и фамилию*:",
        "enter_wallet": "💰 Введите *TRC20 кошелек*:",
        "enter_telegram": "📱 Введите *рабочий телеграм*:",
        "confirm_title": "📝 *Проверьте данные:*\n",
        "confirm_action": "Действие",
        "confirm_name": "Имя",
        "confirm_wallet": "Кошелек",
        "confirm_telegram": "Телеграм",
        "saved": "✅ *Данные успешно сохранены!*",
        "cancelled": "❌ Отменено",
        "action_requisites": "Изменить реквизиты",
        "action_new_employee": "Новый сотрудник",
        "action_change_contacts": "Смена контактов",
        "error": "⚠️ Что-то пошло не так. Попробуйте /start",
    },
    LANG_EN: {
        "lang_prompt": "🌍 Choose language:",
        "menu_title": "📋 *Main Menu*\n\nChoose an action:",
        "btn_requisites": "💳 Change payment details",
        "btn_new_employee": "👤 New employee",
        "btn_change_contacts": "📞 Change contacts",
        "btn_back": "◀️ Back",
        "btn_confirm": "✅ Confirm",
        "btn_cancel": "❌ Cancel",
        "btn_restart": "🔄 Start again",
        "enter_name": "👤 Enter *first and last name*:",
        "enter_wallet": "💰 Enter *TRC20 wallet*:",
        "enter_telegram": "📱 Enter *work telegram*:",
        "confirm_title": "📝 *Please verify:*\n",
        "confirm_action": "Action",
        "confirm_name": "Name",
        "confirm_wallet": "Wallet",
        "confirm_telegram": "Telegram",
        "saved": "✅ *Data saved successfully!*",
        "cancelled": "❌ Cancelled",
        "action_requisites": "Change payment details",
        "action_new_employee": "New employee",
        "action_change_contacts": "Change contacts",
        "error": "⚠️ Something went wrong. Try /start",
    },
}

# Action emojis for channel messages
ACTION_EMOJI = {
    ACT_REQUISITES: "💳",
    ACT_NEW_EMPLOYEE: "👤",
    ACT_CHANGE_CONTACTS: "📞",
}

ACTION_TITLES = {
    ACT_REQUISITES: "Зміна реквізитів",
    ACT_NEW_EMPLOYEE: "Новий співробітник",
    ACT_CHANGE_CONTACTS: "Зміна контактів",
}

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def t(ctx: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    """Get translated text."""
    lang = ctx.user_data.get("lang", LANG_UK)
    return T.get(lang, T[LANG_UK]).get(key, key)


async def send_to_channel(bot: Bot, action: str, name: str, value: str, user_id: int, username: Optional[str]):
    """Send data to Telegram channel instead of database."""
    emoji = ACTION_EMOJI.get(action, "📋")
    title = ACTION_TITLES.get(action, action)
    
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    user_link = f"@{username}" if username else f"ID: {user_id}"
    
    if action == ACT_REQUISITES:
        value_label = "💰 Гаманець"
    else:
        value_label = "📱 Телеграм"
    
    message = (
        f"{emoji} *{title}*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 *Ім'я:* {name}\n"
        f"{value_label}: `{value}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🕐 {now}\n"
        f"👁 Від: {user_link}"
    )
    
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode="Markdown"
    )
    log.info(f"Sent to channel: {action} | {name} | {user_link}")


async def send_or_edit(update: Update, text: str, keyboard: list, parse_mode: str = "Markdown"):
    """Send new message or edit existing one."""
    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=markup, parse_mode=parse_mode)
    elif update.message:
        await update.message.reply_text(text, reply_markup=markup, parse_mode=parse_mode)

# ═══════════════════════════════════════════════════════════════════════════════
# HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point - show language selection."""
    ctx.user_data.clear()
    
    keyboard = [
        [InlineKeyboardButton("🇺🇦 Українська", callback_data=f"lang:{LANG_UK}")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data=f"lang:{LANG_RU}")],
        [InlineKeyboardButton("🇬🇧 English", callback_data=f"lang:{LANG_EN}")],
    ]
    
    await send_or_edit(update, "🌍 Оберіть мову / Выберите язык / Choose language:", keyboard)
    return STATE_LANGUAGE


async def on_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Language selected - show main menu."""
    lang = update.callback_query.data.split(":")[1]
    ctx.user_data["lang"] = lang
    return await show_menu(update, ctx)


async def show_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Display main menu."""
    keyboard = [
        [InlineKeyboardButton(t(ctx, "btn_requisites"), callback_data=f"act:{ACT_REQUISITES}")],
        [InlineKeyboardButton(t(ctx, "btn_new_employee"), callback_data=f"act:{ACT_NEW_EMPLOYEE}")],
        [InlineKeyboardButton(t(ctx, "btn_change_contacts"), callback_data=f"act:{ACT_CHANGE_CONTACTS}")],
    ]
    
    await send_or_edit(update, t(ctx, "menu_title"), keyboard)
    return STATE_MENU


async def on_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Action selected - ask for name."""
    action = update.callback_query.data.split(":")[1]
    ctx.user_data["action"] = action
    
    keyboard = [[InlineKeyboardButton(t(ctx, "btn_back"), callback_data="back:menu")]]
    await send_or_edit(update, t(ctx, "enter_name"), keyboard)
    return STATE_NAME


async def on_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Name received - ask for wallet or telegram."""
    ctx.user_data["name"] = update.message.text.strip()
    action = ctx.user_data.get("action")
    
    keyboard = [[InlineKeyboardButton(t(ctx, "btn_back"), callback_data="back:name")]]
    
    if action == ACT_REQUISITES:
        await update.message.reply_text(t(ctx, "enter_wallet"), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return STATE_WALLET
    else:
        await update.message.reply_text(t(ctx, "enter_telegram"), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return STATE_TELEGRAM


async def on_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Wallet received - show confirmation."""
    ctx.user_data["value"] = update.message.text.strip()
    return await show_confirm(update, ctx)


async def on_telegram(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Telegram received - show confirmation."""
    ctx.user_data["value"] = update.message.text.strip()
    return await show_confirm(update, ctx)


async def show_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show confirmation screen."""
    action = ctx.user_data.get("action")
    name = ctx.user_data.get("name")
    value = ctx.user_data.get("value")
    
    action_text = t(ctx, f"action_{action}")
    
    if action == ACT_REQUISITES:
        value_label = t(ctx, "confirm_wallet")
    else:
        value_label = t(ctx, "confirm_telegram")
    
    text = (
        f"{t(ctx, 'confirm_title')}\n"
        f"📋 *{t(ctx, 'confirm_action')}:* {action_text}\n"
        f"👤 *{t(ctx, 'confirm_name')}:* {name}\n"
        f"📱 *{value_label}:* `{value}`"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(t(ctx, "btn_confirm"), callback_data="confirm:yes"),
            InlineKeyboardButton(t(ctx, "btn_cancel"), callback_data="confirm:no"),
        ]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return STATE_CONFIRM


async def on_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle confirmation."""
    choice = update.callback_query.data.split(":")[1]
    
    if choice == "yes":
        # Send to channel
        user = update.effective_user
        await send_to_channel(
            bot=ctx.bot,
            action=ctx.user_data["action"],
            name=ctx.user_data["name"],
            value=ctx.user_data["value"],
            user_id=user.id,
            username=user.username
        )
        
        keyboard = [[InlineKeyboardButton(t(ctx, "btn_restart"), callback_data="restart")]]
        await send_or_edit(update, t(ctx, "saved"), keyboard)
    else:
        keyboard = [[InlineKeyboardButton(t(ctx, "btn_restart"), callback_data="restart")]]
        await send_or_edit(update, t(ctx, "cancelled"), keyboard)
    
    return ConversationHandler.END


async def on_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle back navigation."""
    target = update.callback_query.data.split(":")[1]
    
    if target == "menu":
        return await show_menu(update, ctx)
    elif target == "name":
        keyboard = [[InlineKeyboardButton(t(ctx, "btn_back"), callback_data="back:menu")]]
        await send_or_edit(update, t(ctx, "enter_name"), keyboard)
        return STATE_NAME
    
    return await show_menu(update, ctx)


async def on_restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Restart from language selection."""
    return await cmd_start(update, ctx)


async def error_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors gracefully."""
    log.error(f"Error: {ctx.error}", exc_info=ctx.error)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    log.info(f"Channel ID: {CHANNEL_ID}")
    
    app = Application.builder().token(TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
            CallbackQueryHandler(on_restart, pattern="^restart$"),
        ],
        states={
            STATE_LANGUAGE: [
                CallbackQueryHandler(on_language, pattern=r"^lang:"),
            ],
            STATE_MENU: [
                CallbackQueryHandler(on_action, pattern=r"^act:"),
            ],
            STATE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_name),
                CallbackQueryHandler(on_back, pattern=r"^back:"),
            ],
            STATE_WALLET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_wallet),
                CallbackQueryHandler(on_back, pattern=r"^back:"),
            ],
            STATE_TELEGRAM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_telegram),
                CallbackQueryHandler(on_back, pattern=r"^back:"),
            ],
            STATE_CONFIRM: [
                CallbackQueryHandler(on_confirm, pattern=r"^confirm:"),
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CallbackQueryHandler(on_restart, pattern="^restart$"),
        ],
        allow_reentry=True,
    )
    
    app.add_handler(conv)
    app.add_error_handler(error_handler)
    
    log.info("🚀 LegendsHR Bot v4.0 started! (Channel mode)")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
