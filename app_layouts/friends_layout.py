import PySimpleGUI as sg

__friends_column = [
    [sg.Text("Friends list"), sg.Button("Reload", key="-RELOAD-"), sg.Button("CheckId", key="-ID-")]
]

layout = [
    [sg.Column(__friends_column, key="-Column-")]
]

