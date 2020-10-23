# Code for Proxy to be up and solve requests

import zmq
import os
import json
import math

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:4444")

print("Socket created!!!")

partsize = 1024 * 1024 * 10

database = 'database.json'

# Function that allows the user to properly login
def login(username, pw):
    print('Checking login information ...')
    with open(database, 'r') as db:
        db_object = json.load(db)
        if username in db_object['users'].keys():
            if pw == db_object['users'][username]['password']:
                socket.send_string('ok')
                print('user logged in successfully')
            else:
                socket.send_string('invalid password')
                print('Invalid password')
        else:
            socket.send_string('not found')
            print('User not found')

# This function registers the new user, checking first
# if it does not exist already
def register(username, pw):
    with open(database, 'r') as db:
        db_object = json.load(db)
    if not username in db_object['users'].keys():
        db_object['users'][username] = {'password': pw, 'files': {}}
        socket.send_string('ok')
        print('User registered successfully')
        with open('database.json', 'w') as db:
            json.dump(db_object, db, indent=4)
    else:
        socket.send_string('Error!!!')
        print('Username already exists')

def newServer(serverIp, serverPort):
    serverId = serverIp + ':' + serverPort
    with open(database, 'r') as db:
        db_object = json.load(db)
    if not serverId in db_object['servers'].keys():
        socket.send_multipart(['ok'.encode()])
        print('Server does not exist, so it can be added')
    else:
        socket.send_multipart(['exists'.encode()])
        print('Server info already exists, Error ...\n')

def createServer(serverIp, serverPort, capacity):

    serverId = serverIp + ':' + serverPort
    serverCapacity = math.ceil(capacity/float(partsize))

    with open(database, 'r') as db:
        db_object = json.load(db)
    db_object['servers'][serverId] = {
    'socket': serverId,
    'capacity': serverCapacity,
    'filled': 0,
    'files': []
    }
    with open(database, 'w') as db:
        json.dump(db_object, db, indent=4)
    socket.send_string(serverId)
    print(f'Server {serverId} created and added successfully!!!\n')




# Function that receives the file part names
# in order to start load balancing
def upload(user, filename, partnames):
    serversockets = []
    serverIndex = 0
    with open(database, 'r') as db:
        db_object = json.load(db)
    activeServers = list(db_object['servers'].keys())
    for part in partnames:
        while True:
            if serverIndex < len(activeServers):
                if db_object['servers'][activeServers[serverIndex]]['filled'] < \
                db_object['servers'][activeServers[serverIndex]]['capacity']:
                    serversockets.append(db_object['servers'][activeServers[serverIndex]]['socket'])
                    db_object['servers'][activeServers[serverIndex]]['files'].append(part)
                    db_object['servers'][activeServers[serverIndex]]['filled'] += 1
                    serverIndex += 1
                    break
                else:
                    serverIndex += 1
            else:
                serverIndex = 0
    db_object['users'][user]['files'][filename]['fileparts'] = partnames
    db_object['users'][user]['files'][filename]['serverparts'] = serversockets
    with open(database, 'w') as db:
        json.dump(db_object, db,indent=4)
    socket.send_multipart(['list of sockets successfully created!!'.encode(),\
    json.dumps(partnames).encode(), json.dumps(serversockets).encode()])
    print('list of sockets successfully created!!')

# This function receives the download request
# and sends to client the list of partnames
# and server locations
def download(user, filename):
    with open(database, 'r') as db:
        db_object = json.load(db)
    partnames = db_object['users'][user]['files'][filename]['fileparts']
    serverparts = db_object['users'][user]['files'][filename]['serverparts']
    socket.send_multipart([json.dumps(partnames).encode(), json.dumps(serverparts).encode()])
    print('partnames and serverparts successfully sent')



# This function allows the client to know whether
# a file to upload already exists, so the client can start
# sending the parts of the file. This also works for
# checking the existence of a file before downloading
def exists(user, filename):
    with open('database.json', 'r') as db:
        db_object = json.load(db)
    if filename in db_object['users'][user]['files'].keys():
        print('file already exists ...')
        socket.send_string('file exists')
    else:
        db_object['users'][user]['files'][filename] = {}
        print('file can be uploaded')
        with open('database.json', 'w') as db:
            json.dump(db_object, db, indent=4)
        socket.send_string('file can be uploaded')

# Function that returns the list of files from
# a specific user
def listfiles(user):
    with open('database.json', 'r') as db:
        db_object = json.load(db)
    files = list(db_object['users'][user]['files'].keys())
    print('Sending list of files to client...')
    socket.send_json(files)
    print('List of files sent successfully!!\n')

# ProxyUp runs the proxy server, so it can start listening
# to requests through the socket
def ProxyUp():
    while True:
        print('Waiting for requests ...\n')
        request = socket.recv_multipart()
        cmd = request[0].decode()
        if cmd == 'login':
            # Code to execute when request is login
            login(request[1].decode(), request[2].decode())
        elif cmd == 'register':
            # Code to execute when request is register
            register(request[1].decode(), request[2].decode())
        elif cmd == 'exists':
            # code to execute when request is exists for upload and download
            exists(request[1].decode(), request[2].decode())
        elif cmd == 'new':
            # code to execute when a server wants to be created
            newServer(request[1].decode(), request[2].decode())
        elif cmd == 'create':
            # code to execute when server is created
            createServer(request[1].decode(), request[2].decode(), float(request[3].decode()))
        elif cmd == 'list':
            # code to execute when request is list
            listfiles(request[1].decode())
        elif cmd == 'upload':
            # code to execute when request is upload
            upload(request[1].decode(), request[2].decode(), json.loads(request[3].decode()))
        elif cmd == 'download':
            # code to execute when request is download
            download(request[1].decode(), request[2].decode())
        print('Finished Transaction!!')

def main():
    ProxyUp()

if __name__ == "__main__":
    main()
