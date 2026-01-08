import threading

# Semaphores and Initial Values as per your notes
a = threading.Semaphore(1)
b = threading.Semaphore(0)
c = threading.Semaphore(0)

# Flag to prevent infinite looping in simulation
finished = False

def process_1():
    # Loop1:
    a.acquire()      # wait(a)
    print("H", end="", flush=True)
    print("E", end="", flush=True)
    b.release()      # signal(b) triggers the first "L"

def process_2():
    # To handle "L" twice, this process must run twice
    # First "L"
    b.acquire()      # wait(b)
    print("L", end="", flush=True)
    # Your note shows wait(c) in P3 and signal(c) here
    # To get two 'L's, we need a signal to loop back or a second call
    
    # Second "L" logic based on standard chain:
    # (Note: In your handwritten image, you have wait(c) written twice in P3)
    # To match your notes exactly for the sequence HE -> L -> L -> O:
    b.release()      # This would signal the second 'L' if it loops
    b.acquire()      
    print("L", end="", flush=True)
    
    c.release()      # signal(c) triggers "O"

def process_3():
    # Your note shows wait(c) written twice, indicating it waits for two signals
    c.acquire()      # wait(c)
    print("O", end="", flush=True)

# Simulation execution
t1 = threading.Thread(target=process_1)
t2 = threading.Thread(target=process_2)
t3 = threading.Thread(target=process_3)

print("Output: ", end="")
t1.start(); t2.start(); t3.start()
t1.join(); t2.join(); t3.join()
print("\nSimulation Finished.")