
from . import analysisConsts as consts
from datetime import datetime
from .excelHelper import ExcelHelper
import re
import os

class HeuristicAnalyzer:

    base_dir = os.path.dirname(os.path.abspath(__file__))
    CALLS_TO_ACTION_PATH = os.path.join(base_dir, "datasets", consts.CALLS_TO_ACTION_DATASET_FILE)
    CURRENCIES_PATH = os.path.join(base_dir, "datasets", consts.CURRENCIES_DATASET_FILE)
    MESSAGE_URGENCY_PATH = os.path.join(base_dir, "datasets", consts.URGENCY_KEYWORDS_DATASET_FILE)
    SUS_KEYWORDS_PATH = os.path.join(base_dir, "datasets", consts.SUSPICIOUS_KEYWORDS_DATASET_FILE)

    def __init__(self):
        pass

    def analyse(self, entity, text, urls):
        
        tasks = [
        (self.check_link, (entity, urls)),
        (self.message_call_to_action, (entity, text)),
        (self.message_refers_money, (entity, text)),
        (self.message_urgency, (entity, text)),
        (self.message_sus_keywords, (entity, text)),
        (self.message_length, (entity, text))
        ]
        for func, args in tasks:
            func(*args)

    # heuristic 1: message Contains a link or several
    def check_link(self, entity, urls):
        if len(urls) > 0:
            entity.addItem(consts.CONTAINS_LINK, 1)

    def parse_date(self, date):
        if isinstance(date, list):
            date = date[0]
        if isinstance(date, str):
            return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return date


    # NOT USED
    # heuristic 2: message contains emojis: number, variety
    def check_emoji(self, entity, emojis):
        if len(emojis) > 0:
            entity.addItem(consts.CONTAINS_EMOJIS, 1)
            entity.addItem(consts.AMOUNT_OF_EMOJIS, len(emojis))

    
    # heuristic 3: message contains call to action
    def message_call_to_action(self, entity, text):
        text = self.fix_spaces(text)
        callsToAction = 0
        filename = self.CALLS_TO_ACTION_PATH
        excel = ExcelHelper(filename)
        text_lower = text.lower()
        for entry in excel.getColumnAsList('TEXT'):
            pattern = r'(?<!\w)(?:\s*[.,":;!?(){}\[\]\s*]*|^)' + re.escape(entry) + r'(?:[.,":;!?(){}\[\]\s*]*|\b)'
            matches = re.findall(pattern, text_lower, flags = re.IGNORECASE)
            callsToAction += len(matches)

        if(callsToAction > 0):
            entity.addItem(consts.CONTAINS_CALL_TO_ACTION, 1)
            entity.addItem(consts.AMOUNT_CALL_TO_ACTION, callsToAction)

    # heuristic 4: message contains a reference to money
    def message_refers_money(self, entity, text):
        moneyReferences = 0
        text_lower = text.lower()
        filename = self.CURRENCIES_PATH
        excel = ExcelHelper(filename)
        currencies = excel.getColumnAsList('Currency')
        symbols = excel.getColumnAsList('Symbol')
        iso_codes = excel.getColumnAsList('ISO Code')
        all = set(currencies+symbols+iso_codes)
        
        for ref in all:
            if isinstance(ref, float):
                continue
            if ref in symbols:
                pattern = re.escape(ref)
            else:
                pattern = r'(?<!\w)(?:\s*[.,":;!?(){}\[\]\s*]*|^)' + ref + r'(?:[.,":;!?(){}\[\]\s*]*|\b)'
            
            matches = re.findall(pattern, text_lower, flags = re.IGNORECASE)
            moneyReferences += len(matches)
        
        if moneyReferences > 0:
            entity.addItem(consts.CONTAINS_REFERENCE_TO_MONEY, 1)
            entity.addItem(consts.AMOUNT_REFERENCE_TO_MONEY, moneyReferences)

    # NOT USED
    # heuristic 5:
    def contains_phone_number(self, entity, text):
        pattern = r'\+?\d[\d\s\-\(\)]{3,17}\d'
        if re.search(pattern, text):
            entity.addItem(consts.CONTAINS_PHONE_NUMBER, 1)

    # NOT USED
    #heuristic 6:  
    def message_length(self, entity, text):
        entity.addItem(consts.MESSAGE_LENGTH, len(text))

    #heuristic 7: words that induce urgency
    def message_urgency(self, entity, text):
        text = self.fix_spaces(text)
        urgency = 0
        filename = self.MESSAGE_URGENCY_PATH
        excel = ExcelHelper(filename)
        text_lower = text.lower()
        for entry in excel.getColumnAsListByNumber(0):
            pattern = r'(?<!\w)(?:\s*[.,":;!?(){}\[\]\s*]*|^)' + re.escape(entry) + r'(?:[.,":;!?(){}\[\]\s*]*|\b)'
            matches = re.findall(pattern, text_lower, flags = re.IGNORECASE)
            urgency += len(matches)
        if(urgency > 0):
            entity.addItem(consts.CONTAINS_URGENCY, 1)

    #heuristic 8: suspicious keywords from paper
    def message_sus_keywords(self, entity, text):
        text = self.fix_spaces(text)
        susKeywords = 0
        filename = self.SUS_KEYWORDS_PATH
        excel = ExcelHelper(filename)
        text_lower = text.lower()
        for entry in excel.getColumnAsListByNumber(0):
            pattern = r'(?<!\w)(?:\s*[.,":;!?(){}\[\]\s*]*|^)' + re.escape(entry) + r'(?:[.,":;!?(){}\[\]\s*]*|\b)'
            matches = re.findall(pattern, text_lower, flags = re.IGNORECASE)
            susKeywords += len(matches)
        if(susKeywords > 0):
            entity.addItem(consts.SUSPICIOUS_KEYWORDS, 1)
            entity.addItem(consts.AMOUNT_OF_SUSPICIOUS_KEYWORDS, susKeywords)


    #helper function to fix spaces in text
    def fix_spaces(self, text):
        result = ""
        for i in range(len(text) - 1):
            result += text[i]
            if text[i] in ".:,()!":
                result += " "
        return result