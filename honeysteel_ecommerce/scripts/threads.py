import threading
import time

# Paylaşılan kaynak
shared_resource = 0

# Mutex (Lock)
mutex = threading.Lock()

def increment():
    global shared_resource
    for _ in range(5):
        with mutex:  
            current = shared_resource
            time.sleep(0.1)  
            shared_resource = current + 1
            print(f"Artırıldı: {shared_resource}")

threads = []
for _ in range(3): 
    thread = threading.Thread(target=increment)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(f"Sonuç: {shared_resource}")
