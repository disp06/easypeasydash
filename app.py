from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from system_monitor import SystemMonitor
from telegram_bot import telegram_bot
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

if not os.path.exists('logs'):
    os.makedirs('logs')

handler = RotatingFileHandler(Config.LOG_FILE, maxBytes=Config.LOG_MAX_SIZE, backupCount=Config.LOG_BACKUP_COUNT)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

system_monitor = SystemMonitor()
system_logs = []

def add_system_log(stats):
    global system_logs
    system_logs.append(stats)
    if len(system_logs) > 1000:
        system_logs = system_logs[-500:]

@app.route('/')
def index():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if telegram_bot.verify_password(password):
            session['authenticated'] = True
            session['login_time'] = datetime.now().isoformat()
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный пароль!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/api/system_stats')
def api_system_stats():
    if 'authenticated' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        stats = system_monitor.get_system_stats()
        add_system_log(stats)
        thresholds = {
            'cpu': Config.CPU_ALERT_THRESHOLD,
            'ram': Config.RAM_ALERT_THRESHOLD,
        }
        alerts = system_monitor.check_alerts(stats, thresholds)
        if alerts:
            for alert in alerts:
                alert_type = 'cpu' if 'CPU' in alert else 'ram'
                telegram_bot.send_alert(alert, alert_type)
                app.logger.warning(f"ALERT: {alert}")
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"Ошибка системных данных: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/speed_test')
def api_speed_test():
    if 'authenticated' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        speed = system_monitor.test_internet_speed()
        if speed:
            return jsonify(speed)
        return jsonify({'error': 'Не удалось выполнить тест скорости'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system_logs')
def api_system_logs():
    if 'authenticated' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(system_logs[-100:])

if __name__ == '__main__':
    if not telegram_bot.current_password:
        telegram_bot.send_new_password()
    app.run(host='0.0.0.0', port=3030, debug=False)
