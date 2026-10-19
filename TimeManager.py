import ntptime
import time

class TimeManager:
    
    def __init__(self, timezone_offset_hours):
        self.tz_offset = int(timezone_offset_hours * 3600)
        ntptime.settime()
    
    def now(self):
        """Returns (year, month, day, hour, minute, second)"""
        t = time.localtime(time.time() + self.tz_offset)
        return t[:6]
    
    def now_str(self):
        y, mo, d, h, mi, s = self.now()
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(y, mo, d, h, mi, s)
    
    def time_str(self):
        _, _, _, h, mi, s = self.now()
        return "{:02d}:{:02d}:{:02d}".format(h, mi, s)
    
    def date_str(self):
        y, mo, d, _, _, _ = self.now()
        return "{:04d}-{:02d}-{:02d}".format(y, mo, d)
    
    def timestamp(self):
        """Raw seconds since epoch, use this for calculations"""
        return time.time() + self.tz_offset
    
    def elapsed_since(self, ts):
        """How many seconds since a recorded timestamp"""
        return self.timestamp() - ts
    
    def is_due(self, last_run_ts, interval_seconds):
        """Returns True if interval has passed since last_run_ts"""
        return self.elapsed_since(last_run_ts) >= interval_seconds
    
    def at_time(self, hour, minute):
        """Returns True if current time matches hour:minute (any second)"""
        _, _, _, h, mi, _ = self.now()
        return h == hour and mi == minute
    
    def between(self, start_hour, start_min, end_hour, end_min):
        """Returns True if current time is within a range"""
        _, _, _, h, mi, _ = self.now()
        current = h * 60 + mi
        start   = start_hour * 60 + start_min
        end     = end_hour * 60 + end_min
        return start <= current < end