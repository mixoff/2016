import os
import cherrypy


PORT_NUMBER = 80 # Maybe set this to 9000.


class App(object):
    @cherrypy.expose
    def index(self):
        """Respond to a GET request."""

        html = """
<html><head>
    <title>Phone Application</title>
</head>
<body>
    <p>Waiting for notification...</p>
    <canvas id="canvas" width='1024px' height='768px'></canvas>
</body>
<script>
    var g = 0;

    function Uint8ToBase64(u8Arr){
        var CHUNK_SIZE = 0x8000; //arbitrary number
        var index = 0;
        var length = u8Arr.length;
        var result = '';
        var slice;
        while (index < length) {
            slice = u8Arr.subarray(index, Math.min(index + CHUNK_SIZE, length)); 
            result += String.fromCharCode.apply(null, slice);
            index += CHUNK_SIZE;
        }
        return btoa(result);
    }
    
    window.onload = function() {
        var canvas = document.getElementById('canvas');
        var ctx = canvas.getContext('2d');
        var ws = new WebSocket('ws://mixoff-identity-test.eu-gb.mybluemix.net/ws_output');
        //var ws = new WebSocket('ws://mixoff-identity-test.eu-gb.mybluemix.net/push');
        ws.binaryType = 'arraybuffer';
        ws.onopen = function(e) { console.log("opened"); }
        ws.onclose = function(e) { console.log("closed"); }
        ws.onmessage = function(e) { 
            console.log("got: " + e.data); 
            console.log("Size = " + e.data.byteLength);
            g = e.data;
            var u8 = new Uint8Array(e.data);
            var b64encoded = Uint8ToBase64(u8);//btoa(String.fromCharCode.apply(null, u8));
            imageObj = new Image();
            imageObj.onload= function() {
                //console.log(imageObj.src)
                ctx.drawImage(imageObj, 0, 0);
            }
            imageObj.src = "data:image/jpg;base64,"+b64encoded;
            
        }
    };
</script>
        """
        return html

if __name__ == '__main__':

    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/public': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'public'
        }
    }   
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(App(), '/', conf)

