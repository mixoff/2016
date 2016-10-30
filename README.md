# 2016
Coding Competition 2016


## Identify Service
POST to https://mixoff-identity-test.eu-gb.mybluemix.net/identify

With a body of
{
	"name":"kevin bacon",
	"url" : "http://blogs.longwood.edu/jameslaycock/files/2015/03/19_Kevin_Bacon.jpg"
}

## Drone Stream/Flight Service
The Parrot SDK provides native C bindings to allow us to stream video frames out. This is possible using higher level bindings such as node-bebop, but the video stream appears very jumpy. The current solution is to start a nodejs process that spawns a c process that starts the video stream writing to a FIFO file. This C process manages a seperate thread where it receives commands via 0MQ. Commands are strictly defines in the JSON format: {"id": 1, "value": 10} where id is the number of the command and value is an optional value for the command (ie the amount of roll when turning). See video/src/BecopController.h for definition of command identifiers.

Dependencies:
    * make
    * gcc
    * libczmq-dev
    * nodejs
    * npm
    * mplayer
    * ffmpeg

### Running the drone stream video
Execute the run.sh script providing the name of the output FIFO:
    ./run.sh bebop_stream

Execute the face recognizer tool pointing it at the fifo stream. Once the stream is established, commands will be sent to move the drone. In order to test without actually flying the drone, export the environment variable TEST to the process:

    TEST=1 ./run.sh bebop_stream

In the above example, the drone will not be moved as it is in test mode. Commands will be sent as folows:
1. After 5 seconds, the drone will takeoff
2. After a further 5 seconds, the drone will bank left
3. After a further 5 seconds seconds, the drone will bank right
4. After a further 10 seconds, the drone will bank left again
5. After a further 5 seconds, the drone will land

The above will probably change alot, see flight/bebop.js where the instructions/timings are defined.

## Analysis Service
POST to https://mixoff-identity-test.eu-gb.mybluemix.net/analyse

With a body of:
{
	"name":"kevin bacon",
	"url" : "http://blogs.longwood.edu/jameslaycock/files/2015/03/19_Kevin_Bacon.jpg"
}

or

{
	"name":"ak47",
	"url" : "http://www.no2star.com/file/2016/09/AKAGUN02leftD.jpg"
}

https://mixoff-identity-test.eu-gb.mybluemix.net/image  
Defaults to kevin. It shows where the face is and the name of the person if it recognises it. Also shows the category (e.g. 'person') at the top corner

https://mixoff-identity-test.eu-gb.mybluemix.net/image?url=http://cp91279.biography.com/1000509261001/1000509261001_1086612957001_Bio-Biography-Britney-Spears-LF1.jpg

Works with objects too (limited to 2MB)

can now POST an image to https://mixoff-identity-test.eu-gb.mybluemix.net/pic to get it displayed. Remember to set the content-type
