# Telegram-бот Vnedrim.AI

## Запуск

1. Создайте бота у [@BotFather](https://t.me/BotFather), скопируйте токен.
2. Узнайте свой ID у [@userinfobot](https://t.me/userinfobot).
3. Скопируйте `.env.example` → `.env` и заполните.
4. Установите зависимости и запустите:

```powershell
cd c:\Users\rostg\vnedrimai\bot
pip install -r requirements.txt
python main.py
```

## Ссылка для сайта

После создания бота ссылка для сайта:

```
https://t.me/vnedriai_manager_bot?start=site
```

Параметр `start=site` попадёт в уведомление админу как источник заявки.

## Что делает бот

- `/start` — заявка + уведомление вам в ЛС
- Меню: анкета, FAQ, решения, процесс аудита, канал, ЛС основателя
- Анкета из 5 шагов → повторное уведомление с полной карточкой

## Данные

Заявки сохраняются в `leads.db` (SQLite).
