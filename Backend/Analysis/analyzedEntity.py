import pickle
from . import analysisConsts as consts
import math

class analyzedEntity:
    
    # Protocol to add a new feature:
    # 1. Add the feature to the consts.py file
    # 2. Add the feature to the binary_features or quantitative_features lists
    # 3. Add the feature to the weights dictionary
    # 4. Add the feature to the heuristic analyzer as a function
    default_weights_file = "Labs/smishing_dataset_lab/files_final/weights.pkl"

    finalScore = None


    analysisDict = {}
    weights = {}

    def __init__(self, weights_file = default_weights_file):
        self.analysisDict = {}
        if weights_file is not None:
            self.weights = self.load_weights(weights_file)

    def load_weights(self, weights_file):
        try:
            with open(weights_file, 'rb') as f:
                weights = pickle.load(f)
            if self.weights == {}: 
                self.weights = weights
            return weights
        except Exception as e:
            print(f"Failed to load weights from {weights_file}: {e}")

    def printLog(self):
        for key in self.analysisDict:
            print("{",key,"}: ", self.analysisDict[key])

    def getScore(self):
        if(self.finalScore is None):
            self.finalScore = self.__calculateScore()
        return self.finalScore

    #private
    def __calculateScore(self):
        
        if not self.analysisDict:
            return 0
        score = 0
        for feature in consts.binary_features:
            score += self.analysisDict.get(feature, 0) * self.weights[feature]
        for feature in consts.quantitative_features:
            if feature in self.analysisDict:
                score += self.normalize_count(self.analysisDict[feature]) * self.weights[feature]
        scaled_score = self.sigmoid((score / 10))
        return scaled_score

    def sigmoid(self, x):
        return 100 / (1 + math.exp(-x))

    def normalize_count(self, count):
        return math.log1p(count)

    def addItem(self, key, value):
        self.analysisDict[key] = value

    def get_property(self, key):
        if key in consts.binary_features and key in self.analysisDict:
            return self.analysisDict[key]
        elif key in consts.quantitative_features and key in self.analysisDict:
            return self.normalize_count(self.analysisDict[key])

    def getDict(self):
        return self.analysisDict
    
    def getLog(self):
        return self.analysisDict

