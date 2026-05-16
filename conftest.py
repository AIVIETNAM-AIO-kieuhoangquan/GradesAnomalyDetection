import sys
import os

# Thêm project root vào sys.path để pytest tìm thấy modules/ và config.py
sys.path.insert(0, os.path.dirname(__file__))
