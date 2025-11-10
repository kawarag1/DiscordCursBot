class CreatePaymentLink():

    def __init__(self, bot_id):
        self.bot_id = bot_id

    def create_link(self):
        return (f"https://discord.com/oauth2/authorize?client_id={self.bot_id}&permissions=8&scope=bot%20applications.commands")