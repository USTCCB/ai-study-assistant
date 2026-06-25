# Java 并发编程笔记

## 线程池
ThreadPoolExecutor 是 Java 中管理线程池的核心类。它通过复用线程减少创建/销毁开销。
核心参数：corePoolSize、maximumPoolSize、keepAliveTime、workQueue。

## synchronized vs ReentrantLock
synchronized 是 JVM 关键字，自动释放锁；ReentrantLock 是 JDK 类，需要手动 lock/unlock，
支持公平锁、可中断、条件变量等高级特性。

## volatile 关键字
volatile 保证变量的可见性和禁止指令重排，但不保证原子性。适合一写多读场景。
