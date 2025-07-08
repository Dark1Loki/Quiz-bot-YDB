# 🤖 QuizlyGame\_Bot — Telegram-бот на Yandex Cloud

**QuizlyGame\_Bot** — это Telegram-бот, который позволяет пользователям проходить викторины. Проект построен на базе `Aiogram`, использует серверлесс-функции **Yandex Cloud Functions** и хранит данные в **Yandex Database (YDB)**.

---

## 🚀 Возможности

- ✅ Прохождение квизов с вариантами ответов
- 🔄 Хранение прогресса и количества правильных ответов
- 📊 Подсчёт баллов (score)
- 🧠 Загрузка вопросов из YDB
- 🧲 Проверка ответов
- 📦 Работает как serverless-приложение через Yandex Cloud Functions

---

## ⚙️ Установка локально (для разработки)

1. Клонируй репозиторий:

   ```bash
   git clone https://github.com/Dark1Loki/Quiz-bot-YDB.git
   cd Quiz-bot-YDB
   ```

2. Создай виртуальное окружение:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Установи зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Создай `.env` и заполни переменные:

   ```env
   API_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   YDB_DATABASE=/ru-central1/.../your-db-id
   YDB_ENDPOINT=grpcs://your-endpoint.ydb.yandexcloud.net:2135
   ```

---

## ☁️ Деплой в Yandex Cloud

1. Создай ZIP-архив с кодом и `requirements.txt`
2. Зайди в Yandex Cloud Functions, создай функцию:
   - Режим: ZIP-архив
   - Язык: Python 3.10
   - Точка входа: `main.handler`
3. Укажи переменные окружения
4. Свяжи с API Gateway

---

## 📃 Структура таблиц YDB

```sql
CREATE TABLE quiz_state (
  user_id Uint64,
  q_idx Uint64,
  ok_count Uint64,
  score Uint64,
  PRIMARY KEY(user_id)
);

CREATE TABLE quiz_data (
  id Uint64,
  question Utf8,
  options List<Utf8>,
  answer Utf8,
  PRIMARY KEY(id)
);
```

---

## 📤 Как добавить вопрос

Через YDB Console:

```sql
UPSERT INTO quiz_data (id, question, options, answer)
VALUES (1, "Какой прибор нужен для приготовления тостов?", ["Toстер", "Холодильник", "Пылесос", "Печь"], "Тостер");
```

---

## 📁 .env.sample

```env
API_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
YDB_DATABASE=/ru-central1/b1g1vxyzabc12345/etn123xyzabcd123
YDB_ENDPOINT=grpcs://ydb.serverless.yandexcloud.net:2135
```

---

## 📄 Лицензия

Проект распространяется по лицензии **MIT**. См. `LICENSE`.

---

## 🤝 Автор

- 👤 Telegram: [@Dark1Loki](https://t.me/Dark1Loki)
- 💼 GitHub: [Dark1Loki](https://github.com/Dark1Loki)

---

## 🧠 TODO / идеи для развития

- 🌟 Многопользовательский режим (PvP)
- ⏱️ Таймер / обратный отсчёт
- 📄 Админка для добавления вопросов
- ⌛ Счётчик времени прохождения

