import re
class regexStripper:
    def __init__(self) -> None:
        pass

    def link_stripper(text):
        url_pattern = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        urls = re.findall(url_pattern, text)
        urls = [match[0] for match in urls]
        text_without_urls = re.sub(url_pattern,'',text)
        return text_without_urls, urls
