#!/opt/local/bin/python

import socketserver

import json


class SchedulerServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


class SchedulerServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            recv = self.request.recv(16777216).decode()
            data = json.loads(recv.strip())
            # process the data, i.e. print it:
            print("Recevied from {}:".format(self.client_address[0]))
            print(data)
            # send some 'ok' back
            self.request.sendall(json.dumps({'return': 'ok'}).encode())
        except Exception as e:
            print("Exception while receiving message: {} \n {}", e.args, e)


if __name__ == '__main__':
    host, port = '127.0.0.1', 13373
    server = SchedulerServer((host, port), SchedulerServerHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()