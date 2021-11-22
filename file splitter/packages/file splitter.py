from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os

original_drc = os.getcwd()

read_unit = 1024 * 16


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.split_file = None
        self.split_file_name = ''
        self.minsize(700, 400)
        try:
            self.wm_iconbitmap('resources/icon.ico')
        except:
            pass
        self.title('File splitter')
        self.choose_files = ttk.Button(
            self,
            text='Please choose the file you want to split',
            command=self.choose_split_files)
        self.choose_file_size_label = ttk.Label(self, text='File size:')
        self.split_into_num = ttk.Label(
            self, text='How many portions do you want to cut into evenly?')
        self.split_into_num_text = Text(self, height=2, width=30)
        self.fixed_split_size = ttk.Label(self, text='Fixed portion size')
        self.split1_button = ttk.Button(
            self,
            text='Start splitting',
            command=lambda: self.file_split(mode=0))
        self.split2_button = ttk.Button(
            self,
            text='Start splitting',
            command=lambda: self.file_split(mode=1))
        self.clear_choose_files = ttk.Button(self,
                                             text='Clear',
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
        self.split1_button.place(x=320, y=180)
        self.split2_button.place(x=300, y=260)
        self.msg = ttk.Label(self, text='Currently no actions')
        self.msg.place(x=0, y=350)
        self.split_file_size = None
        self.calculate_split_into_size = ttk.Button(
            self,
            text='Calculate average portion size',
            command=self.calculate_size)
        self.calculate_split_into_size.place(x=450, y=180)
        self.split_file_size_num = None
        self.split_into_size = ttk.Label(self, text='Average portion size:')
        self.split_into_size.place(x=260, y=220)

    def calculate_size(self):
        if self.split_file_size_num is not None:
            split_into_num = self.split_into_num_text.get('1.0', 'end-1c')
            try:
                split_into_num = int(split_into_num)
            except:
                self.msg.configure(
                    text='The number of portions must be a positive integer')
                return
            if split_into_num <= 0:
                self.msg.configure(
                    text='The number of portions must be a positive integer')
                return
            self.split_into_size.configure(
                text=
                f'Average portion size: {self.convert_size(self.split_file_size_num/split_into_num)}'
            )
            self.msg.configure(text='Calculate finished')
        else:
            self.msg.configure(text='No files are selected')
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
        self.split_into_size.configure(text='Average portion size:')
        self.choose_files_size_show.delete('1.0', END)

    def choose_split_files(self):
        split_file_name = filedialog.askopenfilename(initialdir='.',
                                                     title="Choose file",
                                                     filetype=(("All files",
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

    def file_split_by_chunks(self, file, f, split_size, i, length):
        read_times, remain_size = divmod(split_size, read_unit)
        write_counter = 0
        for k in range(read_times):
            f.write(file.read(read_unit))
            write_counter += read_unit
            if split_size:
                self.msg.configure(
                    text=
                    f'Currently writing portion {i+1}/{length} {round((write_counter/split_size)*100, 3)}%'
                )
                self.msg.update()
        f.write(file.read(remain_size))
        write_counter += remain_size
        if split_size:
            self.msg.configure(
                text=
                f'Currently writing portion {i+1}/{length} {round((write_counter/split_size)*100, 3)}%'
            )
            self.msg.update()

    def file_split(self, mode=0):
        if not self.split_file_name:
            self.msg.configure(text='No files are selected')
            return
        file_path = filedialog.askdirectory(initialdir='.',
                                            title="Choose directory")
        if not file_path:
            return
        os.chdir(file_path)
        if mode == 0:
            split_into_num = self.split_into_num_text.get('1.0', 'end-1c')
            try:
                split_into_num = int(split_into_num)
            except:
                self.msg.configure(
                    text='The number of portions must be a positive integer')
                return
            if split_into_num <= 0:
                self.msg.configure(
                    text='The number of portions must be a positive integer')
                return
            length = self.split_file_size_num
            split_size = length // split_into_num
            counter = 0
            with open(self.split_file_name, 'rb') as file:
                split_file_name = os.path.split(self.split_file_name)[1]
                for i in range(split_into_num):
                    if i != split_into_num - 1:
                        with open(f'{split_file_name} part{i+1}', 'wb') as f:
                            self.file_split_by_chunks(file, f, split_size, i,
                                                      split_into_num)
                        counter += split_size
                    else:
                        with open(f'{split_file_name} part{i+1}', 'wb') as f:
                            self.file_split_by_chunks(file, f,
                                                      length - counter, i,
                                                      split_into_num)
        elif mode == 1:
            fixed_size = self.fixed_split_size_text.get('1.0',
                                                        'end-1c').split()
            try:
                fixed_size_num, unit = float(fixed_size[0]), fixed_size[1]
            except:
                self.msg.configure(
                    text=
                    'Incorrect portion size format, must be \'number KB/MB/GB\''
                )
                return
            if unit == 'KB':
                fixed_size_num *= 1024
            elif unit == 'MB':
                fixed_size_num *= 1024**2
            elif unit == 'GB':
                fixed_size_num *= 1024**3
            else:
                self.msg.configure(text='Only KB, MB, GB are supported')
                return
            length = self.split_file_size_num
            split_size = int(fixed_size_num)
            counter = 0
            part_num = 0
            split_into_num = -(-length // split_size)
            with open(self.split_file_name, 'rb') as file:
                split_file_name = os.path.split(self.split_file_name)[1]
                while True:
                    if counter + split_size >= length:
                        with open(f'{split_file_name} part{part_num+1}',
                                  'wb') as f:
                            self.file_split_by_chunks(file, f,
                                                      length - counter,
                                                      part_num, split_into_num)
                        break
                    else:
                        with open(f'{split_file_name} part{part_num+1}',
                                  'wb') as f:
                            self.file_split_by_chunks(file, f, split_size,
                                                      part_num, split_into_num)
                        counter += split_size
                        part_num += 1
        self.msg.configure(
            text=
            f'Successfully writing the splitted files, please look at {file_path}'
        )
        os.chdir(original_drc)


root = Root()
root.mainloop()
