![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/wetterkrank/dasbot)

# dddasbot
A Telegram bot that helps you learn German der/die/das articles

https://t.me/derdiedas_quizbot

## How to run
- Clone the repo
- Set the env variable `DYNACONF_TOKEN="your_Telegram_bot_token"` in the .env file
- Run `docker-compose up`

## Notes

**Todo**
- Daily quiz ✔
- Spaced repetition ✔
- Webhooks instead of long polling
- i18n

**Spaced repetition**

I've adapted a simple algorithm borrowed from [drill-srs](https://github.com/rr-/drill).

Card score | Wait time
---------- | ---------
0          | (new question)
1          | 1 hour
2          | 1 day
3          | 1 week
4          | 1 month
5          | 3 months
6          | 6 months

A correct answer increases the card's score by 1, while a mistake decreases its score by 1.

**Сorner cases**
- Some nouns can have different gender depending on the meaning: *der See* (lake) - *die See* (sea), *der Leiter* (leader) - *die Leiter* (ladder)
- For some nouns, more than one gender is correct, with the same meaning (*der/das Teil*)
- Sometimes gender depends on the context (die/der *Jugendliche*, *Beschäftigte*, *Erwachsene*, *Geliebte*)
- ... what else?