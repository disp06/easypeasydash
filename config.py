import os
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get('ваш_секретный_ключ') or 'ваш_секретный_ключ'
    TELEGRAM_BOT_TOKEN = os.environ.get('ваш_токен_бота') or 'ваш_токен_бота'
    TELEGRAM_CHAT_ID = os.environ.get('ваш_id_чата') or 'ваш_id_чата'
    
    # Настройки мониторинга
    CPU_ALERT_THRESHOLD = 90  # %
    RAM_ALERT_THRESHOLD = 90  # %
    
    # Настройки логирования
    LOG_FILE = 'logs/system.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
