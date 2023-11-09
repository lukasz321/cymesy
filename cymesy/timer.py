from time import time

class Timer:
    def __init__(self):
        self.start_time = time()

    def __del__(self):
        print(f"Timer destroyed; duration: {round(time() - self.start_time, 5)} sec.")

    def tock(self):
        print(f"Tock; duration: {round(time() - self.start_time, 5)} sec.")
