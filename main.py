import asyncio
from Modules import UIManager

UI = UIManager.UIManager("Friendslist.db")

asyncio.run(UI.login_process())
asyncio.run(UI.run_friends_layout())
