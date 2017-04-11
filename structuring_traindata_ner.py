from nltk import pos_tag
from nltk import word_tokenize
with open("sentences.txt") as fp:
    raw_sentences = fp.read()

raw_sentences = raw_sentences.strip().split('\n')

with open("traindata_os_ner.txt", "w") as fp:
    for sent in raw_sentences:
        sent = word_tokenize(sent)
        pos_tagged_sent = pos_tag(sent)
        for word, tag in pos_tagged_sent:
            print(word, tag)
            fp.write(word + " " + tag + "\n")
        fp.write("\n\n")