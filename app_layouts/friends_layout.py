import PySimpleGUI as sg

__friends_column = [
    [sg.Text("Nintendo Friends List:", size=(20,1))]
]

layout = [
    [sg.Column(__friends_column, key="-Column-")]
]

