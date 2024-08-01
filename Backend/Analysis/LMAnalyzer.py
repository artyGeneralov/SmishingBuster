import numpy as np
import tensorflow as tf
import transformers
import logging
from Labs.smishing_dataset_lab import paths
from transformers import RobertaTokenizer, TFRobertaForSequenceClassification
import json
from Labs.smishing_dataset_lab.CustomModel import CustomModel
transformers.logging.set_verbosity(logging.ERROR)
class LMAnalyzer:
    _instance = None

    def __new__(cls, roberta_model_dir=None, mlp_model_path=None):
        if cls._instance is None:
            cls._instance = super(LMAnalyzer, cls).__new__(cls)
            cls._instance._initialize(roberta_model_dir, mlp_model_path)
        return cls._instance

    def _initialize(self, roberta_model_dir = paths.roberta_save_dir, mlp_model_path = paths.mlp_full_path):
        if not hasattr(self, 'tokenizer'):
            self.tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
            self.roberta_model = TFRobertaForSequenceClassification.from_pretrained(roberta_model_dir, output_hidden_states=True)

            self.mlp_model = tf.keras.models.load_model(mlp_model_path)

    def preprocess_message(self, message):
        inputs = self.tokenizer(message, return_tensors='tf', padding=True, truncation=True, max_length=128)
        
        # features vector as the last hidden layer
        outputs = self.roberta_model(inputs['input_ids'], attention_mask=inputs['attention_mask'], training=False)
        hidden_states = outputs.hidden_states
        features = hidden_states[-1][:, 0, :].numpy()
        
        return features

    def predict_message(self, message):
        features = self.preprocess_message(message)
        prediction = self.mlp_model.predict(features, verbose=0)
        predicted_label = (prediction > 0.5).astype(int).flatten()
        return predicted_label, prediction
