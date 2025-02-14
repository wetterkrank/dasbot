import i18n

i18n.load_path.append('dasbot/locales')
i18n.set('filename_format', '{locale}.{format}')
i18n.set('on_missing_translation', 'error')
i18n.load_everything()

t = i18n.t
