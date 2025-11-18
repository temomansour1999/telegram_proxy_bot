from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import logging
from datetime import datetime
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 6434820732  # Your admin ID

# Proxy data storage
user_sessions = {}
pending_orders = {}
user_languages = {}  # Store user language preferences
order_counter = 1

# Available countries and states
PROXY_LOCATIONS = {
    "US": ["New York", "California", "Texas", "Florida", "Illinois", "Washington"],
    "UK": ["London", "Manchester", "Birmingham", "Liverpool"],
    "Germany": ["Berlin", "Frankfurt", "Munich", "Hamburg"],
    "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary"]
}

AVAILABLE_DAYS = [7, 10, 30]
PROXY_PRICES = {7: 5.00, 10: 7.00, 30: 15.00}

# Language texts
TEXTS = {
    "en": {
        "welcome": "🔧 **Proxy Shop Bot** 🔧\n\nWelcome to our proxy service! Choose an option below:\n\n• 🛒 **Buy Proxy**: Purchase high-quality proxies\n• 💰 **Sell Proxy**: Sell your proxies (coming soon)\n\nClick 'Buy Proxy' to get started!",
        "choose_language": "🌍 **Please choose your language:**",
        "buy_proxy": "🛒 Buy Proxy",
        "sell_proxy": "💰 Sell Proxy",
        "select_country": "🌍 **Select Country**\n\nChoose the country for your proxy:",
        "country_selected": "🌍 **Country: {country}**\n\n📍 **Select State/City:**\nChoose your preferred location:",
        "select_duration": "⏰ **Select Duration**\n\nChoose how many days you want the proxy:",
        "days_button": "📅 {days} Days - ${price}",
        "order_summary": "🛒 **Order Summary**\n\n🌍 **Country:** {country}\n📍 **State:** {state}\n⏰ **Duration:** {days} days\n💰 **Price:** ${price}\n\n**Please confirm your purchase:**",
        "confirm_purchase": "✅ Confirm Purchase",
        "cancel": "❌ Cancel",
        "back": "⬅️ Back",
        "order_received": "⏳ **Order Received!** ⏳\n\n📦 **Order ID:** #{order_id}\n🌍 **Location:** {state}, {country}\n⏰ **Duration:** {days} days\n💰 **Amount:** ${price}\n\n🔄 **Please wait while we process your order...**\nYour proxy details will be sent here once approved by admin.\n\n⏳ Expected time: 1-5 minutes",
        "order_approved": "🎉 **Order Approved!** 🎉\n\n📦 **Order ID:** #{order_id}\n🌍 **Location:** {state}, {country}\n⏰ **Duration:** {days} days\n💰 **Amount:** ${price}\n\n🔧 **Your Proxy Details:**\n**IP:** `{ip}`\n**Port:** `{port}`\n**Username:** `{username}`\n**Password:** `{password}`\n\n**Full format:** `{full_proxy}`\n\n⚡ **Your proxy is now active!**\nExpires in: {days} days\n\nThank you for your purchase! 🛒",
        "order_rejected": "❌ **Order Rejected** ❌\n\n📦 **Order ID:** #{order_id}\n\n😔 **Sorry, something went wrong with your order.**\n\nPlease try again or contact support if the problem persists.\n\nUse /start to begin again.",
        "sell_message": "💰 **Sell Proxies**\n\nOur seller program is currently under development.\nPlease contact @admin for more information.",
        "help_message": "🤖 **Bot Help**\n\nAvailable commands:\n/start - Start the bot\n/buy - Buy a proxy\n/sell - Sell proxies\n/help - Show this help message\n/language - Change language\n\n**Process:**\n1. Select country\n2. Choose state/city\n3. Select duration\n4. Confirm purchase\n5. Wait for admin approval\n6. Receive proxy details"
    },
    "ar": {
        "welcome": "🔧 **بوت متجر البروكسي** 🔧\n\nمرحباً بك في خدمة البروكسي الخاصة بنا! اختر خياراً من الأسفل:\n\n• 🛒 **شراء بروكسي**: شراء بروكسي عالي الجودة\n• 💰 **بيع بروكسي**: بيع بروكسي (قريباً)\n\nانقر 'شراء بروكسي' للبدء!",
        "choose_language": "🌍 **الرجاء اختيار اللغة:**",
        "buy_proxy": "🛒 شراء بروكسي",
        "sell_proxy": "💰 بيع بروكسي",
        "select_country": "🌍 **اختر الدولة**\n\nاختر الدولة للبروكسي:",
        "country_selected": "🌍 **الدولة: {country}**\n\n📍 **اختر الولاية/المدينة:**\nاختر موقعك المفضل:",
        "select_duration": "⏰ **اختر المدة**\n\nاختر عدد الأيام التي تريدها للبروكسي:",
        "days_button": "📅 {days} يوم - ${price}",
        "order_summary": "🛒 **ملخص الطلب**\n\n🌍 **الدولة:** {country}\n📍 **الولاية:** {state}\n⏰ **المدة:** {days} يوم\n💰 **السعر:** ${price}\n\n**الرجاء تأكيد الشراء:**",
        "confirm_purchase": "✅ تأكيد الشراء",
        "cancel": "❌ إلغاء",
        "back": "⬅️ رجوع",
        "order_received": "⏳ **تم استلام الطلب!** ⏳\n\n📦 **رقم الطلب:** #{order_id}\n🌍 **الموقع:** {state}, {country}\n⏰ **المدة:** {days} يوم\n💰 **المبلغ:** ${price}\n\n🔄 **الرجاء الانتظار أثناء معالجة طلبك...**\nسيتم إرسال تفاصيل البروكسي هنا بعد موافقة المسؤول.\n\n⏳ الوقت المتوقع: 1-5 دقائق",
        "order_approved": "🎉 **تمت الموافقة على الطلب!** 🎉\n\n📦 **رقم الطلب:** #{order_id}\n🌍 **الموقع:** {state}, {country}\n⏰ **المدة:** {days} يوم\n💰 **المبلغ:** ${price}\n\n🔧 **تفاصيل البروكسي الخاصة بك:**\n**IP:** `{ip}`\n**المنفذ:** `{port}`\n**اسم المستخدم:** `{username}`\n**كلمة المرور:** `{password}`\n\n**التنسيق الكامل:** `{full_proxy}`\n\n⚡ **بروكسيك نشط الآن!**\nينتهي في: {days} يوم\n\nشكراً لشرائك! 🛒",
        "order_rejected": "❌ **تم رفض الطلب** ❌\n\n📦 **رقم الطلب:** #{order_id}\n\n😔 **عذراً، حدث خطأ ما في طلبك.**\n\nالرجاء المحاولة مرة أخرى أو التواصل مع الدعم إذا استمرت المشكلة.\n\nاستخدم /start للبدء من جديد.",
        "sell_message": "💰 **بيع بروكسي**\n\nبرنامج البائعين قيد التطوير حالياً.\nالرجاء التواصل مع @admin للمزيد من المعلومات.",
        "help_message": "🤖 **مساعدة البوت**\n\nالأوامر المتاحة:\n/start - بدء البوت\n/buy - شراء بروكسي\n/sell - بيع بروكسي\n/help - عرض رسالة المساعدة\n/language - تغيير اللغة\n\n**الخطوات:**\n1. اختر الدولة\n2. اختر الولاية/المدينة\n3. اختر المدة\n4. أكد الشراء\n5. انتظر موافقة المسؤول\n6. استلم تفاصيل البروكسي"
    }
}

def get_user_language(user_id):
    """Get user language preference, default to English."""
    return user_languages.get(user_id, "en")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user_id = update.message.from_user.id
    
    # If user doesn't have language set, show language selection
    if user_id not in user_languages:
        await show_language_selection(update.message)
        return
    
    # User has language set, show main menu
    lang = get_user_language(user_id)
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["buy_proxy"], callback_data="buy_proxy")],
        [InlineKeyboardButton(TEXTS[lang]["sell_proxy"], callback_data="sell")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        TEXTS[lang]["welcome"],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_language_selection(message):
    """Show language selection keyboard."""
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "🌍 **Please choose your language:**\n\n"
        "🇺🇸 English\n"
        "🇸🇦 العربية",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    print(f"🔘 Button clicked: {data} by user {user_id}")  # Debug log
    
    # Handle language selection
    if data.startswith("lang_"):
        language = data.split("_")[1]
        user_languages[user_id] = language
        lang = get_user_language(user_id)
        
        keyboard = [
            [InlineKeyboardButton(TEXTS[lang]["buy_proxy"], callback_data="buy_proxy")],
            [InlineKeyboardButton(TEXTS[lang]["sell_proxy"], callback_data="sell")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            TEXTS[lang]["welcome"],
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    lang = get_user_language(user_id)
    
    if data == "buy_proxy":
        await show_country_selection(query, context, lang)
    elif data.startswith("country_"):
        country = data.split("_")[1]
        user_sessions[user_id] = {"country": country}
        await show_state_selection(query, country, context, lang)
    elif data.startswith("state_"):
        state = data.split("_")[1]
        user_sessions[user_id]["state"] = state
        await show_days_selection(query, context, lang)
    elif data.startswith("days_"):
        days = int(data.split("_")[1])
        user_sessions[user_id]["days"] = days
        await confirm_purchase(query, user_id, context, lang)
    elif data == "confirm_purchase":
        await process_payment(query, user_id, context, lang)
    elif data == "cancel_purchase":
        await query.edit_message_text(TEXTS[lang]["cancel"])
        if user_id in user_sessions:
            del user_sessions[user_id]
    else:
        print(f"❌ Unhandled button data: {data}")

async def show_country_selection(query, context: ContextTypes.DEFAULT_TYPE, lang):
    """Show country selection keyboard."""
    keyboard = []
    for country in PROXY_LOCATIONS.keys():
        keyboard.append([InlineKeyboardButton(f"🇺🇸 {country}", callback_data=f"country_{country}")])
    
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["cancel"], callback_data="cancel_purchase")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        TEXTS[lang]["select_country"],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_state_selection(query, country, context: ContextTypes.DEFAULT_TYPE, lang):
    """Show state selection for the chosen country."""
    states = PROXY_LOCATIONS[country]
    keyboard = []
    
    for state in states:
        keyboard.append([InlineKeyboardButton(f"📍 {state}", callback_data=f"state_{state}")])
    
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["back"], callback_data="buy_proxy")])
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["cancel"], callback_data="cancel_purchase")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        TEXTS[lang]["country_selected"].format(country=country),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_days_selection(query, context: ContextTypes.DEFAULT_TYPE, lang):
    """Show duration selection keyboard."""
    keyboard = []
    
    for days in AVAILABLE_DAYS:
        price = PROXY_PRICES[days]
        keyboard.append([InlineKeyboardButton(
            TEXTS[lang]["days_button"].format(days=days, price=price), 
            callback_data=f"days_{days}"
        )])
    
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["back"], callback_data=f"country_{user_sessions[query.from_user.id]['country']}")])
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["cancel"], callback_data="cancel_purchase")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        TEXTS[lang]["select_duration"],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def confirm_purchase(query, user_id, context: ContextTypes.DEFAULT_TYPE, lang):
    """Show purchase confirmation."""
    session = user_sessions[user_id]
    country = session["country"]
    state = session["state"]
    days = session["days"]
    price = PROXY_PRICES[days]
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["confirm_purchase"], callback_data="confirm_purchase")],
        [InlineKeyboardButton(TEXTS[lang]["cancel"], callback_data="cancel_purchase")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        TEXTS[lang]["order_summary"].format(
            country=country, state=state, days=days, price=price
        ),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def process_payment(query, user_id, context: ContextTypes.DEFAULT_TYPE, lang):
    """Process the payment and notify admin for manual approval."""
    global order_counter
    
    session = user_sessions[user_id]
    country = session["country"]
    state = session["state"]
    days = session["days"]
    price = PROXY_PRICES[days]
    user = query.from_user

    # Create order
    order_id = order_counter
    order_counter += 1
    
    # Get username - prefer @username, fallback to "No username"
    username = f"@{user.username}" if user.username else "No username"
    
    order_data = {
        "order_id": order_id,
        "user_id": user_id,
        "user_name": username,
        "country": country,
        "state": state,
        "days": days,
        "price": price,
        "timestamp": datetime.now(),
        "message_id": query.message.message_id,
        "user_language": lang  # Store user language for notifications
    }
    
    pending_orders[order_id] = order_data
    
    print(f"🛒 New order received: #{order_id} from user {user_id}")
    print(f"📊 Order details: {state}, {country} - {days} days - ${price}")
    print(f"👤 Username: {username}")
    print(f"🌐 Language: {lang}")
    
    # Show waiting message to user
    await query.edit_message_text(
        TEXTS[lang]["order_received"].format(
            order_id=order_id, state=state, country=country, days=days, price=price
        ),
        parse_mode='Markdown'
    )
    
    # Notify admin
    print(f"📢 Attempting to notify admin {ADMIN_ID} about order #{order_id}")
    await notify_admin(order_id, context.bot)

async def notify_admin(order_id, bot):
    """Notify admin about new order with input field for proxy details."""
    try:
        order = pending_orders[order_id]
        
        # Create inline keyboard with input field simulation
        keyboard = [
            [InlineKeyboardButton("📝 Enter Proxy Details", callback_data=f"admin_input_{order_id}")],
            [
                InlineKeyboardButton("✅ Approve & Send", callback_data=f"admin_approve_{order_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{order_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        admin_message = await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🆕 **NEW ORDER - ACTION REQUIRED** 🆕\n\n"
                 f"📦 **Order ID:** #{order_id}\n"
                 f"👤 **Username:** {order['user_name']}\n"
                 f"🌐 **Language:** {order['user_language'].upper()}\n"
                 f"🆔 **User ID:** {order['user_id']}\n"
                 f"🌍 **Location:** {order['state']}, {order['country']}\n"
                 f"⏰ **Duration:** {order['days']} days\n"
                 f"💰 **Amount:** ${order['price']}\n"
                 f"🕒 **Time:** {order['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                 f"**Instructions:**\n"
                 f"1. Click '📝 Enter Proxy Details' to set proxy info\n"
                 f"2. Click '✅ Approve & Send' to send proxy to user\n"
                 f"3. Click '❌ Reject' to reject the order\n\n"
                 f"**Current Proxy Details:**\n"
                 f"`{pending_orders[order_id].get('proxy_details', 'Not set yet')}`",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Store admin message ID for later updates
        pending_orders[order_id]['admin_message_id'] = admin_message.message_id
        print(f"✅ Admin notified successfully about order #{order_id}")
        
    except Exception as e:
        print(f"❌ Failed to notify admin: {e}")
        
        # Provide detailed error information
        error_message = str(e).lower()
        
        if "chat not found" in error_message or "bot was blocked" in error_message:
            print("🚨 CRITICAL: Bot is blocked by admin or chat doesn't exist")
            print("💡 SOLUTION: Start a chat with the bot as admin first!")
        elif "unauthorized" in error_message:
            print("🚨 CRITICAL: Invalid admin ID or bot doesn't have permission")
            print("💡 SOLUTION: Check if admin ID is correct and bot can send messages")
        else:
            print(f"🚨 Unknown error: {e}")
        
        # Don't delete the order - store it for manual processing
        print(f"💾 Order #{order_id} saved in pending_orders for manual processing")

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin actions."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    admin_id = query.from_user.id
    
    print(f"🔘 Admin button clicked: {data} by admin {admin_id}")  # Debug log
    
    # Check if user is admin
    if admin_id != ADMIN_ID:
        await query.message.reply_text("❌ Unauthorized access.")
        return
    
    if data.startswith("admin_input_"):
        order_id = int(data.split("_")[2])
        print(f"📝 Admin requested proxy input for order #{order_id}")
        await request_proxy_details(order_id, query, context)
    elif data.startswith("admin_approve_"):
        order_id = int(data.split("_")[2])
        print(f"✅ Admin approved order #{order_id}")
        await approve_and_send_order(order_id, query, context)
    elif data.startswith("admin_reject_"):
        order_id = int(data.split("_")[2])
        print(f"❌ Admin rejected order #{order_id}")
        await reject_order(order_id, query, context)
    else:
        print(f"❌ Unhandled admin button data: {data}")

async def request_proxy_details(order_id, query, context: ContextTypes.DEFAULT_TYPE):
    """Request proxy details from admin."""
    if order_id not in pending_orders:
        await query.edit_message_text("❌ Order not found or already processed.")
        return
    
    order = pending_orders[order_id]
    
    # Store that we're waiting for proxy details for this order
    context.user_data["waiting_for_proxy_order"] = order_id
    
    # Edit the message to show input instructions
    await query.edit_message_text(
        f"📝 **Enter Proxy Details for Order #{order_id}**\n\n"
        f"👤 Username: {order['user_name']}\n"
        f"🌍 Location: {order['state']}, {order['country']}\n"
        f"⏰ Duration: {order['days']} days\n\n"
        f"**Please send proxy details in this format:**\n"
        f"`IP:PORT:USERNAME:PASSWORD`\n\n"
        f"**Example:**\n"
        f"`192.168.1.1:8080:user123:pass123`\n\n"
        f"After sending the proxy details, return to the order message and click '✅ Approve & Send'.",
        parse_mode='Markdown'
    )

async def approve_and_send_order(order_id, query, context: ContextTypes.DEFAULT_TYPE):
    """Approve order and send proxy details to user."""
    if order_id not in pending_orders:
        await query.edit_message_text("❌ Order not found or already processed.")
        return
    
    order = pending_orders[order_id]
    
    # Check if proxy details are set
    if 'proxy_details' not in order:
        await query.answer("❌ Please set proxy details first by clicking '📝 Enter Proxy Details'", show_alert=True)
        return
    
    proxy_details = order['proxy_details']
    lang = order['user_language']
    
    # Validate proxy format
    parts = proxy_details.split(':')
    if len(parts) != 4:
        await query.answer("❌ Invalid proxy format. Please use IP:PORT:USERNAME:PASSWORD", show_alert=True)
        return
    
    ip, port, proxy_username, password = parts
    
    # Send proxy to user in their language
    try:
        await context.bot.edit_message_text(
            chat_id=order['user_id'],
            message_id=order['message_id'],
            text=TEXTS[lang]["order_approved"].format(
                order_id=order_id,
                state=order['state'],
                country=order['country'],
                days=order['days'],
                price=order['price'],
                ip=ip,
                port=port,
                username=proxy_username,
                password=password,
                full_proxy=proxy_details
            ),
            parse_mode='Markdown'
        )
        
        # Update admin message to show success
        await query.edit_message_text(
            f"✅ **Order Approved & Sent Successfully!**\n\n"
            f"📦 Order ID: #{order_id}\n"
            f"👤 Username: {order['user_name']}\n"
            f"🌐 Language: {lang.upper()}\n"
            f"🌍 Location: {order['state']}, {order['country']}\n"
            f"⏰ Duration: {order['days']} days\n\n"
            f"**Proxy Details Sent:**\n"
            f"`{proxy_details}`\n\n"
            f"User has been notified with the proxy information."
        )
        
        print(f"✅ Proxy delivered for order #{order_id}")
        
    except Exception as e:
        logger.error(f"Failed to send proxy to user: {e}")
        await query.edit_message_text(f"❌ Failed to send proxy: {e}")
    
    # Clean up
    del pending_orders[order_id]

async def reject_order(order_id, query, context: ContextTypes.DEFAULT_TYPE):
    """Reject order and notify user."""
    if order_id not in pending_orders:
        await query.edit_message_text("❌ Order not found or already processed.")
        return
    
    order = pending_orders[order_id]
    lang = order['user_language']
    
    # Notify user in their language
    try:
        await context.bot.edit_message_text(
            chat_id=order['user_id'],
            message_id=order['message_id'],
            text=TEXTS[lang]["order_rejected"].format(order_id=order_id),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to notify user about rejection: {e}")
    
    # Update admin message
    await query.edit_message_text(
        f"❌ **Order Rejected** ❌\n\n"
        f"📦 **Order ID:** #{order_id}\n"
        f"👤 **Username:** {order['user_name']}\n"
        f"🌍 **Location:** {order['state']}, {order['country']}\n\n"
        f"User has been notified that their order was rejected."
    )
    
    # Clean up
    del pending_orders[order_id]

async def handle_proxy_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin proxy details input."""
    if update.message.from_user.id != ADMIN_ID:
        return
    
    # Check if we're waiting for proxy details
    order_id = context.user_data.get("waiting_for_proxy_order")
    if not order_id:
        return
    
    if order_id not in pending_orders:
        await update.message.reply_text("❌ Order not found.")
        context.user_data["waiting_for_proxy_order"] = None
        return
    
    order = pending_orders[order_id]
    proxy_details = update.message.text.strip()
    
    print(f"📝 Admin sent proxy details for order #{order_id}: {proxy_details}")  # Debug log
    
    # Validate proxy format (basic validation)
    parts = proxy_details.split(':')
    if len(parts) != 4:
        await update.message.reply_text(
            "❌ Invalid format. Please use:\n"
            "`IP:PORT:USERNAME:PASSWORD`\n\n"
            "Example:\n"
            "`192.168.1.1:8080:user123:pass123`",
            parse_mode='Markdown'
        )
        return
    
    # Store proxy details in the order
    pending_orders[order_id]['proxy_details'] = proxy_details
    
    # Update the original admin message to show the proxy details
    try:
        keyboard = [
            [InlineKeyboardButton("📝 Enter Proxy Details", callback_data=f"admin_input_{order_id}")],
            [
                InlineKeyboardButton("✅ Approve & Send", callback_data=f"admin_approve_{order_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{order_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_text(
            chat_id=ADMIN_ID,
            message_id=order['admin_message_id'],
            text=f"🆕 **NEW ORDER - ACTION REQUIRED** 🆕\n\n"
                 f"📦 **Order ID:** #{order_id}\n"
                 f"👤 **Username:** {order['user_name']}\n"
                 f"🌐 **Language:** {order['user_language'].upper()}\n"
                 f"🆔 **User ID:** {order['user_id']}\n"
                 f"🌍 **Location:** {order['state']}, {order['country']}\n"
                 f"⏰ **Duration:** {order['days']} days\n"
                 f"💰 **Amount:** ${order['price']}\n"
                 f"🕒 **Time:** {order['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                 f"**Instructions:**\n"
                 f"1. Click '📝 Enter Proxy Details' to set proxy info\n"
                 f"2. Click '✅ Approve & Send' to send proxy to user\n"
                 f"3. Click '❌ Reject' to reject the order\n\n"
                 f"**Current Proxy Details:**\n"
                 f"`{proxy_details}`\n\n"
                 f"✅ **Proxy details saved!** Now click '✅ Approve & Send'.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        await update.message.reply_text(
            f"✅ **Proxy details saved for Order #{order_id}**\n\n"
            f"**Proxy:** `{proxy_details}`\n\n"
            f"Now return to the order message and click '✅ Approve & Send' to deliver the proxy to the user.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Failed to update admin message: {e}")
        await update.message.reply_text(f"❌ Failed to update order: {e}")
    
    # Clear the waiting state
    context.user_data["waiting_for_proxy_order"] = None

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /buy command."""
    user_id = update.message.from_user.id
    lang = get_user_language(user_id)
    
    keyboard = []
    for country in PROXY_LOCATIONS.keys():
        keyboard.append([InlineKeyboardButton(f"🇺🇸 {country}", callback_data=f"country_{country}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        TEXTS[lang]["select_country"],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sell command."""
    user_id = update.message.from_user.id
    lang = get_user_language(user_id)
    
    await update.message.reply_text(
        TEXTS[lang]["sell_message"],
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    user_id = update.message.from_user.id
    lang = get_user_language(user_id)
    
    await update.message.reply_text(
        TEXTS[lang]["help_message"],
        parse_mode='Markdown'
    )

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change language."""
    await show_language_selection(update.message)

async def pending_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending orders (admin only)."""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    if not pending_orders:
        await update.message.reply_text("📭 No pending orders.")
        return
    
    orders_text = "📋 **Pending Orders**\n\n"
    for order_id, order in pending_orders.items():
        orders_text += (
            f"📦 **Order #{order_id}**\n"
            f"👤 Username: {order['user_name']}\n"
            f"🌐 Language: {order['user_language'].upper()}\n"
            f"🌍 {order['state']}, {order['country']}\n"
            f"⏰ {order['days']} days - ${order['price']}\n"
            f"🕒 {order['timestamp'].strftime('%H:%M:%S')}\n"
            f"🔧 Proxy: `{order.get('proxy_details', 'Not set')}`\n\n"
        )
    
    await update.message.reply_text(orders_text, parse_mode='Markdown')

async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Setup command to test admin notifications."""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    # Test notification
    try:
        await update.message.reply_text(
            "🤖 **Bot Setup Test**\n\n"
            "If you received this message, the bot can send you notifications!\n"
            "Now test the order flow by using /buy command in another chat.",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Test failed: {e}")

def main():
    """Start the bot."""
    # Create the Application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers - FIXED: Remove pattern from admin handler registration
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(CommandHandler("sell", sell))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("lang", language_command))
    application.add_handler(CommandHandler("pending", pending_orders_command))
    application.add_handler(CommandHandler("setup", setup_command))
    
    # Add callback handlers - FIXED: Register admin_handler without pattern first
    application.add_handler(CallbackQueryHandler(admin_handler, pattern="^admin_"))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details))
    
    print("🤖 Bot running...")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("🌐 Multi-language support: ACTIVE")
    print("📝 Proxy input system: ACTIVE")
    print("🔧 Debug logging: ENABLED")
    print("🔧 IMPORTANT: Make sure you've started a chat with the bot as admin!")
    print("💡 Use /setup command to test notifications")
    application.run_polling()

if __name__ == '__main__':

    main()
