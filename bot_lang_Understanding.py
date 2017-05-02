import intent
import ner


class BotLU:
    def __init__(self):
        self.intent_classifier = intent.train()
        self.ner_classifier = ner.train()

    def process(self, query):
        it = self.intent_classifier.predict(query_str=query)
        en = self.ner_classifier.predict_entity(query_str=query)
        return {
            "result": it,
            "entities": en
        }

    def get_scores(self):
        ner_score = self.ner_classifier.score()
        intent_score = self.intent_classifier.score()
        return {
            'Entity Recognition': ner_score,
            'Intent Detection': intent_score
        }


if __name__ == "__main__":
    bot_lu = BotLU()
    while True:
        ip = str(input("Enter>> "))
        print(bot_lu.process(ip))
