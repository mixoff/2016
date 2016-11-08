#include <unistd.h>
#include <czmq.h>
#include <stdio.h>

#include "BebopController.h"
#include "cJSON.h"

#define TEST

static void try_exec_cmd(ARCONTROLLER_Device_t *device, const char *msg)
{
    cJSON *root = cJSON_Parse(msg);
    const int cmd_id = cJSON_GetObjectItem(root, "id")->valueint;
    const int value = cJSON_GetObjectItem(root, "value")->valueint;
#ifndef TEST
    switch(cmd_id)
    {
        case CMD_TAKEOFF:
            printf("TAKEOFF\n");
            device->aRDrone3->sendPilotingTakeOff(device->aRDrone3);
            break;
        case CMD_LAND:
            printf("LAND\n");
            device->aRDrone3->sendPilotingLanding(device->aRDrone3);
            break;
        case CMD_EMERGENCY:
            printf("EMERGENCY\n");
            device->aRDrone3->sendPilotingEmergency(device->aRDrone3);
            break;
        case CMD_ROLL:
            printf("ROLL\n");
            device->aRDrone3->setPilotingPCMDRoll(device->aRDrone3, value);
            device->aRDrone3->setPilotingPCMDFlag(device->aRDrone3, 1);
            break;
        case CMD_FLIP:
            printf("FLIP\n");
            device->aRDrone3->sendAnimationsFlip(device->aRDrone3, value);
            break;
	case CMD_CALIBRATE:
	    device->common->sendCalibrationMagnetoCalibration(device->common, 1);
            device->aRDrone3->sendPilotingFlatTrim(device->aRDrone3);
            printf("CALIBRATE\n");
	    break;
        case CMD_UP:
            device->aRDrone3->setPilotingPCMDGaz(device->aRDrone3, value);
            printf("UP\n");
            break;
        default:
            fprintf(stderr, "Failed to parse command!\n");
            break;
    }
#else
    printf("TEST MODE, NOT FLYING DRONE!\n");
#endif
    cJSON_Delete(root);
}

void *poll_input(void *arg)
{
    ARCONTROLLER_Device_t *device = (ARCONTROLLER_Device_t*)(arg);
    zsock_t *pull = zsock_new_pull("tcp://*:5555");
    while (1)
    {
        printf("Awaiting drone command...\n");
        char *msg = zstr_recv(pull);
        try_exec_cmd(device, msg);
        zstr_free(&msg);
        usleep(100);
    }
    zsock_destroy(&pull);

    return NULL;
}
