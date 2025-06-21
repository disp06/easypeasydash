import telebot
import random
import json
import os
import time
import threading
import logging
from datetime import datetime
import schedule
from config import Config

class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(Config.TELEGRAM_BOT_TOKEN)
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.current_password = None
        self.password_used = False
        self.password_file = 'current_password.json'
        self.last_alert_time = {}
        self.alert_cooldown = 600  # 10 минут

        self.load_password()
        schedule.every().day.at("00:00").do(self.send_new_password)
        threading.Thread(target=self.run_scheduler, daemon=True).start()

    def generate_password(self):
        return f"{random.randint(100, 999)}-{random.randint(100, 999)}"

    def save_password(self):
        data = {'password': self.current_password, 'used': self.password_used, 'generated_at': datetime.now().isoformat()}
        with open(self.password_file, 'w') as f:
            json.dump(data, f)

    def load_password(self):
        if os.path.exists(self.password_file):
            try:
                with open(self.password_file, 'r') as f:
                    data = json.load(f)
                    self.current_password = data.get('password')
                    self.password_used = data.get('used', False)
            except:
                self.generate_new_password()
        else:
            self.generate_new_password()

    def generate_new_password(self):
        self.current_password = self.generate_password()
        self.password_used = False
        self.save_password()

    def send_new_password(self):
        self.generate_new_password()
        message = f"🔐 Новый пароль для доступа:\n`{self.current_password}`\nПароль действителен до следующего дня 00:00."
        try:
            self.bot.send_message(self.chat_id, message, parse_mode='Markdown')
            logging.info(f"Новый пароль отправлен: {self.current_password}")
        except Exception as e:
            logging.error(f"Ошибка отправки пароля: {e}")

    def send_alert(self, alert_message, alert_type='general'):
        now = time.time()
        if alert_type in self.last_alert_time and (now - self.last_alert_time[alert_type]) < self.alert_cooldown:
            logging.info(f"Алерт {alert_type} пропущен, интервал не истёк")
            return
        try:
            self.bot.send_message(self.chat_id, f"⚠️ АЛЕРТ\n{alert_message}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.last_alert_time[alert_type] = now
            logging.info(f"Алерт отправлен: {alert_type}")
        except Exception as e:
            logging.error(f"Ошибка отправки алерта: {e}")

    def verify_password(self, input_password):
        if not self.current_password:
            return False
        clean_pass = self.current_password.replace('-', '')
        if input_password == clean_pass and not self.password_used:
            self.password_used = True
            self.save_password()
            self.generate_new_password()
            self.send_new_password()
            return True
        return False

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

telegram_bot = TelegramBot()
