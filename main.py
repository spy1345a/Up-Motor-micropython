import time
import gc
import network
from config import Config
from utelegram import ubot
from TimeManager import TimeManager
import machine

# 80 MHz is the lowest CPU frequency that still keeps WiFi working.
# Lowering it from the 160 MHz default makes the chip run noticeably cooler.
try:
    machine.freq(80_000_000)
except Exception:
    pass

# ====== Config ======
Telegram_token = Config.TOKEN
Group_id       = Config.GROUP_ID

# Pins Config
led   = machine.Pin(Config.Led_pin,   machine.Pin.OUT, value=0)
relay = machine.Pin(Config.Relay_pin, machine.Pin.OUT, value=0)

# Timings Config
TimeZone                = Config.TimeZone
Telegram_Check_interval = Config.Telegram_Check_interval
LOOP_INTERVAL           = Config.short_detect_interval
Telegram_Poll_timeout   = getattr(Config, 'Telegram_Poll_timeout', 5)
NTP_RESYNC              = Config.NTP_RESYNC

# ====== WiFi ======
# WiFi reconnect is non-blocking while the loop runs: we kick off a connect
# attempt and immediately hand control back to the loop, so the relay timer
# stays accurate even while WiFi is down. A retry is issued no faster than
# WIFI_RETRY_SECS until the connection comes back.
WIFI_RETRY_SECS    = 15
wifi_connecting    = False
last_wifi_attempt  = 0

def _wifi_start_connect():
    """Kick off a connect attempt without waiting for it to finish."""
    global wifi_connecting, last_wifi_attempt
    wlan = network.WLAN(network.STA_IF)
    try:
        wlan.config(pm=0)  # disable WiFi power-save (fixes dropped HTTPS)
    except Exception:
        pass
    print("Connecting to WiFi...")
    try:
        if not wlan.active():
            wlan.active(True)
        wlan.connect(Config.WIFI_NAME, Config.WIFI_PASS)
        wifi_connecting = True
        last_wifi_attempt = time.time()
    except Exception as e:
        print("WiFi error:", e)
        wifi_connecting = False

def ensure_wifi(first=False):
    global wifi_connecting
    wlan = network.WLAN(network.STA_IF)
    try:
        wlan.config(pm=0)  # disable WiFi power-save (fixes dropped HTTPS)
    except Exception:
        pass
    if wlan.isconnected():
        if wifi_connecting:
            wifi_connecting = False
            try:
                print("WiFi connected:", wlan.ifconfig())
            except Exception:
                pass
        return True

    if first:
        # At boot: wait so Telegram/NTP setup below has a live connection.
        _wifi_start_connect()
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
        if wlan.isconnected():
            wifi_connecting = False
            try:
                print("WiFi connected:", wlan.ifconfig())
            except Exception:
                pass
            return True
        print("WiFi connection failed")
        return False

    # Main loop: never block. Re-issue the attempt only after the cooldown.
    if not wifi_connecting and time.time() - last_wifi_attempt >= WIFI_RETRY_SECS:
        print("WiFi lost - reconnecting...")
        _wifi_start_connect()
    return False

# Connect before anything that needs the network (NTP + Telegram)
ensure_wifi(first=True)

# ====== Time & Bot ======
clk = TimeManager(timezone_offset_hours=TimeZone)
print("Boot time:", clk.now_str())

bot = ubot(
    token=Telegram_token,
    chat_id=Group_id,
    poll_timeout=Telegram_Poll_timeout,
)
try:
    bot.send("Booted at: " + clk.now_str() +"🫨")
except Exception as e:
    print("Boot send error:", e)
print("Telegram bot setup done")

# ====== State ======
relay_enabled     = False
relay_off_at_ts   = None
last_poll_ts      = 0
last_applied      = None
last_resync_ts    = clk.timestamp()   # last successful NTP sync

# ====== Helpers ======
def relay_on():  relay.value(1)
def relay_off(): relay.value(0)
def led_on():    led.value(1)
def led_off():   led.value(0)

def apply_outputs():
    global last_applied
    if last_applied == relay_enabled:
        return
    if relay_enabled:
        relay_on()
        led_on()
    else:
        relay_off()
        led_off()
    last_applied = relay_enabled

def get_text(message):
    if 'message' not in message:
        return None
    if 'text' not in message['message']:
        return None
    return message['message']['text'].strip()

def start_relay_for_minutes(minutes):
    global relay_enabled, relay_off_at_ts
    relay_enabled = True
    relay_off_at_ts = clk.timestamp() + (minutes * 60)
    apply_outputs()
    bot.send(
        "Relay Control\n"
        "Device Turned ON 🟢\n"
        "Duration: " + str(minutes) + " minute(s)\n"
        "Time  : " + clk.now_str()
    )

def send_state(prefix):
    state = "ON" if relay_enabled else "OFF"
    bot.send(
        "Relay Control\n"
        + prefix + "\n"
        "Relay : " + state + "\n"
        "Time  : " + clk.now_str()
    )

# ====== Handlers ======
def handle_on(message):
    print("handle_on triggered")
    text = get_text(message)
    if text is None:
        return

    parts = text.split()
    minutes = 60
    if len(parts) > 1 and parts[1].isdigit():
        minutes = int(parts[1])
        if minutes <= 0:
            bot.send("Relay Control\nInvalid value. Send minutes greater than 0.")
            return

    start_relay_for_minutes(minutes)

def handle_off(message):
    print("handle_off triggered")
    global relay_enabled, relay_off_at_ts
    if not relay_enabled:
        send_state("Device Already OFF ❌")
        return

    relay_enabled = False
    relay_off_at_ts = None
    apply_outputs()
    send_state("Device Turned OFF 🔴")

def handle_status(message):
    print("handle_status triggered")
    if relay_enabled and relay_off_at_ts is not None:
        remaining = int(relay_off_at_ts - clk.timestamp())
        if remaining < 0:
            remaining = 0
        bot.send(
            "Relay Control\n"
            "Device Status\n"
            "Relay : ON 🟢\n"
            "Left  : " + str(remaining) + " second(s)\n"
            "Time  : " + clk.now_str()
        )
    else:
        send_state("Device Status")

def handle_ping(message):
    print("handle_ping triggered")
    bot.send(
        "Relay Control\n"
        "PONG 🏓\n"
        "Time  : " + clk.now_str()
    )

def handle_time(message):
    print("handle_time triggered")
    bot.send(
        "Relay Control\n"
        "Time  : " + clk.now_str()
    )

def handle_default(message):
    text = get_text(message)
    if text is None:
        return

    text = text.lower()

    if text == 'on':
        handle_on(message)
    elif text == 'off':
        handle_off(message)
    elif text == 'status':
        handle_status(message)

# ====== Register ======
bot.register('/ping',   handle_ping)
bot.register('/time',   handle_time)
bot.register('/on',     handle_on)
bot.register('/off',    handle_off)
bot.register('/status', handle_status)
bot.set_default_handler(handle_default)
print("Listening...\n")

# ====== Main Loop ======
while True:
    ensure_wifi()

    if relay_enabled and relay_off_at_ts is not None:
        if clk.timestamp() >= relay_off_at_ts:
            relay_enabled = False
            relay_off_at_ts = None
            apply_outputs()  # turn the relay off even if Telegram is unreachable
            try:
                bot.send(
                    "Relay Control\n"
                    "Timer completed\n"
                    "Device Turned OFF 🔴\n"
                    "Time  : " + clk.now_str()
                )
            except Exception as e:
                print("Timer send error:", e)

    apply_outputs()
    
    # --- Time ReSync ---
    if clk.is_due(last_resync_ts, NTP_RESYNC):
        clk = TimeManager(timezone_offset_hours=TimeZone)
        last_resync_ts = clk.timestamp()
    
    
    # --- Telegram poll ---
    if clk.is_due(last_poll_ts, Telegram_Check_interval):
        try:
            bot.read_once()
        except Exception as e:
            print("Poll error:", e)
        last_poll_ts = clk.timestamp()
        gc.collect()

    time.sleep(LOOP_INTERVAL)
