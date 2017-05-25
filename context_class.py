# import botclient


class ContextClass:
    def __init__(self):
        self.context_name = None
        self.context_value = None
        self.context_value_jira = None
        self.context_value_ttu = None
        self.context_value_org = None
        self.context_intent = None
        self.handle_flag = False

    def set_context(self, name, intent, value=None):
        if self.context_name != name:
            self.context_value = None
        self.context_name = name
        if value is not None:
            if intent.startswith("jira"):
                self.context_value_jira = value
            elif intent.startswith("ttu"):
                self.context_value_ttu = value
            elif intent.startswith("teradata"):
                self.context_value_org = value
        self.context_intent = intent

    def get_context(self):
        if self.context_intent is not None and self.context_name is not None:
            return self.context_name, self.context_value, self.context_intent
        else:
            return None, None, None

    def handle_context(self, user_ip, bot_client):
        entity = bot_client.bot_lu.ner_classifier.predict_entity(query_str=user_ip)
        intent = self.context_intent
        self.context_value = None
        self.context_intent = None
        self.handle_flag = False
        if "ISU" in entity.keys() and intent.startswith("jira"):
            # print("ISU")
            return [intent, entity]
        elif "OS" in entity.keys() and intent.startswith("ttu"):
            return [intent, entity]
        else:
            # print("NO ISU")
            return ["I'm afraid that, I'm not intelligent enough to answer your question!"]
