#include <unistd.h>
#include <czmq.h>

#include "BebopController.h"
#include "cJSON.h"

static void try_exec_cmd(ARCONTROLLER_Device_t *device, const char *msg)
{
    cJSON *root = cJSON_Parse(msg);
    const int cmd_id = cJSON_GetObjectItem(root, "id")->valueint;
    const int value = cJSON_GetObjectItem(root, "value")->valueint;
#ifndef TEST
    switch(cmd_id)
    {
        case CMD_TAKEOFF:
            device->aRDrone3->sendPilotingTakeOff(device->aRDrone3);
            break;
        case CMD_LAND:
            device->aRDrone3->sendPilotingLanding(device->aRDrone3);
            break;
        case CMD_EMERGENCY:
            device->aRDrone3->sendPilotingEmergency(device->aRDrone3);
            break;
        case CMD_ROLL:
            device->aRDrone3->setPilotingPCMDRoll(device->aRDrone3, value);
            device->aRDrone3->setPilotingPCMDFlag(device->aRDrone3, 1);
            break;
        case CMD_FLIP:
            device->aRDrone3->sendAnimationsFlip(device->aRDrone3, value);
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
    zsock_t *pull = zsock_new_pull("tcp://*:LISTEN_PORT");
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
