import time

class Display:
    def __init__(self, queue):
        self.queue = queue

    def start(self):
        while True:
            while not self.queue.empty():
                msg = self.queue.get()
                print("[display] received:", msg)
            time.sleep(0.2)
