import csv
from hashlib import md5
import sys
from nltk.corpus import wordnet as nltk_wn
from nltk.corpus import stopwords as nltk_sw
import shutil
import os

alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ '
digits = '0123456789'


class Tweet:
	def __init__(self, clss, message):
		self.__clss = clss
		self.__message = message
		self.__original_message = message

	def get_class(self):
		return self.__clss

	def get_id(self, length = 11):
		return str(self.__clss) + '_' + self.get_md5_hash()[0:length]

	def get_message(self):
		return self.__message

	def set_message(self, message):
		self.__message = message

	def get_original_message(self):
		return self.__original_message

	def get_md5_hash(self):
		return md5(self.__original_message.encode()).hexdigest()

	def to_lower(self):
		self.__message = self.__message.lower()

	def remove_symbols(self):
		self.__message = ''.join(x for x in self.__message if x in alphabet or x in digits).strip()

	def __str__(self):
		return self.__clss+': '+self.__message

	def __repr__(self):
		return self.__str__()


class TweetsAggregates:
	def __init__(self, csv_file_name):
		self.__tweets = self.read_tweets(csv_file_name)

	@staticmethod
	def read_tweets(file_name):
		tweets = set()
		with open(file_name, 'r') as _file:
			_content = csv.reader(_file)
			for c in _content:
				tweets.add(Tweet(clss=c[0], message=c[1]))
			del _content
		return list(tweets)

	def all_to_lower(self):
		for t in self.__tweets:
			t.to_lower()

	def remove_symbols(self):
		for t in self.__tweets:
			t.remove_symbols()

	def replacement_for_sinonimos(self):
		# extrai todas as palavras usadas na base de tweets excluindo stopwords (nltk)
		all_words = set(word for tweet in self.__tweets for word in tweet.get_message().split() if word not in nltk_sw.words())  # nltk_sw.words('english')

		# para cada palavra, recupera todos os seus sinonimos e armazena em um dicionario
		words_synonymous = {}  # [palavra] -> sinonimos
		all_synonymous = []  # armazenar todos os sinonimos ; tem que ser lista para poder contar a freq de cada sinonimo
		for w in all_words:
			S = set(syn_word for synset in nltk_wn.synsets(w) for syn_word in synset.lemma_names())  # set para eliminar duplicatas
			if len(S) > 0:
				words_synonymous[w] = list(S)
				all_synonymous += list(S)

		# percorre words_synonymous
		# para cara palavra, ordena a lista de synonimo por 'frequencia do sinonimo na lista all_synconymous' e pelo sinonimo, respectivamente
		# apos ordenar, pega o primeiro sinonimo, que será o mais frequente (em teoria)
		for ws in words_synonymous:
			words_synonymous[ws] = sorted(words_synonymous[ws], key = lambda x: (all_synonymous.count(x), x), reverse=True)[0]

		# substitui cada palavra (quando possivel) pelo seu sinonimo mais significativo
		for t in self.__tweets:
			t.set_message(' '.join(words_synonymous.get(word, word) for word in t.get_message().split() if word not in nltk_sw.words()))

	def remove_single_words(self):
		full_content = '\n'.join(' '+tweet.get_message()+' ' for tweet in self.__tweets)

		for i_tweet in range(len(self.__tweets)):
			for word in self.__tweets[i_tweet].get_message().split():
				if self.__tweets[i_tweet].get_message().count(word) == full_content.count(' '+word+' '):
					try:
						new_message = self.__tweets[i_tweet].get_message().replace(word, '')
						new_message = ' '.join(new_message.split())
						self.__tweets[i_tweet].set_message(new_message)
					except Exception:
						pass

	def remove_single_words2(self):
		word_set = set([word for tweet in self.__tweets for word in tweet.get_message().split()])
		word_ocorrency = {word:[(word in tweet.get_message()) for tweet in self.__tweets].count(True) for word in word_set}

		for i_tweet in range(len(self.__tweets)):
			new_message = ' '.join(word for word in self.__tweets[i_tweet].get_message().split() if word_ocorrency[word] >= 3)
			self.__tweets[i_tweet].set_message(new_message)

	def __str__(self):
		return ''.join(str(t)+'\n' for t in self.__tweets)

	def __repr__(self):
		return self.__str__()

	def __getitem__(self, item):
		return self.__tweets[item]

def save(tweets):
	if os.path.exists('output/'):
		shutil.rmtree('output/')
	os.mkdir('output/')
	with open('lista.csv', 'w') as F:
		for t in tweets:
			#            if len(t.get_message()) < 80:
			#               continue
			F.write('{},"{}","{}","{}"\n'.format(t.get_id(), t.get_class(), t.get_message(), t.get_original_message()))
			output = open('output/' + t.get_id(), 'w')
			output.write(t.get_message())
			output.close()

if __name__=='__main__':
	try:
		base = sys.argv[1]
	except IndexError:
		print('The database name should be passed as an argument through the command line...')
		exit(1)

	print('Read tweets...', end=' ')
	tweets = TweetsAggregates(base)
	print('Ok!')
	#print(tweets)

	save(tweets)
	exit(0)

	print('\n## Todos com letras minúsculas:')
	tweets.all_to_lower()
	print(tweets)

	print('\n## Apenas letras e números (sem símbolos)')
	tweets.remove_symbols()
	print(tweets)

	print('\n## Após substituição por sinônimos mais relevantes')
	tweets.replacement_for_sinonimos()
	print(tweets)

	print('\n## Após retirada de palavras que não se repetem')
	tweets.remove_single_words2()
	print(tweets)
	save(tweets)