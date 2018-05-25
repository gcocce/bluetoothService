
TEMP_FILE = '/sys/class/thermal/thermal_zone0/temp'
def read_temp():
    tFile = open(TEMP_FILE, 'r')
    tempS = tFile.read()
    tempI = int(tempS)
    tempF = float(tempI/1000)
    return tempF
