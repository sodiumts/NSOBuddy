from app_layouts import friends_layout
from Modules import DBManager
import requests
from Modules import NSOApi
import PySimpleGUI as sg


def create_new_friend(username, presence, iss):
    # makes a new layout to append to main friends list column
    return [[sg.Text(username, size=(10, 1)), sg.Text(presence, key=("-pre-", iss))]]


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
        # extending the main layout with friends stored in Friendslist.db
        self.extend_friend_column(1, window, True)
        # calls nso api calling object to receive friends list of the current user
        friends = await self.get_friends_list()

        # initializes the layout
        self.extend_friend_column(friends, window, False)
        while True:
            event, values = window.read(timeout=5000, timeout_key="__TIMEOUT__")

            if event in ("Cancel", "Exit", None):
                break
            if event == "__TIMEOUT__":
                # every timeout check if any of the users friends have changed presence status
                friends = await self.get_friends_list()
                for friend in friends["result"]["friends"]:
                    if friend["presence"]["state"] == "ONLINE":
                        state = f'{friend["presence"]["state"]} Playing: {friend["presence"]["game"]["name"]}'
                        window[("-pre-", friend["id"])].update(value=state)
                    else:
                        window[("-pre-", friend["id"])].update(value=friend["presence"]["state"])

    def extend_friend_column(self, friends, window, first):
        if first:
            # for the first time only use data from the database to update main layout
            usernames = [username[0] for username in self.cursor.execute("SELECT Username FROM FRIENDS")]
            ids = [iss[0] for iss in self.cursor.execute("SELECT Friend_UID FROM FRIENDS")]

            for username, iss in zip(usernames, ids):
                print(username, iss)
                new_friend = create_new_friend(username, "", iss)
                window.extend_layout(window["-Column-"], new_friend)
        else:
            for friend in friends["result"]["friends"]:

                # check if friend already exists in database,
                # if it doesn't, add the friend to the db and extend the layout
                res = self.cursor.execute("SELECT 1 FROM Friends WHERE Friend_UID = ?", (friend["id"],))
                if res.fetchone() != (1,):
                    self.cursor.execute("INSERT INTO Friends (Username,Friend_UID) VALUES (?,?)", (friend["name"],
                                                                                                   friend["id"],))
                    new_friend = create_new_friend(friend["name"], friend["presence"]["state"], friend["id"])
                    window.extend_layout(window["-Column-"], new_friend)
                    self.conn.commit()
