/*---------------------------------------------------------*\
| RedragonK556Controller.h                                  |
|                                                           |
|   Driver for Redragon K556 Devarajas RGB keyboard         |
|   (firmware v1.07, Sonix SN32F248B MCU)                   |
|                                                           |
|   Based on EVisionKeyboardController by                   |
|   Adam Honse (CalcProgrammer1)                            |
|                                                           |
|   This file is part of the OpenRGB project                |
|   SPDX-License-Identifier: GPL-2.0-or-later               |
\*---------------------------------------------------------*/

#pragma once

#include <string>
#include <hidapi.h>
#include "RGBController.h"

#define K556_MAX_PACKET_SIZE                    ( 0x36 )

enum
{
    K556_COMMAND_BEGIN                          = 0x01,
    K556_COMMAND_END                            = 0x02,
    K556_COMMAND_SET_PARAMETER                  = 0x06,
    K556_COMMAND_READ_CUSTOM_COLOR_DATA         = 0x10,
    K556_COMMAND_WRITE_CUSTOM_COLOR_DATA        = 0x11,
};

enum
{
    K556_PARAMETER_MODE                         = 0x00,
    K556_PARAMETER_BRIGHTNESS                   = 0x01,
    K556_PARAMETER_SPEED                        = 0x02,
    K556_PARAMETER_DIRECTION                    = 0x03,
    K556_PARAMETER_RANDOM_COLOR_FLAG            = 0x04,
    K556_PARAMETER_MODE_COLOR                   = 0x05,
};

/*---------------------------------------------------------*\
| Mode IDs for Redragon K556 firmware v1.07                 |
| Probed via HID - these differ from generic EVision        |
\*---------------------------------------------------------*/
enum
{
    K556_MODE_BREATHING                         = 0x01,
    K556_MODE_COLOR_WAVE                        = 0x02,
    K556_MODE_BREATHING_2                       = 0x03,
    K556_MODE_BREATHING_3                       = 0x05,
    K556_MODE_STATIC                            = 0x06,
    K556_MODE_REACTIVE_RIPPLE                   = 0x08,
    K556_MODE_REACTIVE_LINE                     = 0x09,
    K556_MODE_STARLIGHT                         = 0x0A,
    K556_MODE_SPECTRUM_CYCLE                    = 0x0B,
    K556_MODE_RAINBOW_VERTICAL                  = 0x0C,
    K556_MODE_HURRICANE                         = 0x0D,
    K556_MODE_ACCUMULATE                        = 0x0E,
    K556_MODE_STARLIGHT_SLOW                    = 0x0F,
    K556_MODE_VISOR                             = 0x10,
    K556_MODE_RAINBOW_CIRCLE                    = 0x12,
    K556_MODE_CUSTOM                            = 0x14,
};

enum
{
    K556_BRIGHTNESS_LOWEST                      = 0x00,
    K556_BRIGHTNESS_HIGHEST                     = 0x04,
};

enum
{
    K556_SPEED_FASTEST                          = 0x00,
    K556_SPEED_NORMAL                           = 0x00,
    K556_SPEED_SLOWEST                          = 0x0A,
};

class RedragonK556Controller
{
public:
    RedragonK556Controller(hid_device* dev_handle, const char* path);
    ~RedragonK556Controller();

    std::string GetDeviceLocation();
    std::string GetSerialString();

    void        SetKeyboardColors
                    (
                    unsigned char *     color_data,
                    unsigned int        size
                    );

    void        SendKeyboardBegin();

    void        SendKeyboardModeEx
                    (
                    unsigned char       mode,
                    unsigned char       brightness,
                    unsigned char       speed,
                    unsigned char       direction,
                    unsigned char       random_flag,
                    unsigned char       red,
                    unsigned char       green,
                    unsigned char       blue
                    );

    void        SendKeyboardEnd();

private:
    hid_device*             dev;
    std::string             location;

    void        ComputeChecksum
                    (
                    char                usb_buf[64]
                    );

    void        SendKeyboardData
                    (
                    unsigned char *     data,
                    unsigned char       data_size,
                    unsigned short      data_offset
                    );

    void        SendKeyboardParameter
                    (
                    unsigned char       parameter,
                    unsigned char       parameter_size,
                    unsigned char*      parameter_data
                    );
};
