CONTAINS_LINK = "Contains link"
AMOUNT_OF_LINKS = "Amount of links"

CONTAINS_EMOJIS = "Contains emojis"
AMOUNT_OF_EMOJIS = "Amount of emojis"

CONTAINS_CALL_TO_ACTION = "Contains call to action"
AMOUNT_CALL_TO_ACTION = "Amount of calls to action"

CONTAINS_REFERENCE_TO_MONEY = "Contains reference to money"
AMOUNT_REFERENCE_TO_MONEY = "Amount of reference to money"

CONTAINS_PHONE_NUMBER = "Contains phone number"

MESSAGE_LENGTH = "Message length"

CONTAINS_URGENCY = "Contains urgency"
SUSPICIOUS_KEYWORDS = "Suspicious keywords"
AMOUNT_OF_SUSPICIOUS_KEYWORDS = "Amount of suspicious keywords"


binary_features = [
    CONTAINS_LINK, CONTAINS_CALL_TO_ACTION, 
    CONTAINS_REFERENCE_TO_MONEY, CONTAINS_URGENCY, SUSPICIOUS_KEYWORDS
    ]

quantitative_features = [
    AMOUNT_CALL_TO_ACTION, 
    AMOUNT_REFERENCE_TO_MONEY,
    AMOUNT_OF_SUSPICIOUS_KEYWORDS,
    MESSAGE_LENGTH
    ]

all_features = binary_features + quantitative_features



#FILE_NAMES:
CALLS_TO_ACTION_DATASET_FILE = "Calls_to_Action.xlsx"
CORRENCIES_DATASET_FILE = "Currencies.xlsx"
URGENCY_KEYWORDS_DATASET_FILE = "Urgency.xlsx"
SUSPICIOUS_KEYWORDS_DATASET_FILE = "SuspiciousKeywords.xlsx"

