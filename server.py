# Code for Server to be up and solve requests

import zmq
import os
import json
import math

context = zmq.Context()
socket = context.socket(zmq.REP)

spath = '../Server/'




def serverCreation():

    global spath
    req = context.socket(zmq.REQ)
    req.connect("tcp://localhost:4444")

    while True:
        serverIp = str(input('Please insert server ip address: '))
        serverPort = str(input('Please insert server port: '))
        req.send_multipart(['new'.encode(), serverIp.encode(), serverPort.encode()])
        resp = req.recv_multipart()
        if resp[0].decode() == 'ok':
            #you have to create the folder and socket
            capacity = math.ceil(float(input('Server can be created, please insert capacity in GB: ')) * 1073741824)
            req.send_multipart(['create'.encode(), serverIp.encode(), serverPort.encode(), str(capacity).encode()])
            resp = req.recv_string()
            socket.bind("tcp://*:{}".format(resp))
            print("Socket created!!!\n")
            print('Server created and added successfully\n')
            break
        elif resp[0].decode() == 'exists':
            print('Server already exists, please try again ... \n')

def upload(filename, bytes):
    with open(spath + '{}'.format(filename), 'wb') as f:
        f.write(bytes)
    print('filepart saved successfully')
    socket.send_string('uploading ...')

def download(filepart):
    with open(spath + '{}'.format(filepart), 'rb') as f:
        part = f.read()
    print('filepart successfully sent')
    socket.send_multipart(['downloading ...'.encode(), part])

def serverUp():
    while True:
        print('Waiting for requests ...\n')
        request = socket.recv_multipart()
        cmd = request[0].decode()
        if cmd == 'upload':
            # Code to execute when request is upload
            upload(request[1].decode(), request[2])
        elif cmd == 'download':
            # Code to execute when request is download
            download(request[1].decode())

def main():
    serverCreation()
    serverUp()

if __name__ == '__main__':
    main()
