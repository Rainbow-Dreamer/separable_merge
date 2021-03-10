from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.split_file = None
        self.split_file_name = ''
        self.minsize(700, 400)
        self.filedialog = filedialog
        self.title('文件切块')
        self.choose_files = ttk.Button(self,
                                       text='选择您想要切块的文件',
                                       command=self.choose_split_files)
        self.choose_file_size_label = ttk.Label(self, text='文件大小:')
        self.split_into_num = ttk.Label(self, text='想要平均切成几份？')
        self.split_into_num_text = Text(self, height=2, width=30)
        self.fixed_split_size = ttk.Label(self, text='固定切块的文件大小')
        self.split1_button = ttk.Button(
            self, text='开始切块', command=lambda: self.file_split(mode=0))
        self.split2_button = ttk.Button(
            self, text='开始切块', command=lambda: self.file_split(mode=1))
        self.clear_choose_files = ttk.Button(self,
                                             text='清空',
                                             command=self.clear_files)
        self.fixed_split_size_text = Text(self, height=2, width=95)
        self.choose_files_show = Text(self, height=3, width=95)
        self.choose_files_show.configure(state='disabled')
        self.choose_files.place(x=0, y=20)
        self.choose_files_show.place(x=0, y=50)
        self.choose_file_size_label.place(x=0, y=100)
        self.choose_files_size_show = Text(self, height=3, width=95)
        self.choose_files_size_show.place(x=0, y=125)
        self.split_into_num.place(x=0, y=180)
        self.split_into_num_text.place(x=0, y=210)
        self.fixed_split_size.place(x=0, y=260)
        self.fixed_split_size_text.place(x=0, y=300)
        self.clear_choose_files.place(x=300, y=20)
        self.split1_button.place(x=300, y=180)
        self.split2_button.place(x=300, y=260)
        self.msg = ttk.Label(self, text='目前暂时没有动作')
        self.msg.place(x=0, y=350)
        self.split_file_size = None
        self.calculate_split_into_size = ttk.Button(
            self, text='计算分块平均大小', command=self.calculate_size)
        self.calculate_split_into_size.place(x=450, y=180)
        self.split_file_size_num = None
        self.split_into_size = ttk.Label(self, text='平均分块大小:')
        self.split_into_size.place(x=260, y=220)

    def calculate_size(self):
        if self.split_file_size_num is not None:
            split_into_num = self.split_into_num_text.get('1.0', 'end-1c')
            try:
                split_into_num = int(split_into_num)
            except:
                self.msg.configure(text='分块的份数必须为正整数')
                return
            if split_into_num <= 0:
                self.msg.configure(text='分块的份数必须为正整数')
                return
            self.split_into_size.configure(
                text=
                f'平均分块大小: {self.convert_size(self.split_file_size_num/split_into_num)}'
            )
            self.msg.configure(text='计算成功')
        else:
            self.msg.configure(text='未选择任何文件')
            return

    def convert_size(self, size):
        size /= 1024
        if size < 1024:
            return f'{round(size, 2)} KB'
        elif 1024 <= size < 1024**2:
            return f'{round(size/1024, 2)} MB'
        else:
            return f'{round(size/(1024**2), 2)} GB'

    def clear_files(self):
        self.split_file = None
        self.split_file_name = ''
        self.choose_files_show.configure(state='normal')
        self.choose_files_show.delete('1.0', END)
        self.choose_files_show.configure(state='disabled')
        self.split_file_size = None
        self.split_file_size_num = None
        self.split_into_size.configure(text='平均分块大小:')
        self.choose_files_size_show.delete('1.0', END)

    def choose_split_files(self):
        split_file_name = filedialog.askopenfilename(initialdir='.',
                                                     title="选择文件",
                                                     filetype=(("所有文件",
                                                                "*.*"), ))
        if not split_file_name:
            return
        self.split_file_name = split_file_name
        self.choose_files_show.configure(state='normal')
        self.choose_files_show.delete('1.0', END)
        self.choose_files_show.insert(END, self.split_file_name)
        self.choose_files_show.configure(state='disabled')
        self.split_file_size_num = os.path.getsize(self.split_file_name)
        self.split_file_size = self.convert_size(self.split_file_size_num)
        self.choose_files_size_show.delete('1.0', END)
        self.choose_files_size_show.insert(END, self.split_file_size)

    def file_split(self, mode=0):
        if not self.split_file_name:
            self.msg.configure(text='未选择任何文件')
            return
        if mode == 0:
            split_into_num = self.split_into_num_text.get('1.0', 'end-1c')
            try:
                split_into_num = int(split_into_num)
            except:
                self.msg.configure(text='分块的份数必须为正整数')
                return
            if split_into_num <= 0:
                self.msg.configure(text='分块的份数必须为正整数')
                return
            length = self.split_file_size_num
            split_size = length // split_into_num
            try:
                os.mkdir('split files')
            except:
                pass
            os.chdir('split files')
            check_files = os.listdir()
            if check_files:
                for each in check_files:
                    os.remove(each)
            counter = 0
            with open(self.split_file_name, 'rb') as file:
                for i in range(split_into_num):
                    self.msg.configure(text=f'正在写入第{i+1}个分块文件')
                    self.update()
                    if i != split_into_num - 1:
                        with open(f'part{i+1}', 'wb') as f:
                            f.write(bytes(file.read(split_size)))
                        counter += split_size
                    else:
                        with open(f'part{i+1}', 'wb') as f:
                            f.write(bytes(file.read(length - counter)))
        elif mode == 1:
            fixed_size = self.fixed_split_size_text.get('1.0',
                                                        'end-1c').split()
            fixed_size_num, unit = float(fixed_size[0]), fixed_size[1]
            if unit == 'KB':
                fixed_size_num *= 1024
            elif unit == 'MB':
                fixed_size_num *= 1024**2
            elif unit == 'GB':
                fixed_size_num *= 1024**3
            else:
                self.msg.configure(text='只支持KB, MB, GB三种文件大小单位')
                return
            length = self.split_file_size_num
            split_size = int(fixed_size_num)
            try:
                os.mkdir('split files')
            except:
                pass
            os.chdir('split files')
            check_files = os.listdir()
            if check_files:
                for each in check_files:
                    os.remove(each)
            counter = 0
            part_num = 1
            with open(self.split_file_name, 'rb') as file:
                while True:
                    self.msg.configure(text=f'正在写入第{part_num}个分块文件')
                    self.update()
                    if counter + split_size >= length:
                        with open(f'part{part_num}', 'wb') as f:
                            f.write(bytes(file.read(length - counter)))
                        break
                    else:
                        with open(f'part{part_num}', 'wb') as f:
                            f.write(bytes(file.read(split_size)))
                        counter += split_size
                        part_num += 1
        self.msg.configure(text='文件分块成功，请查看当前文件夹下的split files文件夹')
        os.chdir('..')


root = Root()
root.mainloop()
