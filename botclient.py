import bot
import json


def reply(message):
    print("bot: " + message)


if __name__ == "__main__":
    bot_client = bot.Bot()
    with open("replies.json", "r") as fp:
        replies = json.load(fp)
    while True:
        user_ip = str(input("you: "))
        bot_result = bot_client.listen(message=user_ip)
        # print(bot_result)
        user_intent = bot_result["result"]["intent"]
        entities = bot_result["entities"]
        if user_intent == "bot.greet":
            reply(replies["greet"])
        elif user_intent == "teradata.about":
            reply(replies["about"])
        elif user_intent == "teradata.location":
            if entities["LOC"]:
                loc_entity = entities["LOC"]
                for loc in loc_entity:
                    try:
                        reply(replies["location"][loc])
                    except KeyError:
                        reply("There is no Teradata establishment located in " + loc)
            else:
                reply(replies["location"]["india"])
        elif user_intent == "teradata.name.why":
            reply(replies["name"])
        elif user_intent == "ttu.os.support":
            print("TTU OS Support")
        else:
            print("This is strange!")
