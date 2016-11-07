#!/usr/bin/env node

var drone_video_bin = process.env.VIDBIN || '../video/bin/drone';

var chalk = require('chalk')
   ,spawn = require('child_process').spawn
   ,program = require('commander')
   ,zmq = require('zmq')
   ,sock = zmq.socket('push')
   ,util = require('util');

style = { info: chalk.green, error: chalk.red, warn: chalk.yellow }
droneEnv = process.env;

/* Drone commands, matching BebopController.h*/
var commands = {
    TAKEOFF: 1,
    LAND: 2,
    EMERGENCY: 3,
    ROLL: 4,
    FLIP: 5,
    CALIBRATE: 6,
    UP: 7
}

process.on('SIGINT', function() {
	console.log('Caught interrupt');
	drone_cmd(sock, commands.EMERGENCY, 0);
	process.exit(1);
});

var drone_cmd = function(sock, command, value) {
    console.log('Sending commands');
    sock.send(util.format('{"id": %d, "value": %d}', command, value));
}

sock.connect('tcp://127.0.0.1:5555');
drone_cmd(sock, commands.CALIBRATE, 0);
setTimeout(drone_cmd, 5000, sock, commands.CALIBRATE, 0);
setTimeout(drone_cmd, 10000, sock, commands.TAKEOFF, 0);
setTimeout(drone_cmd, 15000, sock, commands.UP, 5);
setTimeout(drone_cmd, 20000, sock, commands.UP, 0);
setTimeout(drone_cmd, 25000, sock, commands.ROLL, -20);
setTimeout(drone_cmd, 35000, sock, commands.LAND, 0);
