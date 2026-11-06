"""Kiến trúc mạng hồi quy LSTM / GRU nhiều bước (multi-horizon): đầu vào 'lookback' ngày, đầu ra 'horizon' ngày tiếp theo."""
import keras
from keras import layers


def build_model(kind: str, lookback: int, n_features: int, horizon: int,
                units: int = 64, n_layers: int = 2, dropout: float = 0.2, lr: float = 1e-3):
    rnn = {"lstm": layers.LSTM, "gru": layers.GRU}[kind]
    inputs = keras.Input(shape=(lookback, n_features))
    x = inputs
    for i in range(n_layers):
        last = i == n_layers - 1
        x = rnn(units, return_sequences=not last)(x)   # lớp cuối chỉ trả vector cuối chuỗi
        x = layers.Dropout(dropout)(x)                 # chống học vẹt (overfitting)
    outputs = layers.Dense(horizon)(x)                 # một lần dự đoán luôn 'horizon' ngày
    model = keras.Model(inputs, outputs, name=kind)
    model.compile(optimizer=keras.optimizers.Adam(lr), loss="huber", metrics=["mae"])
    return model
