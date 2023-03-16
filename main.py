import asyncio
from NSOApiManager import NSOApi
import json
import PySimpleGUI

nso = NSOApi.NSO()
asyncio.run(nso.login_process())



async def main():
    



asyncio.run(main())
