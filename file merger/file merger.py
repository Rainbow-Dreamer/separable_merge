original_drc = os.getcwd()

read_unit = 1024 * 16


def parse_dir(dirname, header, mode=0, get_size=False):
    if mode == 1:
        dirname = dirname.lstrip(header)
    current_files = os.listdir(os.path.join(header, dirname))
    for i, j in enumerate(current_files):
        current_real_path = os.path.join(header, dirname, j)
        if os.path.isdir(current_real_path):
            current_files[i] = parse_dir(current_real_path, header, 1,
                                         get_size)
        else:
            current_file_name = os.path.join(dirname, j)
            current_files[i] = {
                current_file_name: os.path.getsize(current_real_path)
            } if get_size else current_file_name
    return {dirname: current_files}


def get_all_files_in_dir(dirname):
    result = []
    current_files = os.listdir(dirname)
    for i, j in enumerate(current_files):
        current_real_path = os.path.join(dirname, j)
        if os.path.isfile(current_real_path):
            result.append(current_real_path)
        else:
            result += get_all_files_in_dir(current_real_path)
    return result


def get_len(current_dict):
    result = 0
    for each in current_dict.values():
        if type(each) == list:
            for i in each:
                result += get_len(i)
        else:
            result += 1
    return result


def get_unzip_ind(current_dict):
    result = []
    for each in current_dict.values():
        if type(each) == list:
            for i in each:
                result += get_unzip_ind(i)
        else:
            result.append(each)
    return result


def get_unzip_file(current_dict):
    result = []
    for each in current_dict:
        current = current_dict[each]
        if type(current) == list:
            for i in current:
                result += get_unzip_file(i)
        else:
            result.append(each)
    return result


def build_folders(current_dict, choose_file=None):
    for each in current_dict:
        current = current_dict[each]
        if type(current) == list:
            if choose_file:
                if each in choose_file:
                    os.makedirs(each)
            else:
                os.mkdir(each)
            for i in current:
                build_folders(i, choose_file)


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.minsize(850, 600)
        try:
            self.wm_iconbitmap('resources/icon.ico')
        except:
            pass
        self.title('File Merger and Splitter')
        self.choose_files = ttk.Button(self,
                                       text='Add files',
                                       command=self.choose_mix_files)
        self.add_choose_path = ttk.Button(
            self, text='Add folders', command=lambda: self.choose_mix_files(1))
        self.start_mix = ttk.Button(self,
                                    text='Start merging',
                                    command=self.filemix)
        self.clear_choose_files = ttk.Button(self,
                                             text='Clear',
                                             command=self.clear_files)
        self.choose_files_show = Text(self, height=17, width=95, wrap='none')
        self.choose_files_show.configure(state='disabled')
        self.choose_files.place(x=0, y=20)
        self.choose_file_list_bar = ttk.Scrollbar(self, orient="vertical")
        self.choose_file_list_bar_h = ttk.Scrollbar(self, orient="horizontal")
        self.choose_files_show.configure(
            yscrollcommand=self.choose_file_list_bar.set,
            xscrollcommand=self.choose_file_list_bar_h.set)
        self.choose_file_list_bar.config(command=self.choose_files_show.yview)
        self.choose_file_list_bar_h.config(
            command=self.choose_files_show.xview)
        self.choose_file_list_bar.place(x=675, y=50, height=225, anchor=N)
        self.choose_file_list_bar_h.place(x=0, y=283, width=670, anchor=W)
        self.add_choose_path.place(x=150, y=20)
        self.choose_files_show.place(x=0, y=50)
        self.start_mix.place(x=300, y=20)
        self.clear_choose_files.place(x=450, y=20)
        self.choose_unzip_file = ttk.Button(
            self,
            text='Choose the file you want to unzip',
            command=self.choose_unzip_file_name)
        self.start_unzip = ttk.Button(self,
                                      text='Start unzipping',
                                      command=self.file_unzip)
        self.choose_unzip_file.place(x=0, y=300)
        self.start_unzip.place(x=0, y=350)
        self.filenames = []
        self.actual_filenames = []
        self.file_path = '.'
        self.unzip_file_name = ''
        self.unzip_file_name_show = ttk.Label(self, text='')
        self.unzip_file_name_show.place(x=210, y=300)
        self.msg = ttk.Label(self, text='Currently no actions')
        self.msg.place(x=0, y=550)
        self.browse_files = ttk.Button(
            self,
            text='Browse unzippable files (selective unzipping)',
            command=self.browse_files_func)
        self.browse_files.place(x=150, y=350)
        self.save_task_button = ttk.Button(self,
                                           text='Save current task',
                                           command=self.save_task)
        self.save_task_button.place(x=500, y=350)
        self.save_task_button = ttk.Button(self,
                                           text='Import task',
                                           command=self.import_task)
        self.save_task_button.place(x=500, y=400)
        self.is_direct_merge = IntVar()
        self.is_direct_merge.set(0)
        self.direct_merge_button = Checkbutton(self,
                                               text='direct merge',
                                               variable=self.is_direct_merge)
        self.direct_merge_button.place(x=570, y=20)
        self.merge_dict = {}

    def save_task(self):
        file_path = filedialog.asksaveasfile(initialdir='.',
                                             title="Save current task",
                                             filetype=(("All files", "*.*"), ),
                                             initialfile='Untitled.fmt')
        if file_path:
            with open(file_path.name, 'w') as f:
                f.write(str(self.actual_filenames))
                self.msg.configure(
                    text=f'Successfully save task file {file_path.name}')
                self.msg.update()

    def import_task(self, task_file_name=None):
        if not task_file_name:
            task_file_name = filedialog.askopenfilename(
                initialdir='.',
                title="Choose task file",
                filetype=(("fmt file", "*.fmt"), ("All files", "*.*")))
        if task_file_name:
            self.clear_files()
            with open(task_file_name) as f:
                self.actual_filenames = literal_eval(f.read())
            self.choose_files_show.configure(state='normal')
            self.choose_files_show.delete('1.0', END)
            self.choose_files_show.insert(END,
                                          '\n'.join(self.actual_filenames))
            self.choose_files_show.configure(state='disabled')
            for each in self.actual_filenames:
                if os.path.isdir(each):
                    self.filenames += get_all_files_in_dir(each)
                    header, current_path = os.path.split(each)
                    current_dict = parse_dir(current_path,
                                             header,
                                             get_size=True)
                    self.merge_dict.update(current_dict)
                else:
                    self.filenames.append(each)
                    self.merge_dict[os.path.basename(each)] = os.path.getsize(
                        each)
            self.msg.configure(
                text=f'Successfully import task file {task_file_name}')
            self.msg.update()

    def convert_size(self, size):
        size /= 1024
        if size < 1024:
            return f'{round(size, 2)} KB'
        elif 1024 <= size < 1024**2:
            return f'{round(size/1024, 2)} MB'
        else:
            return f'{round(size/(1024**2), 2)} GB'

    def treeview_build_folders(self, current_dict, parent=''):
        for i, j in current_dict.items():
            if type(j) == list:
                current_folder = self.browse_file_list.insert(parent,
                                                              "end",
                                                              i,
                                                              text=i)
                for each in j:
                    self.treeview_build_folders(each, current_folder)
            else:
                self.browse_file_list.insert(parent,
                                             "end",
                                             i,
                                             text=i,
                                             values=(self.convert_size(j), ))

    def clear_browse_file_list(self):
        for item in self.browse_file_list.selection():
            self.browse_file_list.selection_remove(item)

    def browse_files_func(self):
        if not self.unzip_file_name:
            self.msg.configure(text='No file is selected to unzip')
            return
        self.browse_filenames = []
        self.browse_file_window = Toplevel(self)
        try:
            self.browse_file_window.wm_iconbitmap('resources/icon.ico')
        except:
            pass
        self.browse_file_window.minsize(850, 500)
        self.browse_file_window.title('File list')
        self.browse_file_window.focus_force()

        self.browse_file_list_bar = ttk.Scrollbar(self.browse_file_window,
                                                  orient="vertical")
        self.browse_file_list_bar_h = ttk.Scrollbar(self.browse_file_window,
                                                    orient="horizontal")
        self.browse_file_list = ttk.Treeview(
            self.browse_file_window,
            yscrollcommand=self.browse_file_list_bar.set,
            xscrollcommand=self.browse_file_list_bar_h.set,
            height=17)
        self.browse_file_list["columns"] = ("one")
        self.browse_file_list.column("#0", width=400, minwidth=150)
        self.browse_file_list.column("one", width=160, minwidth=50)
        self.browse_file_list.heading("#0", text="File Name", anchor=W)
        self.browse_file_list.heading("one", text="File Size", anchor=W)
        self.browse_file_list.bind('<Button-3>',
                                   lambda e: self.clear_browse_file_list())

        self.browse_file_list_bar.config(command=self.browse_file_list.yview)
        self.browse_file_list_bar_h.config(command=self.browse_file_list.xview)
        self.browse_file_list.place(x=0, y=50)
        self.browse_file_list_bar.place(x=570, y=50, height=360, anchor=N)
        self.browse_file_list_bar_h.place(x=0, y=425, width=570, anchor=W)
        self.browse_file_msg = ttk.Label(
            self.browse_file_window,
            text='Click to choose files and folders you want to unzip')
        self.browse_file_msg.place(x=0, y=20)
        with open(self.unzip_file_name, 'rb') as file:
            current_dict = pickle.load(file)
            filenames = get_unzip_file(current_dict)
            for each in range(len(filenames)):
                current_filename = filenames[each]
                self.browse_filenames.append(current_filename)
        self.treeview_build_folders(current_dict)
        os.chdir(original_drc)
        self.msg.configure(text='Successfully open file list')
        self.select_file_unzip = ttk.Button(
            self.browse_file_window,
            text='Unzip the selected files and folders',
            command=lambda: self.file_unzip(mode=1))
        self.select_file_unzip.place(x=600, y=50)

    def clear_files(self):
        self.filenames.clear()
        self.actual_filenames.clear()
        self.choose_files_show.configure(state='normal')
        self.choose_files_show.delete('1.0', END)
        self.choose_files_show.configure(state='disabled')
        self.merge_dict.clear()

    def choose_mix_files(self, mode=0):
        if mode == 0:
            filenames = filedialog.askopenfilenames(initialdir='.',
                                                    title="Choose files",
                                                    filetype=(("All files",
                                                               "*.*"), ))
            if filenames:
                filenames = list(filenames)
                self.filenames += filenames
                self.actual_filenames += filenames
                self.merge_dict.update({
                    os.path.basename(each): os.path.getsize(each)
                    for each in filenames
                })
                self.choose_files_show.configure(state='normal')
                self.choose_files_show.insert(END, '\n'.join(filenames) + '\n')
                self.choose_files_show.configure(state='disabled')
        else:
            dirnames = tkfilebrowser.askopendirnames(initialdir='.',
                                                     title="Choose folders")
            if dirnames:
                for each in dirnames:
                    self.filenames += get_all_files_in_dir(each)
                    header, current_path = os.path.split(each)
                    current_dict = parse_dir(current_path,
                                             header,
                                             get_size=True)
                    self.merge_dict.update(current_dict)
                self.actual_filenames += dirnames
                self.choose_files_show.configure(state='normal')
                self.choose_files_show.insert(END, '\n'.join(dirnames) + '\n')
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
                                              defaultextension='.fm',
                                              filetype=(("All files",
                                                         "*.*"), ),
                                              initialfile='Untitled.fm')
        if not mixed_name:
            return
        mixed_name = mixed_name.name
        counter = 1
        file_num = len(self.filenames)
        with open(mixed_name, 'wb') as file:
            if not self.is_direct_merge.get():
                file.write(pickle.dumps(self.merge_dict))
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
        os.chdir(unzip_path)
        with open(self.unzip_file_name, 'rb') as file:
            current_dict = pickle.load(file)
            current_dict_size = file.tell()
            unzip_ind = get_unzip_ind(current_dict)
            filenames = get_unzip_file(current_dict)
            if mode == 0:
                build_folders(current_dict)
                length = get_len(current_dict)
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
                current_selected_files = [
                    self.browse_file_list.item(each, 'text')
                    for each in self.browse_file_list.selection()
                ]
                if not current_selected_files:
                    return
                select_file_ind = []
                for i in current_selected_files:
                    if i in filenames:
                        select_file_ind.append(filenames.index(i))
                    else:
                        select_file_ind += [
                            k for k in range(len(filenames))
                            if os.path.split(filenames[k])[0].startswith(i)
                        ]
                select_file_range = [(sum(unzip_ind[:i]),
                                      sum(unzip_ind[:i + 1]))
                                     for i in select_file_ind]
                length = len(select_file_ind)
                file_length = len(filenames)
                build_folders(
                    current_dict,
                    [os.path.dirname(filenames[i]) for i in select_file_ind])
                for each in range(length):
                    current_ind = select_file_ind[each]
                    current_filename = filenames[current_ind]
                    current_file_size = unzip_ind[current_ind]
                    if not current_file_size:
                        current_file_size = 1
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


if __name__ == '__main__':
    root = Root()
    argv = sys.argv
    if len(argv) > 1:
        current_file = argv[1]
        if os.path.splitext(current_file)[1][1:].lower() == 'fmt':
            root.import_task(current_file)
        else:
            root.unzip_file_name = current_file
            root.unzip_file_name_show.configure(text=root.unzip_file_name)
            root.after(100, root.browse_files_func)
    root.mainloop()
