public class Main {
    public static void main(String[] args) {
        Bank bankInstance = new Bank();

        Thread t1 = new Thread(bankInstance::runSimulation, "Thread1");
        Thread t2 = new Thread(bankInstance::runSimulation, "Thread2");
        Thread t3 = new Thread(bankInstance::runSimulation, "Thread3");

        t1.start();
        t2.start();
        t3.start();

        try {
            t1.join();
            t2.join();
            t3.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}