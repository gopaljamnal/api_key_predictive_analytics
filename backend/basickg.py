

import re
import pandas as pd
import bs4
import requests
import spacy
from spacy import displacy
nlp = spacy.load('en_core_web_sm')

from spacy.matcher import Matcher
from spacy.tokens import Span

import networkx as nx

import matplotlib.pyplot as plt
from tqdm import tqdm
import PyPDF2
pd.set_option('display.max_colwidth', 200)



# import wikipedia sentences
candidate_sentences = pd.read_csv('/home/gopal/Downloads/wikisent2.txt')
print(candidate_sentences.shape)




