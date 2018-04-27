import random
import datetime
import math
import os

class ShortId:

    def __init__(self, worker_id=0):
        self.REDUCE_TIME = 1524783675
        self.version = 0
        self.counter = 0
        self.previous_seconds = -1
        self.worker_id = worker_id
        self.__alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'
        self.alphabet = self.__alphabet
        self.shuffle = None

    def reset_alphabet(self):
        self.alphabet = self.__alphabet
        self._reset_shuffle()

    def set_alphabet(self, alphabet):
        if len(alphabet) == 0 or len(set(alphabet)) == 0:
            raise RuntimeError("alphabet can't be empty")
        self.alphabet = alphabet
        self._reset_shuffle()

    def _reset_shuffle(self):
        shuffle = list(set(self.alphabet))
        random.shuffle(shuffle)
        self.shuffle = shuffle

    def get_shuffle(self):
        if not self.shuffle:
            self._reset_shuffle()
        return self.shuffle

    def _encode(self, number):
        done = False
        loop_counter = 0
        result = ''
        while not done:
            index = ((number >> 4 * loop_counter) & 0x0f) | (random.getrandbits(8) & 0x30)
            result += str(self.get_shuffle()[index % len(self.get_shuffle())])
            done = number < pow(16, loop_counter + 1)
            loop_counter += 1
        return result

    def generate(self):
        now = math.ceil(datetime.datetime.utcnow().timestamp())
        seconds =  now - self.REDUCE_TIME
        if seconds == self.previous_seconds:
            self.counter += 1
        else:
            self.previous_seconds = seconds
            self.counter = 0
        result = ''
        result += self._encode(self.version)
        result += self._encode(self.worker_id)
        if self.counter > 0:
            result += self._encode(self.counter)
        result += self._encode(seconds)
        return result


_worker_id = os.environ.get('shortid_worker', 0)
_short_id = ShortId(_worker_id)
set_alphabet = _short_id.set_alphabet
generate = _short_id.generate
reset_alphabet = _short_id.reset_alphabet