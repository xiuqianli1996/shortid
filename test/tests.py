import unittest
import shortid
import threading

class TestShortId(unittest.TestCase):

    def test_should_be_unambiquous_on_a_bunch_of_iterations(self):
        ids = []
        shortid.reset_alphabet()
        for i in range(0, 1000000):
            ids.append(shortid.generate())

        self.assertEqual(len(set(ids)), len(ids))

    def test_generate_max_length(self):
        lengths = []
        shortid.reset_alphabet()
        for i in range(0, 50000):
            lengths.append(len(shortid.generate()))
        self.assertEqual(max(lengths) < 12, True)


    def gen(self):
        for i in range(0, 20000):
            short_id = shortid.generate()
            self.lock.acquire()
            try:
                self.multi.append(short_id)
            finally:
                self.lock.release()


    def test_multi_thread_unique(self):
        self.multi = []
        self.lock = threading.Lock()
        shortid.reset_alphabet()
        for i in range(8):
            t = threading.Thread(target=self.gen)
            t.start()
            t.join()
        self.assertEqual(len(set(self.multi)), len(self.multi))


    def test_change_alphabet(self):
        shortid.set_alphabet('qwertyuiopasdfghjklzxcvbnm1234567890')
        ids = []
        for i in range(0, 10000):
            ids.append(shortid.generate())
        self.assertEqual(len(set(ids)), len(ids))
