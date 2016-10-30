#!/usr/bin/env node

var drone_video_bin = process.env.VIDBIN || '../video/bin/drone';

var chalk = require('chalk')
   ,spawn = require('child_process').spawn
   ,program = require('commander')
   ,zmq = require('zmq')
   ,sock = zmq.socket('push')
   ,util = require('util');

style = { info: chalk.green, error: chalk.red }

/* Drone commands. */
var commands = {
    TAKEOFF: 1,
    LAND: 2,
    EMERGENCY: 3,
    LEFT: 4,
    RIGHT: 5
}
var droneMovementSpeed = 50;

program
    .version('0.0.1')
    .arguments('<fifo>')
    .action(function (fifo) {
        fifoFile=fifo
    });
program.parse(process.argv);

if (typeof fifoFile === 'undefined') {
    console.log(style.error('No fifo file provided!'));
    program.outputHelp(style.green);
    process.exit(1);
};

/* Video Stream */
const droneVideo = spawn(drone_video_bin, [fifoFile]);
droneVideo.stdout.on('data', (data) => {
    console.log(style.info(data));
});

droneVideo.stderr.on('data', (data) => {
    console.log(style.error(data));
});

droneVideo.on('close', (code) => {
    console.log(style.info('Drone video stopped with code: ' + code));
    process.exit(code);
});

var drone_cmd = function(sock, command, value)
{
    console.log(style.info('Command: ' + command + ' Value: ' + value));
    sock.send(util.format('{"id": %d, "value": %d}', command, value));
}

console.log('Beginning drone flight in 10 seconds...');
setTimeout(function() {
    sock.connect('tcp://127.0.0.1:5555');
    setTimeout(drone_cmd, 5000, sock, commands.TAKEOFF, 0);
    setTimeout(drone_cmd, 15000, sock, commands.LEFT, 50);
    setTimeout(drone_cmd, 20000, sock, commands.RIGHT, 50);
    setTimeout(drone_cmd, 25000, sock, commands.LAND, 0);
}, 10000);


