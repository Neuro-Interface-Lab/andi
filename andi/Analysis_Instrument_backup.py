"""
    Python library to use Analog Discovery 2
    Authors: Florian Kolbl / Yannick Bornat
    (c) ETIS - University Cergy-Pontoise
        IMS - University of Bordeaux
        CNRS

    Requires:
        Python 3.6
        dwfconstants.py from digilent (revision 2019-10-15)
        dwf framework installed (provided with digilent 'waveforms' software)
            tested with version 3.12.1

    dev notes:
        - FK 04/02/2021: avoid spaces for indentation, only use tabs
                            all changed, cause a segmentation fault on top layer classes
        - LR 14/04/2021: Add Vrange1 and Vrange2 to bode measurement method
"""


# required libraries
import sys
import ctypes       as ct
import numpy        as np
from   warnings     import warn
from   time         import sleep
import faulthandler
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import dwfconstants as DWFC

faulthandler.enable()


OutputFunctionModesByName = {
        "DC":       DWFC.funcDC,
        "Sine":     DWFC.funcSine,
        "Square":   DWFC.funcSquare,
        "Triangle": DWFC.funcTriangle,
        "Rampup":   DWFC.funcRampUp,
        "Rampdown": DWFC.funcRampDown,
        "Noise":    DWFC.funcNoise,
        "Custom":   DWFC.funcCustom,
        "Play":     DWFC.funcPlay
    }

AcquisitionModeByName = {
        "Single":     DWFC.acqmodeSingle,
        "ScanShift":  DWFC.acqmodeScanShift,
        "ScanScreen": DWFC.acqmodeScanScreen,
        "Record":     DWFC.acqmodeRecord,
    }

TriggerSourceByName = {
        "None":              DWFC.trigsrcNone,
        "PC":                DWFC.trigsrcPC,
        "DetectorAnalogIn":  DWFC.trigsrcDetectorAnalogIn,
        "DetectorDigitalIn": DWFC.trigsrcDetectorDigitalIn,
        "AnalogIn":          DWFC.trigsrcAnalogIn,
        "DigitalIn":         DWFC.trigsrcDigitalIn,
        "DigitalOut":        DWFC.trigsrcDigitalOut,
        "AnalogOut1":        DWFC.trigsrcAnalogOut1,
        "AnalogOut2":        DWFC.trigsrcAnalogOut2,
        "AnalogOut3":        DWFC.trigsrcAnalogOut3,
        "AnalogOut4":        DWFC.trigsrcAnalogOut4,
        "External1":         DWFC.trigsrcExternal1,
        "External2":         DWFC.trigsrcExternal2,
        "External3":         DWFC.trigsrcExternal3,
        "External4":         DWFC.trigsrcExternal4,
        "High":              DWFC.trigsrcHigh,
        "Low":               DWFC.trigsrcLow
    }

TriggerSlopeByName = {
        "rising":  DWFC.DwfTriggerSlopeRise,
        "falling": DWFC.DwfTriggerSlopeFall,
        "either":  DWFC.DwfTriggerSlopeEither
    }

TRIGG_REF_CENTER    = 0    # trigger reference is on the center
TRIGG_REF_LEFT      = 1    # trigger reference is on the left side
TRIGG_REF_RIGHT     = 2    # trigger reference is on the right side
TRIGG_REF_PURELEFT  = 3    # trigger reference is on the left border
TRIGG_REF_PURERIGHT = 4    # trigger reference is on the right border

TriggerReference = {
        "center":       TRIGG_REF_CENTER,
        "left":         TRIGG_REF_LEFT,
        "right":        TRIGG_REF_RIGHT,
        "left border":  TRIGG_REF_PURELEFT,
        "right border": TRIGG_REF_PURERIGHT
    }

AnalogImpedancesByName = {
        "Impedance" : 				DWFC.DwfAnalogImpedanceImpedance,
        "ImpedancePhase" : 			DWFC.DwfAnalogImpedanceImpedancePhase,
        "Resistance" : 				DWFC.DwfAnalogImpedanceResistance,
        "Reactance" : 				DWFC.DwfAnalogImpedanceReactance,
        "Admittance" : 				DWFC.DwfAnalogImpedanceAdmittance,
        "AdmittancePhase" : 		DWFC.DwfAnalogImpedanceAdmittancePhase,
        "Conductance" : 			DWFC.DwfAnalogImpedanceConductance,
        "Susceptance" : 			DWFC.DwfAnalogImpedanceSusceptance,
        "SeriesCapacitance" : 		DWFC.DwfAnalogImpedanceSeriesCapactance,
        "ParallelCapcitance" : 		DWFC.DwfAnalogImpedanceParallelCapacitance,
        "SeriesInductance" : 		DWFC.DwfAnalogImpedanceSeriesInductance,
        "ParallelInductance" : 		DWFC.DwfAnalogImpedanceParallelInductance,
        "ImpedanceDissipation" : 	DWFC.DwfAnalogImpedanceDissipation,
        "ImpedanceQuality" : 		DWFC.DwfAnalogImpedanceQuality,
    }

InstrumentState = {
        "Ready" : 		DWFC.DwfStateReady,
        "Config" : 		DWFC.DwfStateConfig,
        "Prefill" : 	DWFC.DwfStatePrefill,
        "Armed" : 		DWFC.DwfStateArmed,
        "Wait" : 		DWFC.DwfStateWait,
        "Triggered" : 	DWFC.DwfStateTriggered,
        "Running" : 	DWFC.DwfStateRunning,
        "Done" : 		DWFC.DwfStateDone,
    }

SPIDataIdx = {
        "DQ0_MOSI_SISO" :	ct.c_int(0),
        "DQ1_MISO" :		ct.c_int(1),
        "DQ2" : 			ct.c_int(2),
        "DQ3" : 			ct.c_int(3),
    }

SPIMode = {
        "CPOL_0_CPA_0" :	ct.c_int(0),
        "CPOL_0_CPA_1" :	ct.c_int(1),
        "CPOL_1_CPA_0" :	ct.c_int(2),
        "CPOL_1_CPA_1" :	ct.c_int(3),
    }

LogicLevel = {
        "H" :	ct.c_int(1),
        "L" :	ct.c_int(0),
        "Z" :	ct.c_int(-1),
    }

SPI_cDQ = {
        "SISO" : 		ct.c_int(0),
        "MOSI/MISO" : 	ct.c_int(1),
        "dual" : 		ct.c_int(2),
        "quad" : 		ct.c_int(3),
    }

OutputFunctionModesById = { }
for name, id in OutputFunctionModesByName.items():
    OutputFunctionModesById[id.value]=name
AcquisitionModeById = {}
for name, id in AcquisitionModeByName.items():
    AcquisitionModeById[id.value]=name
TriggerSourceById = {}
for name, id in TriggerSourceByName.items():
    TriggerSourceById[id.value]=name
TriggerSlopeById = {}
for name, id in TriggerSlopeByName.items():
    TriggerSlopeById[id.value]=name


# Analog Device Waveform SDK loader
if sys.platform.startswith("win"):
    dwf = ct.cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = ct.cdll.LoadLibrary("/Applications/WaveForms.app/Contents/Frameworks/dwf.framework/dwf")
else:
    dwf = ct.cdll.LoadLibrary("libdwf.so")

#check library loading errors
szerr = ct.create_string_buffer(512)
dwf.FDwfGetLastErrorMsg(szerr)
if szerr[0] != b'\0':
    print(str(szerr.value))
    raise Exception("Error Loading dwf Library !")


def eng_format(v):
    if v<0.0000001:
        return "    0"
    if v<0.001:
        return "{:5.1f}u".format(v*1000000)    
    if v<0.01:
        return "{:4.2f}m".format(v*1000)
    if v<0.1:
        return "{:4.1f}m".format(v*1000)
    if v<1:
        return "{:3.0f}m".format(v*1000)
    if v<10:
        return "{:5.3f}".format(v)
    if v<100:
        return "{:5.2f}".format(v)
    if v<1000:
        return "{:3.0f}".format(v)
    if v<10000:
        return "{:4.2f}k".format(v/1000)
    if v<100000:
        return "{:4.1f}k".format(v/1000)
    if v<1000000:
        return "{:3.0f}k".format(v/1000)
    return "{:4.1f}M".format(v/1000000)

def issue_warning(s):
    #warn("\n--------\nWARNING: {}\n--------".format(s))
    print("WARNING: {}".format(s))

# Print iterations progress, taken from slackoverflow
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


# ███████ ███    ██ ███    ██ ██    ██ ███    ███ ███████ ██████   █████  ████████ ██  ██████  ███    ██
# ██      ████   ██ ████   ██ ██    ██ ████  ████ ██      ██   ██ ██   ██    ██    ██ ██    ██ ████   ██
# █████   ██ ██  ██ ██ ██  ██ ██    ██ ██ ████ ██ █████   ██████  ███████    ██    ██ ██    ██ ██ ██  ██
# ██      ██  ██ ██ ██  ██ ██ ██    ██ ██  ██  ██ ██      ██   ██ ██   ██    ██    ██ ██    ██ ██  ██ ██
# ███████ ██   ████ ██   ████  ██████  ██      ██ ███████ ██   ██ ██   ██    ██    ██  ██████  ██   ████
def nb_connected_devices():
    # ctype variables declaration
    cDevice = ct.c_int()
    # Device enumration
    dwf.FDwfEnum(ct.c_int(0), ct.byref(cDevice))
    return cDevice.value

def device_name(device_number):
    # ctype variables declaration
    devicename = ct.create_string_buffer(64)
    # retrieve name
    dwf.FDwfEnumDeviceName (ct.c_int(device_number), devicename)
    return devicename.value

def device_SerialNumber(device_number):
    # ctype variables declaration
    serialnum = ct.create_string_buffer(16)
    # retrieve serial number
    dwf.FDwfEnumSN (ct.c_int(device_number), serialnum)
    return serialnum.value

def is_opened(device_number):
    # ctype variables declaration
    IsInUse = ct.c_bool()
    # check if the device is already used
    dwf.FDwfEnumDeviceIsOpened(ct.c_int(device_number), ct.byref(IsInUse))
    return IsInUse

def find_first_free_device():
    NB_dev = nb_connected_devices()
    if NB_dev == 0:
        return None
    else:
        dev = 0
        found_one = False
        first_one = 0
        while dev<NB_dev and found_one == False:
            found_one = is_opened(dev)
            dev += 1
        if found_one == False:
            return None
        else:
            return first_one

def open_device(device_number):
    #2020/03/23: complain to YB if you do not agree...
    issue_warning("function open_device() is deprecated, use Andi() instance instead")
    hdwf = ct.c_int()
    dwf.FDwfDeviceOpen(ct.c_int(device_number), ct.byref(hdwf))
    return hdwf

def close_device(hdwf):
    #2020/03/20: complain to YB if you do not agree...
    issue_warning("function close_device() is deprecated, use Andi.close() instead")
    dwf.FDwfDeviceClose(hdwf)

#  █████  ███    ██ ██████  ██      ██████ ██       █████  ███████ ███████
# ██   ██ ████   ██ ██   ██ ██     ██      ██      ██   ██ ██      ██
# ███████ ██ ██  ██ ██   ██ ██     ██      ██      ███████ ███████ ███████
# ██   ██ ██  ██ ██ ██   ██ ██     ██      ██      ██   ██      ██      ██
# ██   ██ ██   ████ ██████  ██      ██████ ███████ ██   ██ ███████ ███████

######################################
## Class for simple use of a device ##
######################################
class Andi(object):
    """docstring for Andi
    This class handles the Analog Discovery 2 device
    """
    def __init__(self, *arg):
        """
        Opens an Analog Discovery 2 device.
        if no argument is given, opens the first available device
        if an integer value 'n' is given, opens the nth device found
        if a string is given, opens the device which has the corresponding
            serial number. Prefer this method if several devices are connected
            to the same computer
        """
        super(Andi, self).__init__()
        self.arg = arg

        #number of connected devices
        cDevices = ct.c_int()
        dwf.FDwfEnum(ct.c_int(0), ct.byref(cDevices))
        if len(arg) == 0:
            test = find_first_free_device()
            if test == None:
                raise Exception('Error: No connected or free device')
            self.andi_number = test
        elif isinstance(arg[0], str):
            serialnum = ct.create_string_buffer(16)
            self.andi_number = None
            for dev in range(cDevices.value):
                # retrieve serial number
                dwf.FDwfEnumSN (ct.c_int(dev), serialnum)
                serialstr = serialnum.value.decode()
                if serialstr[-6:]==arg[0][-6:]:
                    self.andi_number = dev
                    break
            if self.andi_number == None:
                raise Exception("Cannof find device {}".format(arg[0]))
        else:
            self.andi_number = arg[0]

        if is_opened(self.andi_number) == True:
            raise Exception('Error: device already used')

        # Store usefull infos
        self.andi_ID = ct.c_int(self.andi_number)
        self.name =  device_name(self.andi_number)
        self.serialnumber = device_SerialNumber(self.andi_number)
        # Open the device
        self.hdwf = ct.c_int()
        dwf.FDwfDeviceOpen(ct.c_int(self.andi_number), ct.byref(self.hdwf))
        # these are default values
        self.trigg_ref         = TRIGG_REF_CENTER
        self.trigg_position    = 0
        self.acq_freq          = None             # this is to manage acq when set_acq has not been set
        self.warn_analog_trigg = False
        self.in_average_filter_mode(-1)			#input channel are in average mode by default
        self.in_channel_range_set(-1,5.0)		#5.0V input range by default



    #########################################
    ## basic methods for device management ##
    #########################################
    def close(self):
        dwf.FDwfDeviceClose(self.hdwf)

    def __str__(self):
        s = "< Andi {}:{}>".format(self.andi_ID.value, self.serialnumber.decode()[3:])
        return s

    def __repr__(self):
        s = f"Andi({self.andi_ID})"
        return s

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        dwf.FDwfAnalogOutConfigure(self.hdwf, ct.c_int(-1), ct.c_bool(False))       # disables all generator channels
        dwf.FDwfAnalogInChannelEnableSet(self.hdwf, ct.c_int(-1), ct.c_bool(False)) # disables all recording channels
        dwf.FDwfAnalogIOEnableSet(self.hdwf, ct.c_int(False))                       # disables analog output
        dwf.FDwfDeviceClose(self.hdwf)                                              # closes connection to the device
        return False

    def disp_stats(self, header=""):
        print("{}Device ID       : {}".format(header, self.andi_ID.value))
        print("{}Name            : {}".format(header, self.name.decode()))
        print("{}serial          : {}".format(header, self.serialnumber.decode()))
        print("{}----------------------------------------------------------------".format(header))
        print("{}                      Value |       Min |        Max |    Steps".format(header))
        for c in range(self.out_channel_count()):
            if not self.is_out_channel_enable(c):
                print("{}Output channel {} - Disabled".format(header, c))
                continue
            print("{}Output channel {}".format(header, c))
            print("{}    Function    : {}".format(header, self.out_get_function(c)))
            t=self.out_frequency_info(c)
            print("{}    Frequency   : {:>9} | {:>9} | {:>9}".format(header, eng_format(self.out_get_freq(c)), eng_format(t[0]), eng_format(t[1])))
            t=self.out_amplitude_info(c)
            print("{}    Amplitude   : {:>9} | {:>9} | {:>9}".format(header, eng_format(self.out_get_Amp(c)), eng_format(t[0]), eng_format(t[1])))
            t=self.out_offset_info(c)
            print("{}    Offset      : {:>9} | {:>9} | {:>9}".format(header, eng_format(self.out_get_Offset(c)), eng_format(t[0]), eng_format(t[1])))
            t=self.out_symmetry_info(c)
            print("{}    Symetry     : {:>8}% | {:>8}% | {:>8}%".format(header, eng_format(self.out_get_Symmetry(c)), eng_format(t[0]), eng_format(t[1])))
            t=self.out_phase_info(c)
            print("{}    phase       : {:>9} | {:>9} | {:>9}".format(header, eng_format(self.out_get_Phase(c)), eng_format(t[0]), eng_format(t[1])))
        for c in range(self.in_channel_count()):
            if not self.is_in_channel_enable(c):
                print("{}Input channel {} - Disabled".format(header, c))
                continue
            print("{}Input channel {} ({} bits ADC)".format(header, c, self.in_bits_info()))
            t=self.in_channel_range_info(c)
            print("{}    Range       : {:>9} | {:>9} | {:>9} | {:>9}".format(header, eng_format(self.in_channel_range_get(c)), eng_format(t[0]), eng_format(t[1]), eng_format(t[2])))
            t=self.in_channel_offset_info(c)
            print("{}    Offset      : {:>9} | {:>9} | {:>9} | {:>9}".format(header, eng_format(self.in_channel_offset_get(c)), eng_format(t[0]), eng_format(t[1]), eng_format(t[2])))
            print("{}    Attenuation : {:>9} | {:>9} | {:>9}".format(header, eng_format(self.in_channel_attenuation_get(c)), " ", " "))
        print("{}Timebase".format(header))
        t=self.in_frequency_info()
        print("{}    Frequency   : {:>9} | {:>9} | {:>9}".format(header, eng_format(self.in_sampling_freq_get()), eng_format(t[0]), eng_format(t[1])))
        t=self.in_buffer_size_info()
        print("{}    Samples     : {:>9} | {:>9} | {:>9}".format(header, eng_format(self.in_buffer_size_get()), eng_format(t[0]), eng_format(t[1])))
        print("{}Analog trigger".format(header))
        t=self.get_trigger_threshold_info()
        print("{}    Threshold   : {:>9} | {:>9} | {:>9} | {:>9}".format(header, eng_format(self.get_trigger_threshold_value()), eng_format(t[0]), eng_format(t[1]), eng_format(t[2])))
        t=self.get_trigger_hysteresis_info()
        print("{}    Hysteresis  : {:>9} | {:>9} | {:>9} | {:>9}".format(header, eng_format(self.get_trigger_hysteresis_value()), eng_format(t[0]), eng_format(t[1]), eng_format(t[2])))

    def disable_auto_config(self):
        dwf.FDwfDeviceAutoConfigureSet(self.hdwf, ct.c_int(0))

    def enable_auto_config(self):
        dwf.FDwfDeviceAutoConfigureSet(self.hdwf, ct.c_int(1))

    def enable_dynamic_auto_config(self):
        dwf.FDwfDeviceAutoConfigureSet(self.hdwf, ct.c_int(3))

    def print_last_error_message(self):
        szerr = ct.create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))

    #  ██████  ███████ ███    ██ ███████ ██████   █████  ████████  ██████  ██████
    # ██       ██      ████   ██ ██      ██   ██ ██   ██    ██    ██    ██ ██   ██
    # ██   ███ █████   ██ ██  ██ █████   ██████  ███████    ██    ██    ██ ██████
    # ██    ██ ██      ██  ██ ██ ██      ██   ██ ██   ██    ██    ██    ██ ██   ██
    #  ██████  ███████ ██   ████ ███████ ██   ██ ██   ██    ██     ██████  ██   ██
    ###################################
    ## methods for generator control ##
    ###################################
    def out_channel_count(self):
        Count_channels = ct.c_int()
        dwf.FDwfAnalogOutCount(self.hdwf,ct.byref(Count_channels))
        return Count_channels.value

    def reset_out(self, channel):
        dwf.FDwfAnalogOutReset(self.hdwf,ct.c_int(channel))

    def enable_out_channel(self,channel):
        dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_bool(True))

    def disable_out_channel(self,channel):
        dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_bool(False))

    def is_out_channel_enable(self,channel):
        IsEnable = ct.c_bool()
        dwf.FDwfAnalogOutNodeEnableGet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(IsEnable))
        return IsEnable.value

    def out_frequency_info(self,channel):
        f_min = ct.c_double()
        f_max = ct.c_double()
        dwf.FDwfAnalogOutNodeFrequencyInfo(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(f_min), ct.byref(f_max))
        return [f_min.value, f_max.value]

    def out_amplitude_info(self,channel):
        A_min = ct.c_double()
        A_max = ct.c_double()
        dwf.FDwfAnalogOutNodeAmplitudeInfo(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(A_min), ct.byref(A_max))
        return [A_min.value, A_max.value]

    def out_offset_info(self,channel):
        O_min = ct.c_double()
        O_max = ct.c_double()
        dwf.FDwfAnalogOutNodeOffsetInfo(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(O_min), ct.byref(O_max))
        return [O_min.value, O_max.value]

    def out_symmetry_info(self,channel):
        S_min = ct.c_double()
        S_max = ct.c_double()
        dwf.FDwfAnalogOutNodeSymmetryInfo(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(S_min), ct.byref(S_max))
        return [S_min.value, S_max.value]

    def out_phase_info(self,channel):
        P_min = ct.c_double()
        P_max = ct.c_double()
        dwf.FDwfAnalogOutNodePhaseInfo(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(P_min), ct.byref(P_max))
        return [P_min.value, P_max.value]

    def out_data_info(self,channel):
        D_min = ct.c_int()
        D_max = ct.c_int()
        dwf.FDwfAnalogOutNodeDataInfo(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(D_min), ct.byref(D_max))
        return [D_min.value, D_max.value]

    def out_run_info(self,channel):
        T_min = ct.c_double()
        T_max = ct.c_double()
        dwf.FDwfAnalogOutNodeDataInfo(self.hdwf, ct.c_int(channel), ct.byref(T_min), ct.byref(T_max))
        return [T_min.value, T_max.value]

    def out_channel_on(self,channel):
        dwf.FDwfAnalogOutConfigure(self.hdwf, ct.c_int(channel), ct.c_bool(True))

    def out_channel_off(self,channel):
        dwf.FDwfAnalogOutConfigure(self.hdwf, ct.c_int(channel), ct.c_bool(False))

    ###################################
    ## methods for signal generation ##
    ###################################
    ## Basic methods
    def out_set_function(self,channel,function):
        """function can be either:
        (DC, Sine, Square, Triangle, Rampup, Rampdown, Noise, Custom, Play)
        """
        func = OutputFunctionModesByName.get(function, "Invalid function")
        if func == 'Invalid function':
            raise Exception('Invalid generator function : {}'.format(function))
        dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, func)

    def out_get_function(self,channel):
        func = ct.c_ubyte()
        dwf.FDwfAnalogOutNodeFunctionGet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(func))
        return OutputFunctionModesById[func.value]

    def out_set_freq(self,channel,freq):
        dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_double(freq))

    def out_get_freq(self,channel):
        freq = ct.c_double()
        dwf.FDwfAnalogOutNodeFrequencyGet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(freq))
        return freq.value

    def out_set_Amp(self,channel,Amp):
        dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_double(Amp))

    def out_get_Amp(self,channel):
        Amp = ct.c_double()
        dwf.FDwfAnalogOutNodeAmplitudeGet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(Amp))
        return Amp.value

    def out_set_Offset(self,channel,Offset):
        dwf.FDwfAnalogOutNodeOffsetSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_double(Offset))

    def out_get_Offset(self,channel):
        Offset = ct.c_double()
        dwf.FDwfAnalogOutNodeOffsetGet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(Offset))
        return Offset.value

    def out_set_Symmetry(self,channel,Symmetry):
        dwf.FDwfAnalogOutNodeSymmetrySet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_double(Symmetry))

    def out_get_Symmetry(self,channel):
        Symmetry = ct.c_double()
        dwf.FDwfAnalogOutNodeSymmetryGet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(Symmetry))
        return Symmetry.value

    def out_set_Phase(self,channel,Phase):
        dwf.FDwfAnalogOutNodePhaseSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_double(Phase))

    def out_get_Phase(self,channel):
        Phase = ct.c_double()
        dwf.FDwfAnalogOutNodePhaseGet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.byref(Phase))
        return Phase.value

    def out_set_Data(self,channel,data):
        # code 
        dataf = data.astype(np.float64)
        # AnalogOut expects double normalized to +/-1 value
        if np.dtype(data[0]) == np.int8 or np.dtype(data[0]) == np.uint8 :
            # Scaling: UINT8
            dataf /= 128.0
            dataf -= 1.0
        elif np.dtype(data[0]) == np.int16 :
            # Scaling: INT16
            dataf /= 32768.0
        elif np.dtype(data[0]) == np.int32 :
            # Scaling: INT32"
            dataf /= 2147483648.0
        data_c = (ct.c_double * len(dataf))(*dataf)
        # check Data max size
        [D_min,D_max] = self.out_data_info(channel)	
        cBuffer = ct.c_int(0)
        if (D_max) > len(dataf):
            cBuffer.value = len(data)
        else:
            cBuffer.value = int(D_max/D_min)
        dwf.FDwfAnalogOutNodeDataSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, data_c, cBuffer)

    ## Simple generators
    def sine(self,channel,freq,amp,offset = 0,symmetry = 50, phase = 0, activate = True):
        self.reset_out(channel)
        self.enable_out_channel(channel)
        self.out_channel_off(channel)
        self.out_set_function(channel,'Sine')
        self.out_set_freq(channel,freq)
        self.out_set_Amp(channel,amp)
        self.out_set_Offset(channel,offset)
        self.out_set_Symmetry(channel,symmetry)
        self.out_set_Phase(channel,phase)
        if (activate):
            self.out_channel_on(channel)

    def square(self,channel,freq,amp,offset = 0,symmetry = 50, phase = 0, activate = True):
        self.reset_out(channel)
        self.enable_out_channel(channel)
        self.out_channel_off(channel)
        self.out_set_function(channel,'Square')
        self.out_set_freq(channel,freq)
        self.out_set_Amp(channel,amp)
        self.out_set_Offset(channel,offset)
        self.out_set_Symmetry(channel,symmetry)
        self.out_set_Phase(channel,phase)
        if (activate):
            self.out_channel_on(channel)

    def triangle(self,channel,freq,amp,offset = 0,symmetry = 50, phase = 0, activate = True):
        self.reset_out(channel)
        self.enable_out_channel(channel)
        self.out_channel_off(channel)
        self.out_set_function(channel,'Triangle')
        self.out_set_freq(channel,freq)
        self.out_set_Amp(channel,amp)
        self.out_set_Offset(channel,offset)
        self.out_set_Symmetry(channel,symmetry)
        self.out_set_Phase(channel,phase)
        if (activate):
            self.out_channel_on(channel)

    def rampup(self,channel,freq,amp,offset = 0,symmetry = 50, phase = 0):
        print('to be coded')

    def rampdown(self,channel,freq,amp,offset = 0,symmetry = 50, phase = 0):
        print('to be coded')

    def noise(self,channel,freq,amp,offset = 0):
        print('to be coded')
    ## Advanced generators

    def custom(self,channel,fs,data):

        N_samples = len(data)

        pattern_frequency = fs/N_samples

        max_val = np.max(np.abs(data))

        data_normalized = data/max_val

        dwf.FDwfAnalogOutReset(self.hdwf, ct.c_int(channel))
        dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, DWFC.funcCustom) 

        rgdSamples = (ct.c_double*N_samples)()
        for i in range(0,len(rgdSamples)):
            rgdSamples[i] = data[i]

        dwf.FDwfAnalogOutNodeDataSet(self.hdwf, channel, DWFC.AnalogOutNodeCarrier, rgdSamples, ct.c_int(N_samples))
        dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_double(pattern_frequency)) 
        dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, ct.c_int(channel), DWFC.AnalogOutNodeCarrier, ct.c_double(max_val)) 
        dwf.FDwfAnalogOutConfigure(self.hdwf, ct.c_int(channel), ct.c_bool(True))


    # ███████  ██████  ██████  ██████  ███████
    # ██      ██      ██    ██ ██   ██ ██
    # ███████ ██      ██    ██ ██████  █████
    #      ██ ██      ██    ██ ██      ██
    # ███████  ██████  ██████  ██      ███████

    ###############################
    ## methods for scope control ##
    ###############################
    def in_channel_count(self):
        Count_channels = ct.c_int()
        dwf.FDwfAnalogInChannelCount(self.hdwf,ct.byref(Count_channels))
        return Count_channels.value

    def reset_in(self):
        dwf.FDwfAnalogInReset(self.hdwf)

    def in_channels_start(self):
        dwf.FDwfAnalogInConfigure(self.hdwf, ct.c_bool(False), ct.c_bool(True))

    def in_channels_stop(self):
        dwf.FDwfAnalogInConfigure(self.hdwf, ct.c_bool(False), ct.c_bool(False))

    def in_frequency_info(self):
        F_min = ct.c_double()
        F_max = ct.c_double()
        dwf.FDwfAnalogInFrequencyInfo(self.hdwf, ct.byref(F_min), ct.byref(F_max))
        return [F_min.value, F_max.value]

    def in_sampling_freq_set(self,freq):
        dwf.FDwfAnalogInFrequencySet(self.hdwf,ct.c_double(freq))

    def in_sampling_freq_get(self):
        freq = ct.c_double()
        dwf.FDwfAnalogInFrequencyGet(self.hdwf,ct.byref(freq))
        return freq.value
    

    def in_bits_info(self):
        Nbits = ct.c_int()
        dwf.FDwfAnalogInBitsInfo(self.hdwf, ct.byref(Nbits))
        return Nbits.value

    def in_buffer_size_info(self):
        S_min = ct.c_int()
        S_max = ct.c_int()
        dwf.FDwfAnalogInBufferSizeInfo(self.hdwf, ct.byref(S_min), ct.byref(S_max))
        return [S_min.value, S_max.value]

    def in_buffer_size_set(self,size):
        dwf.FDwfAnalogInBufferSizeSet(self.hdwf,ct.c_int(size))

    def in_buffer_size_get(self):
        size = ct.c_int()
        dwf.FDwfAnalogInBufferSizeGet(self.hdwf,ct.byref(size))
        return size.value

    def in_set_aquisition_mode(self,mode):
        aqmode = AcquisitionModeByName.get(mode, "Invalid mode")
        if aqmode == 'Invalid mode':
            print('Error: wrong aquisition mode, scope fail...')
            quit()
        else:
            dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, aqmode)

    #################################
    ## methods for scope recording ##
    #################################
    ## channel configuration methods
    def in_enable_channel(self,channel):
        dwf.FDwfAnalogInChannelEnableSet(self.hdwf, ct.c_int(channel), ct.c_bool(True))

    def in_disable_channel(self,channel):
        dwf.FDwfAnalogInChannelEnableSet(self.hdwf, ct.c_int(channel), ct.c_bool(False))

    def is_in_channel_enable(self,channel):
        IsEnable = ct.c_bool()
        dwf.FDwfAnalogInChannelEnableGet(self.hdwf, ct.c_int(channel), ct.byref(IsEnable))
        return IsEnable.value

    def in_channel_range_info(self,channel):
        V_min = ct.c_double()
        V_max = ct.c_double()
        nSteps = ct.c_double()
        dwf.FDwfAnalogInChannelRangeInfo(self.hdwf,ct.byref(V_min),ct.byref(V_max),ct.byref(nSteps))
        return [V_min.value,V_max.value,nSteps.value]

    def in_channel_range_set(self,channel,Vrange):
        dwf.FDwfAnalogInChannelRangeSet(self.hdwf,ct.c_int(channel),ct.c_double(Vrange))

    def in_channel_range_get(self,channel):
        Vrange = ct.c_double()
        dwf.FDwfAnalogInChannelRangeGet(self.hdwf,ct.c_int(channel),ct.byref(Vrange))
        return Vrange.value

    def in_channel_offset_info(self,channel):
        O_min = ct.c_double()
        O_max = ct.c_double()
        nSteps = ct.c_double()
        dwf.FDwfAnalogInChannelOffsetInfo(self.hdwf,ct.byref(O_min),ct.byref(O_max),ct.byref(nSteps))
        return [O_min.value,O_max.value,nSteps.value]

    def in_channel_offset_set(self,channel,Voffset):
        dwf.FDwfAnalogInChannelOffsetSet(self.hdwf,ct.c_int(channel),ct.c_double(Voffset))

    def in_channel_offset_get(self,channel):
        Voffset = ct.c_double()
        dwf.FDwfAnalogInChannelOffsetGet(self.hdwf,ct.c_int(channel),ct.byref(Voffset))
        return Voffset.value

    def in_channel_attenuation_set(self,channel,xAtt):
        dwf.FDwfAnalogInChannelAttenuationSet(self.hdwf,ct.c_int(channel),ct.c_double(xAtt))

    def in_channel_attenuation_get(self,channel):
        xAtt = ct.c_double()
        dwf.FDwfAnalogInChannelAttenuationGet(self.hdwf,ct.c_int(channel),ct.byref(xAtt))
        return xAtt.value

    def in_set_channel(self,channel,Vrange,Voffset = 0.0, attenuation = 1.0):
        self.in_channel_range_set(channel,Vrange)
        self.in_channel_offset_set(channel,Voffset)
        self.in_channel_attenuation_set(channel,attenuation)

    def in_decimate_filter_mode(self,channel):
        dwf.FDwfAnalogInChannelFilterSet(self.hdwf, ct.c_int(channel), DWFC.filterDecimate)

    def in_average_filter_mode(self,channel):
        dwf.FDwfAnalogInChannelFilterSet(self.hdwf, ct.c_int(channel), DWFC.filterAverage)


    ## Trigger methods
    def get_trigger_timeout(self):
        """returns the current trigger timeout, 0 means no timeout (trigger in mode 'normal')"""
        to = ct.c_double()
        dwf.FDwfAnalogInTriggerAutoTimeoutGet(self.hdwf, ct.byref(to))
        return to.value

    def get_trigger_source(self):
        """returns the current trigger source and channel as a tuple"""
        src = ct.c_ubyte()
        chan = ct.c_int()
        dwf.FDwfAnalogInTriggerSourceGet(self.hdwf, ct.byref(src))
        dwf.FDwfAnalogInTriggerChannelGet(self.hdwf, ct.byref(chan))
        return TriggerSourceById[src.value], chan.value

    def get_trigger_threshold_info(self):
        vmin = ct.c_double()
        vmax = ct.c_double()
        steps = ct.c_double()
        dwf.FDwfAnalogInTriggerLevelInfo(self.hdwf, ct.byref(vmin), ct.byref(vmax), ct.byref(steps))
        return [vmin.value, vmax.value, steps.value]

    def get_trigger_threshold_value(self):
        val = ct.c_double()
        dwf.FDwfAnalogInTriggerLevelGet(self.hdwf, ct.byref(val))
        return val.value

    def get_trigger_hysteresis_info(self):
        vmin = ct.c_double()
        vmax = ct.c_double()
        steps = ct.c_double()
        dwf.FDwfAnalogInTriggerHysteresisInfo(self.hdwf, ct.byref(vmin), ct.byref(vmax), ct.byref(steps))
        return [vmin.value, vmax.value, steps.value]

    def get_trigger_hysteresis_value(self):
        val = ct.c_double()
        dwf.FDwfAnalogInTriggerHysteresisGet(self.hdwf, ct.byref(val))
        return val.value

    def set_Chan_trigger(self, source, threshold, hysteresis=0.01, type="Rising", position=0, ref="center"):
        """
        Set the channel 'source' as the input trigger with given threshold (channels 1 and 2 are respectively
           referenced as sources 0 and 1)
        optionnally, hysteresis can be set to cope with higly noisy inputs (signal must go above
           threshold+hysteresis then below threshold-hysteresis for the trigger to shoot again).
        type is one of "Rising", "Falling" or "Both".
        position makes it possible to shift the trigger in time. By default trigger time is in the center
           of the acquisition. It is possible to change this reference by setting ref as one of "center",
           "left", "right", "left border", "right border". Using "left", the trigger time is positionned
           at 10% of the recording, unsing "left border", acquisition starts precisely at the trigger time.
        
        WARNING: Tests have shown that analog trigger was not specifically accurate, use with caution
           when using averagign techniques
        """
        if threshold<0:
            issue_warning("Threshold is set to a negative value, this is not supported by Analog Discovery 2")
        if hysteresis<0:
            issue_warning("Hysteresis is set to a negative value, which has no meaning")
        self.trigg_ref      = TriggerReference[ref.lower()]
        self.trigg_position = position
        dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, ct.c_double(0))          #disable auto trigger
        dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, DWFC.trigsrcDetectorAnalogIn) # trigsrcDetectorAnalogIn
        dwf.FDwfAnalogInTriggerChannelSet(self.hdwf, ct.c_int(source))            # set listening channel
        dwf.FDwfAnalogInTriggerTypeSet(self.hdwf, DWFC.trigtypeEdge)              # trigtypeEdge
        dwf.FDwfAnalogInTriggerLevelSet(self.hdwf, ct.c_double(threshold))        # set trigger level
        dwf.FDwfAnalogInTriggerHysteresisSet(self.hdwf, ct.c_double(hysteresis))  # 0.01V
        dwf.FDwfAnalogInTriggerFilterSet(self.hdwf, DWFC.filterDecimate)
        dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, TriggerSlopeByName[type.lower()])
        self.warn_analog_trigg = True

    def set_Auto_chan_trigger(self, source, timeout=0.001, type="Rising", position=0, ref="center"):
        """
        Set trigger to "auto"
        """
        self.trigg_ref      = TriggerReference[ref.lower()]
        self.trigg_position = position
        dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, ct.c_double(timeout))    # set timeout value
        dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, DWFC.trigsrcDetectorAnalogIn) # trigsrcDetectorAnalogIn
        dwf.FDwfAnalogInTriggerChannelSet(self.hdwf, ct.c_int(source))            # set listening channel
        dwf.FDwfAnalogInTriggerTypeSet(self.hdwf, DWFC.trigtypeEdge)              # trigtypeEdge
        #dwf.FDwfAnalogInTriggerLevelSet(self.hdwf, ct.c_double(threshold))        # set trigger level
        #dwf.FDwfAnalogInTriggerHysteresisSet(self.hdwf, ct.c_double(hysteresis))  # 0.01V
        dwf.FDwfAnalogInTriggerFilterSet(self.hdwf, DWFC.filterDecimate)
        dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, TriggerSlopeByName[type.lower()])
        self.warn_analog_trigg = True


    def set_Ext_trigger(self, source, type="Rising", position=0, ref="center"):
        """
        Set the external trigger 'source' as the input trigger (T1 and T2 are digital inputs actually
           referenced as 0 and 1)
        type is one of "Rising", "Falling" or "Both".
        position makes it possible to shift the trigger in time. By default trigger time is in the center
           of the acquisition. It is possible to change this reference by setting ref as one of "center",
           "left", "right", "left border", "right border". Using "left", the trigger time is positionned
           at 10% of the recording, unsing "left border", acquisition starts precisely at the trigger time.
        """
        source_name = ["External1", "External2", "External3", "External4"]
        self.trigg_ref      = TriggerReference[ref.lower()]
        dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, ct.c_double(0)) #disable auto trigger
        dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, TriggerSourceByName[source_name[source]])
        dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, TriggerSlopeByName[type.lower()])
        dwf.FDwfAnalogInTriggerTypeSet(self.hdwf, DWFC.trigtypeEdge)           # trigtypeEdge
        self.warn_analog_trigg = False


    def set_AWG_trigger(self, source, type="Rising", position=0, ref="center"):
        """
        DOESNT WORK!! --> seems to work just fine (LR)
        Set the AWG as a trigger 
           referenced as 0 and 1)
        type is one of "Rising", "Falling" or "Both".
        position makes it possible to shift the trigger in time. By default trigger time is in the center
           of the acquisition. It is possible to change this reference by setting ref as one of "center",
           "left", "right", "left border", "right border". Using "left", the trigger time is positionned
           at 10% of the recording, unsing "left border", acquisition starts precisely at the trigger time.
        """
        source_name = ["AnalogOut1", "AnalogOut2", "AnalogOut3", "AnalogOut4"]
        self.trigg_ref      = TriggerReference[ref.lower()]
        self.trigg_position = position
        dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, ct.c_double(0)) #disable auto trigger
        dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, TriggerSourceByName[source_name[source]])
        dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, TriggerSlopeByName[type.lower()])
        #dwf.FDwfAnalogInTriggerTypeSet(self.hdwf, DWFC.trigtypeEdge)           # trigtypeEdge
        self.warn_analog_trigg = False


    ## signal recording methods
    def in_configure_channel_record_Nsamples(self,channel,N,f_sample):
        self.in_sampling_freq_set(f_sample)
        self.in_set_aquisition_mode('Record')
        dwf.FDwfAnalogInRecordLengthSet(self.hdwf, ct.c_double(N/f_sample))

    def in_channel_record_Nsamples(self,channel,N,f_sample,filename=''):
        """Performs continuous acquisition on a single input channel"""
        # variables declaration
        sts = ct.c_byte()
        rgdSamples = (ct.c_double*N)()
        cAvailable = ct.c_int()
        cLost = ct.c_int()
        cCorrupted = ct.c_int()
        fLost = 0
        fCorrupted = 0
        
        self.in_channels_start()
        cSamples = 0

        while cSamples < N:
            dwf.FDwfAnalogInStatus(self.hdwf, ct.c_int(1), ct.byref(sts))
            if cSamples == 0 and (sts == DWFC.DwfStateConfig or sts == DWFC.DwfStatePrefill or sts == DWFC.DwfStateArmed) :
                # Acquisition not yet started.
                continue
            dwf.FDwfAnalogInStatusRecord(self.hdwf, ct.byref(cAvailable), ct.byref(cLost), ct.byref(cCorrupted))
            cSamples += cLost.value
            if cLost.value :
                fLost = 1
            if cCorrupted.value :
                fCorrupted = 1
            if cAvailable.value==0 :
                continue
            if cSamples+cAvailable.value > N :
                cAvailable = ct.c_int(N-cSamples)
            dwf.FDwfAnalogInStatusData(self.hdwf, ct.c_int(0), ct.byref(rgdSamples, ct.sizeof(ct.c_double)*cSamples), cAvailable) # get channel 1 data
            cSamples += cAvailable.value
        if fLost:
            print("Samples were lost! Reduce frequency")
        if fCorrupted:
            print("Samples could be corrupted! Reduce frequency")

        t = np.linspace(0,N/f_sample,num=N,endpoint=False)
        data = np.fromiter(rgdSamples, dtype = np.float64)

        if filename!='':
            f = open(filename, "w")
            for k in range(len(data)):
                f.write(str(t[k])+'\t'+str(data[k])+'\n')
            f.close()
        return t, data

    def record(self, channel, freq, samples=8192, time=None):
        """
        Performs continuous acquisition on a single input channel
        channel : the channel to record
        freq    : the sampling frequency
        samples : the number of samples to acquire
        time    : the duration of the recording
        
        if time is provided, samples is ignored.
        channel must have been configured (with in_set_channel)
        """

        #setting frequency first
        cfreq = ct.c_double()
        dwf.FDwfAnalogInFrequencySet(self.hdwf,ct.c_double(freq))
        dwf.FDwfAnalogInFrequencyGet(self.hdwf, ct.byref(cfreq))
        if abs(cfreq.value/freq - 1) > 0.005:
            issue_warning("Frequency inconsistency ({} instead of {})".format(cfreq.value, freq))

        #managing number of samples (needs frequency to be accurate)
        if time==None:
            localsamples = int(samples)
        else:
            localsamples = int(time*cfreq.value + 1)
        #we use different sample values for recording and reporting
        #to avoid issues when requested number of samples is too low.
        recordsamples=localsamples + localsamples//1000
        if localsamples<8192:    
            recordsamples=8192
        
        # variables declaration
        sts = ct.c_byte()
        rgdSamples = (ct.c_double*recordsamples)()
        cAvailable = ct.c_int()
        cLost = ct.c_int()
        cCorrupted = ct.c_int()
        fLost = 0
        fCorrupted = 0

        #set recording mode
        dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, DWFC.acqmodeRecord)
        #set recording time
        dwf.FDwfAnalogInRecordLengthSet(self.hdwf, ct.c_double(recordsamples/cfreq.value))
        #enables channel
        dwf.FDwfAnalogInChannelEnableSet(self.hdwf, ct.c_int(channel), ct.c_bool(True))
        #initializes the acquisition device without resetting triggers
        dwf.FDwfAnalogInConfigure(self.hdwf, ct.c_bool(False), ct.c_bool(True))

        cSamples = 0
        Samples_Got = 0
        flist = []
        while Samples_Got < recordsamples:
            dwf.FDwfAnalogInStatus(self.hdwf, ct.c_int(1), ct.byref(sts))
            if Samples_Got == 0 and (sts == DWFC.DwfStateConfig or sts == DWFC.DwfStatePrefill or sts == DWFC.DwfStateArmed) :
                # Acquisition not yet started.
                continue
            dwf.FDwfAnalogInStatusRecord(self.hdwf, ct.byref(cAvailable), ct.byref(cLost), ct.byref(cCorrupted))
            if cLost.value :
                fLost = 1
                Samples_Got += cLost.value
            if cCorrupted.value :
                fCorrupted = 1
            if cAvailable.value==0 :
                continue
            if Samples_Got + cAvailable.value > recordsamples :
                cAvailable = ct.c_int(recordsamples-Samples_Got)
            if cAvailable.value>8192:
                cAvailable = ct.c_int(8192)
            #dwf.FDwfAnalogInStatusData(self.hdwf, ct.c_int(0), ct.byref(rgdSamples), cAvailable)
            dwf.FDwfAnalogInStatusData(self.hdwf, ct.c_int(0), ct.byref(rgdSamples, ct.sizeof(ct.c_double)*Samples_Got), cAvailable) # get channel 1 data
            #cSamples += cAvailable.value
            Samples_Got += cAvailable.value
            #dat = np.fromiter(rgdSamples, dtype = np.float, count=cAvailable.value)
            #flist.append(dat)
        if fLost:
            issue_warning("Samples were lost! Reduce frequency")
        if fCorrupted:
            issue_warning("Samples could be corrupted! Reduce frequency")

        t = np.linspace(0, localsamples/cfreq.value, num=localsamples, endpoint=False)
        data = np.fromiter(rgdSamples, dtype = np.float64, count=localsamples)
        return t, data
        #return flist

    def set_acq(self, time=None, freq=1000000, samples=8192, pw2=False):
        """
        defines parameters for acquisition
        freq    : the sampling frequency
        samples : the number of samples to acquire
        time    : the length of the acquisition. The actual data retrieved might be longer.
        pw2     : forces the number of samples to be a power of 2 (this improves some
                    computation times like FFT).
        
        if time is provided, freq and samples are ignored, and the setup detemines the highest frequency and the
        appropriate number of samples to provide the requested recording length at best
        """
        # variables declaration
        cBufMax = ct.c_int()
        cfreq   = ct.c_double()
        dwf.FDwfAnalogInBufferSizeInfo(self.hdwf, 0, ct.byref(cBufMax))
        if time == None:
            assert samples<=cBufMax.value, "max sample count is {}, got {}".format(cBufMax.value, samples)
            self.acq_samples = samples
            dwf.FDwfAnalogInFrequencySet(self.hdwf, ct.c_double(freq))
            dwf.FDwfAnalogInFrequencyGet(self.hdwf, ct.byref(cfreq))
            if abs(cfreq.value/freq - 1) > 0.001:
                issue_warning("Frequency inconsistency ({} instead of {})".format(cfreq.value, freq))
            self.acq_freq    = cfreq.value
            dwf.FDwfAnalogInBufferSizeSet(self.hdwf, ct.c_int(samples))
        else:
            #min sampling period expressed in periods of 10ns (AD is based on 100MHz)
            sampling_period = time/(8191 * 0.00000001)
            if abs(abs((sampling_period %1) - 0.5) - 0.5) > 0.0001:
                #sampling period is not an integer value of 10ns periods, so we choose the value above
                sampling_period = int(sampling_period + 1)
            else:
                #we just round the sampling period
                sampling_period = int(sampling_period + 0.5)
            # set and check the sampling frequency
            dwf.FDwfAnalogInFrequencySet(self.hdwf, ct.c_double(100000000/sampling_period))
            dwf.FDwfAnalogInFrequencyGet(self.hdwf, ct.byref(cfreq))
            self.acq_freq    = cfreq.value
            self.acq_samples = int(cfreq.value * time) + 1
            if pw2:
                if self.acq_samples <4097:
                    self.acq_samples = 4096
                else:
                    self.acq_samples = 8192
        
        #enable recording channel 
        dwf.FDwfAnalogInChannelEnableSet(self.hdwf, ct.c_int(-1), ct.c_bool(True))
        
        #set trigger delay (the only reference offered is center, so we handle left and right manually)
        if self.trigg_ref == TRIGG_REF_CENTER:
            lpos = self.trigg_position
        elif self.trigg_ref == TRIGG_REF_LEFT:
            lpos = self.trigg_position + 0.9*self.acq_samples/(2*self.acq_freq)
        elif self.trigg_ref == TRIGG_REF_RIGHT:
            lpos = self.trigg_position - 0.9*self.acq_samples/(2*self.acq_freq)
        elif self.trigg_ref == TRIGG_REF_PURELEFT:
            lpos = self.trigg_position + self.acq_samples/(2*self.acq_freq)
        elif self.trigg_ref == TRIGG_REF_PURERIGHT:
            lpos = self.trigg_position - self.acq_samples/(2*self.acq_freq)
        else:
            issue_warning("Unexpected value for trigger reference ('{}'), using '{}'".format(self.trigg_ref, TRIGG_REF_CENTER))
            lpos = self.trigg_position
        dwf.FDwfAnalogInTriggerPositionSet(self.hdwf, ct.c_double(lpos))
        actual_trigger = ct.c_double()
        dwf.FDwfAnalogInTriggerPositionGet(self.hdwf, ct.byref(actual_trigger))
        self.acq_position = actual_trigger.value
        
        #starting oscilloscope
        dwf.FDwfAnalogInConfigure(self.hdwf, ct.c_int(1), ct.c_int(1))
        return np.linspace(0,self.acq_samples/self.acq_freq, num=self.acq_samples, endpoint=False) + (self.acq_position - self.acq_samples/(self.acq_freq*2))

    def acq(self, avg=1, quantum=None):
        """
        Performs oscilloscope-like acquisition on the two input channels
        avg     : number of acquisitions to average to improve precision
        quantum : chooses the best avg value to achieve an this precision
                    (avg=1 means 0.0003V precision if range=5V)
        
        if both avg and quantum are defined, values are multiplied, for example, defining
        quantum=0.0001 means 3 acquisitions, but defining both quantum=0.0001 and avg=3 means
        9 acquisition (3 acquisitions at 0.1mV precision)
        
        WARNING: using avg and quantum parameters requires the signal to be repetitive 
        """
        if self.acq_freq == None:
            # someone prefers returning dummy data ?
            issue_warning("set_acq() not called before acq(), this is not good practice! Using default values")
            self.set_acq()
        # manage Quantum
        if quantum == None:
            local_avg = int(max(1, avg))
        else:
            local_avg = max(int(avg*0.0003 / quantum) + 1, 1)

        if local_avg>1 and self.warn_analog_trigg:
            # complain to YB if this one annoys you !
            issue_warning("Analog trigger is not recommended for averaged acquisition")

        # variables declaration
        status = ct.c_byte()
        rgdSamples = (ct.c_double*self.acq_samples)()
        while True:
            dwf.FDwfAnalogInStatus(self.hdwf, ct.c_int(1), ct.byref(status))
            if status.value == DWFC.DwfStateDone.value :
                break
        dwf.FDwfAnalogInStatusData(self.hdwf, 0, rgdSamples, self.acq_samples) # get channel 1 data
        data0 = np.fromiter(rgdSamples, dtype = np.float64)
        dwf.FDwfAnalogInStatusData(self.hdwf, 1, rgdSamples, self.acq_samples) # get channel 2 data
        data1 = np.fromiter(rgdSamples, dtype = np.float64)
        if local_avg == 1:
            return data0, data1
        for _ in range(1, local_avg):
            dwf.FDwfAnalogInConfigure(self.hdwf, ct.c_int(1), ct.c_int(1))
            sleep(self.acq_samples/self.acq_freq)
            while True:
                dwf.FDwfAnalogInStatus(self.hdwf, ct.c_int(1), ct.byref(status))
                if status.value == DWFC.DwfStateDone.value :
                    break
            dwf.FDwfAnalogInStatusData(self.hdwf, 0, rgdSamples, self.acq_samples) # get channel 1 data
            data0 += np.fromiter(rgdSamples, dtype = np.flfloat64oat)
            dwf.FDwfAnalogInStatusData(self.hdwf, 1, rgdSamples, self.acq_samples) # get channel 2 data
            data1 += np.fromiter(rgdSamples, dtype = np.float64)
        return data0/local_avg, data1/local_avg

    # ██     ██  ██████
    # ██    ██  ██    ██
    # ██   ██   ██    ██
    # ██  ██    ██    ██
    # ██ ██      ██████


    ###########################
    ## methods for analog IO ##
    ###########################
    def reset_analogIO(self):
        dwf.FDwfAnalogIOReset(self.hdwf)

    def configure_analogIO(self):
        dwf.FDwfAnalogIOConfigure(self.hdwf)

    def enable_analogIO(self):
        dwf.FDwfAnalogIOEnableSet(self.hdwf, ct.c_int(True))

    def disable_analogIO(self):
        dwf.FDwfAnalogIOEnableSet(self.hdwf, ct.c_int(False))

    def is_analogIO_enable(self):
        IsEnabled = ct.c_bool()
        dwf.FDwfAnalogIOEnableStatus(self.hdwf, ct.byref(IsEnabled))
        return IsEnabled.value

    def set_asymetric_power_supply(self,V_supply=5.):
        dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ct.c_int(0), ct.c_int(0), ct.c_double(True))
        dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ct.c_int(0), ct.c_int(1), ct.c_double(V_supply))
        self.enable_analogIO()

    def set_symetric_power_supply(self,V_supply=5.):
        dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ct.c_int(0), ct.c_int(0), ct.c_double(True))
        dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ct.c_int(0), ct.c_int(1), ct.c_double(V_supply))
        dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ct.c_int(1), ct.c_int(0), ct.c_double(True))
        dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ct.c_int(1), ct.c_int(1), ct.c_double(-V_supply))
        self.enable_analogIO()

    def check_USB_supply(self):
        usbVoltage = ct.c_double()
        usbCurrent = ct.c_double()
        dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, ct.c_int(2), ct.c_int(0), ct.byref(usbVoltage))
        dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, ct.c_int(2), ct.c_int(1), ct.byref(usbCurrent))
        return usbVoltage.value, usbCurrent.value

    def check_Auxiliary_supply(self):
        auxVoltage = ct.c_double()
        auxCurrent = ct.c_double()
        dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, ct.c_int(3), ct.c_int(0), ct.byref(auxVoltage))
        dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, ct.c_int(3), ct.c_int(1), ct.byref(auxCurrent))
        return auxVoltage.value, auxCurrent.value

    ############################
    ## methods for Digital IO ##
    ############################
    def reset_digitalIO(self):
        dwf.FDwfDigitalIOReset(self.hdwf)

    def configure_digitalIO(self):
        dwf.FDwfDigitalIOConfigure(self.hdwf)

    def digitalIO_set_as_output(self,mask):
        dwf.FDwfDigitalIOOutputEnableSet(self.hdwf, ct.c_int(mask))

    def digitalIO_output(self,value):
        dwf.FDwfDigitalIOOutputSet(self.hdwf, ct.c_int(value))  

    def digitalIO_read(self):
        dwRead = ct.c_uint32()
        # fetch digital IO information from the device 
        dwf.FDwfDigitalIOStatus(self.hdwf) 
        # read state of all pins, regardless of output enable
        dwf.FDwfDigitalIOInputStatus(self.hdwf, ct.byref(dwRead)) 
        # dwRead as bitfield (32 digits, removing 0b at the front
        #return int(bin(dwRead.value)[2:].zfill(16))
        return(dwRead.value)
    
    def digitalIO_read_outputs(self):
        dwRead = ct.c_uint32()
        dwf.FDwfDigitalIOOutputGet(self.hdwf, ct.byref(dwRead))
        return(dwRead.value)

    ################################
    ## Impedance/Network Analyser ##
    ################################
    ## Basic methods
    def reset_analyser(self):
        dwf.FDwfAnalogImpedanceReset(self.hdwf)

    def set_analyser_mode(self, mode):
        dwf.FDwfAnalogImpedanceModeSet(self.hdwf, ct.c_int(mode))

    def get_analyser_mode(self):
        analyser_mode = ct.c_int()
        dwf.FDwfAnalogImpedanceModeGet(self.hdwf, ct.byref(analyser_mode))
        return analyser_mode.value

    def set_impedance_analyser_reference(self, resistor):
        dwf.FDwfAnalogImpedanceReferenceSet(self.hdwf, ct.c_double(resistor))

    def get_impedance_analyser_reference(self):
        reference_resistor = ct.c_double()
        dwf.FDwfAnalogImpedanceReferenceGet(self.hdwf, ct.byref(reference_resistor))
        return reference_resistor.value

    def set_analyser_frequency(self, freq):
        dwf.FDwfAnalogImpedanceFrequencySet(self.hdwf, ct.c_double(freq))

    def get_analyser_frequency(self):
        freq = ct.c_double()
        dwf.FDwfAnalogImpedanceFrequencyGet(self.hdwf, ct.byref(freq))
        return freq.value

    def set_analyser_amplitude(self, amp):
        dwf.FDwfAnalogImpedanceAmplitudeSet(self.hdwf, ct.c_double(amp))

    def get_analyser_amplitude(self):
        amp = ct.c_double()
        dwf.FDwfAnalogImpedanceAmplitudeGet(self.hdwf, ct.byref(amp))
        return amp.value

    def set_analyser_offset(self, offset):
        dwf.FDwfAnalogImpedanceOffsetSet(self.hdwf, ct.c_double(offset))

    def get_analyser_offset(self):
        offset = ct.c_double()
        dwf.FDwfAnalogImpedanceOffsetGet(self.hdwf, ct.byref(offset))
        return offset.value

    def set_analyser_probe(self, resistance, capacitance):
        dwf.FDwfAnalogImpedanceProbeSet(self.hdwf, ct.c_double(resistance), ct.c_double(capacitance))

    def get_analyser_probe(self):
        resistance = ct.c_double()
        capacitance = ct.c_double()
        dwf.FDwfAnalogImpedanceProbeGet(self.hdwf, ct.byref(resistance), ct.byref(capacitance))
        return resistance.value, capacitance.value

    def set_analyser_n_period(self, Nperiods):
        dwf.FDwfAnalogImpedancePeriodSet(self.hdwf, ct.c_int(Nperiods)) 

    def get_analyser_n_period(self):
        Nperiods = ct.c_int()
        dwf.FDwfAnalogImpedancePeriodGet(self.hdwf, ct.byref(Nperiods))
        return (Nperiods.value)

    def reset_analyser_compensation_parameters(self):
        dwf.FDwfAnalogImpedanceCompReset(self.hdwf)

    def set_analyser_compensation_parameters(self, OpenResistance, OpenReactance, ShortResistance, ShortReactance):
        dwf.FDwfAnalogImpedanceCompSet(self.hdwf, ct.c_double(OpenResistance), ct.c_double(OpenReactance), ct.c_double(ShortResistance), ct.c_double(ShortReactance))

    def get_analyser_compensation_parameters(self):
        OpenResistance = ct.c_double()
        OpenReactance = ct.c_double()
        ShortResistance = ct.c_double()
        ShortReactance = ct.c_double()
        dwf.FDwfAnalogImpedanceCompGet(ct.byref(OpenResistance), ct.byref(OpenReactance), ct.byref(ShortResistance), ct.byref(ShortReactance))
        return OpenResistance.value, OpenReactance.value, ShortResistance.value, ShortReactance.value

    def start_analyser(self):
        dwf.FDwfAnalogImpedanceConfigure(self.hdwf, ct.c_int(1))

    def stop_analyser(self):
        dwf.FDwfAnalogImpedanceConfigure(self.hdwf, ct.c_int(0))

    def get_analyser_status(self):
        sts = ct.c_byte()
        dwf.FDwfAnalogImpedanceStatus(self.hdwf, ct.byref(sts))
        return sts.value

    def analyzer_ignore_last_value(self):
        # esoteric method...
        dwf.FDwfAnalogImpedanceStatus(self.hdwf, None) 

    def get_analyser_raw_input(self, channel):
        Gain = ct.c_double()
        Phase = ct.c_double()
        dwf.FDwfAnalogImpedanceStatusInput(self.hdwf, ct.c_int(channel), ct.byref(Gain), ct.byref(Phase))
        return Gain.value, Phase.value

    def get_analyser_impedance_measurement(self, measure):
        measured_value = ct.c_double()
        dwf.FDwfAnalogImpedanceStatusMeasure(self.hdwf, AnalogImpedancesByName['measure'], ct.byref(measured_value))
        return measured_value.value

    ## advanced methods
    def configure_network_analyser(self,amp = 1.0, offset = 0.0, Nperiods = 16):
        ''' Configures the Analog Discovery 2 as a network analyser,
                Generator channel 1 (W1 - GND) used as source
                Scope channel 1 connected as input of the DUT (1+ to W1 to the DUT, 1- to GND)
                Scope channel 2 connected as output of the DUT (2+ to the DUT, 2- to GND)

        Inputs:
        ------- 
            amp : 			amplitude of the source in V, by default 1V
            offset : 		offset of the source in V, by default 0V
            Nperiods : 		Number of periods to measure by frequency point, by default 16
        '''
        self.enable_dynamic_auto_config()
        self.reset_analyser()						# resets the analyser
        self.set_analyser_mode(0)					# W1-C1-DUT-C2-R-GND even if useless as no impedance is measured
        self.set_impedance_analyser_reference(1e4)	# even if it seems useless here
        self.set_analyser_amplitude(amp)
        self.set_analyser_offset(offset) 
        self.set_analyser_n_period(Nperiods)
        self.start_analyser()

    def bode_measurement(self, fstart, fstop, n_points = 0, dB = False, deg = False, settling_time=0.01,
        amp = 1.0, offset = 0.0, Nperiods = 16, verbose = True):
        ''' Perform a frequenct sweep to measure Gain and Phase of a DUT

        Inputs: 
        -------
            fstart: 		sweep starting frequency
            fstop: 			sweep stoping frequency
            n_points: 		optional, number of frequency points for the sweep, if unspecified, 10 points per decade
                                will be computed by default 
            dB: 			if False, gain will be returned unitless, if True, gain returned in decibels.
                                False by default
            deg: 			if False, the phase will be returned in radians. If True, phase returned in degrees
                                False by default
            settling_time: 	time imposed to get to steady state on the DUT, after seting a new frequency and 
                                before measurement. In seconds. By default 10 ms
            amp: 			Amplitude of the AWG output
            offset: 		DC offset of the AWG output
            Nperiods:		Number of periods to wait for the measurement 
            verbose: 		verbosity of the algorithm. If true, a progression bar will be displayed in the terminal. 
                                True by default

        Returns:
        --------
            freq: np.array, vector containing the frequencies of the sweep
            gain: np.array, vector containing the gain values, unitless or in dB (see above) CH2/CH1
            phase: np.array, vector containing the phase values, in radians or degrees (see above)
            gain_ch1: np.array, vector containing the gain values, unitless or in dB (see above) CH1/amp (no phase associated)
        '''

    
        sleep(10*settling_time)
        if n_points == 0:
            n_points = 10*np.ceil(np.log10(fstop/fstart)) + 1
        freq = np.logspace(np.log10(fstart), np.log10(fstop), num = n_points)
        gain_ch1 = []
        gain = []
        phase =[]
        if verbose:
            print('Analyzer - Bode: Measurement on '+str(n_points)+' frequencies')
            printProgressBar(0, n_points, prefix = 'Progress:', suffix = 'Complete', length = 50)
        for i in range(len(freq)):
            self.set_analyser_frequency(freq[i])
            sleep(settling_time)
            self.analyzer_ignore_last_value() # ignore last capture, forces a new measurement after the settling time
            while True:
                status = self.get_analyser_status()
                if status == 0 :	# not working when using the DwfState constant...
                    self.print_last_error_message()
                    quit()
                if status == 2: 	# same comment as above...
                    break
            gain1, phase1 = self.get_analyser_raw_input(0)
            gain2, phase2 = self.get_analyser_raw_input(1)

            gain.append(gain2)
            if phase2 < np.pi/2:
                phase.append(phase2+2*np.pi)
            else:
                phase.append(phase2)
                
            gain_ch1.append(1/gain1)
            if verbose:
                printProgressBar(i + 1, n_points, prefix = 'Progress:', suffix = 'Complete', length = 50)
        sleep(10*settling_time)
        gain = np.asarray(gain)
        phase = np.asarray(phase)
        gain_ch1 = np.asarray(gain_ch1)
        if dB:
            gain = 20*np.log10(gain)
            gain_ch1 = 20*np.log10(gain_ch1) 
        if deg:
            phase = 180.*phase/np.pi
        return freq, gain, phase, gain_ch1

    def single_frequency_gain_phase(self,frequency,dB = False, deg = False, settling_time=0.01, verbose = True):
        ''' Perform a single frequency analysis to measure Gain and Phase of a DUT

        Inputs: 
        -------
            frequency: 		sinewave frequency
            n_points: 		optional, number of frequency points for the sweep, if unspecified, 10 points per decade
                                will be computed by default 
            dB: 			if False, gain will be returned unitless, if True, gain returned in decibels.
                                False by default
            deg: 			if False, the phase will be returned in radians. If True, phase returned in degrees
                                False by default
            settling_time: 	time imposed to get to steady state on the DUT, after seting a new frequency and 
                                before measurement. In seconds. By default 10 ms
            amp: 			Amplitude of the AWG output
            offset: 		DC offset of the AWG output
            Nperiods:		Number of periods to wait for the measurement 
            verbose: 		verbosity of the algorithm. If true, a progression bar will be displayed in the terminal. 
                                True by default

        Returns:
        --------
            gain: np.array, vector containing the gain values, unitless or in dB (see above) CH2/CH1
            phase: np.array, vector containing the phase values, in radians or degrees (see above)
            gain_ch1: np.array, vector containing the gain values, unitless or in dB (see above) CH1/amp (no phase associated)
        '''
        self.set_analyser_frequency(frequency)
        sleep(settling_time)
        self.analyzer_ignore_last_value() # ignore last capture, forces a new measurement after the settling time
        while True:
            status = self.get_analyser_status()
            if status == 0 :	# not working when using the DwfState constant...
                self.print_last_error_message()
                quit()
            if status == 2: 	# same comment as above...
                break
        gain1, phase1 = self.get_analyser_raw_input(0)
        gain, phase = self.get_analyser_raw_input(1)
        if phase < np.pi/2:
            phase = (phase+2*np.pi)
        gain_ch1 = 0
        if (gain1 > 0): ## 
            gain_ch1 = (1/gain1)
        sleep(10*settling_time)
        if dB:
            gain = 20*np.log10(gain)
            gain_ch1 = 20*np.log10(gain_ch1) 
        if deg:
            phase = 180.*phase/np.pi
        return gain, phase, gain_ch1

    ############################
    ## Digital communications ##
    ############################

    ## SPI protocol
    def SPI_reset(self):
        dwf.FDwfDigitalSpiReset(self.hdwf)

    def set_SPI_frequency(self, freq):
        dwf.FDwfDigitalSpiFrequencySet(self.hdwf, ct.c_double(freq))

    def set_SPI_Clock_channel(self, channel):
        dwf.FDwfDigitalSpiClockSet(self.hdwf,ct.c_int(channel))

    def set_SPI_Data_channel(self, idxDQ, channel):
        '''
            for idxDQ, consider using the dictionnary: SPIDataIdx
        '''
        dwf.FDwfDigitalSpiDataSet(self.hdwf, idxDQ, ct.c_int(channel))

    def set_SPI_mode(self, mode):
        '''
            for mode, consider using the dictionnary: SPIMode
        '''
        dwf.FDwfDigitalSpiModeSet(self.hdwf, mode)

    def set_SPI_order(self, order):
        dwf.FDwfDigitalSpiOrderSet(self.hdwf,ct.c_int(order))

    def set_SPI_MSB_first(self):
        self.set_SPI_order(1)

    def set_SPI_LSB_first(self):
        self.set_SPI_order(0)

    def set_SPI_CS(self, channel, logiclevel):
        '''
            for logiclevel, consider using the dictionary: LogicLevel
        '''
        dwf.FDwfDigitalSpiSelectSet(self.hdwf,ct.c_int(channel),logiclevel)

    def SPI_write_read(self, cDQ, bit_per_word, values, N_read):
        '''
            for cDQ, consider using the dictionary: SPI_cDQ
        '''
        if type(values) != tuple:
            values = (values ,)
        valuesTX = (ct.c_ubyte*len(values))(*values)
        valuesRX = (ct.c_ubyte*N_read)()
        #dwf.FDwfDigitalSpiWriteRead(self.hdwf, cDQ, ct.c_int(bit_per_word), rgbTX, ct.c_int(len(values)), rgbRX, ct.c_int(N_read))
        dwf.FDwfDigitalSpiWriteRead(self.hdwf, cDQ, ct.c_int(bit_per_word), valuesTX, ct.c_int(len(valuesTX)), valuesRX, ct.c_int(N_read))
        RX = []
        for i in valuesRX:
            RX.append(i)
        return RX

    def SPI_select(self,channel, logiclevel):
        dwf.FDwfDigitalSpiSelect(self.hdwf,ct.c_int(channel),logiclevel)

    def SPI_write_one(self, cDQ, Nbits, value):
        '''
            for cDQ, consider using the dictionary: SPI_cDQ
        '''
        dwf.FDwfDigitalSpiWriteOne(self.hdwf, cDQ, ct.c_int(Nbits),ct.c_uint(value))

    def SPI_read_one(self, cDQ, Nbits):
        '''
            for cDQ, consider using the dictionary: SPI_cDQ
        '''
        rxvalue = ct.c_uint32()
        dwf.FDwfDigitalSpiReadOne(self.hdwf, cDQ, ct.c_int(Nbits),ct.byref(rxvalue))
        #dwf.FDwfDigitalSpiReadOne(self.hdwf, cDQ, ct.c_int(Nbits),rxvalue)
        return rxvalue.value






