training_dataset = "Labs/smishing_dataset_lab/files_final/smishingDB_augmented.csv"
test_dataset = "Labs/smishing_dataset_lab/files_final/testData_augmented.csv"

# features standratized for nn
heuristic_features_save_file = "Labs/smishing_dataset_lab/files_final/heuristic_features_raw.csv"
features_save_file = "Labs/smishing_dataset_lab/files_final/standardized_features_for_nn.csv"
heuristic_features_standardized_save_file = "./Labs/smishing_dataset_lab/files_final/heuristic_features_standardized.csv"
standardization_params_save_file = "./Labs/smishing_dataset_lab/files_final/standardization_params.pkl"
weights_save_file = "Labs/smishing_dataset_lab/files_final/weights.pkl"
nn_save_file = "Labs/smishing_dataset_lab/files_final/smishing_model.keras"

test_features_save_file = "Labs/smishing_dataset_lab/files_final/test_features.csv"
test_features_standardized_save_file = "Labs/smishing_dataset_lab/files_final/test_features_standardized.csv"
test_features_standardization_params_save_file = "Labs/smishing_dataset_lab/files_final/test_standardization_params.pkl"



# lm specific:
model_path = './Labs/smishing_dataset_lab/lm'
tokenizer_path = './Labs/smishing_dataset_lab/lm'
roberta_save_dir = './Labs/smishing_dataset_lab/lm/fine-tuned-roberta'
deep_features_save_path = './Labs/smishing_dataset_lab/lm/deep_features.csv'
mlp_path = './Labs/smishing_dataset_lab/lm'
mlp_name = 'deep_feature_mlp'
mlp_full_path = mlp_path + '/' + mlp_name