#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import re
from datetime import datetime, timedelta
import jdatetime
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ==================== تنظیمات ====================
TELEGRAM_TOKEN = "8994650800:AAEZFoV2TMjTTWeabqTDZmfqCoFaSzDvVK8"
AUTHORIZED_USER_ID = 549531253
SPREADSHEET_ID = "1KYS6HrD2BTPwjZ08DjNPLAPlDHWPMyBwS8zigA15vAY"

SHEET_MOJOODI = "موجودی"
SHEET_HAZINE = "هزینه ها"
SHEET_FOROSH = "فروش روزانه"

SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "capable-memory-482615-e5",
  "private_key_id": "42aaede2a375c72cbbfd895452e3f9dd1858723e",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6uPoqfd9/+Ffr\nOV2zFCcF7X9mWjFdyujGb6Dbb7bitdGhkSrgFLRJEDX5ZI5CiHhinhPjbVWToQvq\nCbPk3iJazJRXZzwlgUeMN9B7cIEVZ9XHBD9LE29sB014NwSpIXC06tFnsFjswz+V\nP8hFml+41ZoEQSIdFsuGqbJuP1aKbzCN6bDfG1d4dL+PmnnzBmM42980ECRJRbjJ\nAiWFuyeOZ6JJdneKONbYWS4Fu89zLIFWLrbuk/rb6aTu/OAIm5kpXgNfVa4Q6kFX\nFmgBwD2b332/k3pnL/xQNIwLmBHe6Z7jc80dkMLCra9nLYrDB5v+8MrHtKRvdJ+X\nhLNSMKWJAgMBAAECggEADgeekmlFTRP/pSa5Dd7WhMlA0JO30FyR63ERRNOqyfOP\n5gQmlNIxbqj3aT7/OmwPIZfPlj/NlYtc/g+PEwQG0Ew9XCjfWdESK2y5L0E3jcBw\nzWSaDd3Oui79SOpXYQ7obUuUguY69EVCZog1l9c+2IBCM44iTk27aqmfBM4hBkMu\nJuamvH8IVYwfIlVJxYO+nm7rpxn0+DRF6S1tHmUKJIb7P0XRx09lj4Zj+llzHqQF\nkExUudbwX0Q3ZFivvgPacqrVHF7EsjotynftNaaAR1+RdJeZBDYNvYxZie0+fFD/\nDaMp62UlfG6C7o3022WlpGB/rtDfvLEsyCl5FqKmQQKBgQDdSXmelMUrTn8zkp19\nLHyP5IQHkq6BAgOBwY3YFgT2J4ppLK5M8bLp9f3a46WwzwLcxCXA+hkjnuvplBmy\nTfJ6xxtmTBJyyJYdIfsvVWJRC9ZDn5+1wJhQLprDJbmmQVg1gqQ+7315Z/u9qGBc\nzIcS3MIpvnD+8uD/JO1nHIZfoQKBgQDYA3NTl5bXRufTXpysxuAeNVftxqab0p/0\npL0BOAZUdsdmaAsjAwlh+jVmTdnKKBzlL/qVvjjiK8QBHn/t/q5zCBYLtRSRuaRl\neGFHRx+A7ccU61naauGMnxgY3dJxGNg2aQ1xlW+wDT8mVyGItwMTFNcKMNY8Wesi\n4UkOaq4c6QKBgQDIy388UqqHHXd3CLc3ekKdHzJe3M7T6UvdVhCr328pHcAOp6iR\n0VAT1E9BbAhRY8apJKNNdKOTGwXesbCPhwNcPYezT5v9492zGb6fuM651A/c1N9L\nQTP0rhVotra7EdhE1gLLyO0GWUCpXDv0ePKoPwFAd7p43VMkshFp2wxjgQKBgEdt\nxKnkm31uNeRgCcDcNmnmy7+Vi6xFFp2IB/OqOfWeHUuQpfYa3/RlD1lX7ud5Iizr\nE5qGfzrSrAqOslDZgYgKKXgPldCmKWVgTBKMwy8X8VfKhzjBVPnx9b7rQtYhGAXN\n8SMY/giiKLqd3zndAohBwOXexkjIlwc+pbC9t/tZAoGAbQ+YG0IrZ/eIkWXFLxeB\nzd3w/agBYjMNjqxOb0IidlLMt3ecMoQBcGWakUdIxw9gMjofUl2S9ZEdQTWUDoOh\nZibApWz8eYhvlxUwI2uAGr+t0ChavKGmivkq0EF+oJAF3tk6hl0SoBJa7POdfeHz\n3L499HnPld+Qd1tWvvtjqFk=\n-----END PRIVATE KEY-----\n",
  "client_email": "abzarforoshi@capable-memory-482615-e5.iam.gserviceaccount.com",
  "client_id": "116892713672063713468",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/abzarforoshi%40capable-memory-482615-e5.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# ==================== لاگ ====================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== گوگل شیت ====================
def get_sheets():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet

def get_shamsi_date():
    now = jdatetime.datetime.now()
    return now.strftime("%Y/%m/%d"), now.strftime("%H:%M")

def format_price(price):
    return f"{int(price):,}"

# ==================== موجودی ====================
def find_item(sheet_mojoodi, name):
    records = sheet_mojoodi.get_all_values()
    for i, row in enumerate(records[1:], start=2):
        if row and row[0].strip() == name.strip():
            return i, row
    return None, None

def add_or_update_item(name, price):
    sp = get_sheets()
    sh = sp.worksheet(SHEET_MOJOODI)
    date_str, _ = get_shamsi_date()
    row_num, existing = find_item(sh, name)
    
    if existing:
        sh.update_cell(row_num, 2, price)
        sh.update_cell(row_num, 4, date_str)
        return "update", existing[1] if len(existing) > 1 else 0
    else:
        new_row = [name, price, 0, date_str, ""]
        sh.append_row(new_row)
        return "new", 0

def get_item_price(name):
    sp = get_sheets()
    sh = sp.worksheet(SHEET_MOJOODI)
    _, row = find_item(sh, name)
    if row and len(row) > 1:
        try:
            return int(str(row[1]).replace(',', '').replace(' ', ''))
        except:
            return 0
    return 0

# ==================== فروش ====================
def add_sale(name, count, sell_price):
    sp = get_sheets()
    sh_forosh = sp.worksheet(SHEET_FOROSH)
    date_str, time_str = get_shamsi_date()
    buy_price = get_item_price(name)
    profit = (sell_price - buy_price) * count
    new_row = [name, count, date_str + " " + time_str, buy_price, sell_price, profit]
    sh_forosh.append_row(new_row)
    return buy_price, profit

# ==================== هزینه ====================
def add_expense(expense_type, amount, description=""):
    sp = get_sheets()
    sh = sp.worksheet(SHEET_HAZINE)
    date_str, _ = get_shamsi_date()
    new_row = [expense_type, date_str, amount, description]
    sh.append_row(new_row)

# ==================== گزارش ====================
def get_report(period="روزانه"):
    sp = get_sheets()
    sh_forosh = sp.worksheet(SHEET_FOROSH)
    sh_hazine = sp.worksheet(SHEET_HAZINE)
    
    today = jdatetime.date.today()
    
    if period == "روزانه":
        start_date = today
        title = f"گزارش روزانه - {today.strftime('%Y/%m/%d')}"
    elif period == "هفتگی":
        start_date = today - jdatetime.timedelta(days=7)
        title = f"گزارش هفتگی - {start_date.strftime('%Y/%m/%d')} تا {today.strftime('%Y/%m/%d')}"
    else:
        start_date = today.replace(day=1)
        title = f"گزارش ماهانه - {today.strftime('%Y/%m')}"

    sales = sh_forosh.get_all_values()[1:]
    expenses = sh_hazine.get_all_values()[1:]

    filtered_sales = []
    for row in sales:
        if not row or not row[0]:
            continue
        try:
            date_part = str(row[2]).split(" ")[0] if len(row) > 2 else ""
            parts = date_part.split("/")
            if len(parts) == 3:
                row_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                if row_date >= start_date:
                    filtered_sales.append(row)
        except:
            continue

    filtered_expenses = []
    for row in expenses:
        if not row or not row[0]:
            continue
        try:
            date_part = str(row[1]) if len(row) > 1 else ""
            parts = date_part.split("/")
            if len(parts) == 3:
                row_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                if row_date >= start_date:
                    filtered_expenses.append(row)
        except:
            continue

    total_revenue = 0
    total_profit = 0
    items_summary = {}

    for row in filtered_sales:
        try:
            name = row[0]
            count = int(str(row[1]).replace(',', ''))
            sell_price = int(str(row[4]).replace(',', ''))
            profit = int(str(row[5]).replace(',', ''))
            revenue = sell_price * count
            total_revenue += revenue
            total_profit += profit
            if name not in items_summary:
                items_summary[name] = {"count": 0, "revenue": 0, "profit": 0, "buy": int(str(row[3]).replace(',', '')), "sell": sell_price}
            items_summary[name]["count"] += count
            items_summary[name]["revenue"] += revenue
            items_summary[name]["profit"] += profit
        except:
            continue

    total_expenses = sum(int(str(r[2]).replace(',', '')) for r in filtered_expenses if len(r) > 2 and r[2])
    net_profit = total_profit - total_expenses

    lines = [f"📊 *{title}*\n"]
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("🛒 *فروش‌ها:*\n")

    for name, data in items_summary.items():
        lines.append(f"▪️ *{name}*")
        lines.append(f"   تعداد: {data['count']} عدد")
        lines.append(f"   قیمت خرید: {format_price(data['buy'])} تومان")
        lines.append(f"   قیمت فروش: {format_price(data['sell'])} تومان")
        lines.append(f"   سود: {format_price(data['profit'])} تومان\n")

    lines.append("━━━━━━━━━━━━━━━━")
    lines.append(f"💰 *فروش کل:* {format_price(total_revenue)} تومان")
    lines.append(f"📈 *مجموع سود فروش:* {format_price(total_profit)} تومان")

    if filtered_expenses:
        lines.append(f"\n💸 *هزینه‌ها:*")
        for row in filtered_expenses:
            lines.append(f"   • {row[0]}: {format_price(int(str(row[2]).replace(',','')))} تومان")
        lines.append(f"📉 *مجموع هزینه‌ها:* {format_price(total_expenses)} تومان")

    lines.append("━━━━━━━━━━━━━━━━")
    emoji = "✅" if net_profit >= 0 else "❌"
    lines.append(f"{emoji} *سود خالص:* {format_price(net_profit)} تومان")

    if not items_summary:
        return f"📊 *{title}*\n\nدر این بازه هیچ فروشی ثبت نشده است."

    return "\n".join(lines)

# ==================== پردازش پیام ====================
def parse_message(text):
    text = text.strip()

    # گزارش
    if "گزارش روزانه" in text:
        return ("report", "روزانه")
    if "گزارش هفتگی" in text:
        return ("report", "هفتگی")
    if "گزارش ماهانه" in text:
        return ("report", "ماهانه")

    # تغییر قیمت: قیمت دریل 2800000
    m = re.match(r'^قیمت\s+(.+?)\s+([\d,]+)$', text)
    if m:
        name = m.group(1).strip()
        price = int(m.group(2).replace(',', ''))
        return ("update_price", name, price)

    # ثبت فروش: فروش دریل 2 عدد 3500000
    m = re.match(r'^فروش\s+(.+?)\s+(\d+)\s*عدد\s+([\d,]+)$', text)
    if m:
        name = m.group(1).strip()
        count = int(m.group(2))
        price = int(m.group(3).replace(',', ''))
        return ("sale", name, count, price)

    # ثبت هزینه: کرایه بار 500000 یا هزینه xxx 300000
    m = re.match(r'^(.+?)\s+([\d,]+)$', text)
    if m:
        label = m.group(1).strip()
        amount = int(m.group(2).replace(',', ''))
        keywords = ["هزینه", "کرایه", "اجاره", "برق", "آب", "گاز", "تلفن", "بیمه", "مالیات", "حقوق", "تعمیر"]
        if any(k in label for k in keywords):
            return ("expense", label, amount)
        # ثبت کالا: دریل 2500000
        return ("item", label, amount)

    return ("unknown",)

# ==================== هندلر اصلی ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != AUTHORIZED_USER_ID:
        await update.message.reply_text("⛔ شما مجاز به استفاده از این ربات نیستید.")
        return

    text = update.message.text
    if not text:
        return

    try:
        result = parse_message(text)
        action = result[0]

        if action == "item":
            name, price = result[1], result[2]
            status, old_price = add_or_update_item(name, price)
            if status == "new":
                msg = f"✅ *کالای جدید ثبت شد*\n\n📦 نام: {name}\n💰 قیمت خرید: {format_price(price)} تومان"
            else:
                msg = f"✅ *قیمت کالا بروزرسانی شد*\n\n📦 نام: {name}\n💰 قیمت قبلی: {format_price(old_price)} تومان\n💰 قیمت جدید: {format_price(price)} تومان"
            await update.message.reply_text(msg, parse_mode='Markdown')

        elif action == "update_price":
            name, price = result[1], result[2]
            status, old_price = add_or_update_item(name, price)
            msg = f"✅ *قیمت بروزرسانی شد*\n\n📦 نام: {name}\n💰 قیمت جدید: {format_price(price)} تومان"
            await update.message.reply_text(msg, parse_mode='Markdown')

        elif action == "sale":
            name, count, sell_price = result[1], result[2], result[3]
            buy_price, profit = add_sale(name, count, sell_price)
            msg = (f"✅ *فروش ثبت شد*\n\n"
                   f"📦 کالا: {name}\n"
                   f"🔢 تعداد: {count} عدد\n"
                   f"💰 قیمت خرید: {format_price(buy_price)} تومان\n"
                   f"💵 قیمت فروش: {format_price(sell_price)} تومان\n"
                   f"📈 سود این فروش: {format_price(profit)} تومان")
            await update.message.reply_text(msg, parse_mode='Markdown')

        elif action == "expense":
            label, amount = result[1], result[2]
            add_expense(label, amount)
            msg = f"✅ *هزینه ثبت شد*\n\n📝 نوع: {label}\n💸 مبلغ: {format_price(amount)} تومان"
            await update.message.reply_text(msg, parse_mode='Markdown')

        elif action == "report":
            period = result[1]
            await update.message.reply_text("⏳ در حال تهیه گزارش...")
            report = get_report(period)
            await update.message.reply_text(report, parse_mode='Markdown')

        else:
            help_text = (
                "❓ *راهنمای دستورات:*\n\n"
                "📦 *ثبت کالا:*\n`دریل 2500000`\n\n"
                "✏️ *تغییر قیمت:*\n`قیمت دریل 2800000`\n\n"
                "🛒 *ثبت فروش:*\n`فروش دریل 2 عدد 3500000`\n\n"
                "💸 *ثبت هزینه:*\n`کرایه بار 500000`\n\n"
                "📊 *گزارش‌ها:*\n`گزارش روزانه`\n`گزارش هفتگی`\n`گزارش ماهانه`"
            )
            await update.message.reply_text(help_text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"⚠️ خطا: {str(e)}\n\nلطفاً دوباره امتحان کنید.")

# ==================== اجرا ====================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("ربات شروع به کار کرد...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
