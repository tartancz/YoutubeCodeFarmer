
import requests



class Discord:
    def __init__(self,
                 channel_id: int,
                 bot_token: str
                 ):
        self.channel_id = channel_id
        self.bot_token = bot_token


    def send(self, message: str) -> None:
        requests.post(
            f"https://discord.com/api/channels/{self.channel_id}/messages",
            headers={
                "Authorization": f"Bot {self.bot_token}"
            },
            data={"content": message}
        )