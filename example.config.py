class Config:
    ## Wifi config
    WIFI_NAME = 'WIFI_SSID'
    WIFI_PASS = 'WIFI_PASSWORD'
    
    ## Telegram config
    TOKEN = 'TELEGRAM_BOT_TOKEN'
    GROUP_ID = TELEGRAM_GROUP_ID # this is intiger negative or positive
    
    ## Pin Config
    Led_pin = 8 # in-Build led of esp32 c3 super mini
    Relay_pin = 10 ## well techenially it is controlling a NPN transister
    Short_detection = 3
    
    ##Time settings
    TimeZone = TIMEZONE # this is float, it uses GMT 
    
    ## Timings settings
    Telegram_Check_internal = 10 #secondes
    short_detect_interval = 2 #secondes
    Telegram_Poll_timeout = 5 #secondes
    
