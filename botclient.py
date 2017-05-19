import traceback
import time
import bot
import json
import jbot
import bottoken
from context_class import ContextClass
from slackclient import SlackClient
from nltk.tokenize import word_tokenize

bottkn = bottoken.bottoken
bot_name = 'batbot'
bot_id = ''
sc_bot = SlackClient(bottkn)

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

jira = jbot.JIRAClass('http://localhost:8080/', 'neloydutta', 'laddu1993')
# jira = None
context = ContextClass()


def processing_reply(user_ip, user_intent, entities, channel):
    if user_intent == "bot.greet":
        context.set_context(name="greet", intent="bot.greet")
        reply(channel, replies["greet"])
    elif user_intent == "teradata.about":
        context.set_context(name="org", intent="teradata.about")
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
        context.set_context(name="org", intent="teradata.location")
    elif user_intent == "teradata.name.why":
        context.set_context(name="org", intent="teradata.name.why")
        reply(channel, replies["name"])
    elif user_intent == "ttu.os.support":
        context.set_context(name="ttu", intent="ttu.os.support")
        print("TTU OS Support")
    elif user_intent == "jira.find.projects":
        if jira is None:
            reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        projects = jira.find_projects()
        reply(channel, "These are all the projects, you are working on:")
        projects = [project['name'] for project in projects]
        projects = ", ".join(projects)
        context.set_context(name="jira", intent="jira.find.projects")
        reply(channel, projects)
    elif user_intent == "jira.get.issue":
        if jira is None:
            reply(channel,
                  "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            if 'message' in issue.keys():
                reply(channel, issue['message'])
            else:
                reply(channel, "Here's what I found about the issue, " + entities['ISU'][0] + "!")
                reply(channel, jbot.issue_json_to_str(issue))
            context.set_context(name="jira", intent="jira.get.issue", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                processing_reply(user_ip, "jira.get.issue", context.context_value, channel)
                context.context_intent = "jira.get.issue"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.get.issue"
                context.handle_flag = True
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose details you want, from the message!')
                reply(channel, "Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.status":
        if jira is None:
            reply(channel,
                  "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            if 'message' in issue.keys():
                reply(channel, issue['message'])
            else:
                reply(channel, "Here's the status I found for the issue, " + entities['ISU'][0] + ":")
                reply(channel, issue['fields']['status'])
            context.set_context(name="jira", intent="jira.issue.status", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                processing_reply(user_ip, "jira.issue.status", context.context_value, channel)
                context.context_intent = "jira.issue.status"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.status"
                context.handle_flag = True
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose status you want, from the message!')
                reply(channel, "Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.reporter":
        if jira is None:
            reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            # print(issue)
            if 'message' in issue.keys():
                reply(channel, issue['message'])
            else:
                # reply(channel, "Here's the reporter of the issue, " + entities['ISU'][0] + ":")
                reply(channel, issue['fields']['reporter'] + " reported the issue " + entities['ISU'][0])
            context.set_context(name="jira", intent="jira.issue.reporter", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                processing_reply(user_ip, "jira.issue.reporter", context.context_value, channel)
                context.context_intent = "jira.issue.reporter"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.reporter"
                context.handle_flag = True
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose reporter you want, from the message!')
                reply(channel, "Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.assignee":
        if jira is None:
            reply(channel,
                  "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        user_ip_t = word_tokenize(user_ip)
        token_list = ['me', 'mine', 'i', 'I', '\'m', 'am', 'myself', 'my']
        available_list = [token for token in token_list if token in user_ip_t]
        if len(available_list) > 0:
            if jira is None:
                reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                return
            issue_list = jira.my_issues()
            # print(issue)
            reply_str = ""
            if len(issue_list) > 0:
                for issue in issue_list:
                    reply_str += jbot.issue_json_to_str(issue) + "\n"
                reply(channel, "These are the issues I found which are assigned to you:")
                reply(channel, reply_str)
            else:
                reply(channel, "Couldn't find any issue which is assigned to you!")
        else:
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                # print(issue)
                if 'message' in issue.keys():
                    reply(channel, issue['message'])
                else:
                    # reply(channel, "Here's the reporter of the issue, " + entities['ISU'][0] + ":")
                    reply(channel, issue['fields']['assignee'] + " is the assignee of the issue " + entities['ISU'][0])
                context.set_context(name="jira", intent="jira.issue.assignee", value=entities)
            else:
                if context.context_name == "jira" and context.context_value is not None:
                    processing_reply(user_ip, "jira.issue.assignee", context.context_value, channel)
                    context.context_intent = "jira.issue.assignee"
                else:
                    context.context_name = "jira"
                    context.context_intent = "jira.issue.assignee"
                    context.handle_flag = True
                    reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose assignee you want, from the message!')
                    reply(channel, "Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.watchers":
        if jira is None:
            reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            # print(issue)
            if 'message' in issue.keys():
                reply(channel, issue['message'])
            elif len(issue['watchers']) > 0:
                reply(channel, "Here are the watchers of the issue, " + entities['ISU'][0] + ":")
                reply(channel, ", ".join(issue['watchers']))
            else:
                reply(channel, "It seems, there are no watchers for the issue " + entities['ISU'][0] + "!")
            context.set_context(name="jira", intent="jira.issue.watchers", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                processing_reply(user_ip, "jira.issue.watchers", context.context_value, channel)
                context.context_intent = "jira.issue.watchers"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.watchers"
                context.handle_flag = True
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose watchers you want, from the message!')
                reply(channel, "Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.comments":
        if jira is None:
            reply(channel, "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            # print(issue)
            if 'message' in issue.keys():
                reply(channel, issue['message'])
            elif len(issue['fields']['comments']) > 0:
                reply(channel, "Here are the comments on the issue, " + entities['ISU'][0] + ":")
                reply(channel, ", ".join(issue['fields']['comments']))
            else:
                reply(channel, "It seems, there are no comments on the issue " + entities['ISU'][0] + "!")
            context.set_context(name="jira", intent="jira.issue.comments", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                processing_reply(user_ip, "jira.issue.comments", context.context_value, channel)
                context.context_intent = "jira.issue.comments"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.comments"
                context.handle_flag = True
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose comments you want, from the message!')
                reply(channel, "Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.votes":
        if jira is None:
            reply(channel,
                  "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            # print(issue)
            if 'message' in issue.keys():
                reply(channel, issue['message'])
            else:
                reply(channel, "Issue " + entities['ISU'][0] + " has " + str(issue['fields']['votes']) + " votes!")
            context.set_context(name="jira", intent="jira.issue.votes", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                processing_reply(user_ip, "jira.issue.votes", context.context_value, channel)
                context.context_intent = "jira.issue.votes"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.votes"
                context.handle_flag = True
                reply(channel, 'I\'m afraid, I couldn\'t understand the issue, whose votes you want, from the message!')
                reply(channel, "Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.mine":
        if jira is None:
            reply(channel,
                  "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return
        issue_list = jira.my_issues()
        # print(issue)
        reply_str = ""
        if len(issue_list) > 0:
            for issue in issue_list:
                reply_str += jbot.issue_json_to_str(issue) + "\n\n"
            reply(channel, "These are the issues I found which are assigned to you:")
            reply(channel, reply_str)
        else:
            reply(channel, "Couldn't find any issue which is assigned to you!")
        context.set_context(name="jira", intent="jira.issue.mine", value=entities)
    else:
        reply(channel, "Okay! This is strange!")
        reply(channel, "Aparently I'm not intelligent enough for answer your question!")


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
        if context.handle_flag is True:
            ret_list = context.handle_context(user_ip, bot_client)
            if len(ret_list) == 2:
                processing_reply(user_ip, ret_list[0], ret_list[1], channel)
            else:
                reply(channel, ret_list[0])
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
        print(bot_result)
        user_intent = bot_result["result"]["intent"]
        entities = bot_result["entities"]
        processing_reply(user_ip, user_intent, entities, channel)
        # except:
        #     traceback.print_exc()
        time.sleep(1)
