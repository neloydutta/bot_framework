import nltk
import sqlite3
from nltk import word_tokenize

import jbot
import json

# jira = jbot.JIRAClass('http://localhost:8080/', 'neloydutta', 'laddu1993')
jira = None
with open("replies.json", "r") as fp:
    replies = json.load(fp)
with open('os_map.json') as fp:
    os_map = json.load(fp)


def processing_org_query(user_ip, user_intent, entities, context):
    reply = []
    if user_intent == "bot.greet":
        context.set_context(name="greet", intent="bot.greet")
        reply.append(replies["greet"])
    elif user_intent == "teradata.about":
        context.set_context(name="org", intent="teradata.about")
        reply.append(replies["about"])
    elif user_intent == "teradata.location":
        try:
            loc_entity = entities["LOC"]
            for loc in loc_entity:
                try:
                    reply.append(replies["location"][loc])
                except KeyError:
                    reply.append("There is no Teradata establishment located in " + loc)
        except KeyError:
            reply.append(replies["location"]["india"])
        context.set_context(name="org", intent="teradata.location")
    elif user_intent == "teradata.name.why":
        context.set_context(name="org", intent="teradata.name.why")
        reply.append(replies["name"])
    else:
        reply.append("Okay! This is strange!")
        reply.append("Aparently I'm not intelligent enough for answer your question!")
    return reply


def processing_jira_query(user_ip, user_intent, entities, context):
    reply = []
    if user_intent == "jira.find.projects":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        projects = jira.find_projects()
        reply.append("These are all the projects, you are working on:")
        projects = [project['name'] for project in projects]
        projects = ", ".join(projects)
        context.set_context(name="jira", intent="jira.find.projects")
        reply.append(projects)
    elif user_intent == "jira.get.issue":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            if 'message' in issue.keys():
                reply.append(issue['message'])
            else:
                reply.append("Here's what I found about the issue, " + entities['ISU'][0] + "!")
                reply.append(jbot.issue_json_to_str(issue))
            context.set_context(name="jira", intent="jira.get.issue", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                reply += processing_jira_query(user_ip, "jira.get.issue", context.context_value, context)
                context.context_intent = "jira.get.issue"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.get.issue"
                context.handle_flag = True
                reply.append('I\'m afraid, I couldn\'t understand the issue, whose details you want, from the message!')
                reply.append("Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.status":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            if 'message' in issue.keys():
                reply.append(issue['message'])
            else:
                reply.append("Here's the status I found for the issue, " + entities['ISU'][0] + ":")
                reply.append(issue['fields']['status'])
            context.set_context(name="jira", intent="jira.issue.status", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                reply += processing_jira_query(user_ip, "jira.issue.status", context.context_value, context)
                context.context_intent = "jira.issue.status"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.status"
                context.handle_flag = True
                reply.append('I\'m afraid, I couldn\'t understand the issue, whose status you want, from the message!')
                reply.append("Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.reporter":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            # print(issue)
            if 'message' in issue.keys():
                reply.append(issue['message'])
            else:
                # reply.append("Here's the reporter of the issue, " + entities['ISU'][0] + ":")
                reply.append(issue['fields']['reporter'] + " reported the issue " + entities['ISU'][0])
            context.set_context(name="jira", intent="jira.issue.reporter", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                reply += processing_jira_query(user_ip, "jira.issue.reporter", context.context_value, context)
                context.context_intent = "jira.issue.reporter"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.reporter"
                context.handle_flag = True
                reply.append(
                    'I\'m afraid, I couldn\'t understand the issue, whose reporter you want, from the message!')
                reply.append("Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.assignee":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        user_ip_t = word_tokenize(user_ip)
        token_list = ['me', 'mine', 'i', 'I', '\'m', 'am', 'myself', 'my']
        available_list = [token for token in token_list if token in user_ip_t]
        if len(available_list) > 0:
            if jira is None:
                reply.append(
                    "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
                return reply
            issue_list = jira.my_issues()
            # print(issue)
            reply_str = ""
            if len(issue_list) > 0:
                for issue in issue_list:
                    reply_str += jbot.issue_json_to_str(issue) + "\n"
                reply.append("These are the issues I found which are assigned to you:")
                reply.append(reply_str)
            else:
                reply.append("Couldn't find any issue which is assigned to you!")
        else:
            if "ISU" in entities.keys():
                issue = jira.find_issue(entities['ISU'][0])
                # print(issue)
                if 'message' in issue.keys():
                    reply.append(issue['message'])
                else:
                    # reply.append("Here's the reporter of the issue, " + entities['ISU'][0] + ":")
                    reply.append(issue['fields']['assignee'] + " is the assignee of the issue " + entities['ISU'][0])
                context.set_context(name="jira", intent="jira.issue.assignee", value=entities)
            else:
                if context.context_name == "jira" and context.context_value is not None:
                    reply += processing_jira_query(user_ip, "jira.issue.assignee", context.context_value, context)
                    context.context_intent = "jira.issue.assignee"
                else:
                    context.context_name = "jira"
                    context.context_intent = "jira.issue.assignee"
                    context.handle_flag = True
                    reply.append(
                        'I\'m afraid, I couldn\'t understand the issue, whose assignee you want, from the message!')
                    reply.append("Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.watchers":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            # print(issue)
            if 'message' in issue.keys():
                reply.append(issue['message'])
            elif len(issue['watchers']) > 0:
                reply.append("Here are the watchers of the issue, " + entities['ISU'][0] + ":")
                reply.append(", ".join(issue['watchers']))
            else:
                reply.append("It seems, there are no watchers for the issue " + entities['ISU'][0] + "!")
            context.set_context(name="jira", intent="jira.issue.watchers", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                reply += processing_jira_query(user_ip, "jira.issue.watchers", context.context_value, context)
                context.context_intent = "jira.issue.watchers"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.watchers"
                context.handle_flag = True
                reply.append(
                    'I\'m afraid, I couldn\'t understand the issue, whose watchers you want, from the message!')
                reply.append("Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.comments":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            # print(issue)
            if 'message' in issue.keys():
                reply.append(issue['message'])
            elif len(issue['fields']['comments']) > 0:
                reply.append("Here are the comments on the issue, " + entities['ISU'][0] + ":")
                reply.append(", ".join(issue['fields']['comments']))
            else:
                reply.append("It seems, there are no comments on the issue " + entities['ISU'][0] + "!")
            context.set_context(name="jira", intent="jira.issue.comments", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                reply += processing_jira_query(user_ip, "jira.issue.comments", context.context_value, context)
                context.context_intent = "jira.issue.comments"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.comments"
                context.handle_flag = True
                reply.append(
                    'I\'m afraid, I couldn\'t understand the issue, whose comments you want, from the message!')
                reply.append("Reply with the ISSUE-ID again!")
    elif user_intent == "jira.issue.votes":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        if "ISU" in entities.keys():
            issue = jira.find_issue(entities['ISU'][0])
            # print(issue)
            if 'message' in issue.keys():
                reply.append(issue['message'])
            else:
                reply.append("Issue " + entities['ISU'][0] + " has " + str(issue['fields']['votes']) + " votes!")
            context.set_context(name="jira", intent="jira.issue.votes", value=entities)
        else:
            if context.context_name == "jira" and context.context_value is not None:
                reply += processing_jira_query(user_ip, "jira.issue.votes", context.context_value, context)
                context.context_intent = "jira.issue.votes"
            else:
                context.context_name = "jira"
                context.context_intent = "jira.issue.votes"
                context.handle_flag = True
                reply.append('I\'m afraid, I couldn\'t understand the issue, whose votes you want, from the message!')
                reply.append("Reply with the ISSUE-ID again!")
        print(reply)
    elif user_intent == "jira.issue.mine":
        if jira is None:
            reply.append(
                "JIRA Connection isn't available.\nTo connect to JIRA, Enter following command:\nJIRA/ server-url username password")
            return reply
        issue_list = jira.my_issues()
        # print(issue)
        reply_str = ""
        if len(issue_list) > 0:
            for issue in issue_list:
                reply_str += jbot.issue_json_to_str(issue) + "\n\n"
            reply.append("These are the issues I found which are assigned to you:")
            reply.append(reply_str)
        else:
            reply.append("Couldn't find any issue which is assigned to you!")
        context.set_context(name="jira", intent="jira.issue.mine", value=entities)
    else:
        reply.append("Okay! This is strange!")
        reply.append("Aparently, I'm not intelligent enough for answer your question!")
    return reply


def connect():
    try:
        con = sqlite3.connect('DB\slackbot.db')
        c = con.cursor()
    except:
        print('DB Connection ERROR!')
    return con,c


def fetch(sql):
    res = ''
    try:
        con, c = connect()
        c.execute(sql)
        res = c.fetchall()
        con.commit()
    except:
        print("Fetch ERROR!")
    finally:
        con.close()
    return res


def processing_ttu_query(user_ip, user_intent, entities, context):
    reply = []
    if user_intent == "ttu.os.support":
        context.set_context(name="ttu", intent="ttu.os.support")
        if "OS" in entities.keys():
            entity = entities["OS"][0]
        elif "ISU" in entities.keys():
            entity = entities["ISU"][0]
        else:
            return ["I couldn't understand the OS for which you need information!"]
        res = "select * from supportmatrix where osversion like \"%" + entity + "%\""
        for i in os_map.keys():
            for j in os_map[i]:
                if j.lower() in res.lower():
                    res = res.lower().replace(j.lower(), i)
        colheaders = ['os-version', 'release-date', 'comment', 'initial-version', 'latest-version',
                              'advance-scouting', 'sheet']
        result = fetch(res)
        result = list(result)
        r = ""
        for i in result:
            if type(i) is tuple and len(colheaders) != len(i):
                r += ", ".join(i)
            elif type(i) is tuple and len(colheaders) == len(i):
                for j in range(len(colheaders)):
                    r += colheaders[j] + ': ' + i[j]
                    if j < len(colheaders) - 1:
                        r += ', '
            else:
                r += i
            r += ' ;\n'
        if len(result) == 0:
            r = "Couldn't find any relevant information for the os " + entity
        reply.append(r)
    else:
        reply.append("Okay! This is strange!")
        reply.append("Aparently, I'm not intelligent enough for answer your question!")
    return reply
