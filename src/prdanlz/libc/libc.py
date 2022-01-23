import ctypes
import ctypes.util

libc = ctypes.CDLL(str(ctypes.util.find_library("c")), use_errno=True)

libc.devname.argtypes = [ctypes.c_longlong, ctypes.c_int]
libc.devname.restype = ctypes.c_char_p

libc.getpagesize.argtypes = []
libc.getpagesize.restype = ctypes.c_int
