import traceback
import time
import bot
import json
import jbot
import query_processing
import bottoken
import random
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

jira = jbot.JIRAClass(bottoken.serverURL, bottoken.username, bottoken.password)
# jira = None
context = ContextClass()


def processing_reply(user_ip, user_intent, entities, channel):
    if user_intent.startswith("jira"):
        ret = query_processing.processing_jira_query(user_ip=user_ip, user_intent=user_intent, entities=entities, context=context)
        # ret = ["No JIRA, " + user_intent + " :: " + json.dumps(entities)]
    elif user_intent.startswith("teradata"):
        ret = query_processing.processing_org_query(user_ip=user_ip, user_intent=user_intent, entities=entities, context=context)
    elif user_intent.startswith("ttu"):
        ret = query_processing.processing_ttu_query(user_ip=user_ip, user_intent=user_intent, entities=entities, context=context)
    elif user_intent == "bot.greet":
        reply(channel, replies["greet"])
        return
    else:
        idx = random.randrange(start=0, stop=len(replies["none"]))
        reply(channel, replies["none"][idx])
        return
    for msg in ret:
        reply(channel, msg)


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
                print("Context => Intent: " + ret_list[0] + ", Entity: " + json.dumps(ret_list[1]))
                processing_reply(user_ip, ret_list[0], ret_list[1], channel)
            # else:
            #     reply(channel, ret_list[0])
            # continue
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
