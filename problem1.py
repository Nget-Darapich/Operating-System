import threading
import time
import random

# --- Shared Memory and Parameters ---
BUFFER_SIZE = 100
buffer = [None] * BUFFER_SIZE
current_write_pos = 0
current_read_pos = 0

# --- Semaphores and Initial Values ---
S = threading.Semaphore(0)      # full_pairs: starts at 0
space = threading.Semaphore(50)  # empty_spaces: room for 50 pairs
lock = threading.Semaphore(1)   # mutex: ensure consecutive storage

def producer(machine_id):
    global current_write_pos
    while True:
        try:
            # Produce pair P1, P2
            p1 = f"M{machine_id}-P1"
            p2 = f"M{machine_id}-P2"
            
            # Rule 1 & 3: Check if 2 spaces are available
            if not space.acquire(timeout=2):
                print(f"ERROR: Machine {machine_id} timed out waiting for buffer space. (Buffer Full)")
                continue

            # Rule 2: Enter critical section for consecutive placement
            lock.acquire()
            
            # Double-check buffer bounds before writing (Error Prevention)
            if buffer[current_write_pos] is not None:
                print(f"CRITICAL ERROR: Overwriting data at index {current_write_pos}")
            
            print(f"Machine {machine_id} placing pair at [{current_write_pos}, {current_write_pos+1}]")
            buffer[current_write_pos] = p1
            buffer[current_write_pos + 1] = p2
            current_write_pos = (current_write_pos + 2) % BUFFER_SIZE
            
            lock.release()
            S.release()  # Signal consumer that pair is ready
            
            time.sleep(random.uniform(0.1, 0.5))
            
        except Exception as e:
            print(f"SYSTEM ERROR in Producer {machine_id}: {e}")
            if lock.locked(): lock.release() # Prevent deadlock on failure

def consumer():
    global current_read_pos
    while True:
        try:
            # Rule 4: Packaging machine breaks if it finds buffer empty
            # wait(S) ensures we only proceed when at least 2 particles exist
            if not S.acquire(timeout=5):
                print("ERROR: Consumer timed out. (Buffer Empty/System Idle)")
                continue
            
            # Error checking for valid pair data
            p1 = buffer[current_read_pos]
            p2 = buffer[current_read_pos + 1]
            
            if p1 is None or p2 is None:
                raise ValueError(f"Consumer found corrupted data at index {current_read_pos}")

            print(f"Consumer fetched: ({p1}, {p2})")
            
            # Clear buffer after fetching (Simulation of removal)
            buffer[current_read_pos] = None
            buffer[current_read_pos + 1] = None
            
            current_read_pos = (current_read_pos + 2) % BUFFER_SIZE
            
            space.release()  # Signal that 1 pair space is now free
            
            # Package and ship
            time.sleep(0.4)
            
        except ValueError as ve:
            print(f"DATA ERROR: {ve}")
        except Exception as e:
            print(f"SYSTEM ERROR in Consumer: {e}")

# Start Simulation
for i in range(1, 4):
    threading.Thread(target=producer, args=(i,), daemon=True).start()
threading.Thread(target=consumer, daemon=True).start()

time.sleep(5)
print("Simulation monitor finished.")