import traceback
import time
import bot
import json
import jbot
from slackclient import SlackClient

bottoken = 'xoxb-140978971921-jWB2RGhyhASYlyBVl6x0HbVZ'
bot_name = 'batbot'
bot_id = ''
sc_bot = SlackClient(bottoken)

users_call = sc_bot.api_call('users.list')
if users_call['ok']:
    for user in users_call['members']:
        if user['name'] == bot_name:
            bot_id = user['id']
            # print('BotID: ' + bot_id)
else:
    print("Slack API connection error!")
    exit(1)


def reply(rchannel, message):
    # print("bot: " + message)
    sc_bot.rtm_send_message(rchannel, message)


def read_from_slack():
    ichannel = ""
    rtm_read_data = sc_bot.rtm_read()
    if len(rtm_read_data) > 0:
        for ip in rtm_read_data:
            # print ip
            if 'text' in ip.keys() and 'user' in ip.keys() and ip['user'] != bot_id:
                command = ip['text']
                ichannel = ip['channel']
                print(ichannel, command)
                return ichannel, command
    return None, None

jira = jbot.JIRAClass('http://localhost:8080/', 'adminuser', 'laddu1993')
# jira = None

if __name__ == "__main__":
    bot_client = bot.Bot()
    print(json.dumps(bot_client.scores()))
    with open("replies.json", "r") as fp:
        replies = json.load(fp)
    if not sc_bot.rtm_connect():
        print('Slack API Connection Error!')
        exit(1)
    while True:
        # try:
        # user_ip = str(input("you: "))
        channel = ""
        channel, user_ip = read_from_slack()
        if channel is None or user_ip is None:
            time.sleep(1)
            continue
        if user_ip.lower().startswith("jira/"):
            user_ip = user_ip[5:]
            user_ip = user_ip.strip()
            user_ip = user_ip.split(" ")
            if len(user_ip) == 3:
                try:
                    jira = jbot.JIRAClass(user_ip[0], user_ip[1], user_ip[2])
                    reply(channel, "JIRA Connection is successful!")
                except:
                    reply(channel, "JIRA Connection was not successful!")
            else:
                reply(channel, "To connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            continue
        bot_result = bot_client.listen(message=user_ip)
        # print(bot_result)
        user_intent = bot_result["result"]["intent"]
        entities = bot_result["entities"]
        if user_intent == "bot.greet":
            reply(channel, replies["greet"])
        elif user_intent == "teradata.about":
            reply(channel, replies["about"])
        elif user_intent == "teradata.location":
            try:
                loc_entity = entities["LOC"]
                for loc in loc_entity:
                    try:
                        reply(channel, replies["location"][loc])
                    except KeyError:
                        reply(channel, "There is no Teradata establishment located in " + loc)
            except KeyError:
                reply(channel, replies["location"]["india"])
        elif user_intent == "teradata.name.why":
            reply(channel, replies["name"])
        elif user_intent == "ttu.os.support":
            print("TTU OS Support")
        elif user_intent == "jira.find.projects":
            if jira is None:
                reply(channel,
                    "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
            projects = jira.find_projects()
            reply(channel, "These are all the projects, you are working on:")
            projects = [project['name'] for project in projects]
            projects = ", ".join(projects)
            reply(channel, projects)
        elif user_intent == "jira.get.issue":
            if jira is None:
                reply(channel,
                    "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                if 'message' in issue.keys():
                    reply(channel, issue['message'])
                else:
                    reply(channel, "Here's what I found about the issue, " + entities['ISU'][0] + "!")
                    reply(channel, jbot.issue_json_to_str(issue))
            else:
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose details you want, from the message!')
        elif user_intent == "jira.issue.status":
            if jira is None:
                reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                if 'message' in issue.keys():
                    reply(channel, issue['status'])
                else:
                    reply(channel, "Here's the status I found for the issue, " + entities['ISU'][0] + ":")
                    reply(channel, issue['fields']['status'])
            else:
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose status you want, from the message!')
        elif user_intent == "jira.issue.reporter":
            if jira is None:
                reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                print(issue)
                if 'message' in issue.keys():
                    reply(channel, issue['status'])
                else:
                    # reply(channel, "Here's the reporter of the issue, " + entities['ISU'][0] + ":")
                    reply(channel, issue['fields']['reporter'] + " reported the issue " + entities['ISU'][0])
            else:
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose reporter you want, from the message!')
        elif user_intent == "jira.issue.assignee":
            if jira is None:
                reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                print(issue)
                if 'message' in issue.keys():
                    reply(channel, issue['status'])
                else:
                    # reply(channel, "Here's the reporter of the issue, " + entities['ISU'][0] + ":")
                    reply(channel, issue['fields']['assignee'] + " is the assignee of the issue " + entities['ISU'][0])
            else:
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose assignee you want, from the message!')
        elif user_intent == "jira.issue.watchers":
            if jira is None:
                reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                print(issue)
                if 'message' in issue.keys():
                    reply(channel, issue['status'])
                elif len(issue['watchers']) > 0:
                    reply(channel, "Here are the watchers of the issue, " + entities['ISU'][0] + ":")
                    reply(channel, ", ".join(issue['watchers']))
                else:
                    reply(channel, "It seems, there are no watchers for the issue " + entities['ISU'][0] + "!")
            else:
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose watchers you seek, from the message!')
        elif user_intent == "jira.issue.comments":
            if jira is None:
                reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                # print(issue)
                if 'message' in issue.keys():
                    reply(channel, issue['status'])
                elif len(issue['fields']['comments']) > 0:
                    reply(channel, "Here are the comments on the issue, " + entities['ISU'][0] + ":")
                    reply(channel, ", ".join(issue['fields']['comments']))
                else:
                    reply(channel, "It seems, there are no comments on the issue " + entities['ISU'][0] + "!")
            else:
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose watchers you seek, from the message!')
        elif user_intent == "jira.issue.votes":
            if jira is None:
                reply(channel,
                    "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                continue
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                # print(issue)
                if 'message' in issue.keys():
                    reply(channel, issue['status'])
                else:
                    reply(channel, "Issue " + entities['ISU'][0] + " has " + str(issue['fields']['votes']) + " votes!")
            else:
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose vote-count you seek, from the message!')
        else:
            print("Okay! This is strange!")
        # except:
        #     traceback.print_exc()
        time.sleep(1)
