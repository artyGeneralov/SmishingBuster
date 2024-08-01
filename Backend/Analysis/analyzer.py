import pickle
import tensorflow as tf
import numpy as np
from langdetect import detect
from langdetect import lang_detect_exception
from googletrans import Translator, LANGUAGES
from Labs.smishing_dataset_lab import paths
from .analyzedEntity import analyzedEntity
from .regexStripper import regexStripper as re
from .heuristic_analyzer import HeuristicAnalyzer as ha
from . import analysisConsts as consts
from Backend.Analysis import LMAnalyzer
from Backend.Analysis import virustotal
tf.get_logger().setLevel('ERROR')



def main():
    # fetch message

    #json_data = json.load(sys.stdin)
    # BAD MESSAGE 1 # 
    # json_data = json.loads('{"message":"Hi! '
    #                         'http://phishing-site.com/give_me_moneysss and also: www.moneygrabbing.com or: bit.ly/84Q5AE0F '
    #                         '  and also ' 
    #                         ' "}')
    # BAD MESSAGE 2 #
    # json_data = json.loads('{"message":"Hello, victim! Click here and Buy!,'
    #                         'http://phishing-site.com/give_me_moneysss and also: www.moneygrabbing.com or: bit.ly/84Q5AE0F '
    #                         ' Give me all your moneysss $ ₪ € 😄😆😅 also https://trem.cellcorn.co.il, ' 
    #                         'https://www.google.com, https://www.walla.co.il/, https://tinyurl.com/eventhubmirsh"}')
    
    #MAYBE BAD MESSAGE #
    # json_data = json.loads('{"message":"Hii, Dolores this is the flower shop we\'ve talked about lets go there'
    #                         ' https://wikipedia.org'
    #                         ' 😄 enjoy!!"}')

    # PROBABLY GOOD MESSSAGE ##
    # json_data = json.loads('{"message":"Hey are we meetting tonight?! I\'ve also texted you,'
    #                         ' the things we needed to do for the party, And I forgot the stupid child at home 🤦'
    #                         ' gonna go get it quick before it flops 😅😅😅 Cya soon !😘😘"}')

    # #bad hebrew message:
    # json_data = json.loads('{"message":"יש לך הפרת תנועה שלא טופלה, נא לבדוק ת הפרטים. לחץ כאן: t.ly/www.e.gov.il"}')
    #message = '{"message":"יש לך הפרת תנועה שלא טופלה, נא לבדוק ת הפרטים. לחץ כאן: t.ly/www.e.gov.il"}'
    #message = "Hii, Dolores this is the flower shop we\'ve talked about lets go there https://wikipedia.org 😄 enjoy!!"
    message = "הביטוח שלך חוייב בסכום גבוה. נא להכנס לאתר ולבדוק את הפרטים. לחץ כאן: t.ly/www.e.gov.il"
    analyze(message)
    pass




def analyze(text):
    #Analyze link here as well omg -.-''
    # what do i want to see from analyzelink(text)?
    # i should get a dictionary
    try:
        vt_scores_str, vt_scores_int = analyze_with_virustotal(text)
        link_analysis_score = max(vt_scores_int)
    except Exception as e:
        vt_scores_str, vt_scores_int = "", [0]
        link_analysis_score = 0
    text = translate_to_english(text)
    statistic_score, features_report = analyze_with_statistical(text)
    nn_prediction, nn_stat = analyze_with_nn(text)
    lm_prediction, lm_stat = analyze_with_lm(text)
    nn_score = nn_prediction[0][0]
    lm_score = lm_prediction[0]
    final_score = calculate_final_score(statistic_score, nn_stat[0][0], lm_stat[0][0], link_analysis_score)
    final_score = round(final_score, 2)
    # create JSON object to return:
    result = {
        "statistic_score": statistic_score,
        "nn_prediction": 'smishing' if nn_score == 1 else 'ham',
        "lm_prediction": 'smishing' if lm_score == 1 else 'ham',
        "final_score": final_score,
        "features_report": str(features_report),
        "virus_total_scores": vt_scores_str
    }
    return result

def analyze_with_virustotal(text):
    _, links = re.link_stripper(text)
    print("Links for virustotal: ", links)
    vt_scores_dict = {}
    vt_scores_int = []
    count = 0
    for link in links:
        virus_total_score = virustotal.analyze_link_virustotal(link)
        vt_scores_dict[f"link{count}"] = virus_total_score
        vt_scores_int.append(virus_total_score)
        count += 1
    vt_scores_str = str(vt_scores_dict)
    return vt_scores_str, vt_scores_int


def analyze_with_statistical(text):
    text, urls = re.link_stripper(text)
    entity = analyzedEntity()
    analyzer = ha()
    analyzer.analyse(entity, text, urls)
    statistic_score = round(entity.getScore(), 2)
    report = entity.getLog()
    return statistic_score, report

def analyze_with_lm(text):
    text,_ = re.link_stripper(text)
    lm_analyzer = LMAnalyzer.LMAnalyzer(paths.roberta_save_dir, paths.mlp_full_path)
    result, prediction_stat = lm_analyzer.predict_message(text)
    return result, prediction_stat

def analyze_with_nn(text):
    entity = analyzedEntity()
    analyzer = ha()
    text, urls = re.link_stripper(text)
    analyzer.analyse(entity, text, urls)
    modelPath = paths.nn_save_file
    model = tf.keras.models.load_model(modelPath)
    features = prepare_features(entity.analysisDict)
    features_array = np.array([features])
    model_prediction = model.predict(features_array, verbose=0)
    predicted_class = np.round(model_prediction).astype(int)
    return predicted_class, model_prediction

def prepare_features(analysis_dict):
    feature_names = consts.all_features
    features = [analysis_dict.get(name, 0) for name in feature_names]
    picklePath = paths.standardization_params_save_file
    with open(picklePath, 'rb') as f:
        standardization_params = pickle.load(f)
    feature_index_map = {name: idx for idx, name in enumerate(feature_names)}
    quantitative_features = consts.quantitative_features
    for feature in quantitative_features:
        idx = feature_index_map[feature]
        mean = standardization_params[feature]['mean']
        std = standardization_params[feature]['std']
        features[idx] = (features[idx] - mean) / std if std != 0 else 0
    return features

def translate_to_english(text):
    try:
        if not isinstance(text, str) or not text.strip():
            return text
        detected_lang = detect(text)
        if detected_lang != 'en':
            translator = Translator()
            translation = translator.translate(text, src=detected_lang, dest='en')
            return translation.text
        else:
            return text
    except lang_detect_exception.LangDetectException as e:
        return text

# function to calculate the final score by the weights of the different models
# the weights are calculated by the F1 score of each model
# the final score is a weighted average of the scores of the models
# the final score is normalized to be between 0 and 100
def calculate_final_score(prediction_statistic, prediction_heuristic_nn, prediction_lm, link_score):
    link_flagged = 1 if link_score > 2 else 0
    f1_statistic = 0.82
    f1_heuristic_nn = 0.80
    f1_lm = 0.91
    sum_f1 = f1_statistic + f1_heuristic_nn + f1_lm 
    weight_statistic = f1_statistic / sum_f1
    weight_heuristic_nn = f1_heuristic_nn / sum_f1
    weight_lm = f1_lm / sum_f1
    prediction_statistic_norm = prediction_statistic / 100
    final_score_norm = (weight_statistic * prediction_statistic_norm + 
                        weight_heuristic_nn * prediction_heuristic_nn + 
                        weight_lm * prediction_lm)
    link_adjustment = 0.4 if link_flagged else -0.2 
    final_score_norm = final_score_norm + link_adjustment
    final_score_norm = max(0, min(1, final_score_norm))
    final_score = final_score_norm * 100
    return final_score

if __name__ == "__main__":
    main()
