from app_layouts import friends_layout
from Modules import DBManager
import requests
from Modules import NSOApi
import PySimpleGUI as sg


def create_new_friend(friend):
    return [[sg.Text(friend["name"]), sg.Text(friend["presence"]["state"], key=("-pre-", friend["id"]))]]


class UIManager(DBManager.DBManager, NSOApi.NSO):
    def __init__(self, db_name):
        # initializer for the DBManager parent class
        super().__init__(db_name=db_name)

        # initializers for the NSO class, since they don't get initialized
        self.Session = requests.Session()

        # declare variables for different tokens
        self.clientID = "71b963c1b7b6d119"
        self.userAgentVersion = "2.5.0"
        self.request_id = None
        self.access_token = None
        self.webApiServerCredential = None
        self.session_token = None

        # the only initializer for the UIManager class
        self.__friends_layout = friends_layout.layout

    async def run_friends_layout(self):

        window = sg.Window("Friends List", self.__friends_layout)

        friends = await self.get_friends_list()

        print(friends)

        while True:
            for friend in friends["result"]["friends"]:
                print(friend["id"])
                res = self.cursor.execute("SELECT 1 FROM Friends WHERE Friend_UID = ?", (friend["id"],))
                if res.fetchone() != 1:
                    self.cursor.execute("INSERT INTO Friends (Username,Friend_UID) VALUES (?,?)", (friend["name"],
                                                                                                   friend["id"],))
                    new_friend = create_new_friend(friend)
                    window.extend_layout(window["-Column-"], new_friend)
                    self.conn.commit()

                print(friend)

            event, values = window.read(timeout=5000, timeout_key="__TIMEOUT__")

            if event in ("Cancel", "Exit", None):
                break
            if event == "-RELOAD-":
                friends = await self.get_friends_list()
                print(friends)
                # for friend in friends["result"]["friends"]:
                #     new_layout = [[sg.Text(friend["name"]), sg.Text(friend["presence"]["state"] )]]
                #     window.extend_layout(window["-Column-"], new_layout)
            if event == "-ID-":
                window[("-pre-", 4900762031226880)].update(value="LOL")
            if event == "__TIMEOUT__":
                friends = await self.get_friends_list()
                for friend in friends["result"]["friends"]:
                    new_friend = create_new_friend(friend)
                    window.extend_layout(window["-Column-"], new_friend)
