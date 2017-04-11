from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.datasets import load_files
from sklearn.ensemble import AdaBoostClassifier
# from sklearn.model_selection import GridSearchCV


class Intent:
    def __init__(self):
        self.train_data_location = "./intent_train"
        self.load_data()
        self.clf = Pipeline([('vect', CountVectorizer()),
                             ('tfidf', TfidfTransformer()),
                             ('clf', AdaBoostClassifier())
                             ])
        self.clf.fit(bot_intent_train.data, bot_intent_train.target)

    def load_data(self):
        global bot_intent_train
        bot_intent_train = load_files(self.train_data_location, description=None, load_content=True, shuffle=True,
                                      encoding='utf-8', decode_error='ignore', random_state=0)

    def predict(self, query_str):
        return_dict = {}
        # print(type(query_str))
        # print(len(query_list))
        if type(query_str) == str:
            query_list = [query_str]
            predicted = self.clf.predict(query_list)
            return_dict['query_string'] = query_str
            return_dict['intent'] = bot_intent_train.target_names[predicted[0]]
        else:
            raise ValueError("Expected str, found " + str(type(query_str)))
        return return_dict


def train():
    text_clf_Ada = Intent()
    return text_clf_Ada


if __name__ == "__main__":
    clf = train()
    print(clf.predict("what version of ttu has windows 10 support"))
