# Code for Proxy to be up and solve requests

import zmq
import os
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("Socket created!!!")


# Function that allows the user to properly login
def login(username, pw):
    print('Checking login information ...')
    with open('db.json', 'r') as db:
        db_object = json.load(db)
        if username in db_object.keys():
            if pw == db_object[username]['password']:
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
    with open('db.json', 'r') as db:
        db_object = json.load(db)
    if not username in db_object.keys():
        db_object[username] = {'password': pw, 'files': []}
        os.mkdir(spath + username)
        socket.send_string('ok')
        print('User registered successfully')
        with open('db.json', 'w') as db:
            json.dump(db_object, db, indent=4)
    else:
        socket.send_string('Error!!!')
        print('Username already exists')

# Function that appends the part of the file in bytes
# to the existing file in the server
def upload(user, filename, part):
    with open(spath + user + '/{}'.format(filename), 'ab') as f:
        f.write(part)
    print('filepart appened successfully')
    socket.send_string('uploading ...')

# This function allows the client to know whether
# a file to upload already exists, so the client can start
# sending the parts of the file
def exists(user, filename):
    with open('db.json', 'r') as db:
        db_object = json.load(db)
    if filename in db_object[user]['files']:
        print('file already exists ...')
        socket.send_string('file exists')
    else:
        print('file can be uploaded')
        db_object[user]['files'].append(filename)
        with open('db.json', 'w') as db:
            json.dump(db_object, db, indent=4)
        socket.send_string('ok')

# Function that returns the list of files from
# a specific user
def listfiles(user):
    with open('db.json', 'r') as db:
        db_object = json.load(db)
    files = db_object[user]['files']
    print('Sending list of files to client...\n')
    socket.send_json(files)

# This function downloads the partsize specified
# by the client
def download(user, filename, pos, partsize):
    with open(spath + user + '/' + filename, 'rb') as f:
        f.seek(pos)
        part = f.read(partsize)
        if not part:
            socket.send_multipart(['Done!!'.encode()])
            print('File downloaded successfully')
        else:
            socket.send_multipart(['downloading...'.encode(), part])


# ServerUp runs the server, so it can start listening
# to requests through the socket
def serverUp():
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
        elif cmd == 'list':
            # code to execute when request is list
            listfiles(request[1].decode())
        elif cmd == 'exists':
            # code to execute when request is exists for upload
            exists(request[1].decode(), request[2].decode())
        elif cmd == 'upload':
            # code to execute when request is upload
            upload(request[1].decode(), request[2].decode(), request[3])
        elif cmd == 'download':
            # code to execute when request is download
            download(request[1].decode(), request[2].decode(), int(request[3].decode()), int(request[4].decode()))
        print('Finished Transaction!!')

def main():
    serverUp()

if __name__ == "__main__":
    main()
