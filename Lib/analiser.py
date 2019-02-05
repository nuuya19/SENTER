from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np 
from keras.models import model_from_json
from random import shuffle
from model_tfidf import TFIDF
import nltk
import csv
import math
from sklearn.feature_extraction.text import TfidfVectorizer
import re, string


class Analiser:
	'''
	variable data training input dan output
	'''
	xdata = []
	ydata = []

	'''
	variable object attributes class
	'''
	tfidf_data = None
	model_loaded = None

	def __init__(self, training_data='data/coba_train.csv'):
		self.preproses(training_data)
		return None

	def preproses(self, filepath):
		f = open(filepath)

		sents = f.read().split('\n')

		shuffle(sents)

		for sent in sents:
			temp = sent.split(';')
			if len(temp) == 2:
				self.xdata.append(temp[0])
				self.ydata.append([int(temp[1])])

		self.tfidf_data = TFIDF([self.xdata, self.ydata])

	def save_model(self, model, filename='model'):
		self.model_loaded = model

		# - save model
		model_json = model.to_json()
		with open("model/" + filename + ".json", "w") as json_file:
		    json_file.write(model_json)

		# - save weight
		model.save_weights("model/" + filename + ".weight")
		print("Model Disimpan")
		# END SAVING MODEL

	def load_model(self, filename='model'):
		model = Sequential()

		# START LOADING MODEL
		json_file = open("model/" + filename + ".json", 'r')
		loaded_model_json = json_file.read()
		json_file.close()
		model = model_from_json(loaded_model_json)
		
		# - load weights
		model.load_weights("model/" + filename + ".weight")
		print("Load Model")
		# END LOADING MODEL

		self.model_loaded = model
		return model

	'''
	Train data 
	'''
	def train(self, output_filename = 'model'):
		X = self.tfidf_data.getOnlyX()
		Y = self.ydata

		model = Sequential()


		
		# - menggunakan 4 layer
		# - 
		# - -  layer 1	: persamaan untuk panjang dimensi fitur data (maks. 300)
		# - -  layer 2 	: persamaan untuk .3xxxx layer 1 (activated tanh)
		# - -  layer 3 	: 5 (activated  tanh)
		# - - output layer 	: 1 (activated sigmoid)
		input_data_dimension = len(X[0])
		input_data_dimension = 300 if input_data_dimension > 300 else input_data_dimension

		model.add(Dense(units=int(0.34 * input_data_dimension), activation='tanh', input_dim=input_data_dimension))
		model.add(Dense(units=5, activation='tanh'))
		model.add(Dense(units=1, activation='sigmoid'))
		

		learning_rate 	= .01
		loss_error		= 'binary_crossentropy'
		batch_size		= 1
		epoch 			= 10

		sgd = SGD(lr=learning_rate)
		model.compile(loss=loss_error, optimizer=sgd, metrics=['accuracy'])

		# start building network
		model.fit(np.array(X), np.array(Y), batch_size=batch_size, nb_epoch=epoch)
		
		#scores = model.evaluate(np.array(X), np.array(Y), verbose=1)
		#print("Accuracy: %.2f%%" % (scores[1]*100))


		# saving model
		self.save_model(model, output_filename)

	def retrain(self, output_filename):
		X = self.tfidf_data.getOnlyX()
		Y = self.ydata
		
		# loading model
		model = self.load_model(output_filename)

		learning_rate 	= .005
		loss_error		= 'binary_crossentropy'
		batch_size		= 1
		epoch 			= 3

		sgd = SGD(lr=learning_rate)
		model.compile(loss=loss_error, optimizer=sgd)
		model.fit(np.array(X), np.array(Y), batch_size=batch_size, nb_epoch=epoch)

		# save model
		self.save_model(model, output_filename)


	def getBinaryResult(self, x):
		return x[0][0]
		#return np.float(x[0][0])
	
	def getStrResult(self, x):
		if x >= 0.7:
			return "Positif"
		elif 0.4 <= x <= 0.69:
			return "Netral"
		else :
			return "Negatif"

	'''
	Test
	'''
	def testFromTrained(self, x):
		if self.model_loaded == None:
			#print ("No Model")
			exit(0)
		
		# model.compile(loss='binary_crossentropy', optimizer=sgd)
		return self.getBinaryResult(self.model_loaded.predict_proba(np.array(x)))
		#return self.getStrResult(self.model_loaded.predict_proba(np.array(x)))

	def testStrFromTrained(self, x):
		if self.model_loaded == None:
			#print ("No Model")
			exit(0)
		
		# model.compile(loss='binary_crossentropy', optimizer=sgd)
		return self.getStrResult(self.model_loaded.predict_proba(np.array(x)))


