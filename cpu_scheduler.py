import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import csv
from copy import deepcopy

class Process:
    def __init__(self, pid, arrival, burst, priority=1):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst
        self.waiting = 0
        self.turnaround = 0
        self.response = -1
        self.completion = 0
        self.level = 0  # Used for MLFQ

class CPUScheduler:
    @staticmethod
    def fcfs(processes):
        procs = sorted(deepcopy(processes), key=lambda x: x.arrival)
        time = 0
        gantt = []
        for proc in procs:
            if time < proc.arrival:
                time = proc.arrival
            start = time
            finish = start + proc.burst
            gantt.append({'pid': proc.pid, 'start': start, 'finish': finish})
            proc.response = start - proc.arrival
            proc.waiting = start - proc.arrival
            proc.turnaround = finish - proc.arrival
            proc.completion = finish
            time = finish
        return gantt, procs

    @staticmethod
    def sjf(processes):
        procs = deepcopy(processes)
        time = 0
        gantt = []
        completed = []
        remaining = procs.copy()
        while remaining:
            available = [p for p in remaining if p.arrival <= time]
            if not available:
                time = min(p.arrival for p in remaining)
                continue
            shortest = min(available, key=lambda x: x.burst)
            start = time
            finish = start + shortest.burst
            gantt.append({'pid': shortest.pid, 'start': start, 'finish': finish})
            shortest.response = start - shortest.arrival
            shortest.waiting = start - shortest.arrival
            shortest.turnaround = finish - shortest.arrival
            shortest.completion = finish
            time = finish
            remaining.remove(shortest)
            completed.append(shortest)
        return gantt, completed

    @staticmethod
    def srt(processes):
        procs = deepcopy(processes)
        time = 0
        gantt = []
        completed = []
        n = len(procs)
        while len(completed) < n:
            available = [p for p in procs if p.arrival <= time and p.remaining > 0]
            if not available:
                time = min(p.arrival for p in procs if p.remaining > 0)
                continue
            shortest = min(available, key=lambda x: x.remaining)
            if shortest.response == -1:
                shortest.response = time - shortest.arrival
            if gantt and gantt[-1]['pid'] == shortest.pid:
                gantt[-1]['finish'] += 1
            else:
                gantt.append({'pid': shortest.pid, 'start': time, 'finish': time + 1})
            shortest.remaining -= 1
            time += 1
            if shortest.remaining == 0:
                shortest.completion = time
                shortest.turnaround = time - shortest.arrival
                shortest.waiting = shortest.turnaround - shortest.burst
                completed.append(shortest)
        return gantt, completed

    @staticmethod
    def round_robin(processes, quantum):
        procs = sorted(deepcopy(processes), key=lambda x: x.arrival)
        time = 0
        gantt = []
        queue = []
        completed = []
        ready_procs = list(procs)
        while ready_procs and ready_procs[0].arrival <= time:
            queue.append(ready_procs.pop(0))
        while queue or ready_procs:
            if not queue:
                time = ready_procs[0].arrival
                while ready_procs and ready_procs[0].arrival <= time:
                    queue.append(ready_procs.pop(0))
            current = queue.pop(0)
            if current.response == -1:
                current.response = time - current.arrival
            exec_time = min(quantum, current.remaining)
            gantt.append({'pid': current.pid, 'start': time, 'finish': time + exec_time})
            for _ in range(exec_time):
                time += 1
                while ready_procs and ready_procs[0].arrival <= time:
                    queue.append(ready_procs.pop(0))
            current.remaining -= exec_time
            if current.remaining > 0:
                queue.append(current)
            else:
                current.completion = time
                current.turnaround = time - current.arrival
                current.waiting = current.turnaround - current.burst
                completed.append(current)
        return gantt, completed

    @staticmethod
    def mlfq(processes, quantums):
        procs = sorted(deepcopy(processes), key=lambda x: x.arrival)
        queues = [[], [], []]
        time = 0
        gantt = []
        completed = []
        ready_procs = list(procs)
        
        while len(completed) < len(procs):
            while ready_procs and ready_procs[0].arrival <= time:
                queues[0].append(ready_procs.pop(0))
            
            current = None
            q_idx = -1
            for i in range(3):
                if queues[i]:
                    current = queues[i].pop(0)
                    q_idx = i
                    break
            
            if not current:
                time = ready_procs[0].arrival if ready_procs else time + 1
                continue

            if current.response == -1:
                current.response = time - current.arrival
            
            q = quantums[q_idx] if q_idx < 2 else current.remaining
            exec_time = min(q, current.remaining)
            gantt.append({'pid': current.pid, 'start': time, 'finish': time + exec_time})
            
            for _ in range(exec_time):
                time += 1
                while ready_procs and ready_procs[0].arrival <= time:
                    queues[0].append(ready_procs.pop(0))
            
            current.remaining -= exec_time
            if current.remaining > 0:
                next_level = min(2, q_idx + 1)
                queues[next_level].append(current)
            else:
                current.completion = time
                current.turnaround = time - current.arrival
                current.waiting = current.turnaround - current.burst
                completed.append(current)
        return gantt, completed

class ProcessInputDialog:
    def __init__(self, parent, process=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add/Edit Process")
        self.dialog.geometry("300x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # PID
        ttk.Label(frame, text="Process ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pid_var = tk.StringVar(value=process.pid if process else "P1")
        ttk.Entry(frame, textvariable=self.pid_var, width=20).grid(row=0, column=1, pady=5)
        
        # Arrival Time
        ttk.Label(frame, text="Arrival Time:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.arrival_var = tk.IntVar(value=process.arrival if process else 0)
        ttk.Spinbox(frame, from_=0, to=100, textvariable=self.arrival_var, width=18).grid(row=1, column=1, pady=5)
        
        # Burst Time
        ttk.Label(frame, text="Burst Time:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.burst_var = tk.IntVar(value=process.burst if process else 5)
        ttk.Spinbox(frame, from_=1, to=100, textvariable=self.burst_var, width=18).grid(row=2, column=1, pady=5)
        
        # Priority
        ttk.Label(frame, text="Priority:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.IntVar(value=process.priority if process else 1)
        ttk.Spinbox(frame, from_=1, to=10, textvariable=self.priority_var, width=18).grid(row=3, column=1, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to OK
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
    def ok_clicked(self):
        pid = self.pid_var.get().strip()
        if not pid:
            messagebox.showerror("Error", "Process ID cannot be empty!", parent=self.dialog)
            return
        
        try:
            arrival = self.arrival_var.get()
            burst = self.burst_var.get()
            priority = self.priority_var.get()
            
            if burst < 1:
                messagebox.showerror("Error", "Burst time must be at least 1!", parent=self.dialog)
                return
                
            self.result = Process(pid, arrival, burst, priority)
            self.dialog.destroy()
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers!", parent=self.dialog)
    
    def cancel_clicked(self):
        self.dialog.destroy()

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Algorithm Simulator")
        self.root.geometry("1400x900")
        self.processes = [
            Process('P1', 0, 5, 1),
            Process('P2', 1, 3, 2),
            Process('P3', 2, 8, 1),
            Process('P4', 3, 6, 3)
        ]
        self.current_figure = None
        self.setup_ui()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        ttk.Label(main_frame, text="🧠 CPU Scheduling Simulator", font=('Arial', 20, 'bold')).grid(row=0, column=0, pady=10)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self.setup_process_frame(top_frame)
        self.setup_control_frame(top_frame)

        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        main_frame.rowconfigure(2, weight=1)

    def setup_process_frame(self, parent):
        pf = ttk.LabelFrame(parent, text="Process Input", padding="10")
        pf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        btn_f = ttk.Frame(pf)
        btn_f.pack(fill=tk.X, pady=5)
        ttk.Button(btn_f, text="➕ Add", command=self.add_process).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_f, text="✏️ Edit", command=self.edit_process).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_f, text="🗑️ Remove", command=self.remove_process).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_f, text="🗑️ Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=2)

        cols = ('PID', 'Arrival', 'Burst', 'Priority')
        self.tree = ttk.Treeview(pf, columns=cols, show='headings', height=6)
        for c in cols: 
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Double-click to edit
        self.tree.bind('<Double-Button-1>', lambda e: self.edit_process())
        
        self.refresh_process_table()

    def setup_control_frame(self, parent):
        cf = ttk.LabelFrame(parent, text="Controls", padding="10")
        cf.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

        self.algo_var = tk.StringVar(value='FCFS')
        algos = [('FCFS', 'FCFS'), ('SJF', 'SJF'), ('SRT', 'SRT'), ('Round Robin', 'RR'), ('MLFQ', 'MLFQ')]
        for t, v in algos:
            ttk.Radiobutton(cf, text=t, variable=self.algo_var, value=v, command=self.toggle_params).pack(anchor=tk.W)

        self.q_frame = ttk.Frame(cf)
        ttk.Label(self.q_frame, text="Quantum:").pack(side=tk.LEFT)
        self.q_var = tk.IntVar(value=2)
        ttk.Spinbox(self.q_frame, from_=1, to=20, textvariable=self.q_var, width=5).pack(side=tk.LEFT)

        ttk.Button(cf, text="▶ Run Simulation", command=self.run_simulation).pack(fill=tk.X, pady=10)

    def toggle_params(self):
        self.q_frame.pack_forget()
        if self.algo_var.get() in ['RR', 'MLFQ']: 
            self.q_frame.pack(pady=5)

    def refresh_process_table(self):
        for i in self.tree.get_children(): 
            self.tree.delete(i)
        for p in self.processes: 
            self.tree.insert('', tk.END, values=(p.pid, p.arrival, p.burst, p.priority))

    def add_process(self):
        # Suggest next process ID
        next_pid = f"P{len(self.processes) + 1}"
        default_process = Process(next_pid, 0, 5, 1)
        
        dialog = ProcessInputDialog(self.root, default_process)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Check for duplicate PID
            if any(p.pid == dialog.result.pid for p in self.processes):
                messagebox.showerror("Error", f"Process ID '{dialog.result.pid}' already exists!")
                return
            self.processes.append(dialog.result)
            self.refresh_process_table()

    def edit_process(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a process to edit.")
            return
        
        idx = self.tree.index(sel[0])
        old_process = self.processes[idx]
        
        dialog = ProcessInputDialog(self.root, old_process)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Check for duplicate PID (excluding current process)
            if any(i != idx and p.pid == dialog.result.pid for i, p in enumerate(self.processes)):
                messagebox.showerror("Error", f"Process ID '{dialog.result.pid}' already exists!")
                return
            self.processes[idx] = dialog.result
            self.refresh_process_table()

    def remove_process(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.processes[idx]
            self.refresh_process_table()
        else:
            messagebox.showinfo("Info", "Please select a process to remove.")

    def clear_all(self):
        if self.processes:
            if messagebox.askyesno("Confirm", "Are you sure you want to clear all processes?"):
                self.processes.clear()
                self.refresh_process_table()

    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Please add at least one process before running simulation.")
            return
        
        algo = self.algo_var.get()
        s = CPUScheduler()
        if algo == 'FCFS': 
            g, r = s.fcfs(self.processes)
        elif algo == 'SJF': 
            g, r = s.sjf(self.processes)
        elif algo == 'SRT': 
            g, r = s.srt(self.processes)
        elif algo == 'RR': 
            g, r = s.round_robin(self.processes, self.q_var.get())
        elif algo == 'MLFQ': 
            g, r = s.mlfq(self.processes, [self.q_var.get(), self.q_var.get()*2, 999])
        self.display_results(g, r)

    def display_results(self, gantt, results):
        # Close any existing figure
        if self.current_figure:
            plt.close(self.current_figure)
            self.current_figure = None
        
        for w in self.results_frame.winfo_children(): 
            w.destroy()
        nb = ttk.Notebook(self.results_frame)
        nb.pack(fill=tk.BOTH, expand=True)

        # Gantt Chart
        gf = ttk.Frame(nb)
        nb.add(gf, text="Gantt Chart")
        fig, ax = plt.subplots(figsize=(10, 2))
        self.current_figure = fig  # Store reference to figure
        colors = plt.cm.Set3.colors
        pid_to_color = {}
        color_idx = 0
        
        for i, s in enumerate(gantt):
            if s['pid'] not in pid_to_color:
                pid_to_color[s['pid']] = colors[color_idx % len(colors)]
                color_idx += 1
            
            ax.barh(0, s['finish']-s['start'], left=s['start'], height=0.5, 
                   color=pid_to_color[s['pid']], edgecolor='black', linewidth=1.5)
            ax.text((s['start']+s['finish'])/2, 0, s['pid'], ha='center', va='center', 
                   fontweight='bold', fontsize=10)
        
        ax.set_yticks([])
        ax.set_xlabel("Time", fontsize=12)
        ax.set_title("Gantt Chart", fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, gf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Metrics Table
        mf = ttk.Frame(nb)
        nb.add(mf, text="Metrics")
        cols = ('PID', 'Waiting', 'Turnaround', 'Response')
        mtree = ttk.Treeview(mf, columns=cols, show='headings')
        for c in cols: 
            mtree.heading(c, text=c)
            mtree.column(c, anchor=tk.CENTER)
        
        total_wait = 0
        total_turn = 0
        total_resp = 0
        
        for p in results: 
            mtree.insert('', tk.END, values=(p.pid, p.waiting, p.turnaround, p.response))
            total_wait += p.waiting
            total_turn += p.turnaround
            total_resp += p.response
        
        # Add averages
        n = len(results)
        mtree.insert('', tk.END, values=('Average', 
                                         f'{total_wait/n:.2f}', 
                                         f'{total_turn/n:.2f}', 
                                         f'{total_resp/n:.2f}'))
        
        mtree.pack(fill=tk.BOTH, expand=True)
    
    def on_closing(self):
        """Clean up resources before closing"""
        if self.current_figure:
            plt.close(self.current_figure)
        plt.close('all')  # Close any remaining matplotlib figures
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()