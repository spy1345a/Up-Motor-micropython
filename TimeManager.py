import ntptime
import time

class TimeManager:
    
    def __init__(self, timezone_offset_hours, ntp_retries=3, retry_delay=2):
        self.tz_offset = int(timezone_offset_hours * 3600)
        self.synced = self._sync_time(ntp_retries, retry_delay)

    def _sync_time(self, retries, delay):
        """Try to sync via NTP. Returns True on success; on repeated failure
        it warns and continues (delta-based timers still work)."""
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                ntptime.settime()
                print("NTP sync OK")
                return True
            except Exception as e:
                last_error = e
                print("NTP sync failed ({}/{}): {}".format(attempt, retries, e))
                time.sleep(delay)
        print("WARNING: NTP sync failed after {} attempts: {}".format(retries, last_error))
        print("WARNING: clock not synced; only time deltas are reliable")
        return False
    
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