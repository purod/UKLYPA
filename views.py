#! /usr/bin/env python
from flask import Flask,render_template,request,url_for
from flask_bootstrap import Bootstrap
from UKLYPA import app

# topic modeling
import numpy as np
import pandas as pd
import re,spacy,folium
from gensim.utils import simple_preprocess
import gensim.corpora as corpora
from nltk.corpus import stopwords
import gensim

# sentiment analysis
from textblob import TextBlob,Word

# files
import pickle
import random 
import time
import os
import json

Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse',methods=['POST'])
def analyse():
	start = time.time()
	if request.method == 'POST':
		rawtext = request.form['rawtext']
		# Part 1. sentiment analysis
		blob = TextBlob(rawtext)
		received_text2 = blob
		blob_sentiment,blob_subjectivity = blob.sentiment.polarity ,blob.sentiment.subjectivity
		number_of_tokens = len(list(blob.words))
		# Extracting Main Points
		nouns = list()
		summary = list()
		for word, tag in blob.tags:
			if tag == 'NN':
				nouns.append(word.lemmatize())
				len_of_words = len(nouns)
				rand_words = random.sample(nouns,len(nouns))
				final_word = list()
				for item in rand_words:
					word = Word(item).pluralize()
					final_word.append(word)
					summary = final_word
					end = time.time()
					final_time = end-start
	
                # Part 2. topic modeling
		
		# 2.1. Load in trained LDA model
		PIK = "/home/ubuntu/Insight_project/UKLYPA/Trained_model.pkl"
		with open(PIK, "rb") as f:
			FM=pickle.load(f)
		FM['model'].mallet_path='/home/ubuntu/Insight_project/UKLYPA/mallet-2.0.8/bin/mallet'
		text = rawtext
                # 2.2. Preprocesssing
                # Remove new line characters
		user_data = re.sub(r'\s+', ' ', text)
                # Remove both www and http
		user_data = re.sub('www', '', user_data)
		user_data = re.sub('http', '', user_data)
		user_data = re.sub('html', '', user_data)
		user_data = re.sub('org', '', user_data)
                # Remove distracting single quotes
		user_data = re.sub(r"\'", "", user_data)

                # tokenization
		user_words = gensim.utils.simple_preprocess(str(user_data), deacc=True)
		
		# define stop words
		stop_words = stopwords.words('english')
		stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

                # remove stop words
		user_nostops = [word for word in simple_preprocess(str(user_words)) if word not in stop_words]
		user_bigram = [FM['bigram_mod'][user_nostops]]
		nlp = spacy.load('en', disable=['parser', 'ner'])
                # lemmatization
		def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
			"""https://spacy.io/api/annotation"""
			texts_out = []
			for sent in texts:
				doc = nlp(" ".join(sent))
				texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
			return texts_out
		user_lemmatized = lemmatization(user_bigram, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
		
                # Term Document Frequency
		user_corpus = [FM['id2word'].doc2bow(text) for text in user_lemmatized]

                # 2.3. calculate the weight vector for a specific petition
		user_weight = np.array([i[1] for i in FM['model'][user_corpus][0]]).reshape(-1,1)
                # transform the topic vector
		user_trans = np.power(user_weight,4)*1000
		
                # Part 3. Integrate topic weight, sentiment score and geographic information 
		if blob_sentiment>0.1:
			user_location = np.dot(FM['loc_topic_pos'].T,user_trans)
		elif blob_sentiment<-0.1:
			user_location = np.dot(FM['loc_topic_neg'].T,user_trans)
		else:
			user_location = np.dot(FM['loc_topic_neu'].T,user_trans)
                # normalization to scale 0-10
		user_norm= np.interp(user_location, (user_location.min(), user_location.max()), (0, 10))
                # Part 4. Plot the map using user_norm
		# add names of parliamentary constituents
		IP='/home/ubuntu/Insight_project/UKLYPA/PreTrain/uk_name.pkl'
		with open(IP, "rb") as f:
			uk_list = pickle.load(f)
		constituent_data = pd.DataFrame(data=user_norm, index=uk_list, columns=['Support Index'])
		constituent_data['pcon17nm'] = constituent_data.index
		constituent_data=constituent_data.reindex(columns=['pcon17nm','Support Index'])
		# map in geojson format
		state_map = '/home/ubuntu/Insight_project/UKLYPA/static/geojson_file.json'
        	# chroploth map
		m = folium.Map(location=[56, -2], zoom_start=5)

		folium_temp = folium.Choropleth(
    		geo_data=state_map,
    		name='choropleth',
    		data=constituent_data,
    		columns=['pcon17nm', 'Support Index'],
    		key_on='feature.properties.pcon17nm',
    		fill_color='YlGnBu',
    		fill_opacity=0.7,
    		line_opacity=0.2,
    		legend_name='Support Index'
		).add_to(m)
		# hover 
		folium_temp.geojson.add_child(
			folium.features.GeoJsonTooltip(['pcon17nm'],labels=False )
		)
		folium.LayerControl().add_to(m)
                # save the map
		m.save('/home/ubuntu/Insight_project/UKLYPA/templates/map1.html')
	return render_template('response.html',received_text = received_text2,number_of_tokens=number_of_tokens,blob_sentiment=blob_sentiment,blob_subjectivity=blob_subjectivity,summary=summary,final_time=final_time)

# Load in petition map
@app.route('/show_map')
def show_map():
	return render_template('map1.html')
# load in default map
@app.route('/def_map')
def def_map():
	return render_template('map.html')

