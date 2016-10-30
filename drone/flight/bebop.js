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
    CALIBRATE: 6
}

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

const droneVideo = spawn(drone_video_bin, [fifoFile]);
droneVideo.stdout.on('data', (data) => {
    console.log(style.info('DRONE_PROC:: ' + data));
});

droneVideo.stderr.on('data', (data) => {
    console.log(style.error('DRONE_PROC:: ' + data));
});

droneVideo.on('close', (code) => {
    console.log(style.error('Drone video stopped with code: ' + code));
    process.exit(code);
});

var drone_cmd = function(sock, command, value) {
    console.log('Sending commands');
    sock.send(util.format('{"id": %d, "value": %d}', command, value));
}

var connect_attempts = 1;

process.on('SIGINT', () => {
    console.log(style.error('SIGINT received, performing emergency stop'));
    drone_cmd(sock, commands.EMERGENCY, 0);
});

sock.on('connect', function(fd, ep) {
    console.log(style.info('Got a connection!'));
    setTimeout(function() {
        setTimeout(drone_cmd, 5000, sock, commands.TAKEOFF, 0);
        setTimeout(drone_cmd, 25000, sock, commands.ROLL, -80);
        setTimeout(drone_cmd, 40000, sock, commands.ROLL, 80);
        setTimeout(drone_cmd, 20000, sock, commands.LAND, 0);
    }, 10000);
    console.log(style.info('Beginning drone flight in 10 seconds'));
});

sock.on('connect_retry', function(fd, ep) {
    console.log(style.warn(util.format('Awaiting connection to drone RPC (attempt %d)', connect_attempts)));
    connect_attempts++;
});

sock.monitor(1000);

setTimeout(function() {
    sock.connect('tcp://127.0.0.1:5555');
}, 1000);
