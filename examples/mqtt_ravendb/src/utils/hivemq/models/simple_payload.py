class SimplePayload:
    def __init__(self, payload: str):
        self.payload: str = payload

    def __str__(self):
        return f"SimplePayload(Message='{self.payload}')"

    def __repr__(self):
        return self.__str__()
