import bot
import json
import jbot

def reply(message):
    print("bot: " + message)


jira = jbot.JIRAClass('http://localhost:8080/', 'adminuser', 'laddu1993')

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
            try:
                loc_entity = entities["LOC"]
                for loc in loc_entity:
                    try:
                        reply(replies["location"][loc])
                    except KeyError:
                        reply("There is no Teradata establishment located in " + loc)
            except KeyError:
                reply(replies["location"]["india"])
        elif user_intent == "teradata.name.why":
            reply(replies["name"])
        elif user_intent == "ttu.os.support":
            print("TTU OS Support")
        elif user_intent == "jira.find.projects":
            projects = jira.find_projects()
            reply("These are all the projects, you are working on:")
            projects = [project['name'] for project in projects]
            projects = ", ".join(projects)
            reply(projects)
        elif user_intent == "jira.get.issue":
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                if 'message' in issue.keys():
                    reply(issue['message'])
                else:
                    reply(json.dumps(issue))
            else:
                reply('I\'m afraid, I couldn\'t inderstand the issue, whose details you want, from the message!')
        else:
            print("This is strange!")
