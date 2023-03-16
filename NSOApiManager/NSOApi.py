import requests
from TokenGetter import getToken


class NSO:
    def __init__(self):
        self.__Session = requests.Session()

        # declare variables for different tokens
        self.__clientID = "71b963c1b7b6d119"
        self.__userAgentVersion = "2.5.0"
        self.__request_id = None
        self.__access_token = None
        self.__webApiServerCredential = None
        self.__session_token = None

    async def login_process(self) -> None:
        # check if there is a previous __session_token that's been generated
        try:
            with open("session_token.txt", "r") as f:
                lines = f.readlines()
                self.__session_token = lines[0]
        except:
            print("session_token.txt file was not found, going to generate.")

        # check if __session_token is valid, otherwise generate a new one
        if self.__session_token:
            if await self.__check_session_token_valid() != 200:
                print("Token expired, need to generate a new one.")
                await self.__get___session_token()
        else:
            await self.__get___session_token()

        # continue the login process to nintendo servers
        await self.__get___access_token()
        await self.login()
        print("API is ready to use.")

    async def __get___session_token(self) -> None:
        self.__session_token = getToken.Login().session_token
        with open("session_token.txt", "w") as f:
            f.write(self.__session_token)
        print("Session token generated successfully.")

    async def __check_session_token_valid(self) -> requests.status_codes:

        url = "https://accounts.nintendo.com/connect/1.0.0/api/token"

        headers = {
            "Headers Host": "accounts.nintendo.com",
            "Content-Type": "application/json; charset=utf-8",
            "Connection": "keep-alive",
            "User-Agent": "OnlineLounge/1.0.4 NASDKAPI iOS",
            "Accept": "application/json",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip, deflate"
        }
        payload = {
            "client_id": self.__clientID,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
            "session_token": self.__session_token
        }
        return self.__Session.post(url=url, headers=headers, json=payload).status_code

    async def __get___access_token(self) -> None:
        url = "https://accounts.nintendo.com/connect/1.0.0/api/token"

        headers = {
            "Headers Host": "accounts.nintendo.com",
            "Content-Type": "application/json; charset=utf-8",
            "Connection": "keep-alive",
            "User-Agent": "OnlineLounge/1.0.4 NASDKAPI iOS",
            "Accept": "application/json",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip, deflate"
        }

        payload = {
            "client_id": self.__clientID,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
            "session_token": self.__session_token
        }

        response = self.__Session.post(url=url, json=payload, headers=headers).json()
        self.__access_token = response["access_token"]
        print("Access token gotten successfully.")

    async def __get_user_info(self) -> tuple:
        url = "https://accounts.nintendo.com/2.0.0/users/me"
        headers = {
            "Host": "api.accounts.nintendo.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "User-Agent": "OnlineLounge / 1.0.4 NASDKAPI iOS",
            "Accept-Language": "en-US",
            "Authorization": "Bearer " + self.__access_token,
            "Accept-Encoding": "gzip,deflate"
        }

        response = self.__Session.get(url=url, headers=headers).json()
        print("User info gotten successfully.")
        return response["country"], response["birthday"], response["language"]

    async def __get_f_key(self) -> tuple:
        url = "https://api.imink.app/f"

        payload = {
            "token": self.__access_token,
            "hash_method": 1
        }

        response = self.__Session.post(url=url, json=payload).json()
        self.__request_id = response["request_id"]
        print("f key gotten successfully.")
        return response["f"], response["timestamp"], response["request_id"]

    async def login(self) -> None:
        url = "https://api-lp1.znc.srv.nintendo.net/v3/Account/Login"

        headers = {
            # "Accept": "application/json",
            "User-Agent": f"com.nintendo.znca/{self.__userAgentVersion} (Android/8.0.0)",
            "X-Platform": "Android",
            "X-ProductVersion": self.__userAgentVersion,
            "Content-Type": "application/json;charset=utf-8"
        }
        user_data = await self.__get_user_info()
        f_key_data = await self.__get_f_key()

        payload = {
            "parameter": {
                "language": user_data[2],
                "naBirthday": user_data[1],
                "naCountry": user_data[0],
                "naIdToken": self.__access_token,
                "requestId": f_key_data[2],
                "timestamp": f_key_data[1],
                "f": f_key_data[0]
            }
        }

        response = self.__Session.post(url=url, json=payload, headers=headers).json()
        self.__webApiServerCredential = response["result"]["webApiServerCredential"]["accessToken"]
        print("webApiServerCredential gotten successfully.")

    async def get_friends_list(self):

        url = "https://api-lp1.znc.srv.nintendo.net/v3/Friend/List"

        headers = {
            "User-Agent": f"com.nintendo.znca/{self.__userAgentVersion} (Android/8.0.0)",
            "X-Platform": "Android",
            "X-ProductVersion": self.__userAgentVersion,
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer ' + self.__webApiServerCredential,
            "requestId": self.__request_id
        }

        response = self.__Session.post(url=url, headers=headers)
        # check if WebApiServerCredential has expired, if it has, generate a new one
        if response.status_code == 401:
            print("WebApiServerCredential expired, generating a new one")
            await self.__get___access_token()
            await self.login()
            return await self.get_friends_list()
        else:
            print("Friends list gotten successfully.")
            return response.json()
