from datetime import timedelta, datetime
from typing import TYPE_CHECKING

import requests

from database.errors import RowDontExistException
from database.models import TokenModel
from redeemer.errors import WoltAuthFailedException, WoltNotAuthorizedException
from redeemer.redeemer import Redeemer, CodeState

if TYPE_CHECKING:
    from requests import Response

ACCESS_TOKEN_URL = 'https://authentication.wolt.com/v1/wauth2/access_token'
REDEEM_DISCOUNT_URL = 'https://restaurant-api.wolt.com/v2/credit_codes/consume'




class Wolt(Redeemer):
    def __init__(self, token_model: TokenModel):
        self.token_model = token_model
        try:
            self.actual_token = self.token_model.get_latest_token()
        except RowDontExistException:
            print("token was not found in database.")
            refresh_token = input("please insert refresh token:")
            self._get_new_token(refresh_token)

    def _get_new_token(self, refresh_token: str):
        """
        will make request for new token to Wolt, then will save response in database and set self.actual_token
        :param refresh_token: refresh token for Wolt
        """

        response = self.make_request_to_new_token(refresh_token)
        response_json = response.json()
        token_id = self.token_model.insert(
            refresh_token=response_json['refresh_token'],
            token=response_json['access_token'],
            expires_in=response_json['expires_in']

        )
        self.actual_token = self.token_model.get_by_id(token_id)

    @staticmethod
    def make_request_to_new_token(refresh_token: str) -> 'response':
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        response = requests.post(ACCESS_TOKEN_URL, data=data)
        if response.status_code != 200:
            raise WoltAuthFailedException(
                f"auth failed with status code: {response.status_code} and text: {response.text}")
        return response

    def get_new_token(self):
        self._get_new_token(self.actual_token.refresh_token)

    def redeem_code(self, code: str) -> CodeState:
        if self.is_token_expired():
            self.get_new_token()

        response = self._make_request_to_code_redeem(code)
        print(response.json())
        print(response.status_code)
        if response.status_code == 401:
            raise WoltNotAuthorizedException("Wolt is not authorized, use get_new_token function.")
        elif response.status_code == 404:
            return CodeState.BAD_CODE
        elif response.status_code == 403:
            resp = response.json()
            if resp.get("error_code") == 482:
                return CodeState.ALREADY_TAKEN
            return CodeState.EXPIRED
        elif response.status_code == 429:
            return CodeState.TOO_MANY_REQUESTS
        elif response.status_code == 201:
            return CodeState.SUCCESSFULLY_REDEEM


    def _make_request_to_code_redeem(self, code: str) -> 'Response':
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f'Bearer {self.actual_token.token}',
        }
        data = {
            "code": code
        }
        return requests.post(REDEEM_DISCOUNT_URL, headers=headers, json=data)

    def is_token_expired(self) -> bool:
        return self.actual_token.created + timedelta(seconds=self.actual_token.expires_in - 10) <= datetime.utcnow() # - 10 is buffer for delay
