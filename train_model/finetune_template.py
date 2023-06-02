from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model
import tensorflow as tf

import numpy as np
import pickle
from PIL import Image
import os
import glob

from tqdm import tqdm
from tensorflow.keras.applications.resnet import ResNet50, preprocess_input


#########arguments##########
IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_DEPTH = 3
BS = 32
INIT_LR = 1e-3
EPOCHS = 100
dataset_dir = 'model_dataset'
#########arguments##########



imagePaths = glob.glob(dataset_dir+'/*/*') 
num_classes = len(next(os.walk(dataset_dir))[1])
data = []
labels = []
for imagePath in tqdm(imagePaths):
	label = imagePath.split(os.path.sep)[-2]
	image = Image.open(imagePath).convert('RGB')
	image = image.resize((IMG_WIDTH, IMG_HEIGHT))
	image = np.asarray(image)
	data.append(image)
	labels.append(label)
data = np.array(data, dtype=np.float32)


le = LabelEncoder()
labels = le.fit_transform(labels)
labels = to_categorical(labels, num_classes)
f = open("le.pickle", "wb")
f.write(pickle.dumps(le))
f.close()


(trainX, testX, trainY, testY) = train_test_split(data, labels, 
	test_size=0.25, random_state=42)
trainX = preprocess_input(trainX)
testX = preprocess_input(testX)


model_checkpoint_callback = ModelCheckpoint(
	filepath='best.h5',
	save_weights_only=False,
	monitor='val_accuracy',
	mode='max',
	save_best_only=True)



base_model = ResNet50(weights=None, include_top=False)
base_model.trainable = True
inputs = tf.keras.Input(shape=(IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH))
x = base_model(inputs, training=True)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
model = tf.keras.Model(inputs, outputs, name='finetune_model')
model.summary()
opt = Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS)
model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])


H = model.fit(x=trainX, y=trainY, batch_size=BS,
	validation_data=(testX, testY), steps_per_epoch=len(trainX) // BS,
	epochs=EPOCHS, callbacks = model_checkpoint_callback)

model = load_model('best.h5')
predictions = model.predict(x=testX, batch_size=BS)
print(classification_report(testY.argmax(axis=1),
		predictions.argmax(axis=1), target_names=le.classes_ ,digits=5))