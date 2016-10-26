#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>

#include <libARSAL/ARSAL.h>
#include <libARController/ARController.h>
#include <libARDiscovery/ARDiscovery.h>

// Function prototypes
void state_changed(eARCONTROLLER_DEVICE_STATE new_state, eARCONTROLLER_ERROR error, void *custom_data);
void begin_streaming();
eARCONTROLLER_ERROR did_receive_frame_callback(ARCONTROLLER_Frame_t *frame, void *custom_data);
eARCONTROLLER_ERROR decoder_config_callback(ARCONTROLLER_Stream_Codec_t codec, void *custom_data);
void terminate(const char *fifo_file);

// Constants
const char *TAG = "BebopStream";
const char *BEBOP_IP_ADDRESS = "192.168.42.1";
const unsigned BEBOP_DISCOVERY_PORT = 44444;

int failed = 0;
int alive = 1;
FILE *videoOut = NULL;
ARSAL_Sem_t state_sem;
ARCONTROLLER_Device_t *device = NULL;
ARDISCOVERY_Device_t *discovery_device = NULL;
eARCONTROLLER_ERROR error = ARCONTROLLER_OK;
eARCONTROLLER_DEVICE_STATE device_state = ARCONTROLLER_DEVICE_STATE_MAX;

void sighandler(int sig)
{
    fprintf(stderr, "Caught SIGINT\n");
    alive = 0;
    exit(EXIT_SUCCESS);
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <fifo_file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    signal(SIGPIPE, SIG_IGN);
    signal(SIGINT, sighandler);
    const char *fifo_file = argv[1];

    if (mkfifo(fifo_file, 0666) < 0)
    {
        fprintf(stderr, "Failed to create fifo file\n");
        exit(EXIT_FAILURE);
    }
    printf("Ok...waiting on a reader for the pipe\n");

    videoOut = fopen(argv[1], "w");
    if (videoOut == NULL)
    {
        fprintf(stderr, "Failed to open %s for writing\n", argv[1]);
        exit(EXIT_FAILURE);
    }
    else
    {
        begin_streaming();
        while (alive && !failed)
        {
            usleep(50);
        }
        terminate(fifo_file);
    }
}


void terminate(const char *fifo_file)
{
    if (device != NULL)
    {
        device_state = ARCONTROLLER_Device_GetState (device, &error);
        if ((error == ARCONTROLLER_OK) && 
                (device_state != ARCONTROLLER_DEVICE_STATE_STOPPED))
        {
            ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "Disconnecting ...");
            ARCONTROLLER_Device_Stop(device);
        }

        ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "ARCONTROLLER_Device_Delete ...");
        ARCONTROLLER_Device_Delete (&device);

        fflush (videoOut);
        fclose (videoOut);
    }

    if (unlink(fifo_file) == -1)
    {
        perror("Failed to unlink fifo file");
    }

    ARSAL_Sem_Destroy (&(state_sem));
    ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "-- END --");
}

void begin_discovery(ARDISCOVERY_Device_t **device, const char *ip, 
                     const unsigned port)
{
    ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "- init discovery device ... ");
    eARDISCOVERY_ERROR errorDiscovery = ARDISCOVERY_OK;

    *device = ARDISCOVERY_Device_New(&errorDiscovery);
    if (errorDiscovery != ARDISCOVERY_OK)
    {
        ARSAL_PRINT(ARSAL_PRINT_ERROR, TAG, "Discovery error :%s", 
                ARDISCOVERY_Error_ToString(errorDiscovery));
        failed = 1;
        return;
    }

    ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, 
            " - ARDISCOVERY_Device_InitWifi ...");
    errorDiscovery = ARDISCOVERY_Device_InitWifi (*device, 
            ARDISCOVERY_PRODUCT_ARDRONE, "bebop", ip, port);
    if (errorDiscovery != ARDISCOVERY_OK)
    {
        ARSAL_PRINT(ARSAL_PRINT_ERROR, TAG, "Discovery error :%s", 
            ARDISCOVERY_Error_ToString(errorDiscovery));
        failed = 1;
        return;
    }
}

void init_device(ARDISCOVERY_Device_t **discovery_device, 
        ARCONTROLLER_Device_t **device_controller, eARCONTROLLER_ERROR *error)
{
    *device_controller = ARCONTROLLER_Device_New(*discovery_device, error);
    if (*error != ARCONTROLLER_OK)
    {
        ARSAL_PRINT (ARSAL_PRINT_ERROR, TAG, 
                "Creation of device controller failed.");
        failed = 1;
    }
}

void begin_streaming(FILE *fifo)
{
    ARSAL_Sem_Init(&(state_sem), 0, 0);

    // create a discovery device
    begin_discovery(&discovery_device, BEBOP_IP_ADDRESS, BEBOP_DISCOVERY_PORT);
    if (failed)
    {
        return;
    }

    // create a device controller
    init_device(&discovery_device, &device, &error);
    if (failed)
    {
        return;
    }
    else
    {
        ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "- delete discovery device ... ");
        ARDISCOVERY_Device_Delete (&discovery_device);
    }

    // set state change callback
    ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "- set state change callback ... ");
    error = ARCONTROLLER_Device_AddStateChangedCallback(device, 
            state_changed, device);
    if (error != ARCONTROLLER_OK)
    {
        failed = 1;
        ARSAL_PRINT (ARSAL_PRINT_ERROR, TAG, "add State callback failed.");
        return;
    }

    // add the frame received callback to be informed when a streaming frame 
    // has been received from the device
    ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "- set video callback ... ");
    error = ARCONTROLLER_Device_SetVideoStreamCallbacks (device, 
            decoder_config_callback, did_receive_frame_callback, 
            NULL , NULL);
    if (error != ARCONTROLLER_OK)
    {
        ARSAL_PRINT(ARSAL_PRINT_ERROR, TAG, "- error :%", 
                ARCONTROLLER_Error_ToString(error));
        failed = 1;
        return;
    }

    // connect to the drone
    ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "- Connecting ...");
    error = ARCONTROLLER_Device_Start (device);
    if (error != ARCONTROLLER_OK)
    {
        ARSAL_PRINT(ARSAL_PRINT_ERROR, TAG, "- error :%s", 
                ARCONTROLLER_Error_ToString(error));
        failed = 1;
        return;
    }

    // wait state update
    ARSAL_Sem_Wait (&(state_sem));
    device_state = ARCONTROLLER_Device_GetState (device, &error);
    if ((error != ARCONTROLLER_OK) || 
            (device_state != ARCONTROLLER_DEVICE_STATE_RUNNING))
    {
        ARSAL_PRINT(ARSAL_PRINT_ERROR, TAG, "- device state:%d", device_state);
        ARSAL_PRINT(ARSAL_PRINT_ERROR, TAG, "- error:%s", 
                ARCONTROLLER_Error_ToString(error));
        failed = 1;
        return;
    }

    // send the command that tells to the Bebop to begin its streaming
    ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "- enable video streaming ... ");
    error = device->aRDrone3->sendMediaStreamingVideoEnable (device->aRDrone3, 1);
    if (error != ARCONTROLLER_OK)
    {
        ARSAL_PRINT(ARSAL_PRINT_ERROR, TAG, "- error :%s", 
                ARCONTROLLER_Error_ToString(error));
        failed = 1;
        return;
    }
}


// called when the state of the device controller has changed
void state_changed(eARCONTROLLER_DEVICE_STATE new_state, 
        eARCONTROLLER_ERROR error, void *custom_data)
{
    ARSAL_PRINT(ARSAL_PRINT_INFO, TAG, "- state changed: %d ..... ", 
            new_state);

    switch (new_state)
    {
        case ARCONTROLLER_DEVICE_STATE_STOPPED:
        case ARCONTROLLER_DEVICE_STATE_RUNNING:
            ARSAL_Sem_Post (&(state_sem));
            break;
        default:
            break;
    }
}

eARCONTROLLER_ERROR decoder_config_callback(ARCONTROLLER_Stream_Codec_t codec, 
                                            void *custom_data)
{
    printf("oh hi\n");
    if (videoOut != NULL)
    {
        if (codec.type == ARCONTROLLER_STREAM_CODEC_TYPE_H264)
        {
            fwrite(codec.parameters.h264parameters.spsBuffer, 
                    codec.parameters.h264parameters.spsSize, 1, videoOut);
            fwrite(codec.parameters.h264parameters.ppsBuffer, 
                    codec.parameters.h264parameters.ppsSize, 1, videoOut);
            fflush (videoOut);
        }
    }
    else
    {
        ARSAL_PRINT(ARSAL_PRINT_WARNING, TAG, "videoOut is NULL.");
    }

    return ARCONTROLLER_OK;
}


eARCONTROLLER_ERROR did_receive_frame_callback(ARCONTROLLER_Frame_t *frame, 
                                               void *custom_data)
{
    if (videoOut != NULL)
    {
        if (frame != NULL)
        {
            fwrite(frame->data, frame->used, 1, videoOut);
            fflush (videoOut);
        }
        else
        {
            ARSAL_PRINT(ARSAL_PRINT_WARNING, TAG, "frame is NULL.");
        }
    }
    else
    {
        ARSAL_PRINT(ARSAL_PRINT_WARNING, TAG, "videoOut is NULL.");
    }

    return ARCONTROLLER_OK;
}
