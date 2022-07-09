#!/bin/sh

pip install flask
pip install boto3
pip install gensim
pip install pandas
pip install nltk
pip install pyenchant
sudo apt-get install libenchant-2-2

python3 -m nltk.downloader punkt
python3 -m nltk.downloader stopwords
python3 -m nltk.downloader averaged_perceptron_tagger
python3 -m nltk.downloader wordnet
python3 -m nltk.downloader omw-1.4
