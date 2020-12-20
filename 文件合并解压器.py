﻿remove_ls = [
    '__pycache__', '文件合并解压器.py', 'split files.txt', '文件切块.exe', '文件切块.py',
    '文件切块运行程序.pyw', '文件合并解压器.exe', '文件合并解压器运行程序.pyw'
]
original_drc = os.getcwd()


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.minsize(700, 600)
        self.filedialog = filedialog
        self.title('任意文件合并解压器')
        self.choose_files = ttk.Button(self,
                                       text='选择您想要合并的文件',
                                       command=self.choose_mix_files)
        self.choose_path = ttk.Button(self,
                                      text='选择文件路径，将合并此路径下所有的文件',
                                      command=self.choose_mix_files_path)
        self.choose_path_show = Text(self, height=4, width=95)
        self.choose_current = ttk.Button(self,
                                         text='合并当前路径下所有的文件',
                                         command=self.filemix3)
        self.start_mix = ttk.Button(self, text='开始合并', command=self.filemix)
        self.start_mix_2 = ttk.Button(self, text='开始合并', command=self.filemix2)
        self.clear_choose_files = ttk.Button(self,
                                             text='清空',
                                             command=self.clear_files)
        self.mix_file_name_text = ttk.Label(self, text='请输入你想要的合并后的文件名')
        self.mix_file_name = Text(self, height=2, width=95)
        self.choose_files_show = Text(self, height=6, width=95)
        self.choose_files_show.configure(state='disabled')
        self.choose_files.place(x=0, y=20)
        self.choose_files_show.place(x=0, y=50)
        self.choose_path.place(x=0, y=150)
        self.choose_path_show.place(x=0, y=180)
        self.choose_current.place(x=0, y=250)
        self.mix_file_name_text.place(x=0, y=280)
        self.mix_file_name.place(x=0, y=310)
        self.start_mix.place(x=300, y=20)
        self.clear_choose_files.place(x=450, y=20)
        self.start_mix_2.place(x=300, y=150)
        self.choose_unzip_file = ttk.Button(
            self, text='选择想要解压的文件', command=self.choose_unzip_file_name)
        self.choose_unzip_file_msg = ttk.Button(
            self, text='选择想要解压的节点信息文件', command=self.choose_unzip_msg_name)
        self.choose_unzip_file_path = ttk.Button(
            self, text='选择想要解压到的路径', command=self.choose_unzip_files_path)
        self.start_unzip = ttk.Button(self,
                                      text='开始解压',
                                      command=self.file_unzip)
        self.choose_unzip_file.place(x=0, y=350)
        self.choose_unzip_file_msg.place(x=0, y=400)
        self.choose_unzip_file_path.place(x=0, y=450)
        self.start_unzip.place(x=0, y=500)
        self.files = []
        self.filenames = []
        self.file_path = ''
        self.unzip_file_name = ''
        self.unzip_file_name_show = ttk.Label(self, text='')
        self.unzip_file_name_show.place(x=125, y=350)
        self.unzip_msg_name = ''
        self.unzip_msg_name_show = ttk.Label(self, text='')
        self.unzip_msg_name_show.place(x=170, y=400)
        self.unzip_path = ''
        self.unzip_path_show = ttk.Label(self, text='')
        self.unzip_path_show.place(x=150, y=450)
        self.msg = ttk.Label(self, text='目前暂时没有动作')
        self.msg.place(x=0, y=550)

    def clear_files(self):
        self.files.clear()
        self.filenames.clear()
        self.choose_files_show.configure(state='normal')
        self.choose_files_show.delete('1.0', END)
        self.choose_files_show.configure(state='disabled')

    def choose_mix_files(self):
        filenames = filedialog.askopenfilenames(initialdir='.',
                                                title="选择文件",
                                                filetype=(("所有文件", "*.*"), ))
        self.filenames += list(filenames)
        self.choose_files_show.configure(state='normal')
        self.choose_files_show.delete('1.0', END)
        self.choose_files_show.insert(END, '\n'.join(self.filenames))
        self.choose_files_show.configure(state='disabled')

    def choose_mix_files_path(self):
        self.file_path = filedialog.askdirectory(initialdir='.', title="选择路径")
        self.choose_path_show.delete('1.0', END)
        self.choose_path_show.insert(END, self.file_path)

    def filemix(self):
        if not self.filenames:
            self.msg.configure(text='合并文件列表为空')
            return
        files = self.files
        mixed_name = self.mix_file_name.get('1.0', 'end-1c')
        if not mixed_name:
            mixed_name = 'mixed.jpg'
        os.chdir(original_drc)
        length_list = []
        with open(mixed_name, 'wb') as file:
            for t in self.filenames:
                self.msg.configure(text=f'正在合并文件 {t}')
                self.update()
                with open(t, 'rb') as f:
                    each = f.read()
                    length_list.append(len(each))
                    file.write(each)
        with open('split files.txt', 'w', encoding='utf-8') as f:
            f.write(
                str(length_list) + ',' +
                str([os.path.basename(i) for i in self.filenames]))
        self.msg.configure(
            text=f'文件合并成功，请看当前路径下的{mixed_name}和解压信息文件split files.txt')

    def filemix2(self):
        mixed_path = self.file_path
        if not mixed_path:
            self.msg.configure(text='未选择合并文件的路径')
            return
        os.chdir(mixed_path)
        self.filenames = os.listdir()
        try:
            self.filenames.remove('__pycache__')
        except:
            pass
        self.filemix()

    def filemix3(self):
        file_name = os.listdir()
        for j in remove_ls:
            try:
                file_name.remove(j)
            except:
                pass
        self.filenames = file_name
        self.filemix()

    def choose_unzip_file_name(self):
        self.unzip_file_name = filedialog.askopenfilename(initialdir='.',
                                                          title="选择文件",
                                                          filetype=(("所有文件",
                                                                     "*.*"), ))
        self.unzip_file_name_show.configure(text=self.unzip_file_name)

    def choose_unzip_msg_name(self):
        self.unzip_msg_name = filedialog.askopenfilename(initialdir='.',
                                                         title="选择解压信息文件",
                                                         filetype=(("所有文件",
                                                                    "*.*"), ))
        self.unzip_msg_name_show.configure(text=self.unzip_msg_name)

    def choose_unzip_files_path(self):
        self.unzip_path = filedialog.askdirectory(initialdir='.',
                                                  title="选择解压的路径")
        self.unzip_path_show.configure(text=self.unzip_path)

    def file_unzip(self):
        if not self.unzip_file_name:
            self.msg.configure(text='未选择要解压的文件')
            return
        if not self.unzip_msg_name:
            self.msg.configure(text='未选择解压信息文件')
            return
        with open(self.unzip_msg_name, 'r', encoding='utf-8') as f:
            unzip = f.read()
        unzip_ind, filenames = eval(unzip)
        if not self.unzip_path:
            self.unzip_path = 'unzipped_files'
        try:
            os.chdir(self.unzip_path)
        except:
            os.mkdir(self.unzip_path)
            os.chdir(self.unzip_path)
        with open(self.unzip_file_name, 'rb') as file:
            for each in range(len(filenames)):
                current_filename = filenames[each]
                self.msg.configure(text=f'正在解压文件 {current_filename}')
                self.update()
                current_length = unzip_ind[each]
                with open(current_filename, 'wb') as f:
                    f.write(file.read(current_length))
        self.msg.configure(text=f'文件解压成功，请到解压路径下查看')
        os.chdir(original_drc)


root = Root()
root.mainloop()
