
import tkinter as tk
from tkinter import ttk, messagebox

from database import query_by_sno, query_by_group


class StudentGroupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("学生群体划分查询系统")
        self.root.geometry("850x550")
        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # 标题
        title = tk.Label(
            self.root,
            text="学生群体划分查询系统",
            font=("微软雅黑", 20, "bold")
        )
        title.pack(pady=15)

        # 学号查询区域
        sno_frame = ttk.LabelFrame(self.root, text="按学生编号查询")
        sno_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(sno_frame, text="学生编号：").pack(
            side="left", padx=10, pady=15
        )

        self.sno_entry = ttk.Entry(sno_frame, width=25)
        self.sno_entry.pack(side="left", padx=5)

        ttk.Button(
            sno_frame,
            text="查询",
            command=self.search_by_sno
        ).pack(side="left", padx=10)

        # 群体标签查询区域
        group_frame = ttk.LabelFrame(self.root, text="按群体标签查询")
        group_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(group_frame, text="群体标签：").pack(
            side="left", padx=10, pady=15
        )

        self.group_box = ttk.Combobox(
            group_frame,
            values=[
                "待提升型",
                "中等发展型",
                "良好发展型",
                "优秀发展型"
            ],
            state="readonly",
            width=22
        )
        self.group_box.pack(side="left", padx=5)
        self.group_box.set("优秀发展型")

        ttk.Button(
            group_frame,
            text="查询",
            command=self.search_by_group
        ).pack(side="left", padx=10)

        # 查询结果表格
        result_frame = ttk.LabelFrame(self.root, text="查询结果")
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("sno", "Chinese", "Math", "cluster", "group")

        self.tree = ttk.Treeview(
            result_frame,
            columns=columns,
            show="headings",
            height=12
        )

        self.tree.heading("sno", text="学生编号")
        self.tree.heading("Chinese", text="语文成绩")
        self.tree.heading("Math", text="数学成绩")
        self.tree.heading("cluster", text="聚类编号")
        self.tree.heading("group", text="群体标签")

        self.tree.column("sno", width=150, anchor="center")
        self.tree.column("Chinese", width=120, anchor="center")
        self.tree.column("Math", width=120, anchor="center")
        self.tree.column("cluster", width=120, anchor="center")
        self.tree.column("group", width=180, anchor="center")

        scrollbar = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # 底部状态
        self.status_label = ttk.Label(
            self.root,
            text="请选择查询方式",
            foreground="gray"
        )
        self.status_label.pack(pady=8)

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def display_results(self, rows):
        self.clear_results()

        for row in rows:
            self.tree.insert("", "end", values=row)

        self.status_label.config(text=f"查询完成，共找到 {len(rows)} 条记录")

    def search_by_sno(self):
        sno = self.sno_entry.get().strip()

        if not sno.isdigit():
            messagebox.showwarning("提示", "请输入有效的学生编号！")
            return

        try:
            result = query_by_sno(int(sno))

            if result:
                self.display_results([result])
            else:
                self.clear_results()
                self.status_label.config(text="没有找到该学生")
                messagebox.showinfo("查询结果", "未找到该学生记录")

        except Exception as e:
            messagebox.showerror("数据库错误", str(e))

    def search_by_group(self):
        group = self.group_box.get()

        if not group:
            messagebox.showwarning("提示", "请选择群体标签！")
            return

        try:
            results = query_by_group(group)
            self.display_results(results)

        except Exception as e:
            messagebox.showerror("数据库错误", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentGroupApp(root)
    root.mainloop()
