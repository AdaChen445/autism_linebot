import os
import numpy as np
from PIL import ImageFont, ImageDraw, Image


def create_member(userID):
	#create user DB
	filename = 'userdata'
	if not os.path.isdir(filename): os.mkdir(filename)
	filename = f'userdata{os.path.sep}{userID}'
	if not os.path.isdir(filename): os.mkdir(filename)


def write_temp_image(userID, imageContent):
	# return image for classification
	path = f'userdata{os.path.sep}{userID}{os.path.sep}tempImage'
	with open(path, 'wb') as fd:
		for chunk in imageContent.iter_content():
			fd.write(chunk)
	img = Image.open(path).convert('RGB')
	img = img.resize((224,224))
	img = np.asarray(img)
	return img


def write_record(userID, imageName, imageContent, result, timeStamp):
	path = f'userdata{os.path.sep}{userID}{os.path.sep}{imageName}'
	# write image into DB
	with open(path, 'wb') as fd:
		for chunk in imageContent.iter_content():
			fd.write(chunk)
	# add date and result on image
	img = Image.open(path)
	font = ImageFont.truetype('msjh.ttc', 50)
	draw = ImageDraw.Draw(img)
	draw.text((10, 30), timeStamp, font=font, fill=(0,255,255))
	draw.text((10, 100), result, font=font, fill=(0,255,255))
	img.save(path)


def read_record(userID, ngrokDBURL):
	imageURLs = []
	imageNames = os.listdir(f'userdata{os.path.sep}{userID}')
	for imageName in imageNames:
		if not imageName == 'tempImage': imageURLs.append(f'{ngrokDBURL}/userdata/{userID}/{imageName}')
	return imageURLs


def _del_record():
	pass

if __name__ == '__main__':
	pass