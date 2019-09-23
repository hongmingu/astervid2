class PingItem:

    def __init__(self, ping_id: str, ping_text: str) -> None:
        self._ping_id = ping_id
        self._ping_text = ping_text

    @property
    def ping_id(self):
        return self._ping_id

    @property
    def ping_text(self):
        return self._ping_text

    @ping_id.setter
    def ping_id(self, ping_id: str):
        self._ping_id = ping_id

    @ping_text.setter
    def ping_text(self, ping_text: str):
        self._ping_text = ping_text


PINGS = [
    PingItem("2", "싸인을보내"),
    PingItem("3", "소용이없네 \n 헤이헤이"),
    PingItem("4", "cause Im lost in"),
    PingItem("5", "sleep"),
    PingItem("6", "The feeling wont let me"),
    PingItem("7", "Lit up heaven in me"),
    PingItem("8", "Something in you"),
    PingItem("9", "안녕하세요 추워"),
    PingItem("10", "넘넘추워 아 더워"),
    PingItem("11", "안녕하세요 찌리찌리찌리 더워"),
    PingItem("12", "안녕하세요 아 더워"),
    PingItem("13", "이대로 사라져버리면안되염이대로 사라져버리면안되염이대로 사라져버리면안되염"),
]