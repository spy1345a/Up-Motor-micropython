from config import Config
import network
import machine
import time

def wifi_connect(WiFi_name, WiFi_password):
    wlan = network.WLAN(network.STA_IF)
    
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    time.sleep(0.5)

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WiFi_name, WiFi_password)
        
        timeout = 15
        while not wlan.isconnected():
            if timeout <= 0:
                print('WiFi connection timed out - rebooting')
                time.sleep(2)
                machine.reset()  # <-- instead of returning False
            machine.idle()
            time.sleep(1)
            timeout -= 1

    try:
        print('network config:', wlan.ipconfig('addr4'))
    except (AttributeError, OSError):
        print('network config:', wlan.ifconfig())

wifi_connect(WiFi_name=Config.WIFI_NAME, WiFi_password=Config.WIFI_PASS)