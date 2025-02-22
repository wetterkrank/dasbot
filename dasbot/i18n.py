import contextvars
import i18n

i18n.load_path.append("dasbot/locales")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("available_locales", ["en", "de", "ru"])
i18n.load_everything()

request_locale = contextvars.ContextVar("request_locale")


def set_locale(locale):
    request_locale.set(locale if locale in i18n.get("available_locales") else "en")
    i18n.set("fallback", "en")

def t(key, **kwargs):
    return i18n.translator.t(key, locale=request_locale.get(), **kwargs)
