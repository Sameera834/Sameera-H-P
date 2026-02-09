import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical

df = pd.read_csv("data.csv")

tokenizer = Tokenizer(num_words=8000, oov_token="<OOV>")
tokenizer.fit_on_texts(df.text)
X = pad_sequences(tokenizer.texts_to_sequences(df.text), maxlen=60)

pickle.dump(tokenizer, open("tokenizer.pkl","wb"))

def train_model(y, name):
    model = Sequential([
        Embedding(8000,128,input_length=60),
        LSTM(128,return_sequences=True),
        Dropout(0.3),
        LSTM(64),
        Dense(64,activation="relu"),
        Dense(y.shape[1],activation="softmax")
    ])
    model.compile("adam","categorical_crossentropy",metrics=["accuracy"])
    model.fit(X,y,epochs=15,batch_size=32)
    model.save(f"{name}_model.h5")

encoders = {}
for col in ["intent","sentiment","emotion"]:
    le = LabelEncoder()
    y = to_categorical(le.fit_transform(df[col]))
    encoders[col] = le
    train_model(y,col)

pickle.dump(encoders,open("encoders.pkl","wb"))
print("✅ All models trained & saved")
