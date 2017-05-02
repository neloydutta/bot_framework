import traceback
import bot
import json
import jbot


def reply(message):
    print("bot: " + message)


# jira = jbot.JIRAClass('http://localhost:8080/', 'adminuser', 'laddu1993')
jira = None

if __name__ == "__main__":
    bot_client = bot.Bot()
    print(json.dumps(bot_client.scores()))
    with open("replies.json", "r") as fp:
        replies = json.load(fp)
    while True:
        try:
            user_ip = str(input("you: "))
            if user_ip.lower().startswith("jira/"):
                user_ip = user_ip[5:]
                user_ip = user_ip.strip()
                user_ip = user_ip.split(" ")
                if len(user_ip) == 3:
                    try:
                        jira = jbot.JIRAClass(user_ip[0], user_ip[1], user_ip[2])
                        reply("JIRA Connection is successful!")
                    except:
                        reply("JIRA Connection was not successful!")
                else:
                    reply("To connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
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
                if jira is None:
                    reply(
                        "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                    continue
                projects = jira.find_projects()
                reply("These are all the projects, you are working on:")
                projects = [project['name'] for project in projects]
                projects = ", ".join(projects)
                reply(projects)
            elif user_intent == "jira.get.issue":
                if jira is None:
                    reply(
                        "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                    continue
                if "ISU" in entities.keys():
                    issue = jira.find_issue(entities['ISU'][0])
                    if 'message' in issue.keys():
                        reply(issue['message'])
                    else:
                        reply("Here's what I found about the issue, " + entities['ISU'][0] + "!")
                        reply(jbot.issue_json_to_str(issue))
                else:
                    reply('I\'m afraid, I couldn\'t understand the issue, whose details you want, from the message!')
            elif user_intent == "jira.issue.status":
                if jira is None:
                    reply("JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                    continue
                if "ISU" in entities.keys():
                    issue = jira.find_issue(entities['ISU'][0])
                    if 'message' in issue.keys():
                        reply(issue['status'])
                    else:
                        reply("Here's the status I found for the issue, " + entities['ISU'][0] + ":")
                        reply(issue['fields']['status'])
                else:
                    reply('I\'m afraid, I couldn\'t understand the issue, whose status you want, from the message!')
            elif user_intent == "jira.issue.reporter":
                if jira is None:
                    reply("JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                    continue
                if "ISU" in entities.keys():
                    issue = jira.find_issue(entities['ISU'][0])
                    print(issue)
                    if 'message' in issue.keys():
                        reply(issue['status'])
                    else:
                        # reply("Here's the reporter of the issue, " + entities['ISU'][0] + ":")
                        reply(issue['fields']['reporter'] + " reported the issue " + entities['ISU'][0])
                else:
                    reply('I\'m afraid, I couldn\'t understand the issue, whose reporter you want, from the message!')
            elif user_intent == "jira.issue.assignee":
                if jira is None:
                    reply("JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                    continue
                if "ISU" in entities.keys():
                    issue = jira.find_issue(entities['ISU'][0])
                    print(issue)
                    if 'message' in issue.keys():
                        reply(issue['status'])
                    else:
                        # reply("Here's the reporter of the issue, " + entities['ISU'][0] + ":")
                        reply(issue['fields']['assignee'] + " is the assignee of the issue " + entities['ISU'][0])
                else:
                    reply('I\'m afraid, I couldn\'t understand the issue, whose assignee you want, from the message!')
            elif user_intent == "jira.issue.watchers":
                if jira is None:
                    reply("JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                    continue
                if "ISU" in entities.keys():
                    issue = jira.find_issue(entities['ISU'][0])
                    print(issue)
                    if 'message' in issue.keys():
                        reply(issue['status'])
                    elif len(issue['watchers']) > 0:
                        reply("Here are the watchers of the issue, " + entities['ISU'][0] + ":")
                        reply(", ".join(issue['watchers']))
                    else:
                        reply("It seems, there are no watchers for the issue " + entities['ISU'][0] + "!")
                else:
                    reply('I\'m afraid, I couldn\'t understand the issue, whose watchers you seek, from the message!')
            elif user_intent == "jira.issue.comments":
                if jira is None:
                    reply("JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                    continue
                if "ISU" in entities.keys():
                    issue = jira.find_issue(entities['ISU'][0])
                    # print(issue)
                    if 'message' in issue.keys():
                        reply(issue['status'])
                    elif len(issue['fields']['comments']) > 0:
                        reply("Here are the comments on the issue, " + entities['ISU'][0] + ":")
                        reply(", ".join(issue['fields']['comments']))
                    else:
                        reply("It seems, there are no comments on the issue " + entities['ISU'][0] + "!")
                else:
                    reply('I\'m afraid, I couldn\'t understand the issue, whose watchers you seek, from the message!')
            elif user_intent == "jira.issue.votes":
                if jira is None:
                    reply(
                        "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                    continue
                if "ISU" in entities.keys():
                    issue = jira.find_issue(entities['ISU'][0])
                    # print(issue)
                    if 'message' in issue.keys():
                        reply(issue['status'])
                    else:
                        reply("Issue " + entities['ISU'][0] + " has " + str(issue['fields']['votes']) + " votes!")
                else:
                    reply('I\'m afraid, I couldn\'t understand the issue, whose vote-count you seek, from the message!')
            else:
                print("Okay! This is strange!")
        except:
            traceback.print_exc()
