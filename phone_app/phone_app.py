import time
import BaseHTTPServer


HOST_NAME = '127.0.0.1' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 80 # Maybe set this to 9000.


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        html = """
<html><head>
    <title>Phone Application</title>
</head>
<body>
    <p>Waiting for notification...</p>
    <canvas id="canvas" width='100%' height='100%'></canvas>
</body>
<script>
    window.onload = function() {
        var canvas = document.getElementById('canvas');
        var ctx = canvas.getContext('2d');
        var ws = new WebSocket('ws://mixoff-identity-test.eu-gb.mybluemix.net/push');
        //ws.binaryType = 'arraybuffer'; // IS THIS CORRECT??
        ws.onopen = function(e) { alert("opened"); }
        ws.onclose = function(e) { alert("closed"); }
        ws.onmessage = function(e) { 
            alert("got: " + e.data); 
            
        }
    };
</script>
        """
        s.wfile.write(html)


        #s.wfile.write("<html><head><title>Phone Application</title></head>")
        #s.wfile.write("<body><p>This is a test.</p>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        #s.wfile.write("<p>You accessed path: %s</p>" % s.path)


        s.wfile.write("</body></html>")

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
