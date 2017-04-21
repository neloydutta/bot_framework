import os
import re
import itertools
from nltk import conlltags2tree, pos_tag, word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk import tree2conlltags
from nltk.chunk import ChunkParserI
from sklearn.linear_model import Perceptron
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline


def to_conll_iob(annotated_sentence):
    """
    `annotated_sentence` = list of triplets [(w1, t1, iob1), ...]
    Transform a pseudo-IOB notation: O, PERSON, PERSON, O, O, LOCATION, O
    to proper IOB notation: O, B-PERSON, I-PERSON, O, O, B-LOCATION, O
    """
    proper_iob_tokens = []
    for idx, annotated_token in enumerate(annotated_sentence):
        tag, word, ner = annotated_token

        if ner != 'O':
            if idx == 0:
                ner = "B-" + ner
            elif annotated_sentence[idx - 1][2] == ner:
                ner = "I-" + ner
            else:
                ner = "B-" + ner
        proper_iob_tokens.append((tag, word, ner))
    return proper_iob_tokens


def read_gmb_ner(corpus_root):
    for root, dirs, files in os.walk(corpus_root):
        for filename in files:
            if filename.endswith(".txt"):
                with open(os.path.join(root, filename), 'r') as file_handle:
                    file_content = file_handle.read()
                    annotated_sentences = file_content.strip().split('\n\n')
                    for annotated_sentence in annotated_sentences:
                        annotated_tokens = [seq for seq in annotated_sentence.split('\n') if seq]
                        if len(annotated_tokens) == 0:
                            continue
                        standard_form_tokens = []

                        for idx, annotated_token in enumerate(annotated_tokens):
                            annotations = annotated_token.split(' ')
                            # print(annotated_sentence)
                            # print(annotated_token)
                            # print(annotations)
                            word, tag, ner = annotations[0], annotations[1], annotations[2]

                            # if ner != 'O':
                            #     ner = ner.split('-')[1]

                            standard_form_tokens.append((word, tag, ner))

                        conll_tokens = to_conll_iob(standard_form_tokens)
                        yield conlltags2tree(conll_tokens)


def shape(word):
    word_shape = 'other'
    if re.match('[0-9]+(\.[0-9]*)?|[0-9]*\.[0-9]+$', word):
        word_shape = 'number'
    elif re.match('\W+$', word):
        word_shape = 'punct'
    elif re.match('[A-Z][a-z]+$', word):
        word_shape = 'capitalized'
    elif re.match('[A-Z]+$', word):
        word_shape = 'uppercase'
    elif re.match('[a-z]+$', word):
        word_shape = 'lowercase'
    elif re.match('[A-Z][a-z]+[A-Z][a-z]+[A-Za-z]*$', word):
        word_shape = 'camelcase'
    elif re.match('[A-Za-z]+$', word):
        word_shape = 'mixedcase'
    elif re.match('__.+__$', word):
        word_shape = 'wildcard'
    elif re.match('[A-Za-z0-9]+\.$', word):
        word_shape = 'ending-dot'
    elif re.match('[A-Za-z0-9]+\.[A-Za-z0-9\.]+\.$', word):
        word_shape = 'abbreviation'
    elif re.match('[A-Za-z0-9]+\-[A-Za-z0-9\-]+.*$', word):
        word_shape = 'contains-hyphen'

    return word_shape


stemmer = SnowballStemmer('english')

def ner_features(tokenst, index, history):
    """
    `tokens`  = a POS-tagged sentence [(w1, t1), ...]
    `index`   = the index of the token we want to extract features for
    `history` = the previous predicted IOB tags
    """

    # Pad the sequence with placeholders
    tokens = [('__START2__', '__START2__'), ('__START1__', '__START1__')] + tokenst + [('__END1__', '__END1__'),
                                                                                            ('__END2__', '__END2__')]
    history = ['__START2__', '__START1__'] + list(history)

    # shift the index with 2, to accommodate the padding
    index += 2
    word, pos = tokens[index]
    prevword, prevpos = tokens[index - 1]
    prevprevword, prevprevpos = tokens[index - 2]
    nextword, nextpos = tokens[index + 1]
    nextnextword, nextnextpos = tokens[index + 2]
    previob = history[-1]
    prevpreviob = history[-2]

    feat_dict = {
        'word': word,
        'lemma': stemmer.stem(word),
        'pos': pos,
        'shape': shape(word),

        'next-word': nextword,
        'next-pos': nextpos,
        'next-lemma': stemmer.stem(nextword),
        'next-shape': shape(nextword),

        'next-next-word': nextnextword,
        'next-next-pos': nextnextpos,
        'next-next-lemma': stemmer.stem(nextnextword),
        'next-next-shape': shape(nextnextword),

        'prev-word': prevword,
        'prev-pos': prevpos,
        'prev-lemma': stemmer.stem(prevword),
        'prev-iob': previob,
        'prev-shape': shape(prevword),

        'prev-prev-word': prevprevword,
        'prev-prev-pos': prevprevpos,
        'prev-prev-lemma': stemmer.stem(prevprevword),
        'prev-prev-iob': prevpreviob,
        'prev-prev-shape': shape(prevprevword),
    }

    return feat_dict


class ScikitLearnChunker(ChunkParserI):
    @classmethod
    def to_dataset(cls, parsed_sentences, feature_detector):
        """
        Transform a list of tagged sentences into a scikit-learn compatible POS dataset
        :param parsed_sentences:
        :param feature_detector:
        :return:
        """
        X, y = [], []
        for parsed in parsed_sentences:
            if len(parsed) == 0:
                continue
            iob_tagged = tree2conlltags(parsed)
            words, tags, iob_tags = zip(*iob_tagged)

            tagged = list(zip(words, tags))

            for index in range(len(iob_tagged)):
                X.append(feature_detector(tagged, index, history=iob_tags[:index]))
                y.append(iob_tags[index])

        return X, y

    @classmethod
    def get_minibatch(cls, parsed_sentences, feature_detector, batch_size=50):
        batch = list(itertools.islice(parsed_sentences, batch_size))
        X, y = cls.to_dataset(batch, feature_detector)
        return X, y

    @classmethod
    def train(cls, parsed_sentences, feature_detector, all_classes, **kwargs):
        X, y = cls.get_minibatch(parsed_sentences, feature_detector, kwargs.get('batch_size', 50))
        vectorizer = DictVectorizer(sparse=False)
        vectorizer.fit(X)

        clf = Perceptron(verbose=10, n_jobs=-1, n_iter=kwargs.get('n_iter', 5))

        while len(X):
            X = vectorizer.transform(X)
            clf.partial_fit(X, y, all_classes)
            X, y = cls.get_minibatch(parsed_sentences, feature_detector, kwargs.get('batch_size', 50))

        clf = Pipeline([
            ('vectorizer', vectorizer),
            ('classifier', clf)
        ])

        return cls(clf, feature_detector)

    def __init__(self, classifier, feature_detector):
        self._classifier = classifier
        self._feature_detector = feature_detector

    def parse(self, tokens):
        """
        Chunk a tagged sentence
        :param tokens: List of words [(w1, t1), (w2, t2), ...]
        :return: chunked sentence: nltk.Tree
        """
        history = []
        iob_tagged_tokens = []
        for index, (word, tag) in enumerate(tokens):
            iob_tag = self._classifier.predict([self._feature_detector(tokens, index, history)])[0]
            history.append(iob_tag)
            iob_tagged_tokens.append((word, tag, iob_tag))
            # print(word, tag, iob_tag)
        return conlltags2tree(iob_tagged_tokens)

    def score(self, parsed_sentences):
        """
        Compute the accuracy of the tagger for a list of test sentences
        :param parsed_sentences: List of parsed sentences: nltk.Tree
        :return: float 0.0 - 1.0
        """
        X_test, y_test = self.__class__.to_dataset(parsed_sentences, self._feature_detector)
        return self._classifier.score(X_test, y_test)

    def extract_entities(self, result):
        entity = {}
        entity_word = ""
        ner_tag = ""
        for idx, tup in enumerate(result):
            if tup[2] != 'O':
                if idx == 0:
                    entity_word += tup[0] + " "
                elif entity_word == "":
                    entity_word += tup[0] + " "
                elif result[idx - 1][2].split('-')[1] == tup[2].split('-')[1]:
                    entity_word += tup[0] + " "
                else:
                    if not entity_word == "":
                        if result[idx - 1][2].split('-')[1] not in entity.keys():
                            entity[result[idx - 1][2].split('-')[1]] = []
                        entity[result[idx - 1][2].split('-')[1]].append(entity_word.strip())
                        entity_word = ""
            elif not entity_word == "":
                if result[idx - 1][2].split('-')[1] not in entity.keys():
                    print(result[idx - 1][2].split('-')[1])
                    entity[result[idx - 1][2].split('-')[1]] = []
                entity[result[idx - 1][2].split('-')[1]].append(entity_word.strip())
                entity_word = ""
        if not entity_word == "":
            if result[len(result) - 1][2].split('-')[1] not in entity.keys():
                entity[result[len(result) - 1][2].split('-')[1]] = []
            entity[result[len(result) - 1][2].split('-')[1]].append(entity_word.strip())
        return entity

    def predict_entity(self, query_str):
        result = self.parse(pos_tag(word_tokenize(query_str)))
        result = tree2conlltags(result)
        return self.extract_entities(result)


def train():
    if not os.path.exists("./ner_train") or len(os.listdir("./ner_train")) <= 0:
        raise Exception("No Training-Data found!")
    reader_train = read_gmb_ner("./ner_train")
    # reader_test = read_gmb_ner("./ner_os_traindata")
    all_classes = ['O', 'B-OS', 'I-OS', 'B-LOC', 'I-LOC', 'B-ISU', 'I-ISU']
    pa_ner = ScikitLearnChunker.train(itertools.islice(reader_train, 50000), feature_detector=ner_features,
                                      all_classes=all_classes, batch_size=50, n_iter=5)
    # accuracy = pa_ner.score(itertools.islice(reader_test, 1000))
    # print("Accuracy:", accuracy)
    return pa_ner


if __name__ == "__main__":
    ner_clf = train()
    while True:
        try:
            ip = str(input("Enter>>"))
            print(ner_clf.predict_entity(ip))
        except Exception as e:
            raise e


