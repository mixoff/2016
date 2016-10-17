"use strict";

var bebop = require("node-bebop")
var colours = require('colors');

var drone = bebop.createClient();

drone.connect(function() {
    drone.on('ready', function() {
        console.log(colours.green('drone::ready'));
    });
});
