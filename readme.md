![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/wetterkrank/dasbot)

# dddasbot
A Telegram bot that helps you learn German der/die/das articles

https://t.me/derdiedas_quizbot

## How to run
- Clone the repo
- Note the DB connection string and DB name in `settings.toml`
- Set the env variable `DYNACONF_TOKEN="your_Telegram_bot_token"`
- If you don't use .env file, create it anyway and leave it empty
- Run `docker-compose up`

## Notes

**Todo**
- ~~Daily quiz~~ ✔
- Spaced repetition
- Webhooks instead of long polling
- i18n

**Сorner cases**
- Some nouns can have different gender depending on the meaning: der See (lake) - die See (sea), der Leiter (leader) - die Leiter (ladder)
- For some nouns, more than one gender is correct, with the same meaning (der/das Teil)
- Sometimes gender depends on the context (die/der Jugendliche, Beschäftigte, Erwachsene, Geliebte)
- ... what else?