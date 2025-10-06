import nltk
import re

# Download nltk
nltk.download('punkt_tab')      
nltk.download('wordnet')    
nltk.download('omw-1.4') 
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('stopwords')

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import pos_tag

stop_words = set(stopwords.words('english'))

class Lemmalizer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def get_wordnet_pos(tag):
        if tag.startswith('J'):  
            return 'a'
        elif tag.startswith('V'):  
            return 'v'
        elif tag.startswith('N'):  
            return 'n'
        elif tag.startswith('R'):  
            return 'r'
        else:
            return 'n'  

    def lemmalize(self, sentence):
        tokens = word_tokenize(sentence)
        tagged_tokens = pos_tag(tokens)
        lemmatized_sentence = []

        for word, tag in tagged_tokens:
            if word.lower() == 'are' or word.lower() in ['is', 'am']:
                lemmatized_sentence.append(word)  
            else:
                lemmatized_sentence.append(self.lemmatizer.lemmatize(word, self.get_wordnet_pos(tag)))
        return lemmatized_sentence
    
    def lemmalize_sentence(self, sentence):
        lemmatized_sentence = self.lemmalize(sentence)
        return " ".join(lemmatized_sentence)
    
    def lemmalize_words(self, tokens):
        token_sentence = " ".join(tokens)
        lemmatized_tokens = self.lemmalize(token_sentence)
        return lemmatized_tokens
    
# Instance
lemmalizer = Lemmalizer()

#-- Remove Stop Word
def remove_stopwords(text):
    words = text.split(" ")
    clean_sentences = " ".join([word for word in words if word.lower() not in stop_words])
    return clean_sentences
        

#-- Parse Element
def parse_element(text):
    # Regex patterns
    object_pattern = r"<o>\s*(.*?)\s*</o>"
    action_pattern = r"<ac>\s*(.*?)\s*</ac>"
    adj_pattern = r"<adj>\s*(.*?)\s*</adj>"

    # Extract using re.findall
    return {
        "objects": re.findall(object_pattern, text),
        "actions": re.findall(action_pattern, text),
        "adjectives": re.findall(adj_pattern, text)
    }