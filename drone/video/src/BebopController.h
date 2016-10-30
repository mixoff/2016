#ifndef BEBOP_CONTROLLER_H
#define BEBOP_CONTROLLER_H

#include <libARSAL/ARSAL.h>
#include <libARController/ARController.h>

#define CMD_TAKEOFF 1
#define CMD_LAND 2
#define CMD_EMERGENCY 3
#define CMD_LEFT 4
#define CMD_RIGHT 5

void *poll_input(void *device);

#endif /* BEBOP_CONTROLLER_H */
