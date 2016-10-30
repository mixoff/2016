#!/bin/bash

RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

FIFO=$1


echo -e ${BLUE}
echo -e "=========================="
echo -e "SUPER AWESOME DRONE TIME"
echo -e "=========================="
echo -e ${NC}

die_with_msg() {
    >&2 echo -e "${RED}$1${NC}"
    exit 1
}

if [ "$#" -ne 1 ]; then
    die_with_msg "Usage: $0 <fifo_file>"
fi

echo -e "${YELLOW}- Building video streamer${NC}"
make -s -C video || die_with_msg "Failed to build drone!"

echo -e "${YELLOW}- Running drone controller${NC}"
export VIDBIN=video/bin/drone
source video/arsdk3/native-wrapper.sh 
echo
pkill -9 drone
rm -rf ${FIFO}
nodejs flight/bebop.js ${FIFO}
