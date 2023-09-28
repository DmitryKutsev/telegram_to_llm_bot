from langdetect import detect

def detect_lang(text):
    """
    Detects the language of the given text using the langdetect library.
    
    Args:
        text (str): The text to detect the language of.
    
    Returns:
        str: The detected language code (e.g. 'en' for English, 'ru' for Russian).
              If the language cannot be detected, returns 'unknown'.
    """
    try:
        lang = detect(text)
    except Exception as e:
        lang = 'unknown'
    return lang
