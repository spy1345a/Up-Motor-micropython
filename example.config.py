class Config:
    ## Wifi config
    WIFI_NAME = 'WIFI_SSID'
    WIFI_PASS = 'WIFI_PASSWORD'
    
    ## Telegram config
    TOKEN = 'TELEGRAM_BOT_TOKEN'
    GROUP_ID = -12345678 # this is intiger negative or positive
    
    ## Pin Config
    Led_pin = 8 # in-Build led of esp32 c3 super mini
    Relay_pin = 10 ## well techenially it is controlling a NPN transister
    Short_detection = 3 # not used , maybe updated later
    
    ##Time settings
    TimeZone = 0.0 # this is float, it uses GMT 
    
    ## Timings settings
    Telegram_Check_internal = 10 #secondes
    short_detect_interval = 2 #secondes
    Telegram_Poll_timeout = 5 #secondes
    
