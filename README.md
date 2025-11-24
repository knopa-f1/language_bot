
# Language Bot

**A Telegram bot for learning new words**
This bot was created to help users build their Lithuanian vocabulary from Russian or English.

### Features:
- Fun and interactive way to learn Lithuanian words.
- Supports **Russian** and **English** as base languages.
- Provides progress tracking and customizable reminders for consistent learning.

### Technologies Used:
- **Python**: Core programming language.
- **Aiogram**: For seamless interaction with Telegram.
- **Fluentogram**: For internationalization and multi-language support.
- **SQLAlchemy ORM** and **Alembic**: For database integration and migration management.

### Status:
This bot is live and actively used in production, with **700+ active users**.
Try it yourself: [@SpeakLithuanianBot](https://t.me/SpeakLithuanianBot).

---

## Setup Instructions

1. **Obtain a Telegram Bot Token:**
   Request your token from [@BotFather](https://t.me/BotFather).

2. **Set Up the Database:**
   Use a database like PostgreSQL for optimal performance.

3. **Configure Environment Variables:**
   Edit the `.env` file to include your bot token and database connection details.

4. **Install Dependencies:**
   Run `pip install -r requirements.txt` to install all required libraries.

5. **Start the Bot:**
   Launch the bot by running `main.py` as a service.

---

## User Guide

### What the Bot Does
The bot helps you learn Lithuanian words easily and enjoyably.

### How to Use It
1. Hit the **"Let’s go"** button to get started.
2. The bot will present you with a word in Lithuanian or your chosen language (English/Russian) along with multiple-choice translations.
3. Select the correct translation to proceed.

### Additional Features
- **Reminders:**
   Set custom schedules for learning sessions in the **Settings** section.
- **Progress Tracking:**
   View your learning statistics via the **Statistics** button.

Start expanding your Lithuanian vocabulary today with [@SpeakLithuanianBot](https://t.me/SpeakLithuanianBot)!
