# import botclient

class ContextClass:
    def __init__(self):
        self.context_name = None
        self.context_value = None
        self.context_intent = None
        self.handle_flag = False

    def set_context(self, name, intent, value=None):
        if self.context_name != name:
            self.context_value = None
        self.context_name = name
        if value is not None:
            self.context_value = value
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
        if "ISU" in entity.keys() or "OS":
            # print("ISU")
            return [intent, entity]
        else:
            # print("NO ISU")
            return ["I'm afraid that, I'm not intelligent enough to answer your question!"]
