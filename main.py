import os

import cv2.cv2 as cv2
import numpy as np
from keras.callbacks import EarlyStopping
from keras.layers import ConvLSTM2D, Dropout, Flatten, Dense
from keras.models import Sequential
from keras.optimizers import SGD
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

data_dir = 'video_data'
img_height, img_width = 64, 64
seq_len = 70

classes = ['biking', 'diving', 'swing']


def frames_extraction(video_path):
    frames_list = []

    vid_obj = cv2.VideoCapture(video_path)
    # Used as counter variable
    count = 1
    while count <= seq_len:
        success, image = vid_obj.read()
        if success:
            image = cv2.resize(image, (img_height, img_width))

            frames_list.append(image)
            count += 1
        else:
            print("Defected frame")
            break

    return frames_list


def create_data(input_dir):
    X = []
    Y = []

    classes_list = os.listdir(input_dir)
    for c in classes_list:
        sub_folders_list = os.listdir(os.path.join(input_dir, c))
        for f in sub_folders_list:
            for ff in os.listdir(os.path.join(input_dir, c, f)):
                frames = frames_extraction(os.path.join(os.path.join(input_dir, c, f), ff))
                if len(frames) == seq_len:
                    X.append(frames)

                    y = [0] * len(classes)
                    y[classes.index(c)] = 1

                    Y.append(y)

    X = np.asarray(X)
    Y = np.asarray(Y)
    return X, Y


X, Y = create_data(data_dir)
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, shuffle=True, random_state=0)
model = Sequential()
model.add(ConvLSTM2D(filters=64,
                     kernel_size=(3, 3),
                     return_sequences=True,
                     input_shape=(seq_len, img_height, img_width, 3)))
model.add(ConvLSTM2D(filters=128,
                     kernel_size=(3, 3),
                     return_sequences=True,
                     input_shape=(seq_len, img_height, img_width, 3)))
model.add(ConvLSTM2D(filters=256,
                     kernel_size=(3, 3),
                     return_sequences=False,
                     input_shape=(seq_len, img_height, img_width, 3)))
model.add(Dropout(0.2))
model.add(Flatten())
model.add(Dense(256, activation="relu"))
model.add(Dropout(0.3))
model.add(Dense(3, activation="softmax"))
model.summary()

opt = SGD(lr=0.001)
model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=["accuracy"])

early_stop = EarlyStopping(patience=7)
callbacks = [early_stop]

history = model.fit(x=X_train, y=y_train, epochs=40, batch_size=8, shuffle=True, validation_split=0.2,
                    callbacks=callbacks)

y_pred = model.predict(X_test)
y_pred = np.argmax(y_pred, axis=1)
y_test = np.argmax(y_test, axis=1)

print(classification_report(y_test, y_pred))
