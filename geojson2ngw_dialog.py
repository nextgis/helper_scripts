#!/usr/bin/env python
# -*- coding: utf-8 -*-
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Label,FileBrowser, \
    Button, TextBox, CheckBox, Widget
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys
import os



class programModel(object):
    def __init__(self):
        #тут можно например обернуть вызов библиотеки от NGW Connect
        self.fieldValues = None


    def run(self, payload):
        #save entered fields values in object
        self.fieldValues = payload

        
        arguments = ''

        print payload


        if payload['url'] != '':
            arguments += ' --url ' + payload['url']
        if payload['login'] != '':
            arguments += ' --login ' + payload['login']
        if payload['password'] != '':
            arguments += ' --password ' + payload['password']
        if payload['folder'] != '':
            arguments += ' --folder ' + payload['folder']
        if payload['parent'] != '':
            arguments += ' --parent ' + payload['parent']
        if payload['groupname'] != '':
            arguments += ' --groupname ' + payload['groupname']

        cmd = 'python geojson2ngw.py ' + arguments
        os.system(cmd)

        print
        raw_input('[Enter] - Return to dialog   [Ctrl+C] - Quit')





    def get_all(self):
        #Get saved form values of default values
        if self.fieldValues is None:
            return {"url": "http://.nextgis.com", "login": "administrator", "password": "", "groupname": "", "folder": "", "parent": ""}
        else:
            return self.fieldValues





class NGWUploaderView(Frame):
    def __init__(self, screen, model):
        super(NGWUploaderView, self).__init__(screen,
                                          screen.height * 2 // 3,
                                          screen.width * 2 // 3,
                                          hover_focus=True,
                                          title="Upload geodata to NGW",
                                          reduce_cpu=True)
        # Save off the model that accesses the contacts database.
        self._model = model

        regexpIsURL=    r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$'
        regexpIsDight = '^[\s\d]*$'

        # Create the form for displaying the list of contacts.
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Label("Upload all geojson from folder into NextGISWeb as new layers, and create of simple mapserver style."))
        layout.add_widget(Divider())
        layout.add_widget(Text("NGW URL or nextgis.com account:", "url",validator = regexpIsURL))
        layout.add_widget(Text("Login:", "login"))
        layout.add_widget(Text("Password:", "password",hide_char="*"))
        layout.add_widget(Text("New resourse group name (optional):", "groupname"))
        layout.add_widget(Text("Path to folder with geojson (optional):", "folder"))
        layout.add_widget(Text("parent folder id (optional):", "parent",validator = regexpIsDight))
        #layout.add_widget(CheckBox("", label="Create webmap:", name="create_webmap"))
        #layout.add_widget(TextBox(
        #    Widget.FILL_FRAME, "Notes:", "notes", as_string=True))
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        #layout2.add_widget(Button("Cancel", self._cancel), 2)
        layout2.add_widget(Button("Quit", self._quit), 3)
        self.fix()

    def reset(self):
        # Do standard reset to clear out form, then populate with new data.
        super(NGWUploaderView, self).reset()
        self.data = self._model.get_all()

    def _ok(self):
        self.save()
        self._screen.close()



        self._model.run(self.data)
        raise(RestartApp(""))



        raise NextScene("Main")

    @staticmethod
    def _cancel():
        raise NextScene("Main")

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")



def demo(screen, scene):
    scenes = [
        Scene([NGWUploaderView(screen, program)], -1, name="Main")
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene)


class RestartApp(Exception):
    pass

program = programModel()
last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
    except RestartApp as r:
        print(r)
