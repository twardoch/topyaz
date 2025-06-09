#!/usr/bin/env bash

echo "---------- GIGAPIXEL AI ----------"
echo "$ topyaz gp ./testdata/palms.jpg"
topyaz gp ./testdata/man.jpg --scale 2

echo "---------- PHOTO AI ----------"
echo "$ topyaz photo ./testdata/man.jpg --override-autopilot --upscale True --noise False"
topyaz photo ./testdata/man.jpg --override-autopilot --upscale True --noise False

echo "---------- VIDEO AI ----------"
echo "$ topyaz video ./testdata/video.mp4 --model amq-13 --scale 2 --interpolate --fps 60"
topyaz video ./testdata/video.mp4 --model amq-13 --scale 2 --interpolate --fps 60

echo "---------------------------"
