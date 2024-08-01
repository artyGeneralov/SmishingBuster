import tensorflow as tf

class CustomModel(tf.keras.Model):
    def __init__(self, mlp_model, normalizer):
        super(CustomModel, self).__init__()
        self.normalizer = normalizer
        self.mlp_model = mlp_model

    def call(self, inputs):
        normalized_inputs = self.normalizer(inputs)
        return self.mlp_model(normalized_inputs)