# dasbot
A Telegram bot that helps you learn German der/die/das articles

https://dasbot.yak.supplies


## How to run
- Clone the repo
- Edit settings/set the env variables (see `settings.toml` and `.env.example`)

- Create and activate a virtual environment: `python3 -m venv .venv && source ./.venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Run `make run`

As an alternative,
- Run `docker-compose up` after the first two steps

## Notes

**Todo**
- Daily quiz ✔
- Spaced repetition ✔
- Statistics ✔
- Hint: translation and/or context ✔
- Webhooks instead of long polling ✔
- Add Docker build/push actions to CI ✔
- Randomize quiz time on 1st start ✔
- Move DB to MongoDB Atlas ✔
- i18n
- Revise the words database
- Let users add their words
- "Forget me" command
- Custom quiz intervals ("N times/day every 3 hours")
- Postpone broadcast when restarting after outage (use a one-off script?)

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
