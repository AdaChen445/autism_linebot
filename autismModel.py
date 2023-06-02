import os
import numpy as np
import pickle
from PIL import ImageFont, ImageDraw, Image
from tensorflow.keras.models import load_model


def model_classify(img):
	batch_size = 32
	model = load_model('best.h5')
	img = np.expand_dims(img, axis=0)
	result_id = np.argmax(model.predict(img, batch_size), axis=1)

	with open('le.pickle', 'rb') as temp:
		le = pickle.load(temp)
	result = le.classes_[result_id]

	if result == 'positive': return '陽性'
	elif result == 'negative': return '陰性'



if __name__ == '__main__':
	pass