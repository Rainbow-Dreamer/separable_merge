from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import sys
import pickle
from ast import literal_eval
from copy import deepcopy as copy
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

abs_path = os.path.dirname(sys.executable)
os.chdir(abs_path)
sys.path.append(abs_path)
with open('packages/file merger.py', encoding='utf-8') as f:
    exec(f.read())
