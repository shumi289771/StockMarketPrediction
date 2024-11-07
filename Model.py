import tensorflow as tf
from keras_tuner import RandomSearch

class Model:
    def __init__(self, model_type, input_shape):
        self.model_type = model_type
        self.input_shape = input_shape
        self.model = None

    def build_model(self, hp):
        model = tf.keras.Sequential()
        if self.model_type == 'CNN+GRU':
            model.add(tf.keras.layers.Conv1D(filters=hp.Int('conv_filters', 32, 128, step=32),
                                             kernel_size=hp.Choice('conv_kernel', [3, 5]),
                                             activation='relu', input_shape=self.input_shape))
            model.add(tf.keras.layers.GRU(hp.Int('gru_units', 32, 128, step=32), return_sequences=True))
        elif self.model_type == 'CNN+LSTM':
            model.add(tf.keras.layers.Conv1D(filters=hp.Int('conv_filters', 32, 128, step=32),
                                             kernel_size=hp.Choice('conv_kernel', [3, 5]),
                                             activation='relu', input_shape=self.input_shape))
            model.add(tf.keras.layers.LSTM(hp.Int('lstm_units', 32, 128, step=32), return_sequences=True))
        elif self.model_type == 'LSTM':
            model.add(tf.keras.layers.LSTM(hp.Int('lstm_units', 32, 128, step=32), input_shape=self.input_shape))

        model.add(tf.keras.layers.Dense(1))  # Pour la prédiction de la valeur suivante
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def tune_hyperparameters(self, X_train, y_train):
        tuner = RandomSearch(
            self.build_model,
            objective='val_loss',
            max_trials=5,
            executions_per_trial=1,
            directory='tuner_logs',
            project_name=f'{self.model_type}_tuning'
        )
        
        tuner.search(X_train, y_train, epochs=10, validation_split=0.2)
        self.model = tuner.get_best_models(num_models=1)[0]
        return tuner

    def train_best_model(self, X_train, y_train, epochs=50):
        self.model.fit(X_train, y_train, epochs=epochs, validation_split=0.2)
        print("Modèle entraîné")

    def save_model(self, path="best_model.h5"):
        self.model.save(path)
        print(f"Modèle enregistré dans {path}")

    def predict(self, X):
        return self.model.predict(X)
