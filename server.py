# Code for Server to be up and solve requests

import zmq
import os
import json
import math

context = zmq.Context()
socket = context.socket(zmq.REP)

spath = '../Servers/'




def serverCreation():

    global socket
    global spath
    req = context.socket(zmq.REQ)
    req.connect("tcp://localhost:4444")

    serverNum = str(input('Please insert server number: '))
    req.send_multipart(['new'.encode(), serverNum.encode()])
    resp = req.recv_multipart()
    if resp[0].decode() == 'ok':
        #you have to create the folder and socket
        capacity = math.ceil(float(input('Server can be created, please insert capacity in GB: ')) * 1073741824)
        req.send_multipart(['create'.encode(), serverNum.encode(), str(capacity).encode()])
        resp = req.recv_string()
        spath = spath + 'Server' + serverNum
        os.mkdir(spath)
        socket.bind("tcp://*:{}".format(resp))
        print("Socket created!!!\n")
        print('Server created and added successfully\n')
    elif resp[0].decode() == 'exists':
        print('Reloading server ... \n')
        spath = spath + serverNum
        socket.bind("tcp://*:{}".format(resp[1].decode()))
        print("Socket created!!!\n")
        print('Server is Up!!\n')


def serverUp():
    pass

def main():
    serverCreation()
    serverUp()

if __name__ == '__main__':
    main()
