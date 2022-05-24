from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import sys

abs_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(abs_path)
sys.path.append(abs_path)
with open('packages/file splitter.py', encoding='utf-8') as f:
    exec(f.read())
