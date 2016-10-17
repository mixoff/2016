"use strict";

var bebop = require("node-bebop")
    , colours = require('colors')
    , ffmpeg = require('fluent-ffmpeg');

var drone = bebop.createClient();
var video = drone.getVideoStream();

var command = ffmpeg('sample.mp4')
                .on('start', cmd => console.log(cmd))
                .withNativeFramerate()
                .videoCodec('copy')
                .noAudio()
                .outputOptions(['-f rtsp'])
                .output('rtsp://127.0.0.1:12345/live.sdp')
                .on('error', function(err) {
                    console.log(colours.red(err));
                })
                .on('codecData', function(data) {
                    console.log(colours.green(data.video));
                    console.log(colours.green(data.video_details));
                })
                .on('stderr', function(stderr) {
                    console.log(colours.yellow(stderr));
                })
                .on('end', function() {
                    console.log('finished')
                });

drone.connect(function() {
    drone.on('ready', function() {
        drone.MediaStreaming.videoEnable(1);
        console.log(colours.green('drone::ready'));
        command.run();
    });
});
