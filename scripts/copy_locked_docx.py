from __future__ import annotations

import argparse
import ctypes
import os
from ctypes import wintypes


GENERIC_READ = 0x80000000
OPEN_EXISTING = 3
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
CHUNK_SIZE = 1024 * 1024


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE,
]
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.ReadFile.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID,
]
kernel32.ReadFile.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL


def open_shared_read(path: str) -> wintypes.HANDLE:
    handle = kernel32.CreateFileW(
        path,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        0,
        None,
    )
    if handle == INVALID_HANDLE_VALUE:
        raise ctypes.WinError(ctypes.get_last_error())
    return handle


def copy_with_shared_read(src: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    handle = open_shared_read(src)
    try:
        buffer = (ctypes.c_char * CHUNK_SIZE)()
        bytes_read = wintypes.DWORD()
        with open(dst, "wb", buffering=0) as wf:
            while True:
                ok = kernel32.ReadFile(handle, buffer, CHUNK_SIZE, ctypes.byref(bytes_read), None)
                if not ok:
                    raise ctypes.WinError(ctypes.get_last_error())
                if bytes_read.value == 0:
                    break
                wf.write(buffer[: bytes_read.value])
    finally:
        kernel32.CloseHandle(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    args = parser.parse_args()

    copy_with_shared_read(args.src, args.dst)
    print(args.dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
