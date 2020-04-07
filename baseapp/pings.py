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


DEFAULT_PINGS = [
    PingItem("de_2", "싸인을보내"),
    PingItem("de_3", "소용이없네 \n 헤이헤이"),
    PingItem("de_4", "cause Im lost in"),
    PingItem("de_5", "sleep"),
    PingItem("de_6", "The feeling wont let me"),
    PingItem("de_7", "Lit up heaven in me"),
    PingItem("de_8", "Something in you"),
    PingItem("de_9", "안녕하세요 추워"),
    PingItem("de_10", "넘넘추워 아 더워"),
    PingItem("de_11", "안녕하세요 찌리찌리찌리 더워"),
    PingItem("de_12", "안녕하세요 아 더워"),
    PingItem("de_13", "이대로 사라져버리면안되염이대로 사라져버리면안되염이대로 사라져버리면안되염"),
]