from redeemer import Redeemer, CodeState

class Wolt(Redeemer):
    def __init__(self, token_model):
        self.token_model = token_model

    def redeem_code(self, code: str) -> CodeState:
        if code.lower() == "ag100v5cz25j":
            return CodeState.SUCCESSFULLY_REDEEM
        return CodeState.BAD_CODE