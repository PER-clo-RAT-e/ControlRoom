class BaseBot:
    def __init__(self, token):
        self.token = token

    def _logic(self):
        pass

    def send_message(self, text):
        pass

    def process_message(self, message):
        pass