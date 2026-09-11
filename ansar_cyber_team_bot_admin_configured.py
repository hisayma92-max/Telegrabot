"""
ANSAR CYBER TEAM — Safe Telegram Bot Demo
------------------------------------------
This bot recreates the requested Telegram-style menu and admin/user separation.

IMPORTANT:
- The "SMS BOMBER", "EMAIL BOMBER", "BULK SMS" and "PRANK CALL" buttons are DEMO ONLY.
- This code does NOT send calls, SMS, emails, spam, or requests to third-party services.
- Replace BOT_TOKEN and ADMIN_ID before running.
- User data is stored locally in bot_data.json.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================
# CONFIG — FILL THESE IN
# =========================
BOT_TOKEN = "8684552528:AAGXCXd8GRfFjQQ7HUxhOa5eNlGcrCwK4-w"
ADMIN_ID = 7740120627  # Sole admin Telegram numeric ID

DATA_FILE = Path("bot_data.json")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# =========================
# LOCAL DATA
# =========================
def load_data() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        return {
            "users": {},
            "subscriptions": {},
            "usage": {},
        }

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"users": {}, "subscriptions": {}, "usage": {}}


def save_data(data: Dict[str, Any]) -> None:
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def register_user(user) -> Dict[str, Any]:
    data = load_data()
    uid = str(user.id)

    if uid not in data["users"]:
        data["users"][uid] = {
            "id": user.id,
            "name": user.full_name,
            "username": user.username or "N/A",
        }
        data["usage"][uid] = {
            "prank_call": 0,
            "sms_bomber": 0,
            "email_bomber": 0,
            "bulk_sms": 0,
        }
        save_data(data)

    return data


def is_admin(user_id: int) -> bool:
    return ADMIN_ID != 0 and user_id == ADMIN_ID


# =========================
# KEYBOARDS
# =========================
def user_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🚀 PRANK CALL", callback_data="demo:prank")],
        [
            InlineKeyboardButton("✉️ BULK SMS", callback_data="demo:bulk"),
            InlineKeyboardButton("💣 SMS BOMBER", callback_data="demo:sms"),
            InlineKeyboardButton("📧 EMAIL BOMBER", callback_data="demo:email"),
        ],
        [
            InlineKeyboardButton("👤 PROFILE", callback_data="profile"),
            InlineKeyboardButton("🎁 BONUS", callback_data="bonus"),
            InlineKeyboardButton("🔗 REFER", callback_data="refer"),
        ],
        [
            InlineKeyboardButton("🎟 REDEEM", callback_data="redeem"),
            InlineKeyboardButton("🎙 CALL RECORD", callback_data="call_record"),
            InlineKeyboardButton("🛒 SUBSCRIPTION", callback_data="subscription"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📊 BOT STATS", callback_data="admin:stats"),
            InlineKeyboardButton("👥 USERS", callback_data="admin:users"),
        ],
        [
            InlineKeyboardButton("📢 BROADCAST", callback_data="admin:broadcast"),
            InlineKeyboardButton("🧹 RESET STATS", callback_data="admin:reset"),
        ],
        [
            InlineKeyboardButton("⬅️ USER MENU", callback_data="home"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# =========================
# TEXT SCREENS
# =========================
def home_text(user) -> str:
    role = "👑 ADMIN ACCESS" if is_admin(user.id) else "👤 USER ACCESS"

    return (
        "🟢 *ANSAR CYBER TEAM*\n\n"
        "⚡ NEON CONTROL PANEL • DEMO MODE\n"
        f"🔐 Access: *{role}*\n\n"
        "Choose an option from the buttons below.\n\n"
        "⚠️ All communication/testing actions in this version are "
        "non-operational demos."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)

    await update.message.reply_text(
        home_text(user),
        parse_mode="Markdown",
        reply_markup=user_keyboard(),
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)

    if not is_admin(user.id):
        await update.message.reply_text("❌ Admin access denied.")
        return

    await update.message.reply_text(
        "👑 *ADMIN CONTROL PANEL*\n\n"
        "Only the configured ADMIN_ID can use these controls.",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )


# =========================
# CALLBACKS
# =========================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data
    register_user(user)

    # ----- Admin-only callbacks -----
    if data.startswith("admin:"):
        if not is_admin(user.id):
            await query.edit_message_text("❌ Admin access denied.")
            return

        action = data.split(":", 1)[1]
        db = load_data()

        if action == "stats":
            users = len(db["users"])
            usage = db.get("usage", {})

            totals = {
                "prank_call": sum(v.get("prank_call", 0) for v in usage.values()),
                "sms_bomber": sum(v.get("sms_bomber", 0) for v in usage.values()),
                "email_bomber": sum(v.get("email_bomber", 0) for v in usage.values()),
                "bulk_sms": sum(v.get("bulk_sms", 0) for v in usage.values()),
            }

            text = (
                "📊 *BOT STATISTICS*\n\n"
                f"👥 Registered users: `{users}`\n"
                f"🚀 Demo prank calls: `{totals['prank_call']}`\n"
                f"💣 Demo SMS actions: `{totals['sms_bomber']}`\n"
                f"📧 Demo email actions: `{totals['email_bomber']}`\n"
                f"✉️ Demo bulk SMS actions: `{totals['bulk_sms']}`"
            )

            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=admin_keyboard(),
            )
            return

        if action == "users":
            users = db["users"]
            if not users:
                text = "👥 No users registered yet."
            else:
                lines = ["👥 *REGISTERED USERS*\n"]
                for i, u in enumerate(users.values(), start=1):
                    lines.append(
                        f"{i}. `{u['id']}` — {u['name']} (@{u['username']})"
                    )
                text = "\n".join(lines[:101])

            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=admin_keyboard(),
            )
            return

        if action == "reset":
            for uid in db["usage"]:
                db["usage"][uid] = {
                    "prank_call": 0,
                    "sms_bomber": 0,
                    "email_bomber": 0,
                    "bulk_sms": 0,
                }
            save_data(db)

            await query.edit_message_text(
                "✅ Demo usage statistics reset.",
                reply_markup=admin_keyboard(),
            )
            return

        if action == "broadcast":
            context.user_data["awaiting_broadcast"] = True
            await query.edit_message_text(
                "📢 *BROADCAST MODE*\n\n"
                "Send your next message and it will be prepared as a "
                "broadcast preview.\n\n"
                "For safety, this template does not automatically send "
                "messages to users.",
                parse_mode="Markdown",
                reply_markup=admin_keyboard(),
            )
            return

    # ----- Normal user callbacks -----
    if data == "home":
        await query.edit_message_text(
            home_text(user),
            parse_mode="Markdown",
            reply_markup=user_keyboard(),
        )
        return

    if data == "profile":
        db = load_data()
        uid = str(user.id)
        usage = db["usage"].get(uid, {})

        text = (
            "👤 *PROFILE INFO*\n\n"
            f"🎂 Name: *{user.full_name}*\n"
            f"🆔 Chat ID: `{user.id}`\n"
            "⏳ Subscription Left: Demo Mode 🟢\n\n"
            "📊 *Usage Statistics:*\n"
            f"🚀 Prank Calls: {usage.get('prank_call', 0)}\n"
            f"💣 SMS Demo: {usage.get('sms_bomber', 0)}\n"
            f"📧 Email Demo: {usage.get('email_bomber', 0)}\n"
            f"✉️ Bulk SMS Demo: {usage.get('bulk_sms', 0)}"
        )

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=user_keyboard(),
        )
        return

    if data == "bonus":
        await query.edit_message_text(
            "🎁 *BONUS*\n\n"
            "Demo bonus system is ready for future integration.",
            parse_mode="Markdown",
            reply_markup=user_keyboard(),
        )
        return

    if data == "refer":
        await query.edit_message_text(
            "🔗 *REFER*\n\n"
            "Referral system placeholder.\n"
            "A real referral/reward system can be added later.",
            parse_mode="Markdown",
            reply_markup=user_keyboard(),
        )
        return

    if data == "redeem":
        await query.edit_message_text(
            "🎟 *REDEEM*\n\n"
            "Enter a valid demo redemption code in the future.",
            parse_mode="Markdown",
            reply_markup=user_keyboard(),
        )
        return

    if data == "call_record":
        await query.edit_message_text(
            "🎙 *CALL RECORD*\n\n"
            "No real calls are made or recorded by this safe demo.",
            parse_mode="Markdown",
            reply_markup=user_keyboard(),
        )
        return

    if data == "subscription":
        await query.edit_message_text(
            "🛒 *SUBSCRIPTION PACKAGE*\n\n"
            "15 Days — 80 BDT\n"
            "30 Days — 120 BDT\n\n"
            "Payment processing is intentionally not connected in this demo.",
            parse_mode="Markdown",
            reply_markup=user_keyboard(),
        )
        return

    if data.startswith("demo:"):
        action = data.split(":", 1)[1]
        db = load_data()
        uid = str(user.id)

        usage_key = {
            "prank": "prank_call",
            "bulk": "bulk_sms",
            "sms": "sms_bomber",
            "email": "email_bomber",
        }[action]

        db["usage"].setdefault(uid, {
            "prank_call": 0,
            "sms_bomber": 0,
            "email_bomber": 0,
            "bulk_sms": 0,
        })
        db["usage"][uid][usage_key] += 1
        save_data(db)

        labels = {
            "prank": "🚀 PRANK CALL",
            "bulk": "✉️ BULK SMS",
            "sms": "💣 SMS BOMBER",
            "email": "📧 EMAIL BOMBER",
        }

        await query.edit_message_text(
            f"{labels[action]}\n\n"
            "🟢 DEMO MODE\n\n"
            "This button is only a UI/demo action. "
            "It does not send calls, SMS, emails, spam, or requests "
            "to any external target.",
            reply_markup=user_keyboard(),
        )
        return


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)

    if is_admin(user.id) and context.user_data.get("awaiting_broadcast"):
        context.user_data["awaiting_broadcast"] = False

        await update.message.reply_text(
            "📢 *BROADCAST PREVIEW*\n\n"
            f"{update.message.text}\n\n"
            "ℹ️ Preview only. Automatic mass messaging is disabled in this safe template.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(),
        )
        return

    await update.message.reply_text(
        home_text(user),
        parse_mode="Markdown",
        reply_markup=user_keyboard(),
    )


def main():
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise SystemExit(
            "Please put your Telegram bot token into BOT_TOKEN first."
        )

    if ADMIN_ID == 0:
        raise SystemExit(
            "Please put your Telegram numeric ID into ADMIN_ID first."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("ANSAR CYBER TEAM bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
