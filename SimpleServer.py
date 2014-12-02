import os
import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

HandlerClass = SimpleHTTPRequestHandler
ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.0"

def SimpleServer( path='.', port=8888 ):
	os.chdir( path )

	server_address = ('127.0.0.1', port)
	HandlerClass.protocol_version = Protocol
	httpd = ServerClass(server_address, HandlerClass)

	httpd.serve_forever()

if __name__ == '__main__':
	kwargs = {}
	if sys.argv[1]:
		kwargs['path'] = sys.argv[1]
	SimpleServer( **kwargs )
