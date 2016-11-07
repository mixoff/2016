#ifndef BEBOP_CONTROLLER_H
#define BEBOP_CONTROLLER_H

#include <libARSAL/ARSAL.h>
#include <libARController/ARController.h>

/* Command Identifiers. */
#define CMD_TAKEOFF 1
#define CMD_LAND 2
#define CMD_EMERGENCY 3
#define CMD_ROLL 4
#define CMD_FLIP 5
#define CMD_CALIBRATE 6
#define CMD_UP 7

/* ZMQ listen port. */
#define LISTEN_PORT 5555

void *poll_input(void *device);

#endif /* BEBOP_CONTROLLER_H */
