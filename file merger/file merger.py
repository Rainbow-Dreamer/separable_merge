remove_ls = [
    '__pycache__', 'file merger.py', 'file merger start program.pyw',
    'file merger.exe'
]
original_drc = os.getcwd()

read_unit = 1024 * 16


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.minsize(850, 600)
        self.filedialog = filedialog
        self.title('File Merger and Splitter')
        self.choose_files = ttk.Button(
            self,
            text='Choose the files you want to merge',
            command=self.choose_mix_files)
        self.choose_path = ttk.Button(
            self,
            text=
            'Choose file path, will merge all of the files under the file path',
            command=self.choose_mix_files_path)
        self.choose_path_show = Text(self, height=6, width=95)
        self.choose_current = ttk.Button(
            self,
            text='Merge all of the files\nunder current directory',
            command=self.filemix3)
        self.start_mix = ttk.Button(self,
                                    text='Start merging',
                                    command=self.filemix)
        self.start_mix_2 = ttk.Button(self,
                                      text='Start merging',
                                      command=self.filemix2)
        self.clear_choose_files = ttk.Button(self,
                                             text='Clear',
                                             command=self.clear_files)
        self.choose_files_show = Text(self, height=14, width=95)
        self.choose_files_show.configure(state='disabled')
        self.choose_files.place(x=0, y=20)
        self.choose_files_show.place(x=0, y=50)
        self.choose_path.place(x=0, y=260)
        self.choose_path_show.place(x=0, y=290)
        self.choose_current.place(x=685, y=50)
        self.start_mix.place(x=300, y=20)
        self.clear_choose_files.place(x=450, y=20)
        self.start_mix_2.place(x=400, y=260)
        self.choose_unzip_file = ttk.Button(
            self,
            text='Choose the file you want to unzip',
            command=self.choose_unzip_file_name)
        self.start_unzip = ttk.Button(self,
                                      text='Start unzipping',
                                      command=self.file_unzip)
        self.choose_unzip_file.place(x=0, y=400)
        self.start_unzip.place(x=0, y=450)
        self.files = []
        self.filenames = []
        self.file_path = '.'
        self.unzip_file_name = ''
        self.unzip_file_name_show = ttk.Label(self, text='')
        self.unzip_file_name_show.place(x=210, y=400)
        self.msg = ttk.Label(self, text='Currently no actions')
        self.msg.place(x=0, y=550)
        self.browse_files = ttk.Button(
            self,
            text='Browse unzippable files (selective unzipping)',
            command=self.browse_files_func)
        self.browse_files.place(x=150, y=450)
        self.save_task_button = ttk.Button(self,
                                           text='Save current task',
                                           command=self.save_task)
        self.save_task_button.place(x=500, y=450)
        self.save_task_button = ttk.Button(self,
                                           text='Import task',
                                           command=self.import_task)
        self.save_task_button.place(x=500, y=500)

    def save_task(self):
        file_path = filedialog.asksaveasfile(initialdir='.',
                                             title="Save current task",
                                             filetype=(("All files", "*.*"), ),
                                             initialfile='Untitled.fmt')
        if file_path:
            with open(file_path.name, 'w') as f:
                f.write(str(self.filenames))
                self.msg.configure(
                    text=f'Successfully save task file {file_path.name}')
                self.msg.update()

    def import_task(self):
        task_file_name = filedialog.askopenfilename(
            initialdir='.',
            title="Choose task file",
            filetype=(("fmt file", "*.fmt"), ("All files", "*.*")))
        if task_file_name:
            with open(task_file_name) as f:
                self.filenames = literal_eval(f.read())
            self.choose_files_show.configure(state='normal')
            self.choose_files_show.delete('1.0', END)
            self.choose_files_show.insert(END, '\n'.join(self.filenames))
            self.choose_files_show.configure(state='disabled')
            self.msg.configure(
                text=f'Successfully import task file {task_file_name}')
            self.msg.update()

    def browse_files_func(self):
        if not self.unzip_file_name:
            self.msg.configure(text='No file is selected to unzip')
            return
        self.browse_filenames = []
        self.browse_file_window = Toplevel(self)
        self.browse_file_window.minsize(800, 500)
        self.browse_file_window.title('File list')
        self.browse_file_window.focus_force()

        self.browse_file_list_bar = ttk.Scrollbar(self.browse_file_window,
                                                  orient="vertical")
        self.browse_file_list_bar_h = ttk.Scrollbar(self.browse_file_window,
                                                    orient="horizontal")
        self.browse_file_list = Listbox(
            self.browse_file_window,
            yscrollcommand=self.browse_file_list_bar.set,
            xscrollcommand=self.browse_file_list_bar_h.set,
            width=80,
            height=20)
        self.browse_file_list_bar.config(command=self.browse_file_list.yview)
        self.browse_file_list_bar_h.config(command=self.browse_file_list.xview)
        self.browse_file_list.place(x=0, y=50)
        self.browse_file_list_bar.place(x=570, y=50, height=360, anchor=N)
        self.browse_file_list_bar_h.place(x=0, y=420, width=570, anchor=W)
        self.browse_file_list.bind("<<ListboxSelect>>", self.select_file)
        self.browse_file_list.config(selectbackground='light green')
        self.browse_file_list.config(selectforeground='black')
        self.browse_file_list.config(activestyle='none')
        self.browse_file_msg = ttk.Label(
            self.browse_file_window,
            text=
            'Click to choose files you want to unzip, green means selected, click again when selected to unselect.'
        )
        self.browse_file_msg.place(x=0, y=20)
        with open(self.unzip_file_name, 'rb') as file:
            current_dict = pickle.load(file)
            filenames = list(current_dict.keys())
            for each in range(len(filenames)):
                current_filename = filenames[each]
                self.browse_filenames.append(current_filename)
                self.browse_file_list.insert(END, current_filename)

        os.chdir(original_drc)
        self.selected_files = [
            False for i in range(len(self.browse_filenames))
        ]
        self.msg.configure(text='Successfully open file list')
        self.select_file_unzip = ttk.Button(
            self.browse_file_window,
            text='Unzip the selected files',
            command=lambda: self.file_unzip(mode=1))
        self.select_file_unzip.place(x=600, y=50)

    def select_file(self, e=None):
        current_ind = self.browse_file_list.index(ANCHOR)
        if self.selected_files[current_ind]:
            self.selected_files[current_ind] = False
            self.browse_file_list.itemconfig(current_ind, {'bg': 'white'})
            self.browse_file_list.selection_clear(current_ind)
        else:
            self.selected_files[current_ind] = True
            self.browse_file_list.itemconfig(current_ind,
                                             {'bg': 'light green'})

    def clear_files(self):
        self.files.clear()
        self.filenames.clear()
        self.choose_files_show.configure(state='normal')
        self.choose_files_show.delete('1.0', END)
        self.choose_files_show.configure(state='disabled')

    def choose_mix_files(self):
        filenames = filedialog.askopenfilenames(initialdir='.',
                                                title="Choose files",
                                                filetype=(("All files",
                                                           "*.*"), ))
        if filenames:
            self.filenames += list(filenames)
            self.choose_files_show.configure(state='normal')
            self.choose_files_show.delete('1.0', END)
            self.choose_files_show.insert(END, '\n'.join(self.filenames))
            self.choose_files_show.configure(state='disabled')

    def choose_mix_files_path(self):
        self.file_path = filedialog.askdirectory(initialdir='.',
                                                 title="Choose directory")
        self.choose_path_show.delete('1.0', END)
        self.choose_path_show.insert(END, self.file_path)

    def filemix(self):
        if not self.filenames:
            self.msg.configure(text='The merge file list is empty')
            return
        mixed_name = filedialog.asksaveasfile(initialdir='.',
                                              title="Save merged file",
                                              filetype=(("All files",
                                                         "*.*"), ),
                                              initialfile='Untitled')
        if not mixed_name:
            return
        mixed_name = mixed_name.name
        length_list = [os.path.getsize(each) for each in self.filenames]
        counter = 1
        file_num = len(self.filenames)
        file_names = [os.path.basename(i) for i in self.filenames]
        merge_dict = {
            file_names[i]: length_list[i]
            for i in range(len(file_names))
        }
        with open(mixed_name, 'wb') as file:
            file.write(pickle.dumps(merge_dict))
            for t in self.filenames:
                current_file_size = os.path.getsize(t)
                file_size_counter = 0
                f = open(t, 'rb')
                while True:
                    current_chunk = f.read(read_unit)
                    if current_chunk:
                        file.write(current_chunk)
                        file_size_counter += len(current_chunk)
                        self.msg.configure(
                            text=
                            f'{counter}/{file_num} Merging {round((file_size_counter/current_file_size)*100, 3)}% of file {t}'
                        )
                        self.msg.update()
                    else:
                        break
                f.close()
                file.flush()
                os.fsync(file.fileno())
                counter += 1
        os.chdir(original_drc)
        self.msg.configure(
            text=f'Successfully merge the files, please look at {mixed_name}')

    def filemix2(self):
        mixed_path = self.file_path
        if not mixed_path:
            self.msg.configure(text='No file path is selected')
            return
        os.chdir(mixed_path)
        self.filenames = [i for i in os.listdir() if os.path.isfile(i)]
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
        self.filenames = [i for i in file_name if os.path.isfile(i)]
        self.filemix()

    def choose_unzip_file_name(self):
        self.unzip_file_name = filedialog.askopenfilename(
            initialdir='.',
            title="Choose files",
            filetype=(("All files", "*.*"), ))
        self.unzip_file_name_show.configure(text=self.unzip_file_name)

    def file_unzip(self, mode=0):
        if not self.unzip_file_name:
            self.msg.configure(text='No file is selected to unzip')
            self.update()
            return
        unzip_path = filedialog.askdirectory(
            initialdir='.', title="Choose the directory to unzip to")
        if not unzip_path:
            return
        try:
            os.chdir(unzip_path)
        except:
            os.mkdir(unzip_path)
            os.chdir(unzip_path)
        with open(self.unzip_file_name, 'rb') as file:
            current_dict = pickle.load(file)
            current_dict_size = file.tell()
            unzip_ind = list(current_dict.values())
            filenames = list(current_dict.keys())
            if mode == 0:
                length = len(filenames)
                for each in range(length):
                    current_filename = filenames[each]
                    current_file_size = unzip_ind[each]
                    read_times, remain_size = divmod(current_file_size,
                                                     read_unit)
                    write_counter = 0
                    with open(current_filename, 'wb') as f:
                        for k in range(read_times):
                            f.write(file.read(read_unit))
                            write_counter += read_unit
                            if current_file_size:
                                self.msg.configure(
                                    text=
                                    f'{each+1}/{length} Unzipping {round((write_counter/current_file_size)*100, 3)}% of file {current_filename}'
                                )
                                self.msg.update()
                        f.write(file.read(remain_size))
                        write_counter += remain_size
                        if current_file_size:
                            self.msg.configure(
                                text=
                                f'{each+1}/{length} Unzipping {round((write_counter/current_file_size)*100, 3)}% of file {current_filename}'
                            )
                            self.msg.update()
            else:
                select_file_ind = [
                    i for i in range(len(self.selected_files))
                    if self.selected_files[i]
                ]
                select_file_range = [(sum(unzip_ind[:i]),
                                      sum(unzip_ind[:i + 1]))
                                     for i in select_file_ind]
                length = len(select_file_ind)
                file_length = len(filenames)
                for each in range(length):
                    current_ind = select_file_ind[each]
                    current_filename = filenames[current_ind]
                    current_file_size = unzip_ind[current_ind]
                    current_select_file_range = select_file_range[each]
                    file.seek(current_select_file_range[0] + current_dict_size)
                    read_times, remain_size = divmod(current_file_size,
                                                     read_unit)
                    write_counter = 0
                    with open(current_filename, 'wb') as f:
                        for k in range(read_times):
                            f.write(file.read(read_unit))
                            write_counter += read_unit
                            self.msg.configure(
                                text=
                                f'{each+1}/{length} Unzipping {round((write_counter/current_file_size)*100, 3)}% of file {current_filename}'
                            )
                            self.msg.update()
                        f.write(file.read(remain_size))
                        write_counter += remain_size
                        self.msg.configure(
                            text=
                            f'{each+1}/{length} Unzipping {round((write_counter/current_file_size)*100, 3)}% of file {current_filename}'
                        )
                        self.msg.update()
        self.msg.configure(
            text=
            f'Successfully unzip the files, please look at the directory {unzip_path}'
        )
        os.chdir(original_drc)


root = Root()
root.mainloop()
