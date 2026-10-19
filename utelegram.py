import time
import gc
import ujson
import urequests



class ubot:
    
    def __init__(self, token, chat_id, offset=0, poll_timeout=5):
        self.url = 'https://api.telegram.org/bot' + token
        self.commands = {}
        self.default_handler = None
        # message_offset is the next update_id Telegram should return
        self.message_offset = offset
        self.sleep_btw_updates = 3
        self.poll_timeout = poll_timeout
        self.chat_id = chat_id

        # Drop any messages that arrived before/while booting
        messages = self.read_messages()
        if messages:
            self.message_offset = messages[-1]['update_id'] + 1


    def send(self, text):
        data = {'chat_id': self.chat_id, 'text': text}
        response = None
        try:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            response = urequests.post(self.url + '/sendMessage', json=data, headers=headers)
            return True
        except Exception as e:
            print("send error:", e)
            return False
        finally:
            if response is not None:
                try:
                    response.close()
                except Exception:
                    pass

    def read_messages(self):
        result = []
        self.query_updates = {
            'offset': self.message_offset,
            'limit': 10,
            'timeout': self.poll_timeout,
            'allowed_updates': ['message']}

        response = None
        try:
            response = urequests.post(self.url + '/getUpdates', json=self.query_updates)
            update_messages = response.json()
            if update_messages and 'result' in update_messages:
                for item in update_messages['result']:
                    result.append(item)
            return result
        except (ValueError):
            return None
        except (OSError):
            print("OSError: request timed out")
            return None
        finally:
            if response is not None:
                try:
                    response.close()
                except Exception:
                    pass

    def listen(self):
        while True:
            self.read_once()
            time.sleep(self.sleep_btw_updates)
            gc.collect()

    def read_once(self):
        messages = self.read_messages()
        if messages:
            for message in messages:
                self.message_offset = message['update_id'] + 1
                self.message_handler(message)
    
    def register(self, command, handler):
        self.commands[command] = handler

    def set_default_handler(self, handler):
        self.default_handler = handler

    def set_sleep_btw_updates(self, sleep_time):
        self.sleep_btw_updates = sleep_time

    def message_handler(self, message):
        if 'text' in message['message']:
            parts = message['message']['text'].split(' ')
            if parts[0] in self.commands:
                self.commands[parts[0]](message)
            else:
                if self.default_handler:
                    self.default_handler(message)
