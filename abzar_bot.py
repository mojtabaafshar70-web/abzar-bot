import logging
import re
import jdatetime
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8994650800:AAEZFoV2TMjTTWeabqTDZmfqCoFaSzDvVK8"
AUTHORIZED_USER_ID = 549531253
SPREADSHEET_ID = "1KYS6HrD2BTPwjZ08DjNPLAPlDHWPMyBwS8zigA15vAY"
SHEET_MOJOODI = "موجودی"
SHEET_HAZINE = "هزینه ها"
SHEET_FOROSH = "فروش روزانه"

PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDVDvL9zL6BU2pe\nzdTD7RWN1gQQhQ9uIraUS84NIzmCa8o7x0pkFvuNtLjcrePIZxwSCgTJqu2AeD1q\nf06JY2TSj/fHydCflXtpIdOa0msUWv7WhPUjA5yQZFQlB/xMksB1X3m3XiCKkNgi\n2NiIVOJDwklQuO8U633qSqPGiB+mjyM2+Waw/jhTQFtRAdBDDoPzc5NF85w3WcDQ\nfoJvZ9Ef9qN0RzxyciBHvDWR+UpbnHId1Q4P65J73SUz4XUQvWwFJVD9vgJX/ez7\nfugnt3LvxnC2Z+Q5bbv2wxnldh+UE9wM+/svwDhFSNnuwWUBKlPeHoArgWmCc9BP\nJYDW73GXAgMBAAECggEAB3WsVYbx2jTueEuvbTC23K5BAPpEeqNMGzZQP5Ubi8QN\n/GvTRsMOcBa2X9uiw9iAWubvTGEbGBcEDd+C0Dw8daoR9dr/qya6GTzUjz4nMgfb\nL+2cNTg7wH55LiOKcBZPSlmObGvAqrlWWybJstqt+8tb2WMWoKsVT7ro4w5oqHv+\niZCcAUnR0vytKyEEZudenlTv3oWzIs3rbTFZD1JMzYzU7jXUw7pjuKAANjqEngbB\nqgMn8BVKfChvF5miD5F1j1AzbNOjOylnxj96Nszrng2PQtbpVqABFDVkltACh0U7\nnWz9pt1lgPpQhF6DYoz8la6nzbNyBvKDddSAPv4UCQKBgQDwKQpNu9n8Q9Z3tDPp\ndXdCvzeGFjt5iklvcvl4YeWT2HfaymsvNRJFRwzOi68c7znzvHBBN15lah9B0EAt\nTouIFhIooNGfP1mSMjUz08pWQ6Pv/Ex16dgJCLdVYaz8RnWCl9zi8gtFpPrk1p4A\nXPHSI0FvuMiMuWrjqqeak7yH6wKBgQDjHE9FX1PcYVYxBEAKpaGHCIFsXj7yFqTU\n2ESMT1ClOyypfLlhNYZ5ZyJPxVf79gnEHOPKXWELQl8S2H4svLFDMTc5ByTsJPRx\nrHnIVYpDJLfa5Ruco+m4FTKdgrb7Q6Ya3L5bql3zrYMNaAnk6cvwCftbKGQlo44i\nORSBZWneBQKBgQDKAWtGSU0o8JK0K2JC6+g9v4NfiNHMALKWSPpn9MhbnIfsA7k2\ngwh0Nzghf8LyrpJrXsR5Rq5i1WmnPRjOQzQAargpbmQD9BBOdWbkyi92cfyx/uD9\niY2Kw8cZzUfpBwcOqthEGF283fGfjJpoKcXKAJeo9p/SJqAvEbtavQumswKBgQCg\nwy5d5e/f5Ur04ZRPtRUVF/E9e61FAsBlJj3HsHFetPeVdgNni1MIZvgDzabNZUle\neDDK07TZGn9gQL13/43fCVyU0rjRLAuY18VRCTQY+Unn+hvEksbjlqXAl4HddPKE\nu1NIYd2lm2JUQBwY3WKOJRK3YW0as57uHMemHNqG3QKBgB/kkzBE1/z7HA5QnnrF\nzmrgudtxfLiiggsuWJb/sX25Ff0luUkMddPrSSyZRmB5oMAcHyxmhA37LhJCHiES\nN6C7WggkJtDvNYFgfKJV/r1fujJtZbkVcUIrfcFXoJmJn8hXTzEHNWuJFTrg5YDW\n7wmrytrvaD7F7x5X0OMX644Z\n-----END PRIVATE KEY-----\n"

SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "capable-memory-482615-e5",
  "private_key_id": "e711e07ec620ed77eea0f1e6949ca5b9151528c7",
  "private_key": PRIVATE_KEY,
  "client_email": "abzarforoshi@capable-memory-482615-e5.iam.gserviceaccount.com",
  "client_id": "116892713672063713468",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/abzarforoshi%40capable-memory-482615-e5.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sheets():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

def get_shamsi():
    now = jdatetime.datetime.now()
    return now.strftime("%Y/%m/%d"), now.strftime("%H:%M")

def fp(price):
    try:
        return f"{int(price):,}"
    except:
        return str(price)

def find_item(sh, name):
    rows = sh.get_all_values()
    for i, row in enumerate(rows[1:], start=2):
        if row and row[0].strip() == name.strip():
            return i, row
    return None, None

def add_or_update_item(name, price):
    sp = get_sheets()
    sh = sp.worksheet(SHEET_MOJOODI)
    date_str, _ = get_shamsi()
    row_num, existing = find_item(sh, name)
    if existing:
        old_price = existing[1] if len(existing) > 1 else 0
        sh.update_cell(row_num, 2, price)
        sh.update_cell(row_num, 4, date_str)
        return "update", old_price
    else:
        sh.append_row([name, price, 0, date_str, ""])
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

def add_sale(name, count, sell_price):
    sp = get_sheets()
    sh = sp.worksheet(SHEET_FOROSH)
    date_str, time_str = get_shamsi()
    buy_price = get_item_price(name)
    profit = (sell_price - buy_price) * count
    sh.append_row([name, count, date_str + " " + time_str, buy_price, sell_price, profit])
    return buy_price, profit

def delete_sale(name, count):
    sp = get_sheets()
    sh = sp.worksheet(SHEET_FOROSH)
    rows = sh.get_all_values()
    today = jdatetime.date.today().strftime("%Y/%m/%d")
    for i, row in enumerate(rows[1:], start=2):
        if (row and row[0].strip() == name.strip() and
                str(row[1]).strip() == str(count).strip() and
                today in str(row[2])):
            sh.delete_rows(i)
            return True
    for i, row in enumerate(rows[1:], start=2):
        if row and row[0].strip() == name.strip() and str(row[1]).strip() == str(count).strip():
            sh.delete_rows(i)
            return True
    return False

def add_expense(label, amount):
    sp = get_sheets()
    sh = sp.worksheet(SHEET_HAZINE)
    date_str, _ = get_shamsi()
    sh.append_row([label, date_str, amount, ""])

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
        title = "گزارش هفتگی"
    else:
        start_date = today.replace(day=1)
        title = f"گزارش ماهانه - {today.strftime('%Y/%m')}"
    sales = sh_forosh.get_all_values()[1:]
    expenses = sh_hazine.get_all_values()[1:]
    filtered_sales = []
    for row in sales:
        if not row or not row[0]: continue
        try:
            date_part = str(row[2]).split(" ")[0]
            parts = date_part.split("/")
            if len(parts) == 3:
                rd = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                if rd >= start_date:
                    filtered_sales.append(row)
        except: continue
    filtered_expenses = []
    for row in expenses:
        if not row or not row[0]: continue
        try:
            parts = str(row[1]).split("/")
            if len(parts) == 3:
                rd = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                if rd >= start_date:
                    filtered_expenses.append(row)
        except: continue
    total_revenue = 0
    total_profit = 0
    items = {}
    for row in filtered_sales:
        try:
            name = row[0]
            count = int(str(row[1]).replace(',', ''))
            sell_price = int(str(row[4]).replace(',', ''))
            profit = int(str(row[5]).replace(',', ''))
            buy = int(str(row[3]).replace(',', ''))
            revenue = sell_price * count
            total_revenue += revenue
            total_profit += profit
            if name not in items:
                items[name] = {"count": 0, "revenue": 0, "profit": 0, "buy": buy, "sell": sell_price}
            items[name]["count"] += count
            items[name]["revenue"] += revenue
            items[name]["profit"] += profit
        except: continue
    total_exp = 0
    for r in filtered_expenses:
        try:
            total_exp += int(str(r[2]).replace(',', ''))
        except: continue
    net = total_profit - total_exp
    if not items:
        return f"📊 *{title}*\n\nدر این بازه هیچ فروشی ثبت نشده."
    lines = [f"📊 *{title}*\n━━━━━━━━━━━━━━━━\n🛒 *فروش‌ها:*\n"]
    for name, d in items.items():
        lines.append(f"▪️ *{name}*")
        lines.append(f"   تعداد: {d['count']} عدد")
        lines.append(f"   خرید: {fp(d['buy'])} | فروش: {fp(d['sell'])}")
        lines.append(f"   سود: {fp(d['profit'])} تومان\n")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append(f"💰 فروش کل: {fp(total_revenue)} تومان")
    lines.append(f"📈 مجموع سود: {fp(total_profit)} تومان")
    if filtered_expenses:
        lines.append(f"💸 هزینه‌ها: {fp(total_exp)} تومان")
    lines.append("━━━━━━━━━━━━━━━━")
    emoji = "✅" if net >= 0 else "❌"
    lines.append(f"{emoji} *سود خالص: {fp(net)} تومان*")
    return "\n".join(lines)

def parse_single(text):
    text = text.strip()
    if "گزارش روزانه" in text: return ("report", "روزانه")
    if "گزارش هفتگی" in text: return ("report", "هفتگی")
    if "گزارش ماهانه" in text: return ("report", "ماهانه")
    # حذف فروش (مرجوعی)
    m = re.match(r'^حذف\s+(.+?)\s+(\d+)$', text)
    if m: return ("delete_sale", m.group(1).strip(), int(m.group(2)))
    # تغییر قیمت
    m = re.match(r'^قیمت\s+(.+?)\s+([\d,]+)$', text)
    if m: return ("update_price", m.group(1).strip(), int(m.group(2).replace(',', '')))
    # فروش
    m = re.match(r'^فروش\s+(.+?)\s+(\d+)\s*عدد\s+([\d,]+)$', text)
    if m: return ("sale", m.group(1).strip(), int(m.group(2)), int(m.group(3).replace(',', '')))
    # هزینه یا کالا
    m = re.match(r'^(.+?)\s+([\d,]+)$', text)
    if m:
        label = m.group(1).strip()
        amount = int(m.group(2).replace(',', ''))
        keywords = ["هزینه", "کرایه", "اجاره", "برق", "آب", "گاز", "تلفن", "بیمه", "مالیات", "حقوق", "تعمیر"]
        if any(k in label for k in keywords):
            return ("expense", label, amount)
        return ("item", label, amount)
    return ("unknown",)

def parse_msg(text):
    # اگه چند دستور با - جدا شده بود
    if " - " in text or "\n" in text:
        parts = re.split(r' - |\n', text)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) > 1:
            return [parse_single(p) for p in parts]
    return [parse_single(text)]

async def process_action(result, update):
    action = result[0]
    if action == "item":
        name, price = result[1], result[2]
        status, old = add_or_update_item(name, price)
        if status == "new":
            return f"✅ *کالای جدید ثبت شد*\n📦 {name}\n💰 {fp(price)} تومان"
        else:
            return f"✅ *قیمت بروزرسانی شد*\n📦 {name}\n💰 {fp(price)} تومان"
    elif action == "update_price":
        name, price = result[1], result[2]
        add_or_update_item(name, price)
        return f"✅ *قیمت بروزرسانی شد*\n📦 {name}\n💰 {fp(price)} تومان"
    elif action == "sale":
        name, count, sell_price = result[1], result[2], result[3]
        buy_price, profit = add_sale(name, count, sell_price)
        return (f"✅ *فروش ثبت شد*\n📦 {name}\n🔢 {count} عدد\n"
                f"💰 خرید: {fp(buy_price)} | فروش: {fp(sell_price)}\n"
                f"📈 سود: {fp(profit)} تومان")
    elif action == "delete_sale":
        name, count = result[1], result[2]
        ok = delete_sale(name, count)
        if ok:
            return f"🗑️ *فروش حذف شد*\n📦 {name} - {count} عدد"
        else:
            return f"❌ فروش *{name}* با تعداد {count} پیدا نشد."
    elif action == "expense":
        label, amount = result[1], result[2]
        add_expense(label, amount)
        return f"✅ *هزینه ثبت شد*\n📝 {label}\n💸 {fp(amount)} تومان"
    elif action == "report":
        return get_report(result[1])
    else:
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("⛔ دسترسی ندارید.")
        return
    text = update.message.text
    if not text: return
    try:
        actions = parse_msg(text)
        # اگه گزارش بود اول اعلام کن
        if any(a[0] == "report" for a in actions):
            await update.message.reply_text("⏳ در حال تهیه گزارش...")
        results = []
        for action in actions:
            if action[0] == "unknown":
                continue
            msg = await process_action(action, update)
            if msg:
                results.append(msg)
        if results:
            await update.message.reply_text("\n\n".join(results), parse_mode='Markdown')
        else:
            help_text = (
                "❓ *راهنما:*\n\n"
                "📦 ثبت کالا: `دریل 2500000`\n"
                "✏️ تغییر قیمت: `قیمت دریل 2800000`\n"
                "🛒 ثبت فروش: `فروش دریل 2 عدد 3500000`\n"
                "🗑️ حذف فروش: `حذف قفل آویز 20`\n"
                "💸 ثبت هزینه: `کرایه بار 500000`\n"
                "📊 گزارش: `گزارش روزانه` | `گزارش هفتگی` | `گزارش ماهانه`\n\n"
                "📌 *چند فروش با هم:*\n"
                "`فروش قفل 1 عدد 200000 - فروش مته 2 عدد 50000`"
            )
            await update.message.reply_text(help_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await update.message.reply_text(f"⚠️ خطا رخ داد.\n{str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("ربات شروع به کار کرد...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()