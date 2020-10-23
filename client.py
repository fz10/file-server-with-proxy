# Code for clients

import zmq
import json
import os
import getpass
import math
import hashlib

context = zmq.Context()

#  Socket to talk to server
print("Connecting to server ...\n")
socket = context.socket(zmq.REQ)
proxy = "tcp://localhost:4444"
socket.connect(proxy)

partsize = 1024 * 1024 * 10
cpath = '../Clients/'
dpath = '../Clients/Downloads/'
user = ''

# This function executes first, allows the user to login
# or to register a new one
def login():
    validator = False
    global user
    global socket
    while not validator:
        username = input('Please insert Username: ')
        pw = getpass.getpass('Password: ')
        socket.send_multipart(['login'.encode(), username.encode(), pw.encode()])
        resp = socket.recv_string()
        if resp == 'ok':
            user = username
            validator = True
            print('successfully logged in !!!')
        elif resp == 'invalid password':
            print(resp + ", please try again \n")
        elif resp == 'not found':
            uresp = input('Username does not exist, do you want to create a new one? y / n ...\n')
            if uresp == 'y':
                while True:
                    username = input('Please insert new Username: ')
                    pw = getpass.getpass('Create Password: ')
                    socket.send_multipart(['register'.encode(), username.encode(), pw.encode()])
                    resp = socket.recv_string()
                    if resp == 'ok':
                        user = username
                        validator = True
                        print('User registered successfully and logged in !!!\n')
                        break
                    else:
                        print('User already exists, try again ...')
            else:
                print('Try again ...\n')

# This function checks if the file exists in the client's directory
def exists(filename, path):
    list = os.listdir(path)
    if filename in list:
        return True
    else:
        return False

def hash(bytes):
    hasher = hashlib.sha256()
    hasher.update(bytes)
    return hasher.hexdigest()

# This function hashes the parts of the file that
# will be uploaded
def hashparts(filename, parts):
    with open(cpath + filename, 'rb') as f:
        while True:
            part = f.read(partsize)
            if not part:
                print('parts hashed successfully')
                break
            parts.append(hash(part))
    return parts


# This function uploads a file to the server segmenting it
def upload():
    validator = False
    while not validator:
        filename = input('Please insert the filename to upload: ')
        newname = filename
        if exists(filename, cpath):
            while True:
                socket.send_multipart(['exists'.encode(), user.encode(), newname.encode()])
                resp = socket.recv_string()
                if resp == 'file exists':
                    newname = input('file already exists in server, please insert a new name for it: ')
                else:
                    print(resp)
                    break
            parts = []
            # name = os.path.splitext(newname)[0]
            # ext = os.path.splitext(newname)[1]
            # quantityParts = math.ceil(float(os.path.getsize(cpath + filename)) / float(partsize))
            # for i in range(0, quantityParts):
            #     parts.append(name + user + str(i))
            jparts = json.dumps(hashparts(filename, parts))
            socket.send_multipart(['upload'.encode(), user.encode(), newname.encode(), jparts.encode()])
            resp = socket.recv_multipart()
            print(resp[0].decode())
            validator = True
        else:
            print('filename is not correct, please try again ...\n')
    partnames = json.loads(resp[1].decode())
    serversockets = json.loads(resp[2].decode())
    socket.disconnect(proxy)
    with open(cpath + filename, 'rb') as f:
        i = 0
        while True:
            bytes = f.read(partsize)
            if not bytes:
                print('File uploaded successfully\n')
                break
            # Send part to a specific socket
            socket.connect("tcp://{}".format(serversockets[i]))
            socket.send_multipart(['upload'.encode(), partnames[i].encode(), bytes])
            resp = socket.recv_string()
            print(resp)
            socket.disconnect("tcp://{}".format(serversockets[i]))
            i += 1
    socket.connect(proxy)



# This function requests the list of files whose owner is
# the current user
def list():
    print('Requesting list of files to server...\n')
    socket.send_multipart(['list'.encode(), user.encode()])
    files = socket.recv_json()
    print("--------------------------------------------\n \
    Existing files in servers: \n")
    for file in files:
        print('    ', file, "\n")
    print("--------------------------------------------\n\
    Listing successful !!\n")

# This function requests downloads from the servers
# first checks if it exists in database, then it checks
# if it exists in 'Downloads folder'
def download():
    newname = ''
    while True: #let's check file existence in server
        filename = input('Please insert filename to Download: ')
        socket.send_multipart(['exists'.encode(), user.encode(), filename.encode()])
        resp = socket.recv_string()
        if resp == 'file exists':
            newname = filename
            print('Filename Correct')
            break
        else:
            print('file does not exist, please try again...\n')
    #let's check if it exists or not in 'Downloads'
    while True:
        if exists(newname, dpath):
            newname = input('file already exists in Downloads folder, please insert a new name for it: ')
        else:
            break
    socket.send_multipart(['download'.encode(), user.encode(), filename.encode()] )
    resp = socket.recv_multipart()
    partnames = json.loads(resp[0].decode())
    serverparts = json.loads(resp[1].decode())
    socket.disconnect(proxy)
    with open(dpath + newname, 'ab') as f:
        i = 0
        while i < len(partnames):
            socket.connect("tcp://{}".format(serverparts[i]))
            socket.send_multipart(['download'.encode(), partnames[i].encode()])
            resp = socket.recv_multipart()
            print(resp[0].decode())
            f.write(resp[1])
            socket.disconnect("tcp://{}".format(serverparts[i]))
            i += 1
        print('File downloaded successfully as {}'.format(newname))
    socket.connect(proxy)






# Workflow is the function where the client will be able to request to
# upload, list or download files from the server
def workflow():
    while True:
        print('--------------------------------------------')
        print('You\'re logged in as {}\n'.format(user))
        print('- list\n- upload\n- download\n')
        cmd = input('Please select one of the above options: ')
        if cmd == 'list':
            # Code to execute when option is 'list'
            list()
        elif cmd == 'upload':
            # Code to execute when option is 'upload'
            upload()
        elif cmd == 'download':
            # Code to execute when option is 'download'
            download()


def main():
    login()
    workflow()


if __name__ == "__main__":
    main()
