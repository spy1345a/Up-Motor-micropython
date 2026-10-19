# Up-Motor (upmoter)

A MicroPython project (ESP32-class board) that controls a **relay + LED over Telegram**.
Send a command from a Telegram group and the device switches the relay on/off, with an
optional auto-off timer.

## What it does

- Connects to WiFi on boot and reconnects automatically if the link drops.
- Syncs the clock over NTP and applies a timezone offset.
- Listens for Telegram messages and controls a relay (and status LED).
- `/on <minutes>` turns the relay on for a set duration, then switches it off automatically.
- Reports state and timer remaining time back to the Telegram group.

## Files

| File | Role |
|------|------|
| `boot.py` | Connects to WiFi at startup; reboots if it times out. |
| `config.py` | **Local secrets/settings — not committed.** See below. |
| `example.config.py` | Template to copy into `config.py` (committed). |
| `main.py` | Relay/LED pins, command handlers, timer logic, main loop. |
| `TimeManager.py` | NTP sync, timezone offset, timestamp/interval helpers. |
| `utelegram.py` | Small homemade Telegram bot library (long-poll). |

## Commands

| Command | Action |
|---------|--------|
| `/on [minutes]` | Turn relay ON. Defaults to 60 minutes if omitted. |
| `/off` | Turn relay OFF. |
| `/status` | Report relay state and seconds remaining. |
| `/ping` | Health check (PONG). |
| `/time` | Report current device time. |

Plain text (no slash) also works: `on`, `off`, `status`.

## `config.py` (create it yourself, keep it private)

`config.py` is git-ignored because it holds WiFi and Telegram credentials.
A ready-to-edit template is provided as **`example.config.py`** — copy it to
`config.py` and fill in your own values.
It defines a `Config` class with these attributes:

```python
class Config:
    # WiFi
    WIFI_NAME = "..."
    WIFI_PASS = "..."

    # Telegram
    TOKEN    = "..."   # bot token from @BotFather
    GROUP_ID = "..."   # target chat/group id

    # Pins
    Led_pin   = 2
    Relay_pin = 4

    # Timing
    TimeZone                 = 0     # hours offset from UTC
    Telegram_Check_internal  = 3     # seconds between Telegram polls
    short_detect_interval    = 0.5   # main loop sleep (seconds)
    Telegram_Poll_timeout    = 5     # optional; long-poll wait (defaults to 5)
```

> Note: attribute names `Telegram_Check_internal` and `short_detect_interval` are
> spelled exactly as used by the code.

## Deploy

Copy `boot.py`, `main.py`, `TimeManager.py`, `utelegram.py`, and your `config.py`
to the board (e.g. with `mpremote` or `ampy`), then reset:

```sh
mpremote cp boot.py main.py TimeManager.py utelegram.py config.py :
mpremote reset
```

## License

Licensed under the **PolyForm Noncommercial License 1.0.0** — see [LICENSE](LICENSE).

You are free to use, copy, modify, and share this code for any
**noncommercial** purpose (personal, hobby, educational, research, charity,
etc.). **Commercial use is not permitted.** For commercial licensing, contact
the licensor.
