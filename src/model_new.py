import dataset as ds
import gensim 
from gensim.utils import simple_preprocess
import numpy as np
import math
import pandas as pd
# import pydot
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import LSTM
from keras.utils import plot_model
from keras.preprocessing import sequence

from keras.models import Model



# Load W2V Model #
w2v = gensim.models.Word2Vec.load('../vocab')
numWords = len(w2v.wv.vocab)
dimension = w2v.vector_size

# Load in text data and transform to vectors #
df = pd.read_csv('../data/sampleTrain.csv', encoding = 'ISO-8859-1')

tweet_vecs = []
outputs = []
lengths = []



for index,row in df.iterrows():
	#tweets.append(row[5])
	tokens = row[6].split(" ")
	lengths.append(len(tokens))
	vec = []
	#tweet_vec = []
	for word in tokens:
		#vec = []
		try:
			idx = w2v.wv.vocab[word].index
			# vec.extend(w2v.wv[word].tolist())
			vec.extend([idx])
			# vec.extend(w2v[word])
																	##  CURRENTLY PUSHING INDEX OF WORD EMBEDDING VECTOR INSTEAD OF VECTOR ITSELF. (EACH IDX REPRESENTS)
																	##  This assumes that the embedding layer is functioning by mapping the index that it is fed to a wordvector
																	##  This change fixed the following error:
																	# 	
																	#    InvalidArgumentError (see above for traceback): indices[0,8] = -1 is not in [0, 135731)
																	#	 [[Node: embedding_1/Gather = Gather[Tindices=DT_INT32, Tparams=DT_FLOAT, validate_indices=true, _device="/job:localhost/replica:0/task:0/cpu:0"](embedding_1/embeddings/read, _recv_embedding_1_input_0)]]


		# zero padding
		except TypeError:
			vec.extend([0])											# This should not be zero! it is supposed to map to a vector that represnts a any word not in the dict
																	# Look to see if it is possible to add a ceritan word to the model in gensim?
			# vec.extend(np.zeros(dimension))
		# word not it dict
		except KeyError:
			vec.extend([0])
			# vec.extend(np.zeros(dimension))
		#tweet_vec.append(vec)

	if (row[1] == 4):
		outputs.append(1)
	else:
		outputs.append(row[1])
	tweet_vecs.append(vec)

#print(lengths)
mean = sum(lengths)/len(lengths)
std = np.std(lengths) 
time_sequence = math.ceil(mean + (2*std))
tweet_vecs = np.array(tweet_vecs)
print("\n ---- Tweet  Vectors --- \n")
print(tweet_vecs)

# train and test data format #
X_train = sequence.pad_sequences(tweet_vecs, maxlen=time_sequence) 		# Fixed by downgrading to numpy 1.11.2 
print("\n ---- x train ---- \n")
print(X_train)
#X_test = sequence.pad_sequences(, maxlen=time_sequence)
weights = np.load(open('../vocab_weights', 'rb'))



#print(time_sequence, weights.shape[1])

# create Model #
model = Sequential()
embed = Embedding(name="inpt", input_dim=weights.shape[0], output_dim=weights.shape[1], input_length=time_sequence, weights=[weights])
print(embed)
model.add(embed) # input_length=time_sequence, 
model.add(LSTM(1, dropout=0.2, recurrent_dropout=0.2)) # input_shape=(None, weights.shape[0], weights.shape[1])) 
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
print(model.summary())


intermediate_layer_model = Model(inputs=model.input,
                                 outputs=model.get_layer('inpt').output)
intermediate_output = intermediate_layer_model.predict(X_train)
print(intermediate_output)


print("\n ---- fitting model ---- \n")

# Fit and Train Model #
model.fit(X_train, outputs, epochs=10, batch_size=60)








