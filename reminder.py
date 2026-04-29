import tkinter as tk
import threading
import time

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("释放助手 · 圣多纳")
        self.root.geometry("390x420")
        self.root.resizable(False, False)

        # 默认参数（单位：秒）
        self.interval = tk.IntVar(value=30)      # 间隔时间
        self.duration = tk.IntVar(value=3)       # 显示时间
        self.max_count = tk.IntVar(value=0)      # 0 表示无限循环
        self.opacity = tk.DoubleVar(value=0.85)

        self.running = False
        self.current_reminder_thread = None
        self.reminder_win = None
        self.cancel_flag = False

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="💡 圣多纳释放提醒器", font=("微软雅黑", 14, "bold")).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=5, padx=20, fill="x")

        tk.Label(frame, text="⏱️ 弹出间隔（秒）:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frame, textvariable=self.interval, width=8).grid(row=0, column=1, padx=5)

        tk.Label(frame, text="⏳ 显示时长（秒）:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frame, textvariable=self.duration, width=8).grid(row=1, column=1, padx=5)

        tk.Label(frame, text="🔁 总循环次数（0=无限）:").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(frame, textvariable=self.max_count, width=8).grid(row=2, column=1, padx=5)

        tk.Label(frame, text="🌫️ 透明度 (0.2～1.0):").grid(row=3, column=0, sticky="w", pady=5)
        tk.Scale(frame, from_=0.2, to=1.0, resolution=0.01, orient="horizontal", variable=self.opacity, length=150).grid(row=3, column=1, padx=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)
        self.start_btn = tk.Button(btn_frame, text="▶ 开始", command=self.start, width=10, bg="#c7e9c7")
        self.start_btn.pack(side="left", padx=10)
        self.stop_btn = tk.Button(btn_frame, text="⏹️ 停止", command=self.stop, width=10, bg="#f5c2c2")
        self.stop_btn.pack(side="left", padx=10)

        self.status_label = tk.Label(self.root, text="⚪ 未启动", fg="gray")
        self.status_label.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start(self):
        if self.running:
            return
        self.running = True
        self.cancel_flag = False
        self.current_count = 0
        self.status_label.config(text="🟢 运行中", fg="green")
        threading.Thread(target=self._remind_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.cancel_flag = True
        self._close_reminder_if_open()
        self.status_label.config(text="⚪ 已停止", fg="gray")

    def _close_reminder_if_open(self):
        if self.reminder_win and self.reminder_win.winfo_exists():
            self.reminder_win.destroy()
            self.reminder_win = None

    def _show_reminder(self, text="现在想要什么？"):
        def create_window():
            # 如果已有提醒窗口，先关闭
            if self.reminder_win and self.reminder_win.winfo_exists():
                self.reminder_win.destroy()
            win = tk.Toplevel(self.root)
            win.title("")
            win.overrideredirect(True)  # 无边框
            win.attributes("-topmost", True)  # 置顶
            win.attributes("-alpha", self.opacity.get())  # 透明度

            # 显示文本
            label = tk.Label(win, text=text, font=("微软雅黑", 20, "bold"), fg="white", bg="#2c3e50", padx=30, pady=20)
            label.pack()

            win.update_idletasks()
            # 定位到右下角
            screen_width = win.winfo_screenwidth()
            screen_height = win.winfo_screenheight()
            win_width = win.winfo_width()
            win_height = win.winfo_height()
            x = screen_width - win_width - 20
            y = screen_height - win_height - 60
            win.geometry(f"+{x}+{y}")

            self.reminder_win = win

            # 设定自动关闭计时器
            win.after(int(self.duration.get() * 1000), lambda: self._close_reminder_if_open())

        # 必须在主线程中创建窗口
        self.root.after(0, create_window)

    def _remind_loop(self):
        max_cycles = self.max_count.get()
        while self.running and not self.cancel_flag:
            if max_cycles > 0 and self.current_count >= max_cycles:
                self.root.after(0, self.stop)
                self.root.after(0, lambda: self.status_label.config(text="✅ 已完成设定次数", fg="blue"))
                break

            self.current_count += 1
            # 弹出提醒
            self._show_reminder("现在想要什么？")
            # 等待显示时长（此期间不做事情，但可响应停止）
            for _ in range(int(self.duration.get())):
                if not self.running or self.cancel_flag:
                    break
                time.sleep(1)

            # 等待间隔（不打断当前显示）
            for _ in range(int(self.interval.get())):
                if not self.running or self.cancel_flag:
                    break
                time.sleep(1)

        self.running = False

    def on_close(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()