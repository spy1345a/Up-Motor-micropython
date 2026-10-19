import time
from config import Config
from utelegram import ubot
from TimeManager import TimeManager
import machine

# ====== Config ======
Telegram_token = Config.TOKEN
Group_id       = Config.GROUP_ID

# Pins Config
led   = machine.Pin(Config.Led_pin,   machine.Pin.OUT, value=0)
relay = machine.Pin(Config.Relay_pin, machine.Pin.OUT, value=0)

# Timings Config
TimeZone               = Config.TimeZone
Telegram_Check_interval = Config.Telegram_Check_internal
LOOP_INTERVAL           = Config.short_detect_interval

# ====== Time & Bot ======
clk = TimeManager(timezone_offset_hours=TimeZone)
print("Boot time:", clk.now_str())

bot = ubot(token=Telegram_token, chat_id=Group_id)
try:
    bot.send("Booted at: " + clk.now_str())
except Exception as e:
    print("Boot send error:", e)
print("Telegram bot setup done")

# ====== State ======
relay_enabled     = False
relay_off_at_ts   = None
last_poll_ts      = 0

# ====== Helpers ======
def relay_on():  relay.value(1)
def relay_off(): relay.value(0)
def led_on():    led.value(1)
def led_off():   led.value(0)

def apply_outputs():
    if relay_enabled:
        relay_on()
        led_on()
    else:
        relay_off()
        led_off()

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
        "Device Turned ON\n"
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
        send_state("Device Already OFF")
        return

    relay_enabled = False
    relay_off_at_ts = None
    apply_outputs()
    send_state("Device Turned OFF")

def handle_status(message):
    print("handle_status triggered")
    if relay_enabled and relay_off_at_ts is not None:
        remaining = int(relay_off_at_ts - clk.timestamp())
        if remaining < 0:
            remaining = 0
        bot.send(
            "Relay Control\n"
            "Device Status\n"
            "Relay : ON\n"
            "Left  : " + str(remaining) + " second(s)\n"
            "Time  : " + clk.now_str()
        )
    else:
        send_state("Device Status")

def handle_ping(message):
    print("handle_ping triggered")
    bot.send(
        "Relay Control\n"
        "PONG\n"
        "Time: " + clk.now_str()
    )

def handle_time(message):
    print("handle_time triggered")
    bot.send(
        "Relay Control\n"
        "Time: " + clk.now_str()
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
    if relay_enabled and relay_off_at_ts is not None:
        if clk.timestamp() >= relay_off_at_ts:
            relay_enabled = False
            relay_off_at_ts = None
            apply_outputs()
            bot.send(
                "Relay Control\n"
                "Timer completed\n"
                "Device Turned OFF\n"
                "Time  : " + clk.now_str()
            )

    apply_outputs()

    # --- Telegram poll ---
    if clk.is_due(last_poll_ts, Telegram_Check_interval):
        try:
            bot.read_once()
        except Exception as e:
            print("Poll error:", e)
        last_poll_ts = clk.timestamp()

    time.sleep(LOOP_INTERVAL)
