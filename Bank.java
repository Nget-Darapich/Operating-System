import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Bank {
    public static int balance = 0;
    // Uncomment the lock lines to simulate a Mutex Lock
    // private static final Lock lock = new ReentrantLock();

    public void deposit() {
        balance += 100;
    }

    public void withdraw() {
        balance -= 100;
    }

    public int getValue() {
        return balance;
    }

    public void runSimulation() {
        // lock.lock(); // Acquire lock
        try {
            deposit();
            System.out.println("Value after deposit " + Thread.currentThread().getName() + ": " + getValue());
            withdraw();
            System.out.println("Value after withdraw " + Thread.currentThread().getName() + ": " + getValue());
        } finally {
            // lock.unlock(); // Release lock
        }
    }
}