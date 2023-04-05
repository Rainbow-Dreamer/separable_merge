original_drc = os.getcwd()

with open('config.json', encoding='utf-8') as f:
    current_settings = json.load(f)

read_unit = current_settings['read_unit']
kdf_iterations = current_settings['kdf_iterations']
if read_unit.endswith('KB'):
    read_unit_num = int(read_unit.split('KB')[0])
    read_unit = read_unit_num * 1024
elif read_unit.endswith('MB'):
    read_unit_num = int(read_unit.split('MB')[0])
    read_unit = read_unit_num * (1024**2)
elif read_unit.endswith('GB'):
    read_unit_num = int(read_unit.split('GB')[0])
    read_unit = read_unit_num * (1024**3)


def normal_path(path):
    return path.replace('\\', '/')


def parse_dir(dirname, header, mode=0, get_size=False):
    if mode == 1:
        dirname = dirname[len(header) + 1:]
    current_files = os.listdir(os.path.join(header, dirname))
    for i, j in enumerate(current_files):
        current_real_path = normal_path(os.path.join(header, dirname, j))
        if os.path.isdir(current_real_path):
            current_files[i] = parse_dir(current_real_path, header, 1,
                                         get_size)
        else:
            current_file_name = normal_path(os.path.join(dirname, j))
            current_files[i] = {
                current_file_name: os.path.getsize(current_real_path)
            } if get_size else current_file_name
    return {dirname: current_files}


def get_all_files_in_dir(dirname):
    result = []
    current_files = os.listdir(dirname)
    for i, j in enumerate(current_files):
        current_real_path = normal_path(os.path.join(dirname, j))
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


class header:

    def __init__(self):
        self.merge_dict = {}
        self.has_password = False
        self.salt = ''


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
                                       command=self.choose_merge_files)
        self.add_choose_path = ttk.Button(
            self,
            text='Add folders',
            command=lambda: self.choose_merge_files(1))
        self.start_merge = ttk.Button(self,
                                      text='Start merging',
                                      command=self.file_merge)
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
        self.start_merge.place(x=300, y=20)
        self.clear_choose_files.place(x=450, y=20)
        self.choose_unzip_file = ttk.Button(
            self,
            text='Choose the file you want to unzip',
            command=self.choose_unzip_file_name)
        self.start_unzip = ttk.Button(self,
                                      text='Start unzipping',
                                      command=self.file_unzip)
        self.choose_unzip_file.place(x=0, y=350)
        self.start_unzip.place(x=0, y=400)
        self.set_password_button = ttk.Button(self,
                                              text='Set password',
                                              command=self.set_password)
        self.set_password_button.place(x=580, y=20)
        self.filenames = []
        self.actual_filenames = []
        self.unzip_file_name = ''
        self.msg = ttk.Label(self, text='Currently no actions')
        self.msg.place(x=0, y=550)
        self.browse_files = ttk.Button(
            self,
            text='Browse unzippable files (selective unzipping)',
            command=self.browse_files_func)
        self.browse_files.place(x=150, y=400)
        self.save_task_button = ttk.Button(self,
                                           text='Save current task',
                                           command=self.save_task)
        self.save_task_button.place(x=500, y=400)
        self.import_task_button = ttk.Button(self,
                                             text='Import task',
                                             command=self.import_task)
        self.import_task_button.place(x=500, y=450)
        self.is_direct_merge = IntVar()
        self.is_direct_merge.set(0)
        self.direct_merge_button = Checkbutton(self,
                                               text='direct merge',
                                               variable=self.is_direct_merge)
        self.direct_merge_button.place(x=700, y=20)
        self.current_header = header()
        self.current_unzip_header = None
        self.browse_file_window = None
        self.set_password_window = None
        self.ask_password_window = None
        self.current_decrypted = False
        self.current_password = None
        self.already_get_header = False

    def save_task(self):
        file_path = filedialog.asksaveasfile(title="Save current task",
                                             filetypes=(("All files", "*"), ),
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
                title="Choose task file",
                filetypes=(("fmt file", ".fmt"), ("All files", "*")))
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
                    self.filenames.extend(get_all_files_in_dir(each))
                    header, current_path = os.path.split(each)
                    current_dict = parse_dir(current_path,
                                             header,
                                             get_size=True)
                    self.current_header.merge_dict.update(current_dict)
                elif os.path.isfile(each):
                    self.filenames.append(each)
                    self.current_header.merge_dict[os.path.basename(
                        each)] = os.path.getsize(each)
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
                self.file_path_dict[i] = True
                current_folder = self.browse_file_list.insert(parent,
                                                              "end",
                                                              i,
                                                              text=i)
                for each in j:
                    self.treeview_build_folders(each, current_folder)
            else:
                self.file_path_dict[i] = False
                self.browse_file_list.insert(parent,
                                             "end",
                                             i,
                                             text=i,
                                             values=(self.convert_size(j), ))

    def clear_browse_file_list(self):
        for item in self.browse_file_list.selection():
            self.browse_file_list.selection_remove(item)

    def browse_files_func(self):
        if self.browse_file_window is not None and self.browse_file_window.winfo_exists(
        ):
            self.browse_file_window.focus_force()
            return
        if not self.unzip_file_name:
            self.msg.configure(text='No file is selected to unzip')
            return
        if not self.already_get_header:
            with open(self.unzip_file_name, 'rb') as file:
                self.current_unzip_header = pickle.load(file)
            self.already_get_header = True
        if self.current_unzip_header.has_password and not self.current_decrypted:
            self.ask_password(self.current_unzip_header)
        else:
            self.open_browse_file_window(self.current_unzip_header)

    def open_browse_file_window(self, current_header):
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
        current_dict = current_header.merge_dict
        filenames = get_unzip_file(current_dict)
        for each in range(len(filenames)):
            current_filename = filenames[each]
            self.browse_filenames.append(current_filename)
        self.file_path_dict = {}
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
        self.current_header.merge_dict.clear()

    def choose_merge_files(self, mode=0):
        if mode == 0:
            filenames = filedialog.askopenfilenames(title="Choose files",
                                                    filetypes=(("All files",
                                                                "*"), ))
            if filenames:
                filenames = list(filenames)
                for each in filenames:
                    current_filename = os.path.basename(each)
                    if current_filename not in self.current_header.merge_dict:
                        self.filenames.append(each)
                        self.actual_filenames.append(each)
                        self.choose_files_show.configure(state='normal')
                        self.choose_files_show.insert(END, each + '\n')
                        self.choose_files_show.configure(state='disabled')
                        self.current_header.merge_dict[
                            current_filename] = os.path.getsize(each)
        else:
            dirname = filedialog.askdirectory(title="Choose folders")
            if dirname:
                header, current_path = os.path.split(dirname)
                if current_path not in self.current_header.merge_dict:
                    current_dict = parse_dir(current_path,
                                             header,
                                             get_size=True)
                    self.current_header.merge_dict.update(current_dict)
                    dirname = normal_path(dirname)
                    self.actual_filenames.append(dirname)
                    self.choose_files_show.configure(state='normal')
                    self.choose_files_show.insert(END, dirname + '\n')
                    self.choose_files_show.configure(state='disabled')
                    self.filenames.extend(get_all_files_in_dir(dirname))

    def file_merge(self):
        if not self.filenames:
            self.msg.configure(text='The merge file list is empty')
            return
        merged_name = filedialog.asksaveasfile(title="Save merged file",
                                               defaultextension='.fm',
                                               filetypes=(("All files",
                                                           "*"), ),
                                               initialfile='Untitled.fm')
        if not merged_name:
            return
        merged_name = merged_name.name
        counter = 1
        file_num = len(self.filenames)
        current_encrypt = False
        with open(merged_name, 'wb') as file:
            if not self.is_direct_merge.get():
                if self.current_header.has_password:
                    current_encrypt = True
                    current_salt = self.generate_salt()
                    self.current_header.salt = current_salt
                    current_key = self.generate_key(self.current_password,
                                                    current_salt)
                    new_header = copy(self.current_header)
                    new_header.merge_dict = current_key.encrypt(
                        str(new_header.merge_dict).encode('utf-8'))
                    file.write(pickle.dumps(new_header))
                else:
                    file.write(pickle.dumps(self.current_header))
            for t in self.filenames:
                current_file_size = os.path.getsize(t)
                file_size_counter = 0
                f = open(t, 'rb')
                while True:
                    current_chunk = f.read(read_unit)
                    if current_chunk:
                        current_length = len(current_chunk)
                        if current_encrypt:
                            current_chunk = current_key.encrypt(current_chunk)
                        file.write(current_chunk)
                        file_size_counter += current_length
                        self.msg.configure(
                            text=
                            f'{counter}/{file_num} Merging {round((file_size_counter/current_file_size)*100, 3):.3f}% of file {t}'
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
            text=f'Merging is finished, please look at {merged_name}')

    def choose_unzip_file_name(self):
        current_file_name = filedialog.askopenfilename(title="Choose files",
                                                       filetypes=(("All files",
                                                                   "*"), ))
        if current_file_name:
            self.unzip_file_name = current_file_name
            self.msg.configure(text=f'choose file {self.unzip_file_name}')
            self.current_decrypted = False
            self.already_get_header = False
            self.current_unzip_header = None

    def build_folders(self, current_dict):
        for each in current_dict:
            current = current_dict[each]
            if type(current) == list:
                os.makedirs(each, exist_ok=True)
                for i in current:
                    self.build_folders(i)

    def find_file_path_dict(self, path, current_dict):
        for key, value in current_dict.items():
            if key == path:
                return current_dict
            else:
                if isinstance(value, list):
                    for each in value:
                        result = self.find_file_path_dict(path, each)
                        if result is not None:
                            return result

    def find_path_filenames(self, path, current_dict, unzip_filenames):
        for key, value in current_dict.items():
            if isinstance(value, list):
                current_dir = os.path.join(path, os.path.split(key)[1])
                os.makedirs(current_dir, exist_ok=True)
                for each in value:
                    self.find_path_filenames(current_dir, each,
                                             unzip_filenames)
            else:
                current_filename = os.path.join(path, os.path.split(key)[1])
                unzip_filenames.append(current_filename)

    def file_unzip(self, mode=0):
        if not self.unzip_file_name:
            self.msg.configure(text='No file is selected to unzip')
            self.update()
            return
        if not self.already_get_header:
            with open(self.unzip_file_name, 'rb') as file:
                self.current_unzip_header = pickle.load(file)
            self.already_get_header = True
        if self.current_unzip_header.has_password and not self.current_decrypted:
            self.ask_password(self.current_unzip_header,
                              mode=1,
                              unzip_mode=mode)
        else:
            print(111, self.current_unzip_header.merge_dict)
            self.file_unzip_func(self.current_unzip_header, mode)

    def file_unzip_func(self, current_header, mode=0):
        unzip_path = filedialog.askdirectory(
            title="Choose the directory to unzip to")
        if not unzip_path:
            return
        os.chdir(unzip_path)
        with open(self.unzip_file_name, 'rb') as file:
            current_file_header = pickle.load(file)
            current_read_unit = read_unit
            if current_header.has_password:
                current_key = self.generate_key(self.current_password,
                                                current_header.salt)
                current_read_unit = len(
                    current_key.encrypt(b'a' * current_read_unit))
                self.update_merge_dict_with_key(current_header.merge_dict,
                                                current_key, current_read_unit)
            current_dict = current_header.merge_dict
            current_dict_size = file.tell()
            unzip_ind = get_unzip_ind(current_dict)
            filenames = get_unzip_file(current_dict)
            if mode == 0:
                self.build_folders(current_dict)
                length = get_len(current_dict)
                for each in range(length):
                    current_filename = filenames[each]
                    current_file_size = unzip_ind[each]
                    read_times, remain_size = divmod(current_file_size,
                                                     current_read_unit)
                    write_counter = 0
                    with open(current_filename, 'wb') as f:
                        for k in range(read_times):
                            current_chunk = file.read(current_read_unit)
                            if current_header.has_password:
                                current_chunk = current_key.decrypt(
                                    current_chunk)
                            f.write(current_chunk)
                            write_counter += current_read_unit
                            if current_file_size:
                                self.msg.configure(
                                    text=
                                    f'{each+1}/{length} Unzipping {round((write_counter/current_file_size)*100, 3):.3f}% of file {current_filename}'
                                )
                                self.msg.update()
                        remain_part = file.read(remain_size)
                        if current_header.has_password:
                            remain_part = current_key.decrypt(remain_part)
                        f.write(remain_part)
                        write_counter += remain_size
                        if current_file_size:
                            self.msg.configure(
                                text=
                                f'{each+1}/{length} Unzipping {round((write_counter/current_file_size)*100, 3):.3f}% of file {current_filename}'
                            )
                            self.msg.update()
            elif mode == 1:
                current_selected_files = [
                    self.browse_file_list.item(each, 'text')
                    for each in self.browse_file_list.selection()
                ]
                if not current_selected_files:
                    return
                select_file_ind = []
                unzip_filenames = []
                for i in current_selected_files:
                    if i in filenames:
                        select_file_ind.append(filenames.index(i))
                        current_filename = os.path.split(i)[1]
                        unzip_filenames.append(current_filename)
                    else:
                        current_dir = os.path.split(i)[1]
                        current_inds = [
                            k for k in range(len(filenames))
                            if os.path.split(filenames[k])[0].startswith(i)
                        ]
                        select_file_ind.extend(current_inds)
                        current_dir = os.path.split(i)[1]
                        os.makedirs(current_dir, exist_ok=True)
                        current_file_path_dict = self.find_file_path_dict(
                            i, current_dict)
                        self.find_path_filenames('', current_file_path_dict,
                                                 unzip_filenames)
                select_file_range = [(sum(unzip_ind[:i]),
                                      sum(unzip_ind[:i + 1]))
                                     for i in select_file_ind]
                length = len(select_file_ind)
                file_length = len(filenames)
                for each in range(length):
                    current_ind = select_file_ind[each]
                    current_filename = unzip_filenames[each]
                    current_file_size = unzip_ind[current_ind]
                    current_select_file_range = select_file_range[each]
                    file.seek(current_select_file_range[0] + current_dict_size)
                    read_times, remain_size = divmod(current_file_size,
                                                     current_read_unit)
                    write_counter = 0
                    with open(current_filename, 'wb') as f:
                        for k in range(read_times):
                            current_chunk = file.read(current_read_unit)
                            if current_header.has_password:
                                current_chunk = current_key.decrypt(
                                    current_chunk)
                            f.write(current_chunk)
                            write_counter += current_read_unit
                            if current_file_size:
                                self.msg.configure(
                                    text=
                                    f'{each+1}/{length} Unzipping {round((write_counter/current_file_size)*100, 3):.3f}% of file {current_filename}'
                                )
                                self.msg.update()
                        remain_part = file.read(remain_size)
                        if current_header.has_password:
                            remain_part = current_key.decrypt(remain_part)
                        f.write(remain_part)
                        write_counter += remain_size
                        if current_file_size:
                            self.msg.configure(
                                text=
                                f'{each+1}/{length} Unzipping {round((write_counter/current_file_size)*100, 3):.3f}% of file {current_filename}'
                            )
                            self.msg.update()
        self.msg.configure(
            text=
            f'Unzipping is finished, please look at the directory {unzip_path}'
        )
        os.chdir(original_drc)

    def set_password(self):
        if self.set_password_window is not None and self.set_password_window.winfo_exists(
        ):
            self.set_password_window.focus_force()
            return
        self.set_password_window = Toplevel(self)
        try:
            self.set_password_window.wm_iconbitmap('resources/icon.ico')
        except:
            pass
        self.set_password_window.minsize(350, 200)
        self.set_password_window.title('Set password')
        self.set_password_window.focus_force()
        self.set_password_entry = ttk.Entry(self.set_password_window, width=20)
        if self.current_password:
            self.set_password_entry.insert(END, self.current_password)
        self.set_password_entry.place(x=20, y=20)
        self.set_password_label = ttk.Label(self.set_password_window,
                                            text='enter password here')
        self.set_password_label.place(x=180, y=20)
        self.set_password_func_button = ttk.Button(
            self.set_password_window,
            text='set password',
            command=self.set_password_func)
        self.set_password_func_button.place(x=20, y=100)

    def set_password_func(self):
        current_password = self.set_password_entry.get()
        if not current_password:
            self.current_header.has_password = False
            self.current_header.salt = ''
            self.current_password = current_password
        else:
            self.current_header.has_password = True
            self.current_password = current_password

    def ask_password(self, current_header, mode=0, unzip_mode=0):
        if self.ask_password_window is not None and self.ask_password_window.winfo_exists(
        ):
            self.ask_password_window.focus_force()
            return
        self.ask_password_window = Toplevel(self)
        try:
            self.ask_password_window.wm_iconbitmap('resources/icon.ico')
        except:
            pass
        self.ask_password_window.minsize(350, 200)
        self.ask_password_window.title('Enter password')
        self.ask_password_window.focus_force()
        self.ask_password_entry = ttk.Entry(self.ask_password_window, width=20)
        self.ask_password_entry.place(x=20, y=20)
        self.ask_password_label = ttk.Label(self.ask_password_window,
                                            text='enter password here')
        self.ask_password_label.place(x=180, y=20)
        self.ask_password_func_button = ttk.Button(
            self.ask_password_window,
            text='try password',
            command=lambda: self.ask_password_func(current_header, mode,
                                                   unzip_mode))
        self.ask_password_func_button.place(x=20, y=100)

    def ask_password_func(self, current_header, mode, unzip_mode):
        current_password = self.ask_password_entry.get()
        current_key = self.verify_key(current_password, current_header.salt)
        if current_key:
            self.ask_password_window.destroy()
            self.current_decrypted = True
            self.current_password = current_password
            current_header.merge_dict = literal_eval(
                current_key.decrypt(current_header.merge_dict).decode('utf-8'))
            if mode == 0:
                self.open_browse_file_window(current_header)
            else:
                self.file_unzip_func(current_header, unzip_mode)
        else:
            self.msg.configure(text='incorrect password')

    def verify_key(self, password, salt):
        try:
            password = password.encode('utf-8')
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                             length=32,
                             salt=salt,
                             iterations=kdf_iterations)
            key = base64.urlsafe_b64encode(kdf.derive(password))
            current_key = Fernet(key)
        except:
            return False

        new_read_unit = len(current_key.encrypt(b'a' * read_unit))
        with open(self.unzip_file_name, 'rb') as file:
            current_file_header = pickle.load(file)
            test_file = file.read(new_read_unit)
            try:
                decrypt_file = current_key.decrypt(test_file)
                return current_key
            except:
                return False

    def generate_salt(self):
        salt = os.urandom(16)
        return salt

    def generate_key(self, password, salt):
        password = password.encode('utf-8')
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=32,
                         salt=salt,
                         iterations=kdf_iterations)
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        return f

    def get_new_file_size_with_key(self, current_key, current_file_size,
                                   new_read_unit):
        read_times, remain_size = divmod(current_file_size, read_unit)
        new_file_size = read_times * new_read_unit + len(
            current_key.encrypt(b'a' * remain_size))
        return new_file_size

    def update_merge_dict_with_key(self, current_dict, current_key,
                                   new_read_unit):
        for key, value in current_dict.items():
            if isinstance(value, list):
                for each in value:
                    self.update_merge_dict_with_key(each, current_key,
                                                    new_read_unit)
            else:
                current_dict[key] = self.get_new_file_size_with_key(
                    current_key, value, new_read_unit)


if __name__ == '__main__':
    root = Root()
    argv = sys.argv
    if len(argv) > 1:
        current_file = argv[1]
        original_drc = os.path.dirname(current_file)
        if os.path.splitext(current_file)[1][1:].lower() == 'fmt':
            root.import_task(current_file)
        else:
            root.unzip_file_name = current_file
            root.msg.configure(text=f'choose file {root.unzip_file_name}')
            root.after(100, root.browse_files_func)
    root.mainloop()
