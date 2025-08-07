import tkinter as tk
from tkinter import ttk, messagebox
from backend import SimpleDatabase
from typing import Optional, Dict

class DatabaseFrontend:
    def __init__(self, root):
        self.root = root
        self.root.title("诗云-by dshzsh")
        
        # 初始化数据库
        self.db = SimpleDatabase()
        
        # 创建UI
        self.create_widgets()
        
        # 加载示例数据
        self.update_table_list()
        
    def create_widgets(self):
        # 顶部控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 表选择
        ttk.Label(control_frame, text="选择表:").grid(row=0, column=0, padx=5, pady=5)
        self.table_var = tk.StringVar()
        self.table_combobox = ttk.Combobox(control_frame, textvariable=self.table_var, state="readonly")
        self.table_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.table_combobox.bind("<<ComboboxSelected>>", self.on_table_selected)
        
        # 刷新按钮
        ttk.Button(control_frame, text="刷新", command=self.refresh_data).grid(row=0, column=2, padx=5, pady=5)
        
        # 查询面板
        filter_frame = ttk.LabelFrame(self.root, text="查询条件", padding="10")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.query_entries = {}
        ttk.Label(filter_frame, text="ID:").grid(row=0, column=0, padx=5, pady=2)
        self.query_entries["id"] = ttk.Entry(filter_frame)
        self.query_entries["id"].grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(filter_frame, text="标题:").grid(row=0, column=2, padx=5, pady=2)
        self.query_entries["title"] = ttk.Entry(filter_frame)
        self.query_entries["title"].grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(filter_frame, text="内容:").grid(row=0, column=4, padx=5, pady=2)
        self.query_entries["content"] = ttk.Entry(filter_frame)
        self.query_entries["content"].grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Button(filter_frame, text="应用查询", command=self.apply_querys).grid(row=0, column=6, padx=10, pady=2)
        
        # 数据表格
        # 创建Treeview框架
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Treeview
        self.tree = ttk.Treeview(self.tree_frame)
        
        # 设置自动换行的样式
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=20)  # 增加行高以容纳换行文本
        
        # 添加垂直滚动条
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 添加水平滚动条（可选，如果列很多）
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定右键菜单
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_selection)
        
        # 分页控制
        page_frame0 = ttk.Frame(self.root, padding="10")
        page_frame0.pack(fill=tk.X)

        page_frame = ttk.Frame(self.root, padding="10")
        page_frame.pack(fill=tk.X)
        
        self.page_info = ttk.Label(page_frame0, text="第0页/共0页 (共0条记录)",wraplength=1000)
        self.page_info.pack(side=tk.LEFT, padx=5)
        

        ttk.Label(page_frame, text="每页行数:").pack(side=tk.LEFT, padx=5)
        self.rows_per_page_var = tk.IntVar(value=10)  # 默认10行
        self.rows_per_page_entry = ttk.Entry(page_frame, textvariable=self.rows_per_page_var, width=5)
        self.rows_per_page_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(page_frame, text="应用", command=self.update_rows_per_page).pack(side=tk.LEFT, padx=5)

        ttk.Button(page_frame, text="首页", command=self.first_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(page_frame, text="上一页", command=self.prev_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(page_frame, text="下一页", command=self.next_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(page_frame, text="尾页", command=self.last_page).pack(side=tk.LEFT, padx=5)
        
        self.page_entry = ttk.Entry(page_frame, width=5)
        self.page_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(page_frame, text="跳转", command=self.go_to_page).pack(side=tk.LEFT, padx=5)
        
        # 初始化变量
        self.current_table = None
        self.current_page = 1
        self.total_pages = 1
        self.querys = {}
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_selection(self):
        """复制选中内容到剪贴板"""
        selected_item = self.tree.selection()
        if selected_item:
            # 获取选中行的所有值
            item_values = self.tree.item(selected_item, "values")
            
            # 将所有列的值用制表符 `\t` 连接
            text_to_copy = "\t".join(str(value) for value in item_values)
            
            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)


    def update_rows_per_page(self):
        try:
            rows = int(self.rows_per_page_var.get())
            if rows <= 0:
                raise ValueError
            self.current_page = 1  # 重置到第一页
            self.load_table_data(self.current_page)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的正整数")
            self.rows_per_page_var.set(10)  # 恢复默认值
        
    def update_table_list(self):
        tables = list(self.db.tables.keys())
        self.table_combobox["values"] = tables
        if tables:
            self.table_combobox.current(0)
            self.on_table_selected()
    
    def on_table_selected(self, event=None):
        self.current_table = self.table_var.get()
        if self.current_table:
            self.current_page = 1
            self.load_table_data()
    
    def get_max_row(self):
        try:
            max_rows = int(self.rows_per_page_var.get())
            if max_rows <= 0:
                max_rows = 10
        except:
            max_rows = 10
        return max_rows

    def load_table_data(self, page: int = 1, row: int = -1):
        if not self.current_table:
            return
                    
        # 获取当前设置的每页行数
        max_rows = self.get_max_row()

        # 从数据库获取数据
        result = self.db.get_page(
            table_name=self.current_table,
            page=page,
            max_rows = max_rows
        )
        
        if "error" in result:
            messagebox.showerror("错误", result["error"])
            return
        
        # 更新分页信息
        self.current_page = result["page"]
        self.total_pages = result["total_pages"]
        self.update_page_info(result["total_rows"])
        
        # 清除现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 设置列
        if not result["data"]:
            self.tree["columns"] = []
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
            return
            
        columns = list(result["data"][0].keys())
        self.tree["columns"] = columns

        self.tree["show"] = "headings"  # 这行代码隐藏了默认的第一列
        
        # 设置表头
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.W)
        
        # 添加数据
        for i, row_data in enumerate(result["data"]):
            values = [row_data.get(col, "") for col in columns]
            item_id = self.tree.insert("", tk.END, values=values)
            
            # 如果指定了row且当前行匹配，则选中该行
            if row != -1 and i == row:
                self.tree.selection_set(item_id)
                self.tree.focus(item_id)
                # 可选：滚动到选中的行
                self.tree.see(item_id)
    
    def update_page_info(self, total_rows: int):
        self.page_info.config(text=f"第{self.current_page}页 / 共{self.total_pages}页 (共{total_rows}条记录)")
    
    def refresh_data(self):
        if self.current_table:
            self.load_table_data(self.current_page)
    
    def apply_querys(self):
        if not self.current_table:
            return
            
        # 收集筛选条件
        self.querys = {}
        for key, entry in self.query_entries.items():
            value = entry.get().strip()
            if value:
                self.querys[key] = value
        
        result = self.db.query_data(
            table_name = self.current_table,
            max_rows = self.get_max_row(),
            filters = self.querys
        )

        if "error" in result:
            messagebox.showerror("错误", result["error"])
            return
        
        self.current_page = result["page"]

        self.load_table_data(self.current_page, result["row"])
    
    
    def first_page(self):
        if self.current_page != 1:
            self.current_page = 1
            self.load_table_data(self.current_page)
    
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_table_data(self.current_page)
    
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_table_data(self.current_page)
    
    def last_page(self):
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.load_table_data(self.current_page)
    
    def go_to_page(self):
        try:
            page = int(self.page_entry.get())
            if 1 <= page <= self.total_pages:
                self.current_page = page
                self.load_table_data(self.current_page)
            else:
                messagebox.showerror("错误", f"请输入1到{self.total_pages}之间的页码")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的页码数字")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseFrontend(root)
    root.geometry("1050x650")
    root.mainloop()