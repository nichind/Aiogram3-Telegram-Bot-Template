def translate(locale: str = "en", context: str = "") -> str | None:
    """
    Project translator.

    locale: (str, optional) Defaults to "en", language code.
    context: (str, optional) Defaults to "", line to translate.

    Returns translated line or context, if line wasn't found in selected and english locale.
    """
    def get(loc):
        with open(f'./locales/{loc}.txt', 'r', encoding='UTF-8') as f:
            for line in f.readlines():
                if line[:line.index('=')] == context:
                    return line[line.index('=')+1:].replace('\\n', '\n')[:-2 if line[-2:] == '\n' else 0]
            raise FileNotFoundError

    try:
        return get(locale)
    except FileNotFoundError:
        try:
            return get('en')
        except Exception:
            return context
    except Exception:
        return context
