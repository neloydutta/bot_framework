from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.datasets import load_files
from sklearn.ensemble import RandomForestClassifier
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# from sklearn.model_selection import GridSearchCV

stop_words = " ".join(stopwords.words('english'))
stop_words = word_tokenize(stop_words, language='english')


class Intent:
    def __init__(self):
        self.train_data_location = "./intent_train"
        self.load_data()
        self.clf = Pipeline([('vect', CountVectorizer()),
                             ('tfidf', TfidfTransformer()),
                             ('clf', RandomForestClassifier())
                             ])
        self.clf.fit(self.bot_intent_train.data, self.bot_intent_train.target)

    def load_data(self):
        self.bot_intent_train = load_files(self.train_data_location, description=None, load_content=True, shuffle=True,
                                      encoding='utf-8', decode_error='ignore', random_state=0)

    def predict(self, query_str):
        words = word_tokenize(query_str)
        words = [word for word in words if word not in stop_words and word not in string.punctuation]
        query = " ".join(words).strip()
        return_dict = {}
        # print(type(query_str))
        # print(len(query_list))
        if type(query) == str:
            query_list = [query]
            predicted = self.clf.predict(query_list)
            return_dict['query_string'] = query_str
            return_dict['intent'] = self.bot_intent_train.target_names[predicted[0]]
        else:
            raise ValueError("Expected str, found " + str(type(query_str)))
        return return_dict

    def score(self):
        bot_intent_test = load_files(self.train_data_location, description=None, load_content=True, shuffle=True,
                                      encoding='utf-8', decode_error='ignore', random_state=0)
        return self.clf.score(bot_intent_test.data, bot_intent_test.target)


def train():
    text_clf = Intent()
    return text_clf


if __name__ == "__main__":
    clf = train()
    print(clf.score())
    while True:
        ip = str(input("Enter>> "))
        print(clf.predict(ip))
