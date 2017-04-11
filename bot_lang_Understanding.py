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


if __name__ == "__main__":
    bot_lu = BotLU()
    while True:
        ip = str(input("Enter>> "))
        print(bot_lu.process(ip))