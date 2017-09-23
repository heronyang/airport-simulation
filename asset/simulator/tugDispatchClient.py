
import sys
import socket
import json

if __name__=='__main__':
  fdat = None
  if len(sys.argv)>1:
    with open(sys.argv[1]) as fin:
      fdat = fin.read()
  else:
    with open('input.json') as fin:
      fdat = fin.read()

  data = json.loads(fdat)
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect(('127.0.0.1', 13374))
  sock.send(json.dumps(data).encode())
  result = json.loads(sock.recv(4096).decode())
  print(result)
  sock.close()
