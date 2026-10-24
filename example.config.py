class Config:
    ## Wifi config
    WIFI_NAME = 'WIFI_SSID'
    WIFI_PASS = 'WIFI_PASSWORD'
    
    ## Telegram config
    TOKEN = 'TELEGRAM_BOT_TOKEN'
    GROUP_ID = -12345678 # this is an integer, negative or positive
    
    ## Pin Config
    Led_pin = 8 # in-build LED of esp32 c3 super mini
    Relay_pin = 10 ## technically it is controlling an NPN transistor
    Short_detection = 3 # not used, maybe updated later
    
    ## Time settings
    TimeZone = 0.0 # this is a float, it uses GMT
    
    ## Timing settings
    Telegram_Check_interval = 10 # seconds
    short_detect_interval = 2 # seconds
    Telegram_Poll_timeout = 5 # seconds
    NTP_RESYNC = 3600 # seconds (3600s = 1h)
