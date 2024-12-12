#!/usr/bin/env python3

# DX7 CC to SysEx programmer script.
#
# It is designed for 8 CC controls - one of the controls is for selecting the bank of parameters
# and the other 7 are for the parameters themselves.
#
# The suggested layout is to use 4 by 2 knobs, where the top left knob is for the bank selection.
#
# You can override the CC IDs used for the controls by editing /etc/pimidipy.conf and setting the
# following variables:
#
# DX7_BANK_CONTROL_0=30
# DX7_BANK_CONTROL_1=31
# DX7_BANK_CONTROL_2=32
# DX7_BANK_CONTROL_...=...
# DX7_BANK_CONTROL_7=37
#
# The 0 control is the one for selecting the bank.
#
# By default, DX7 Device ID 1 is used, you may override this by setting the DX7_DEVICE_ID environment
# variable in /etc/pimidipy.conf. Use values 0-15 for device IDs 1-16.
#
# You may also map CC controls to DX7 parameters directly by setting the following variables in
# /etc/pimidipy.conf:
#
# DX7_PARAM_n=ch:cc_id   # 'ch' is the MIDI channel number to listen to, use numbers between 0-15 for channels 1-16.
#
# or
#
# DX7_PARAM_n=cc_id      # Channel 1 is assumed, equivalent to 0:cc_id
#
# where 'n' is the DX7 parameter ID (see below comments & code) and 'cc_id' is the CC ID to listen to.
#
# It's also possible to provide more than one CC ID for a parameter by separating them with a comma.
#

# Based on information from https://github.com/asb2m10/dexed/blob/master/Documentation/sysex-format.txt
#
#Parameter
# Number    Parameter                  Value Range
#---------  ---------                  -----------
#  0        OP6 EG rate 1              0-99
#  1         "  "  rate 2               "
#  2         "  "  rate 3               "
#  3         "  "  rate 4               "
#  4         "  " level 1               "
#  5         "  " level 2               "
#  6         "  " level 3               "
#  7         "  " level 4               "
#  8        OP6 KBD LEV SCL BRK PT      "        C3= $27
#  9         "   "   "   "  LFT DEPTH   "
# 10         "   "   "   "  RHT DEPTH   "
# 11         "   "   "   "  LFT CURVE  0-3       0=-LIN, -EXP, +EXP, +LIN
# 12         "   "   "   "  RHT CURVE   "            "    "    "    "  
# 13        OP6 KBD RATE SCALING       0-7
# 14        OP6 AMP MOD SENSITIVITY    0-3
# 15        OP6 KEY VEL SENSITIVITY    0-7
# 16        OP6 OPERATOR OUTPUT LEVEL  0-99
# 17        OP6 OSC MODE (fixed/ratio) 0-1        0=ratio
# 18        OP6 OSC FREQ COARSE        0-31
# 19        OP6 OSC FREQ FINE          0-99
# 20        OP6 OSC DETUNE             0-14       0: det=-7
# 21 \
#  |  > repeat above for OSC 5, OSC 4,  ... OSC 1
#125 /
#126        PITCH EG RATE 1            0-99
#127          "    " RATE 2              "
#128          "    " RATE 3              "
#129          "    " RATE 4              "
#130          "    " LEVEL 1             "
#131          "    " LEVEL 2             "
#132          "    " LEVEL 3             "
#133          "    " LEVEL 4             "
#134        ALGORITHM #                 0-31
#135        FEEDBACK                    0-7
#136        OSCILLATOR SYNC             0-1
#137        LFO SPEED                   0-99
#138         "  DELAY                    "
#139         "  PITCH MOD DEPTH          "
#140         "  AMP   MOD DEPTH          "
#141        LFO SYNC                    0-1
#142         "  WAVEFORM                0-5, (data sheet claims 9-4 ?!?)
#                                       0:TR, 1:SD, 2:SU, 3:SQ, 4:SI, 5:SH
#143        PITCH MOD SENSITIVITY       0-7
#144        TRANSPOSE                   0-48   12 = C2
#145        VOICE NAME CHAR 1           ASCII
#146        VOICE NAME CHAR 2           ASCII
#147        VOICE NAME CHAR 3           ASCII
#148        VOICE NAME CHAR 4           ASCII
#149        VOICE NAME CHAR 5           ASCII
#150        VOICE NAME CHAR 6           ASCII
#151        VOICE NAME CHAR 7           ASCII
#152        VOICE NAME CHAR 8           ASCII
#153        VOICE NAME CHAR 9           ASCII
#154        VOICE NAME CHAR 10          ASCII
#155        OPERATOR ON/OFF
#              bit6 = 0 / bit 5: OP1 / ... / bit 0: OP6

from collections import defaultdict
from pimidipy import *
pimidipy = PimidiPy()

from os import getenv

DX7_DEVICE_ID = getenv("DX7_DEVICE_ID", 0)

DX7_PARAMETERS = [
	{ "id":  0,  "min": 0, "max":  99, "name": "OP6 EG rate 1" },
	{ "id":  1,  "min": 0, "max":  99, "name": "OP6 EG rate 2" },
	{ "id":  2,  "min": 0, "max":  99, "name": "OP6 EG rate 3" },
	{ "id":  3,  "min": 0, "max":  99, "name": "OP6 EG rate 4" },
	{ "id":  4,  "min": 0, "max":  99, "name": "OP6 EG level 1" },
	{ "id":  5,  "min": 0, "max":  99, "name": "OP6 EG level 2" },
	{ "id":  6,  "min": 0, "max":  99, "name": "OP6 EG level 3" },
	{ "id":  7,  "min": 0, "max":  99, "name": "OP6 EG level 4" },
	{ "id":  8,  "min": 0, "max":  99, "name": "OP6 KBD LEV SCL BRK PT" },
	{ "id":  9,  "min": 0, "max":  99, "name": "OP6 KBD LEV SCL LFT DEPTH" },
	{ "id": 10,  "min": 0, "max":  99, "name": "OP6 KBD LEV SCL RHT DEPTH" },
	{ "id": 11,  "min": 0, "max":   3, "name": "OP6 KBD LEV SCL LFT CURVE" },
	{ "id": 12,  "min": 0, "max":   3, "name": "OP6 KBD LEV SCL RHT CURVE" },
	{ "id": 13,  "min": 0, "max":   7, "name": "OP6 KBD RATE SCALING" },
	{ "id": 14,  "min": 0, "max":   3, "name": "OP6 AMP MOD SENSITIVITY" },
	{ "id": 15,  "min": 0, "max":   7, "name": "OP6 KEY VEL SENSITIVITY" },
	{ "id": 16,  "min": 0, "max":  99, "name": "OP6 OPERATOR OUTPUT LEVEL" },
	{ "id": 17,  "min": 0, "max":   1, "name": "OP6 OSC MODE (fixed/ratio)" },
	{ "id": 18,  "min": 0, "max":  31, "name": "OP6 OSC FREQ COARSE" },
	{ "id": 19,  "min": 0, "max":  99, "name": "OP6 OSC FREQ FINE" },
	{ "id": 20,  "min": 0, "max":  14, "name": "OP6 OSC DETUNE" },
	{ "id": 21,  "min": 0, "max":  99, "name": "OP5 EG rate 1" },
	{ "id": 22,  "min": 0, "max":  99, "name": "OP5 EG rate 2" },
	{ "id": 23,  "min": 0, "max":  99, "name": "OP5 EG rate 3" },
	{ "id": 24,  "min": 0, "max":  99, "name": "OP5 EG rate 4" },
	{ "id": 25,  "min": 0, "max":  99, "name": "OP5 EG level 1" },
	{ "id": 26,  "min": 0, "max":  99, "name": "OP5 EG level 2" },
	{ "id": 27,  "min": 0, "max":  99, "name": "OP5 EG level 3" },
	{ "id": 28,  "min": 0, "max":  99, "name": "OP5 EG level 4" },
	{ "id": 29,  "min": 0, "max":  99, "name": "OP5 KBD LEV SCL BRK PT" },
	{ "id": 30,  "min": 0, "max":  99, "name": "OP5 KBD LEV SCL LFT DEPTH" },
	{ "id": 31,  "min": 0, "max":  99, "name": "OP5 KBD LEV SCL RHT DEPTH" },
	{ "id": 32,  "min": 0, "max":   3, "name": "OP5 KBD LEV SCL LFT CURVE" },
	{ "id": 33,  "min": 0, "max":   3, "name": "OP5 KBD LEV SCL RHT CURVE" },
	{ "id": 34,  "min": 0, "max":   7, "name": "OP5 KBD RATE SCALING" },
	{ "id": 35,  "min": 0, "max":   3, "name": "OP5 AMP MOD SENSITIVITY" },
	{ "id": 36,  "min": 0, "max":   7, "name": "OP5 KEY VEL SENSITIVITY" },
	{ "id": 37,  "min": 0, "max":  99, "name": "OP5 OPERATOR OUTPUT LEVEL" },
	{ "id": 38,  "min": 0, "max":   1, "name": "OP5 OSC MODE (fixed/ratio)" },
	{ "id": 39,  "min": 0, "max":  31, "name": "OP5 OSC FREQ COARSE" },
	{ "id": 40,  "min": 0, "max":  99, "name": "OP5 OSC FREQ FINE" },
	{ "id": 41,  "min": 0, "max":  14, "name": "OP5 OSC DETUNE" },
	{ "id": 42,  "min": 0, "max":  99, "name": "OP4 EG rate 1" },
	{ "id": 43,  "min": 0, "max":  99, "name": "OP4 EG rate 2" },
	{ "id": 44,  "min": 0, "max":  99, "name": "OP4 EG rate 3" },
	{ "id": 45,  "min": 0, "max":  99, "name": "OP4 EG rate 4" },
	{ "id": 46,  "min": 0, "max":  99, "name": "OP4 EG level 1" },
	{ "id": 47,  "min": 0, "max":  99, "name": "OP4 EG level 2" },
	{ "id": 48,  "min": 0, "max":  99, "name": "OP4 EG level 3" },
	{ "id": 49,  "min": 0, "max":  99, "name": "OP4 EG level 4" },
	{ "id": 50,  "min": 0, "max":  99, "name": "OP4 KBD LEV SCL BRK PT" },
	{ "id": 51,  "min": 0, "max":  99, "name": "OP4 KBD LEV SCL LFT DEPTH" },
	{ "id": 52,  "min": 0, "max":  99, "name": "OP4 KBD LEV SCL RHT DEPTH" },
	{ "id": 53,  "min": 0, "max":   3, "name": "OP4 KBD LEV SCL LFT CURVE" },
	{ "id": 54,  "min": 0, "max":   3, "name": "OP4 KBD LEV SCL RHT CURVE" },
	{ "id": 55,  "min": 0, "max":   7, "name": "OP4 KBD RATE SCALING" },
	{ "id": 56,  "min": 0, "max":   3, "name": "OP4 AMP MOD SENSITIVITY" },
	{ "id": 57,  "min": 0, "max":   7, "name": "OP4 KEY VEL SENSITIVITY" },
	{ "id": 58,  "min": 0, "max":  99, "name": "OP4 OPERATOR OUTPUT LEVEL" },
	{ "id": 59,  "min": 0, "max":   1, "name": "OP4 OSC MODE (fixed/ratio)" },
	{ "id": 60,  "min": 0, "max":  31, "name": "OP4 OSC FREQ COARSE" },
	{ "id": 61,  "min": 0, "max":  99, "name": "OP4 OSC FREQ FINE" },
	{ "id": 62,  "min": 0, "max":  14, "name": "OP4 OSC DETUNE" },
	{ "id": 63,  "min": 0, "max":  99, "name": "OP3 EG rate 1" },
	{ "id": 64,  "min": 0, "max":  99, "name": "OP3 EG rate 2" },
	{ "id": 65,  "min": 0, "max":  99, "name": "OP3 EG rate 3" },
	{ "id": 66,  "min": 0, "max":  99, "name": "OP3 EG rate 4" },
	{ "id": 67,  "min": 0, "max":  99, "name": "OP3 EG level 1" },
	{ "id": 68,  "min": 0, "max":  99, "name": "OP3 EG level 2" },
	{ "id": 69,  "min": 0, "max":  99, "name": "OP3 EG level 3" },
	{ "id": 70,  "min": 0, "max":  99, "name": "OP3 EG level 4" },
	{ "id": 71,  "min": 0, "max":  99, "name": "OP3 KBD LEV SCL BRK PT" },
	{ "id": 72,  "min": 0, "max":  99, "name": "OP3 KBD LEV SCL LFT DEPTH" },
	{ "id": 73,  "min": 0, "max":  99, "name": "OP3 KBD LEV SCL RHT DEPTH" },
	{ "id": 74,  "min": 0, "max":   3, "name": "OP3 KBD LEV SCL LFT CURVE" },
	{ "id": 75,  "min": 0, "max":   3, "name": "OP3 KBD LEV SCL RHT CURVE" },
	{ "id": 76,  "min": 0, "max":   7, "name": "OP3 KBD RATE SCALING" },
	{ "id": 77,  "min": 0, "max":   3, "name": "OP3 AMP MOD SENSITIVITY" },
	{ "id": 78,  "min": 0, "max":   7, "name": "OP3 KEY VEL SENSITIVITY" },
	{ "id": 79,  "min": 0, "max":  99, "name": "OP3 OPERATOR OUTPUT LEVEL" },
	{ "id": 80,  "min": 0, "max":  1,  "name": "OP3 OSC MODE (fixed/ratio)" },
	{ "id": 81,  "min": 0, "max":  31, "name": "OP3 OSC FREQ COARSE" },
	{ "id": 82,  "min": 0, "max":  99, "name": "OP3 OSC FREQ FINE" },
	{ "id": 83,  "min": 0, "max":  14, "name": "OP3 OSC DETUNE" },
	{ "id": 84,  "min": 0, "max":  99, "name": "OP2 EG rate 1" },
	{ "id": 85,  "min": 0, "max":  99, "name": "OP2 EG rate 2" },
	{ "id": 86,  "min": 0, "max":  99, "name": "OP2 EG rate 3" },
	{ "id": 87,  "min": 0, "max":  99, "name": "OP2 EG rate 4" },
	{ "id": 88,  "min": 0, "max":  99, "name": "OP2 EG level 1" },
	{ "id": 89,  "min": 0, "max":  99, "name": "OP2 EG level 2" },
	{ "id": 90,  "min": 0, "max":  99, "name": "OP2 EG level 3" },
	{ "id": 91,  "min": 0, "max":  99, "name": "OP2 EG level 4" },
	{ "id": 92,  "min": 0, "max":  99, "name": "OP2 KBD LEV SCL BRK PT" },
	{ "id": 93,  "min": 0, "max":  99, "name": "OP2 KBD LEV SCL LFT DEPTH" },
	{ "id": 94,  "min": 0, "max":  99, "name": "OP2 KBD LEV SCL RHT DEPTH" },
	{ "id": 95,  "min": 0, "max":   3, "name": "OP2 KBD LEV SCL LFT CURVE" },
	{ "id": 96,  "min": 0, "max":   3, "name": "OP2 KBD LEV SCL RHT CURVE" },
	{ "id": 97,  "min": 0, "max":   7, "name": "OP2 KBD RATE SCALING" },
	{ "id": 98,  "min": 0, "max":   3, "name": "OP2 AMP MOD SENSITIVITY" },
	{ "id": 99,  "min": 0, "max":   7, "name": "OP2 KEY VEL SENSITIVITY" },
	{ "id": 100, "min": 0, "max":  99, "name": "OP2 OPERATOR OUTPUT LEVEL" },
	{ "id": 101, "min": 0, "max":   1, "name": "OP2 OSC MODE (fixed/ratio)" },
	{ "id": 102, "min": 0, "max":  31, "name": "OP2 OSC FREQ COARSE" },
	{ "id": 103, "min": 0, "max":  99, "name": "OP2 OSC FREQ FINE" },
	{ "id": 104, "min": 0, "max":  14, "name": "OP2 OSC DETUNE" },
	{ "id": 105, "min": 0, "max":  99, "name": "OP1 EG rate 1" },
	{ "id": 106, "min": 0, "max":  99, "name": "OP1 EG rate 2" },
	{ "id": 107, "min": 0, "max":  99, "name": "OP1 EG rate 3" },
	{ "id": 108, "min": 0, "max":  99, "name": "OP1 EG rate 4" },
	{ "id": 109, "min": 0, "max":  99, "name": "OP1 EG level 1" },
	{ "id": 110, "min": 0, "max":  99, "name": "OP1 EG level 2" },
	{ "id": 111, "min": 0, "max":  99, "name": "OP1 EG level 3" },
	{ "id": 112, "min": 0, "max":  99, "name": "OP1 EG level 4" },
	{ "id": 113, "min": 0, "max":  99, "name": "OP1 KBD LEV SCL BRK PT" },
	{ "id": 114, "min": 0, "max":  99, "name": "OP1 KBD LEV SCL LFT DEPTH" },
	{ "id": 115, "min": 0, "max":  99, "name": "OP1 KBD LEV SCL RHT DEPTH" },
	{ "id": 116, "min": 0, "max":   3, "name": "OP1 KBD LEV SCL LFT CURVE" },
	{ "id": 117, "min": 0, "max":   3, "name": "OP1 KBD LEV SCL RHT CURVE" },
	{ "id": 118, "min": 0, "max":   7, "name": "OP1 KBD RATE SCALING" },
	{ "id": 119, "min": 0, "max":   3, "name": "OP1 AMP MOD SENSITIVITY" },
	{ "id": 120, "min": 0, "max":   7, "name": "OP1 KEY VEL SENSITIVITY" },
	{ "id": 121, "min": 0, "max":  99, "name": "OP1 OPERATOR OUTPUT LEVEL" },
	{ "id": 122, "min": 0, "max":   1, "name": "OP1 OSC MODE (fixed/ratio)" },
	{ "id": 123, "min": 0, "max":  31, "name": "OP1 OSC FREQ COARSE" },
	{ "id": 124, "min": 0, "max":  99, "name": "OP1 OSC FREQ FINE" },
	{ "id": 125, "min": 0, "max":  14, "name": "OP1 OSC DETUNE" },
	{ "id": 126, "min": 0, "max":  99, "name": "PITCH EG RATE 1" },
	{ "id": 127, "min": 0, "max":  99, "name": "PITCH EG RATE 2" },
	{ "id": 128, "min": 0, "max":  99, "name": "PITCH EG RATE 3" },
	{ "id": 129, "min": 0, "max":  99, "name": "PITCH EG RATE 4" },
	{ "id": 130, "min": 0, "max":  99, "name": "PITCH EG LEVEL 1" },
	{ "id": 131, "min": 0, "max":  99, "name": "PITCH EG LEVEL 2" },
	{ "id": 132, "min": 0, "max":  99, "name": "PITCH EG LEVEL 3" },
	{ "id": 133, "min": 0, "max":  99, "name": "PITCH EG LEVEL 4" },
	{ "id": 134, "min": 0, "max":  31, "name": "ALGORITHM #" },
	{ "id": 135, "min": 0, "max":   7, "name": "FEEDBACK" },
	{ "id": 136, "min": 0, "max":   1, "name": "OSCILLATOR SYNC" },
	{ "id": 137, "min": 0, "max":  99, "name": "LFO SPEED" },
	{ "id": 138, "min": 0, "max":  99, "name": "LFO DELAY" },
	{ "id": 139, "min": 0, "max":  99, "name": "LFO PITCH MOD DEPTH" },
	{ "id": 140, "min": 0, "max":  99, "name": "LFO AMP MOD DEPTH" },
	{ "id": 141, "min": 0, "max":   1, "name": "LFO SYNC" },
	{ "id": 142, "min": 0, "max":   5, "name": "LFO WAVEFORM" },
	{ "id": 143, "min": 0, "max":   7, "name": "PITCH MOD SENSITIVITY" },
	{ "id": 144, "min": 0, "max":  48, "name": "TRANSPOSE" },
	{ "id": 145, "min": 0, "max": 127, "name": "VOICE NAME CHAR 1" },
	{ "id": 146, "min": 0, "max": 127, "name": "VOICE NAME CHAR 2" },
	{ "id": 147, "min": 0, "max": 127, "name": "VOICE NAME CHAR 3" },
	{ "id": 148, "min": 0, "max": 127, "name": "VOICE NAME CHAR 4" },
	{ "id": 149, "min": 0, "max": 127, "name": "VOICE NAME CHAR 5" },
	{ "id": 150, "min": 0, "max": 127, "name": "VOICE NAME CHAR 6" },
	{ "id": 151, "min": 0, "max": 127, "name": "VOICE NAME CHAR 7" },
	{ "id": 152, "min": 0, "max": 127, "name": "VOICE NAME CHAR 8" },
	{ "id": 153, "min": 0, "max": 127, "name": "VOICE NAME CHAR 9" },
	{ "id": 154, "min": 0, "max": 127, "name": "VOICE NAME CHAR 10" },
	{ "id": 155, "min": 0, "max":  63, "name": "OPERATOR ON/OFF "},
]

DX7_NAME_TO_PARAMETER_ID = { parameter["name"]: parameter["id"] for parameter in DX7_PARAMETERS }

CONTROL_BANKS = [
	{ "name": "OP1 1/3",        "parameters": [ 105, 106, 107, 108, 109, 110, 111 ] },
	{ "name": "OP1 2/3",        "parameters": [ 112, 113, 114, 115, 116, 117, 118 ] },
	{ "name": "OP1 3/3",        "parameters": [ 119, 120, 121, 122, 123, 124, 125 ] },
	{ "name": "OP2 1/3",        "parameters": [  84,  85,  86,  87,  88,  89,  90 ] },
	{ "name": "OP2 2/3",        "parameters": [  91,  92,  93,  94,  95,  96,  97 ] },
	{ "name": "OP2 3/3",        "parameters": [  98,  99, 100, 101, 102, 103, 104 ] },
	{ "name": "OP3 1/3",        "parameters": [  63,  64,  65,  66,  67,  68,  69 ] },
	{ "name": "OP3 2/3",        "parameters": [  70,  71,  72,  73,  74,  75,  76 ] },
	{ "name": "OP3 3/3",        "parameters": [  77,  78,  79,  80,  81,  82,  83 ] },
	{ "name": "OP4 1/3",        "parameters": [  42,  43,  44,  45,  46,  47,  48 ] },
	{ "name": "OP4 2/3",        "parameters": [  49,  50,  51,  52,  53,  54,  55 ] },
	{ "name": "OP4 3/3",        "parameters": [  56,  57,  58,  59,  60,  61,  62 ] },
	{ "name": "OP5 1/3",        "parameters": [  21,  22,  23,  24,  25,  26,  27 ] },
	{ "name": "OP5 2/3",        "parameters": [  28,  29,  30,  31,  32,  33,  34 ] },
	{ "name": "OP5 3/3",        "parameters": [  35,  36,  37,  38,  39,  40,  41 ] },
	{ "name": "OP6 1/3",        "parameters": [   0,   1,   2,   3,   4,   5,   6 ] },
	{ "name": "OP6 2/3",        "parameters": [   7,   8,   9,  10,  11,  12,  13 ] },
	{ "name": "OP6 3/3",        "parameters": [  14,  15,  16,  17,  18,  19,  20 ] },
	{ "name": "PITCH EG Rate",  "parameters": [ 126, 127, 128, 129 ] },
	{ "name": "PITCH EG Level", "parameters": [ 130, 131, 132, 133 ] },
	{ "name": "LFO",            "parameters": [ 137, 138, 139, 140, 141, 142 ] },
	{ "name": "MISC 1/3",       "parameters": [ 134, 135, 136, 143, 144, 145, 146 ] },
	{ "name": "MISC 2/3",       "parameters": [ 147, 148, 149, 150, 151, 152, 153 ] },
	{ "name": "MISC 3/3",       "parameters": [ 154, 155 ] },
]

LONGEST_PARAMETER_NAME_LEN = max([ len(parameter["name"]) for parameter in DX7_PARAMETERS ])

def build_parameter_change_event(device_id, parameter_id, value):
	if device_id < 0 or device_id > 15:
		raise ValueError("Invalid device ID")
	if parameter_id < 0 or parameter_id > len(DX7_PARAMETERS):
		raise ValueError("Invalid parameter ID")
	if value < DX7_PARAMETERS[parameter_id]["min"] or value > DX7_PARAMETERS[parameter_id]["max"]:
		raise ValueError(f"Value '{value}' out of range for parameter '{DX7_PARAMETERS[parameter_id]['name']}'")
	return SysExEvent([ 0xf0, 0x43, 0x10 | device_id, (parameter_id & 0x80) >> 7, (parameter_id & 0x7f), value, 0xf7 ])

def remap_cc_value(cc_value, min_value, max_value):
	return int(min_value + (cc_value / 127.0) * (max_value - min_value))

bank_cc_controls = {}
direct_cc_mappings = defaultdict(list)

for i in range(8):
	id = getenv(f"DX7_BANK_CONTROL_{i}", i)
	if id is not None:
		bank_cc_controls[int(id)] = i

def parse_param_mappings(mappings):
	result = []
	mapping = mappings.split(",")
	for m in mapping:
		if ":" in m:
			channel, cc = m.split(":")
		else:
			channel, cc = (0, m)
		result.append((int(channel), int(cc)))
	return result

for i in range(len(DX7_PARAMETERS)):
	mappings = getenv(f"DX7_PARAM_{i}", None)
	if mappings is not None:
		m = parse_param_mappings(mappings)
		for channel, cc in m:
			direct_cc_mappings[(channel, cc)].append(i)

current_bank = 0

def switch_bank(bank_id):
	global current_bank
	if current_bank != bank_id:
		current_bank = bank_id
		print(" ")
		print(f"Switched to bank {CONTROL_BANKS[current_bank]['name']}, controls:")
		print("[{}]".format("Bank select".ljust(LONGEST_PARAMETER_NAME_LEN)), end=" ")
		for i, param_id in enumerate(CONTROL_BANKS[current_bank]["parameters"]):
			print("[{}]".format(DX7_PARAMETERS[param_id]["name"].ljust(LONGEST_PARAMETER_NAME_LEN)), end=" " if i % 7 != 2 else "\n")
		if i != 2:
			print()

def set_parameter(device_id, param_id, value):
	print(f"Setting {DX7_PARAMETERS[param_id]['name']} to {value}")
	output.write(build_parameter_change_event(device_id, param_id, value))

def handle_cc(cc_channel, cc_id, cc_value):
	global current_bank
	if cc_id in bank_cc_controls:
		id = bank_cc_controls[cc_id]
		if id == 0:
			switch_bank(remap_cc_value(cc_value, 0, len(CONTROL_BANKS) - 1))
		else:
			bank = CONTROL_BANKS[current_bank]
			id -= 1
			if id < len(bank["parameters"]):
				param_id = bank["parameters"][id]
				param_value = remap_cc_value(cc_value, DX7_PARAMETERS[param_id]["min"], DX7_PARAMETERS[param_id]["max"])
				set_parameter(DX7_DEVICE_ID, param_id, param_value)

	for param_id in direct_cc_mappings[(cc_channel, cc_id)]:
		param_value = remap_cc_value(cc_value, DX7_PARAMETERS[param_id]["min"], DX7_PARAMETERS[param_id]["max"])
		set_parameter(DX7_DEVICE_ID, param_id, param_value)

print("DX7 MIDI controller started")

input = pimidipy.open_input(0)
output = pimidipy.open_output(0)

print("Using input port:", input.name)
print("Using output port:", output.name)

def process_midi_message(message):
	if isinstance(message, ControlChangeEvent):
		handle_cc(message.channel, message.control, message.value)
	else:
		# Pass the message through.
		output.write(message)

input.add_callback(process_midi_message)

pimidipy.run()
