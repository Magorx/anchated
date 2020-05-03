#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import socketserver
import threading
from time import sleep

SERVER_NAME = 'Simple'
QUEUE = []


class User:
    def __init__(self, name, ip, handler):
        self.name = name
        self.ip = ip
        self.handler = handler
        self.partner = None

    def connect(self, user):
        if user.partner:
            return

        self.partner = user
        user.partner = self

        self.send("] You've been connected to {}. He's your new partner. /ex to disconnect".format(user.name))
        user.send("] You've been connected to {}. He's your new partner. /ex to disconnect".format(self.name))

    def disconnect(self):
        if self.partner:
            self.partner.send("] You've been disconnected from {}.".format(self.name))
            self.partner.partner = None
            self.send("] You've been disconnected from {}.".format(self.partner.name))
            self.partner = None
        else:
            self.send("] You didn't have a partner. /qu to get into queue")

    def send(self, message):
        message = message.encode('utf-8')
        self.handler.request.send(message)

    def enter_queue(self):
        if self not in QUEUE:
            QUEUE.append(self)
            self.send('] Entered queue. People there: {}'.format(len(QUEUE)))
        else:
            self.send('] You are alredy in queue. People there: {}'.format(len(QUEUE)))

    def leave_queue(self):
        while self in QUEUE:
            QUEUE.remove(self)


class MyHandler(socketserver.BaseRequestHandler):
    def __init__(self, *args):
        super().__init__(*args)

    def afk_check(self):
        while True:
            if not self.user.partner:
                self.user.send("] qq, it's an afk check")
            sleep(3)

    def handle(self):
        user_ip = self.client_address[0]
        print('[connect] {}'.format(user_ip))

        try:
            user = User('noname', user_ip, self)
            self.user = user
            user.send("] You've connected to server '{}'".format(SERVER_NAME))
            user.send("] What is you name for this session?")
            name = self.request.recv(1024)
            name = name.decode()
            if name:
                user.name = name
            user.send("] You don't have a partner for now. Send '/qu' to get into queue")
        except Exception as e:
            print('[disconnect] {} | {}'.format(user.ip, e))

        try:
            while True:
                data = self.request.recv(1024)
                data = data.decode("utf-8")
                if not data:
                    continue
                if data == '/queue' or data == '/qu':
                    user.enter_queue()
                elif data == '/exit' or data == '/ex':
                    user.disconnect()
                    user.leave_queue()
                elif data == '/echo' or data == '/ec':
                    user.leave_queue()
                    user.disconnect()
                    user.send('] You went echo with yourself')
                    user.partner = user
                else:
                    if not user.partner:
                        user.send("] You don't have a partner for now. Send '/qu' to get into queue")
                    else:
                        message = '< ' + data
                        print(message)
                        user.partner.send(message)
        except Exception as e:
            print('[disconnect] {} | {}'.format(user.ip, e))
            user.leave_queue()
            if user.partner:
                user.partner.send("] You've been disconnected from {}.".format(user.name))
                user.partner.partner = None


class MyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class Connector:
    def __init__(self, queue_list):
        self.queue = queue_list

    def connect(self):  # write logic of your connector here
        while len(self.queue) > 1:
            user_1 = self.queue[-1]
            user_2 = self.queue[-2]
            user_1.connect(user_2)
            self.queue.pop()
            self.queue.pop()

    def connect_process(self):
        while True:
            self.connect()
            sleep(1)


class Server(MyServer):
    def __init__(self, name, ip, port, connector, *args):
        super().__init__((ip, port), MyHandler)
        global SERVER_NAME
        SERVER_NAME = name
        self.name = SERVER_NAME
        self. ip = ip
        self.port = port

        self.connector = connector(QUEUE)
        connector_thread = threading.Thread(target=self.connector.connect_process)
        connector_thread.start()
