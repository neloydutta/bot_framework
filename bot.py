import bot_lang_Understanding
import json
import generating_traindata


class Bot:
    def __init__(self):
        self.bot_lu = bot_lang_Understanding.BotLU()

    def listen(self, message):
        result = self.bot_lu.process(query=message)
        # print(result)
        with open("query-received.txt", "a") as fp:
            json.dump(result, fp)
            fp.write("\n")
        return result

    def bot_reply(self, result):
        print("User Intent for the message was: " + result['result']['intent'])
        if result['entities'].keys():
            print("Entities: ", )
            for entity_type in result['entities']:
                print("\n" + entity_type, )
                for entity in result['entities'][entity_type]:
                    print(entity + ", ", )


def train_for_user_samples():
    with open("query-received.txt", "r") as fp:
        queries = fp.read()
    queries = queries.strip().split("\n")
    with open("data.json", "r") as fp:
        data = json.load(fp)
    for query in queries:
        query_json = json.loads(query)
        print(query_json["result"]["query_string"] + " => " + query_json["result"]["intent"])
        ip = str(input("Approve? (y/n) "))
        if ip == "y" or ip == "Y":
            if query_json["result"]["intent"] in data.keys():
                data[query_json["result"]["intent"]].append(query_json["result"]["query_string"])
            else:
                data['endcount'][query_json["result"]["intent"]] = 0
                data[query_json["result"]["intent"]] = []
                data[query_json["result"]["intent"]].append(query_json["result"]["query_string"])
    with open("data.json", "w") as fp:
        json.dump(data, fp)
    generating_traindata.generate()
    return Bot()


if __name__ == "__main__":
    bot = Bot()
    while True:
        msg = str(input("Enter: "))
        print(bot.listen(message=msg))
    train_for_user_samples()
