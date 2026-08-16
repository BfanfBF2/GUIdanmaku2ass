#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from merge_ass import *

# ---------- 路径配置（自动适配当前用户）----------
USER = os.getenv("USER") or os.getlogin()
DANMAKU_DIR = os.path.expanduser("~/danmaku2ass")
LINKS_FILE = os.path.join(DANMAKU_DIR, "links.txt")
RULES_FILE = os.path.join(DANMAKU_DIR, "rules.txt")
BASH_SCRIPT = os.path.join(DANMAKU_DIR, "bdanmaku.sh")
RENAME_SCRIPT = os.path.join(DANMAKU_DIR, "renameass.py")



# 定义 MergeWindow 类（放在 Application 类外部或内部）

class MergeWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("合并 ASS 弹幕")
        self.geometry("600x400")
        self.resizable(True, True)

        self.file_list = []   # 存储文件路径

        # 顶部提示
        ttk.Label(self, text="添加多个 ASS 文件，按时间顺序合并成一个文件").pack(pady=5)

        # 文件列表区域
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # 按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="添加文件", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="移除选中", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空列表", command=self.clear_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="合并", command=self.merge_files).pack(side=tk.RIGHT, padx=5)

        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self, textvariable=self.status_var).pack(pady=5)

    def add_files(self):
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="选择 ASS 弹幕文件",
            filetypes=[("ASS files", "*.ass"), ("All files", "*.*")]
        )
        if files:
            for f in files:
                if f not in self.file_list:
                    self.file_list.append(f)
                    self.listbox.insert(tk.END, os.path.basename(f))
            self.status_var.set(f"已添加 {len(files)} 个文件，共 {len(self.file_list)} 个")

    def remove_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        # 从后往前删除
        for idx in reversed(selected):
            del self.file_list[idx]
            self.listbox.delete(idx)
        self.status_var.set(f"当前共 {len(self.file_list)} 个文件")

    def clear_list(self):
        self.file_list.clear()
        self.listbox.delete(0, tk.END)
        self.status_var.set("列表已清空")

    def merge_files(self):
        if len(self.file_list) < 2:
            self.status_var.set("至少选择两个文件才能合并")
            return

        from tkinter import filedialog
        output_path = filedialog.asksaveasfilename(
            title="保存合并后的 ASS 文件",
            defaultextension=".ass",
            filetypes=[("ASS files", "*.ass")]
        )
        if not output_path:
            return

        self.status_var.set("正在合并，请稍候...")
        self.update_idletasks()

        try:
            # 调用 merge_ass 模块
            from merge_ass import merge_ass_files
            merge_ass_files(self.file_list, output_path)
            self.status_var.set(f"合并完成！保存至：{output_path}")
            # 可选：自动打开所在文件夹
        except Exception as e:
            self.status_var.set(f"合并失败：{e}")
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("B站弹幕工具 by BfanfBF2")
        self.geometry("820x750")
        self.resizable(True, True)

        # 确保 danmaku2ass 目录存在
        os.makedirs(DANMAKU_DIR, exist_ok=True)
        os.chdir(DANMAKU_DIR)

        # 窗口图标（可选）
        icon_path = os.path.join(DANMAKU_DIR, "app_icon.png")
        if os.path.exists(icon_path):
            try:
                self.iconphoto(True, tk.PhotoImage(file=icon_path))
            except:
                pass

        self.create_widgets()
        self.load_links()
        self.load_rules()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---------- 链接输入 ----------
        link_frame = ttk.LabelFrame(main_frame, text="B站链接（每行一个）", padding="5")
        link_frame.pack(fill=tk.BOTH, expand=False, pady=5)

        self.link_text = scrolledtext.ScrolledText(link_frame, height=6, wrap=tk.NONE)
        self.link_text.pack(fill=tk.BOTH, expand=True)

        link_btn_frame = ttk.Frame(link_frame)
        link_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(link_btn_frame, text="保存链接到 links.txt", command=self.save_links).pack(side=tk.LEFT, padx=5)

        # ---------- 规则管理 ----------
        rule_frame = ttk.LabelFrame(main_frame, text="字幕重命名规则（选填）", padding="5")
        rule_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("关键词", "目标文件夹模板")
        self.tree = ttk.Treeview(rule_frame, columns=columns, show="headings", height=6)
        self.tree.heading("关键词", text="关键词")
        self.tree.heading("目标文件夹模板", text="目标文件夹模板")
        self.tree.column("关键词", width=200)
        self.tree.column("目标文件夹模板", width=400)
        self.tree.pack(fill=tk.BOTH, expand=True)

        rule_btn_frame = ttk.Frame(rule_frame)
        rule_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(rule_btn_frame, text="添加规则", command=self.add_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(rule_btn_frame, text="删除选中", command=self.delete_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(rule_btn_frame, text="保存规则到 rules.txt", command=self.save_rules).pack(side=tk.LEFT, padx=5)

        # ---------- 高级设置 ----------
        settings_frame = ttk.LabelFrame(main_frame, text="高级设置", padding="5")
        settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(settings_frame, text="每个链接处理后的等待秒数（防风控）:").pack(side=tk.LEFT, padx=5)
        self.sleep_var = tk.IntVar(value=0)
        sleep_spin = ttk.Spinbox(settings_frame, from_=0, to=60, textvariable=self.sleep_var, width=5)
        sleep_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(settings_frame, text="秒").pack(side=tk.LEFT)

        # ---------- 日志输出 ----------
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ---------- 底部控制 ----------
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)
        self.start_btn = ttk.Button(bottom_frame, text="🚀 开始处理", command=self.start_process)
        self.start_btn.pack(side=tk.RIGHT, padx=5)
        self.merge_btn = ttk.Button(bottom_frame, text="🧩 合并弹幕", command=self.open_merge_window)
        self.merge_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="清空日志", command=self.clear_log).pack(side=tk.RIGHT, padx=5)

    # ---------- 链接相关 ----------
    def load_links(self):
        if os.path.exists(LINKS_FILE):
            with open(LINKS_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            self.link_text.delete(1.0, tk.END)
            self.link_text.insert(tk.END, content)

    def save_links(self):
        content = self.link_text.get(1.0, tk.END).strip()
        with open(LINKS_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        self.log("✅ 链接已保存到 links.txt")

    # ---------- 规则相关 ----------
    def load_rules(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or '|' not in line:
                        continue
                    key, tmpl = line.split('|', 1)
                    self.tree.insert("", tk.END, values=(key.strip(), tmpl.strip()))

    def add_rule(self):
        key = simpledialog.askstring("添加规则", "请输入关键词（用于匹配文件名）：")
        if not key:
            return
        tmpl = simpledialog.askstring("添加规则", "请输入目标文件夹模板（含 {ep:02d} 占位符）：")
        if not tmpl:
            return
        self.tree.insert("", tk.END, values=(key, tmpl))
        self.log(f"➕ 添加规则：{key} → {tmpl}")

    def delete_rule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选中要删除的规则")
            return
        for item in selected:
            values = self.tree.item(item, "values")
            self.tree.delete(item)
            self.log(f"🗑️ 删除规则：{values[0]}")

    def save_rules(self):
        rules = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if len(values) == 2:
                rules.append(f"{values[0]}|{values[1]}")
        with open(RULES_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(rules))
        self.log("✅ 规则已保存到 rules.txt")

    # ---------- 日志相关 ----------
    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.update_idletasks()

    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

    # ---------- 主流程 ----------
    def start_process(self):
        self.save_links()
        self.save_rules()

        # 检查必要文件
        missing = []
        if not os.path.exists(BASH_SCRIPT):
            missing.append("bdanmaku.sh")
        if not os.path.exists(RENAME_SCRIPT):
            missing.append("renameass.py")
        if missing:
            messagebox.showerror("错误", f"在 {DANMAKU_DIR} 下缺少以下文件：\n" + "\n".join(missing))
            return

        if not os.path.exists(LINKS_FILE) or os.path.getsize(LINKS_FILE) == 0:
            messagebox.showwarning("提示", "links.txt 为空，请先输入链接")
            return

        self.start_btn.config(state='disabled')
        self.log("=" * 50)
        self.log("开始处理...")

        # 构建环境变量，传递防风控延迟
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["SLEEP_SECONDS"] = str(self.sleep_var.get())

        # 1. 执行 bdanmaku.sh
        self.log("▶️ 执行 bdanmaku.sh ...")
        try:
            proc = subprocess.Popen(
                ["bash", BASH_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=DANMAKU_DIR,
                bufsize=1,
                env=env
            )
            for line in proc.stdout:
                self.log(line.rstrip())
            proc.wait()
            if proc.returncode != 0:
                self.log(f"❌ bdanmaku.sh 执行失败，返回码 {proc.returncode}")
                self.start_btn.config(state='normal')
                return
        except Exception as e:
            self.log(f"❌ 执行出错：{e}")
            self.start_btn.config(state='normal')
            return

        # 2. 执行 renameass.py
        self.log("▶️ 执行 renameass.py ...")
        try:
            proc = subprocess.Popen(
                ["python3", RENAME_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=DANMAKU_DIR,
                bufsize=1,
                env=env
            )
            for line in proc.stdout:
                self.log(line.rstrip())
            proc.wait()
            if proc.returncode != 0:
                self.log(f"❌ renameass.py 执行失败，返回码 {proc.returncode}")
            else:
                self.log("✅ 全部处理完成！")
        except Exception as e:
            self.log(f"❌ 执行出错：{e}")

        self.start_btn.config(state='normal')
        self.log("=" * 50)

    # 在 Application 类中增加以下方法

    def open_merge_window(self):
        """打开合并弹幕的独立窗口"""
        MergeWindow(self)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
