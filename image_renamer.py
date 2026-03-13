import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IMG 图片重命名工具")
        self.root.geometry("800x650")
        
        self.folder_path = "./images"
        self.images = []
        self.current_index = 0
        self.csv_filename = "renamed_log.csv"
        
        # --- UI 界面设置 ---
        self.img_label = tk.Label(root)
        self.img_label.pack(pady=15)
        
        self.info_label = tk.Label(root, text="请先选择一个包含图片的文件夹", font=("Arial", 12))
        self.info_label.pack(pady=5)
        
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(pady=10)
        
        tk.Label(self.entry_frame, text="输入新名称: ", font=("Arial", 12)).pack(side=tk.LEFT)
        self.name_entry = tk.Entry(self.entry_frame, font=("Arial", 14), width=30)
        self.name_entry.pack(side=tk.LEFT)
        # 绑定回车键，按下回车自动保存
        self.name_entry.bind('<Return>', lambda event: self.save_and_next())
        
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=10)
        
        self.select_btn = tk.Button(self.btn_frame, text="选择文件夹", command=self.select_folder, width=15)
        self.select_btn.grid(row=0, column=0, padx=10)
        
        self.skip_btn = tk.Button(self.btn_frame, text="跳过 (Skip)", command=self.skip_image, state=tk.DISABLED, width=15)
        self.skip_btn.grid(row=0, column=1, padx=10)

        self.save_btn = tk.Button(self.btn_frame, text="保存并下一张", command=self.save_and_next, state=tk.DISABLED, bg="#4CAF50", fg="white", width=15)
        self.save_btn.grid(row=0, column=2, padx=10)

    def select_folder(self):
        # 弹出选择文件夹对话框
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            return
            
        self.csv_path = os.path.join(self.folder_path, self.csv_filename)
        
        # 筛选出以 "IMG" 开头的文件 (不区分大小写)
        all_files = os.listdir(self.folder_path)
        self.images = [
            f for f in all_files 
            if f.upper().startswith("IMG") or f.upper().startswith("微信") and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.heic'))
        ]
        
        if not self.images:
            messagebox.showinfo("提示", "该文件夹中没有找到以 'IMG' 开头的图片！")
            return
            
        self.current_index = 0
        self.save_btn.config(state=tk.NORMAL)
        self.skip_btn.config(state=tk.NORMAL)
        self.load_image()

    def load_image(self):
        # 检查是否处理完所有图片
        if self.current_index >= len(self.images):
            self.info_label.config(text="🎉 所有以 IMG 开头的图片都已处理完毕！")
            self.img_label.config(image='')
            self.name_entry.delete(0, tk.END)
            self.name_entry.config(state=tk.DISABLED)
            self.save_btn.config(state=tk.DISABLED)
            self.skip_btn.config(state=tk.DISABLED)
            messagebox.showinfo("完成", "任务完成！CSV记录已更新。")
            return

        current_file = self.images[self.current_index]
        img_path = os.path.join(self.folder_path, current_file)

        try:
            # 加载并自动缩小图片以适应窗口 (等比例缩放)
            img = Image.open(img_path)
            img.thumbnail((700, 400)) 
            self.photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.photo)
        except Exception as e:
            self.info_label.config(text=f"无法加载图片: {current_file}")
            
        self.info_label.config(text=f"正在处理 ({self.current_index + 1}/{len(self.images)}): {current_file}")
        self.name_entry.delete(0, tk.END)
        self.name_entry.focus() # 自动把光标放到输入框中

    def save_and_next(self):
        new_name = self.name_entry.get().strip()
        if not new_name:
            messagebox.showwarning("警告", "名字不能为空，请输入新名称！")
            return

        # 确保新名称以 .jpg 结尾
        if not new_name.lower().endswith('.jpg'):
            new_name += '.jpg'

        old_file = self.images[self.current_index]
        old_path = os.path.join(self.folder_path, old_file)
        new_path = os.path.join(self.folder_path, new_name)

        # 防止新名称与已有文件冲突
        if os.path.exists(new_path) and old_path != new_path:
            messagebox.showerror("错误", f"文件 {new_name} 已存在，请换一个名称！")
            return

        try:
            # 1. 实际重命名系统中的文件
            os.rename(old_path, new_path)
            
            # 2. 追加记录到 CSV 文件 (不存在则会自动创建)
            csv_exists = os.path.isfile(self.csv_path)
            with open(self.csv_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 如果文件刚创建，写入表头
                if not csv_exists:
                    writer.writerow(["原文件名", "新文件名"])
                writer.writerow([old_file, new_name])
                
            # 进入下一张图片
            self.current_index += 1
            self.load_image()
            
        except Exception as e:
            messagebox.showerror("错误", f"重命名失败: {e}")

    def skip_image(self):
        # 遇到不想改名的图片可以直接跳过
        self.current_index += 1
        self.load_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRenamerApp(root)
    root.mainloop()