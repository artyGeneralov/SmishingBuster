import pickle
import time
import pandas as pd
import sys
import os
import math
import numpy as np
from Labs.smishing_dataset_lab import paths
from Backend.Analysis.heuristic_analyzer import HeuristicAnalyzer as ha
from Backend.Analysis.analyzedEntity import analyzedEntity
from Backend.Analysis.regexStripper import regexStripper as res
from Backend.Analysis.LMAnalyzer import LMAnalyzer
from Labs.smishing_dataset_lab.CustomModel import CustomModel
from Labs.smishing_dataset_lab.smishingDB import SmishingDB
from Backend.Analysis import analysisConsts as consts
import tensorflow as tf
from transformers import RobertaTokenizer, TFRobertaForSequenceClassification
import logging

logger = tf.get_logger()
logger.setLevel(logging.ERROR)

project_root = os.path.abspath('../..')
print("Project Root:", project_root)
sys.path.append(project_root)

def main():
    menu_options = [
        ("Run feature extraction from training set", feature_extraction, [paths.training_dataset, paths.heuristic_features_save_file]),
        ("Run feature extraction from test set", test_dataset_feature_extraction, [paths.test_dataset, paths.test_features_save_file]),
        ("Run feature standardization for NN for test set", test_dataset_feature_standartization, [paths.test_features_save_file, paths.test_features_standardized_save_file, paths.test_features_standardization_params_save_file]),
        ("Run feature standardization for NN", feature_standartization, [paths.heuristic_features_save_file, paths.heuristic_features_standardized_save_file, paths.standardization_params_save_file]),
        ("Calculate and Save the weights for the statistical analysis", calculate_and_save_weights, [paths.heuristic_features_save_file, paths.weights_save_file]),
        ("Train heuristic nn model", train_and_save_heuristic_nn_model, [paths.heuristic_features_standardized_save_file, paths.nn_save_file]),
        ("Fine-tune RoBERTa Model", fine_tune_roberta_model, [paths.training_dataset, paths.roberta_save_dir]),
        ("Extract deep semantic features", extract_deep_semantic_features, [paths.roberta_save_dir, paths.training_dataset, paths.deep_features_save_path]),
        ("Train deep lm model", train_and_save_deep_lm_model, [paths.deep_features_save_path, paths.mlp_path, paths.mlp_name]),
        ("Evaluate heuristic statistic weights model", evaluate_heuristic_statistic_weights_model, [paths.test_dataset]),
        ("Evaluate heuristic nn model", evaluate_heuristic_nn_model, [paths.test_features_standardized_save_file, paths.nn_save_file]),
        ("Evaluate deep lm model", evaluate_deep_lm_model, [paths.roberta_save_dir, paths.mlp_full_path, paths.test_dataset]),
        ("Exit", sys.exit, [])
    ]
    
    while True:
        display_menu(menu_options)
        choice = input("Enter your choice: ")
        
        try:
            choice = int(choice) - 1
            if 0 <= choice < len(menu_options):
                description, function, args = menu_options[choice]
                function(*args)
            else:
                print("Invalid choice. Please try again.")
        except ValueError as e:
            print("Stack trace:", e)
            print("Invalid input. Please enter a number.")


def display_menu(menu_options):
    for i, (description, _, _) in enumerate(menu_options, start=1):
        print(f"{i}. {description}")

# menu functions

def feature_extraction(training_dataset, features_save_file):
    print("Running feature extraction...")
    analyze_messages(training_dataset, output_csv=features_save_file)
    print("Feature extraction completed.")

def feature_standartization(heuristic_features_save_file, stnadardized_features_save_file, standardization_params__save_file):
    print("Running feature standartization...")
    standardizeFeatures(heuristic_features_save_file, stnadardized_features_save_file, standardization_params__save_file)
    print("Feature standartization completed.")

def test_dataset_feature_extraction(test_dataset, test_features_save_file):
    print("Running feature extraction on test dataset...")
    analyze_messages(test_dataset, output_csv=test_features_save_file)
    print("Feature extraction completed.")

def test_dataset_feature_standartization(test_features_file, standardized_features_save_file, standardization_params_save_file):
    print("Running feature standartization on test dataset...")
    standardizeFeatures(test_features_file, standardized_features_save_file, standardization_params_save_file)
    print("Feature standartization completed.")

def calculate_and_save_weights(heuristic_features_save_file, weights_save_file):
    statistic_weights_calculator(heuristic_features_save_file, weights_save_file)
    print("Calculating and saving weights...")

def train_and_save_heuristic_nn_model(standardized_features_file, nn_save_file):
    print("Training heuristic NN model...")
    heuristic_nn_train_and_save(standardized_features_file, nn_save_file)
    print("Training completed.")

def fine_tune_roberta_model(train_dataset_file, roberta_save_dir):
    print("Fine-tuning RoBERTa model...")
    train_roberta_model(train_dataset_file, roberta_save_dir)
    print("Fine-tuning completed.")

def extract_deep_semantic_features(pretrained_roberta, training_data_file, deep_features_save_file):
    print("Extracting deep semantic features...")
    extract_features_from_finetuned_model(training_data_file, pretrained_roberta, output_file=deep_features_save_file)
    print("Extraction completed.")

def train_and_save_deep_lm_model(deep_features_csv, model_path, model_name):
    print("Training deep LM model...")
    lm_model_train_and_save(deep_features_csv, model_path, model_name)
    print("Training completed.")

def evaluate_heuristic_statistic_weights_model(test_dataset):
    print("Evaluating heuristic statistic weights model...")
    evaluation_results = evaluate_analyzer(test_dataset)
    print("Evaluation completed, results:")
    print(evaluation_results)

def evaluate_heuristic_nn_model(test_features_standardized, nn_save_file):
    print("Evaluating heuristic NN model...")
    evaluation_results = evaluate_heuristic_nn(nn_save_file, test_features_standardized)
    print(evaluation_results)
    print("Evaluation completed.")

def evaluate_deep_lm_model(roberta_path, mlp_path, test_dataset):
    print("Evaluating deep LM model...")
    evaluation_results = evaluate_lm_model(roberta_path, mlp_path, test_dataset)
    print(evaluation_results)
    print("Evaluation completed.")


# actual implementation


def statistic_weights_calculator(training_dataset, weights_save_file):
    data = pd.read_csv(training_dataset)
    good_features = data[data['LABEL'] == 0]
    bad_features = data[data['LABEL'] == 1]
    bad_binary_percentages, bad_quantitative_averages = calculate_feature_statistics(
        bad_features, consts.binary_features, consts.quantitative_features
    )
    good_binary_percentages, good_quantitative_averages = calculate_feature_statistics(
        good_features, consts.binary_features, consts.quantitative_features
    )
    final_weights = {}
    SMOOTHING_FACTOR = 0.01
    MAX_WEIGHT = 5
    for feature in consts.binary_features + consts.quantitative_features:
        if feature in consts.binary_features:
            probHighScoring = max(bad_binary_percentages.get(feature, 0), SMOOTHING_FACTOR)
            probLowScoring = max(good_binary_percentages.get(feature, 0), SMOOTHING_FACTOR)

        else:
            probHighScoring = max(bad_quantitative_averages.get(feature, 0), SMOOTHING_FACTOR)
            probLowScoring = max(good_quantitative_averages.get(feature, 0), SMOOTHING_FACTOR)
        oddsRatio = (probHighScoring / probLowScoring) if probLowScoring > 0 else 0
        #print(f"feature: {feature}, odds ratio: {oddsRatio}, oddsHigh: {probHighScoring}, oddsLow: {probLowScoring}")
        if oddsRatio > 0:
            weight_ln = math.log(oddsRatio)
        else:
            weight_ln = 0
        final_weights[feature] = weight_ln
    percentile_based_max = np.percentile(list(final_weights.values()), 95)
    scaling_factor = 100 / percentile_based_max if percentile_based_max > 0 else 0
    scaling_factor = min(scaling_factor, MAX_WEIGHT)
    print(f"percentile_based_max: {percentile_based_max}")
    print(f"Scaling factor: {scaling_factor}")
    for feature in final_weights:
        scaled_weight = final_weights[feature] * scaling_factor
        final_weights[feature] = min(scaled_weight, MAX_WEIGHT)
    print("Final weights for features after percentile scaling and capping:")
    for feature, weight in final_weights.items():
        print(f"{feature}: {weight}")
    if weights_save_file is not None:
        with open(weights_save_file, 'wb') as f:
            pickle.dump(final_weights, f)
    return final_weights

def evaluate_analyzer(test_data_path, thresholds=[1,5,10,20,30,40,50,60,70,80,90]):
    print("Evaluating the analyzer on the test data.")
    db = SmishingDB(test_data_path)
    db.open_file()
    y_test = db.get_full_column('LABEL')
    entity_list = analyze_messages(test_data_path)
    scores = []

    for enitity in entity_list:
        scores.append(enitity.getScore())
    scores = [float(score) for score in scores]
    results = []
    for threshold in thresholds:
        y_pred = (np.array(scores) > threshold).astype(int)
        true_positives = np.sum((y_test == 1) & (y_pred == 1))
        true_negatives = np.sum((y_test == 0) & (y_pred == 0))
        false_positives = np.sum((y_test == 0) & (y_pred == 1))
        false_negatives = np.sum((y_test == 1) & (y_pred == 0))
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        accuracy = (true_positives + true_negatives) / len(y_test)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        results.append({
            'threshold': threshold,
            'precision': precision,
            'recall': recall,
            'accuracy': accuracy,
            'f1': f1
        })
        finalResults = "Results: \n\n"
        for result in results:
            finalResults += f"Threshold: {result['threshold']}\n\n"
            finalResults += f"Precision: {result['precision']:.4f}\n"
            finalResults += f"Recall: {result['recall']:.4f}\n"
            finalResults += f"Accuracy: {result['accuracy']:.4f}\n"
            finalResults += f"F1 Score: {result['f1']:.4f}\n\n"
            finalResults += "-------------------------\n"
    return finalResults

def standardizeFeatures(features_file, standardized_features_file = None, standardization_params_file = None):
    db = SmishingDB(features_file)
    db.open_file()
    df = db.get_data_object()
    standardization_params = {}
    for feature in consts.quantitative_features:
        mean = df[feature].mean()
        std = df[feature].std()
        df[feature] = (df[feature] - mean) / std
        standardization_params[feature] = {'mean': mean, 'std': std}
    if(standardization_params_file is not None):
        with open(standardization_params_file, 'wb') as f:
            pickle.dump(standardization_params, f)
        print(f"Standardization params saved to '{standardization_params_file}'.")
    if standardized_features_file is not None:
        df.to_csv(standardized_features_file, index=False)
        print(f"Data saved to '{standardized_features_file}'.")
    return df, standardization_params

def analyze_messages(messages_file, n=-1, output_csv=None):
    print("\nAnalyzing messages:")
    db = SmishingDB(messages_file)
    db.open_file()
    data = db.get_data_object()
    if n != -1:
        data = data.head(n)
    analyzer = ha()
    count = 1
    times, all_features = [], []
    analyzed_entity_list = []
    for _, row in data.iterrows():
        start_time = time.time()
        message = row['TEXT']
        label = row['LABEL']
        if not isinstance(message, str):
            continue
        text, urls = res.link_stripper(message)
        text, _ = res.emoji_stripper(text)
        entity = analyzedEntity()
        analyzed_entity_list.append(entity)
        analyzer.analyse(entity, text, urls)
        features = entity.analysisDict
        features['LABEL'] = label
        all_features.append(features)
        end_time = time.time()
        elapsed_time = end_time - start_time
        times.append(elapsed_time)
        average_time_per_step = sum(times) / len(times)
        estimated_remaining_time = average_time_per_step * (len(data) - count)
        sys.stdout.write(f"\rStep {count}/{len(data)} completed. Last step took {format_time(elapsed_time)} seconds. Estimated remaining time: {format_time(estimated_remaining_time)} seconds")
        sys.stdout.flush()
        count += 1
        

    if output_csv is not None:
        try:
            df = pd.DataFrame(all_features).fillna(0)
            # make LABEL the leftmost
            columns = ['LABEL'] + [col for col in df.columns if col != 'LABEL']
            df = df[columns]
            df.to_csv(output_csv, index=False)
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")

    return analyzed_entity_list

def heuristic_nn_train_and_save(standardized_features_path, save_path = None, test_size=0.2, batch_size=32, epochs=100):
    df = pd.read_csv(standardized_features_path)
    X = df.drop('LABEL', axis=1).values
    y = df['LABEL'].values
    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    dataset = dataset.shuffle(buffer_size=len(X))
    train_size = int(len(X) * (1 - test_size))
    train_dataset = dataset.take(train_size).batch(batch_size)
    test_dataset = dataset.skip(train_size).batch(batch_size)
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_dim=X.shape[1]),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    history = model.fit(train_dataset, epochs=epochs, validation_data=test_dataset, verbose=1)
    if save_path is not None:
        model.save(save_path)
    return model, history

def evaluate_heuristic_nn(model_path, test_features_standardized):
    model = tf.keras.models.load_model(model_path)

    df = pd.read_csv(test_features_standardized)
    X_test = df.drop('LABEL', axis=1).values
    y_test = df['LABEL'].values

    y_pred_prob = model.predict(X_test)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten() 

    true_positives = np.sum((y_test == 1) & (y_pred == 1))
    true_negatives = np.sum((y_test == 0) & (y_pred == 0))
    false_positives = np.sum((y_test == 0) & (y_pred == 1))
    false_negatives = np.sum((y_test == 1) & (y_pred == 0))

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    accuracy = (true_positives + true_negatives) / len(y_test)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    finalResults = "Results: \n\n"
    finalResults += f"Precision: {precision:.4f}\n"
    finalResults += f"Recall: {recall:.4f}\n"
    finalResults += f"Accuracy: {accuracy:.4f}\n"
    finalResults += f"F1 Score: {f1:.4f}\n\n"
    finalResults += "-------------------------\n"

    return finalResults

def train_roberta_model(train_dataset_file, roberta_save_dir, num_labels=2, epochs=2):
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    db = SmishingDB(train_dataset_file)
    db.open_file()
    data = db.get_data_object()
    train_texts = data['TEXT'].tolist()
    train_labels = data['LABEL'].values.astype('int32')  # Ensure labels are int32
    train_inputs = tokenizer(train_texts, return_tensors='tf', padding=True, truncation=True, max_length=128)
    train_dataset = tf.data.Dataset.from_tensor_slices((dict(train_inputs), train_labels))
    train_dataset = train_dataset.shuffle(buffer_size=1024).batch(32)
    model = TFRobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=num_labels)
    optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')
    model.compile(optimizer=optimizer, loss=loss, metrics=[metric])
    model.fit(train_dataset, epochs=epochs)
    model.save_pretrained(roberta_save_dir)
    print("Model saved to:", roberta_save_dir)
    return model

def extract_features_from_finetuned_model(training_data_path, model_dir, output_file=None, batch_size=32):
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    model = TFRobertaForSequenceClassification.from_pretrained(model_dir, output_hidden_states=True)
    db = SmishingDB(training_data_path)
    db.open_file()
    data = db.get_data_object()
    texts = data['TEXT'].tolist()
    labels = data['LABEL'].tolist()  # Get the labels
    
    features = []
    total_steps = len(texts) // batch_size + (1 if len(texts) % batch_size != 0 else 0)
    times = []
    for i in range(0, len(texts), batch_size):
        start_time = time.time()
        batch_texts = texts[i:i+batch_size]
        inputs = tokenizer(batch_texts, return_tensors='tf', padding=True, truncation=True, max_length=128)

        input_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']

        outputs = model(input_ids, attention_mask = attention_mask, training=False)
        hidden_states = outputs.hidden_states
        batch_features = hidden_states[-1][:, 0, :].numpy()  # hidden states from previous layer
        features.append(batch_features)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        times.append(elapsed_time)
        
        average_time_per_step = sum(times) / len(times)
        estimated_remaining_time = average_time_per_step * (total_steps - (i // batch_size + 1))
        
        current_step = i // batch_size + 1
        sys.stdout.write(f"\rStep {current_step}/{total_steps} completed. Last step took {format_time(elapsed_time)}. Estimated remaining time: {format_time(estimated_remaining_time)}")
        sys.stdout.flush()
    
    features = np.vstack(features)
    
    if output_file is not None:
        df_features = pd.DataFrame(features)
        df_features['LABEL'] = labels[:len(features)]
        df_features.to_csv(output_file, index=False) 
        print(f"\nFeatures saved to '{output_file}'")
    
    return features

def lm_model_train_and_save(deep_features_csv, model_path, model_name='custom_deep_feature_mlp'):
    db = SmishingDB(deep_features_csv)
    db.open_file()
    data = db.get_data_object()
    features = data.drop(columns=['LABEL']).values
    labels = data['LABEL'].values
    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    dataset = dataset.shuffle(buffer_size=1024).batch(32)
    mlp_model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(features.shape[1],)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    mlp_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    normalizer = tf.keras.layers.Normalization()
    normalizer.adapt(features)
    custom_model = CustomModel(mlp_model, normalizer)
    custom_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    custom_model.fit(dataset, epochs=50, validation_data=dataset, verbose=1)
    if model_path is not None:
        model_full_path = model_path + '/' + model_name
        custom_model.save(model_full_path)
    return custom_model

def evaluate_lm_model(roberta_path, mlp_path, test_dataset):
    analyzer = LMAnalyzer(roberta_path, mlp_path)
    db = SmishingDB(test_dataset)
    db.open_file()
    test_data = db.get_data_object()
    test_texts = test_data['TEXT'].tolist()
    test_labels = test_data['LABEL'].values.astype(float)
    test_dataset = tf.data.Dataset.from_tensor_slices((test_texts, test_labels))
    test_dataset = test_dataset.batch(32)
    accuracy = tf.keras.metrics.BinaryAccuracy()
    precision = tf.keras.metrics.Precision()
    recall = tf.keras.metrics.Recall()
    auc = tf.keras.metrics.AUC()
    count = 1
    times = []
    for text, label in zip(test_texts, test_labels):
        start_time = time.time()
        
        features = analyzer.preprocess_message(text)
        prediction = analyzer.mlp_model.predict(features)
        predicted_label = (prediction > 0.5).astype(int).flatten()
        accuracy.update_state([label], predicted_label)
        precision.update_state([label], predicted_label)
        recall.update_state([label], predicted_label)
        auc.update_state([label], predicted_label)

        end_time = time.time()
        elapsed_time = end_time - start_time
        times.append(elapsed_time)
        average_time_per_step = sum(times) / len(times)
        estimated_remaining_time = average_time_per_step * (len(test_texts) - count)
        sys.stdout.write(f"\rStep {count}/{len(test_texts)} completed. Last step took {format_time(elapsed_time)} seconds. Estimated remaining time: {format_time(estimated_remaining_time)} seconds")
        sys.stdout.flush()
        count += 1

    precision_value = precision.result().numpy()
    recall_value = recall.result().numpy()
    if precision_value + recall_value == 0:
        f1_value = 0
    else:
        f1_value = 2 * (precision_value * recall_value) / (precision_value + recall_value)
    print(f"Accuracy: {accuracy.result().numpy():.4f}")
    print(f"Precision: {precision.result().numpy():.4f}")
    print(f"Recall: {recall.result().numpy():.4f}")
    print(f"AUC: {auc.result().numpy():.4f}")
    print(f"F1 Score: {f1_value:.4f}")
    return {
        'accuracy': accuracy.result().numpy(),
        'precision': precision.result().numpy(),
        'recall': recall.result().numpy(),
        'auc': auc.result().numpy(),
        'f1_score': f1_value
    }

# helper functions

def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    return f"{int(mins)}m {int(secs)}s"

def log_normalize_feature_values(feature_values):
    return [math.log1p(value) for value in feature_values]

def calculate_feature_statistics(df, binary_features, quantitative_features):
    binary_feature_counts = {feature: 0 for feature in binary_features}
    quantitative_feature_values = {feature: [] for feature in quantitative_features}
    total_entities = len(df)
    for _, row in df.iterrows():
        
        for feature in binary_features:
            if row.get(feature):
                binary_feature_counts[feature] += 1
        for feature in quantitative_features:
            if feature in row and row[feature]:
                quantitative_feature_values[feature].append(row[feature])
    normalized_quantitative_values = {
        feature: log_normalize_feature_values(values)
        for feature, values in quantitative_feature_values.items()
    }
    binary_feature_percentages = {
        feature: (count / total_entities * 100) if total_entities > 0 else 0
        for feature, count in binary_feature_counts.items()
    }
    quantitative_feature_averages = {
        feature: (sum(values) / len(values)) if len(values) > 0 else 0
        for feature, values in normalized_quantitative_values.items()
    }
    return binary_feature_percentages, quantitative_feature_averages

if __name__ == "__main__":
    main()
