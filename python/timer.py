from time import time

class Timer:
    def __init__(self):
        self.start_time = time()
    
    def __del__(self):
        print(f"Duration: {round(time() - self.start_time, 4)} sec.")

if __name__ == "__main__":
    from time import sleep
    from random import randint

    for _ in range(1, 5):
        _ = Timer()
        sleep(randint(1, 4))
    
