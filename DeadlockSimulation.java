import java.util.concurrent.Semaphore;

class Account {
    String name;
    int balance;
    // Semaphore with 1 permit = Mutex
    Semaphore lock = new Semaphore(1);

    Account(String name, int balance) {
        this.name = name;
        this.balance = balance;
    }
}

class Transfer {
    static void transfer(Account from, Account to, int amount) {
        // LOCK ORDERING: Always lock the accounts in the same alphabetical order
        Account first, second;
        if (from.name.compareTo(to.name) < 0) {
            first = from;
            second = to;
        } else {
            first = to;
            second = from;
        }

        try {
            System.out.println(Thread.currentThread().getName() + " attempting to lock " + first.name);
            first.lock.acquire();
            System.out.println(Thread.currentThread().getName() + " locked " + first.name);

            // Small delay to prove deadlock is impossible now
            Thread.sleep(100);

            System.out.println(Thread.currentThread().getName() + " attempting to lock " + second.name);
            second.lock.acquire();
            System.out.println(Thread.currentThread().getName() + " locked " + second.name);

            // Critical Section
            if (from.balance >= amount) {
                from.balance -= amount;
                to.balance += amount;
                System.out.println(Thread.currentThread().getName() + " transferred $" + amount + " successfully.");
            } else {
                System.out.println(Thread.currentThread().getName() + " failed: Insufficient funds.");
            }

            // Release in reverse order
            second.lock.release();
            first.lock.release();
            System.out.println(Thread.currentThread().getName() + " released all locks.");

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

public class DeadlockSimulation {
    public static void main(String[] args) {
        Account account1 = new Account("Account-1", 1000);
        Account account2 = new Account("Account-2", 1000);

        // Thread 1: Acc1 -> Acc2
        Thread t1 = new Thread(() -> 
            Transfer.transfer(account1, account2, 100), "Thread-1");

        // Thread 2: Acc2 -> Acc1
        Thread t2 = new Thread(() -> 
            Transfer.transfer(account2, account1, 200), "Thread-2");

        t1.start();
        t2.start();
    }
}