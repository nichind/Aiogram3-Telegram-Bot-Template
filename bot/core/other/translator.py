from os import getcwd


def translate(locale: str = "en", context: str = "") -> str:
    """
    Project translator.

    locale: (str, optional) Defaults to "en", language code.
    context: (str, optional) Defaults to "", line to translate.

    Returns translated line or context, if line wasn't found in selected and english locale.
    """
    def get(loc):
        with open(f'{getcwd()}/locales/{loc}.txt', 'r', encoding='UTF-8') as f:
            for line in locale.readlines():
                if '=' in line and line.split('=')[0].strip().upper() == context.upper():
                    return line[line.index('=') + 1:].replace('\\n', '\n').replace('\\t', '\t')
            raise FileNotFoundError

    try:
        if locale is None:
            locale = 'en'
        return get(locale)
    except FileNotFoundError:
        try:
            return get('en')
        except Exception:
            return context
    except Exception:
        return context
