from ctypes import byref, create_string_buffer, sizeof

from win32more.Windows.Win32.Foundation import HWND, RECT
from win32more.Windows.Win32.Graphics.Gdi import (
    BI_RGB,
    BITMAPINFO,
    BITMAPINFOHEADER,
    CAPTUREBLT,
    DIB_RGB_COLORS,
    SRCCOPY,
    BitBlt,
    CreateCompatibleBitmap,
    CreateCompatibleDC,
    DeleteDC,
    DeleteObject,
    GetDC,
    GetDIBits,
    ReleaseDC,
    SelectObject,
)
from win32more.Windows.Win32.UI.WindowsAndMessaging import GetClientRect

from .png import png_from_rgba


def capture_client(hwnd):
    rect = RECT()
    GetClientRect(hwnd, byref(rect))
    return capture_device_context(
        hwnd,
        0,
        0,
        rect.right - rect.left,
        rect.bottom - rect.top,
    )


def capture_screen(x, y, width, height):
    return capture_device_context(HWND(0), x, y, width, height)


def capture_device_context(hwnd, source_x, source_y, width, height):
    width = max(1, round(width))
    height = max(1, round(height))
    source_x = round(source_x)
    source_y = round(source_y)

    source_dc = GetDC(hwnd)
    if not source_dc:
        raise RuntimeError("Unable to get source device context")

    memory_dc = CreateCompatibleDC(source_dc)
    if not memory_dc:
        ReleaseDC(hwnd, source_dc)
        raise RuntimeError("Unable to create compatible device context")

    bitmap = CreateCompatibleBitmap(source_dc, width, height)
    if not bitmap:
        DeleteDC(memory_dc)
        ReleaseDC(hwnd, source_dc)
        raise RuntimeError("Unable to create screenshot bitmap")

    previous_bitmap = SelectObject(memory_dc, bitmap)
    try:
        if not BitBlt(
            memory_dc,
            0,
            0,
            width,
            height,
            source_dc,
            source_x,
            source_y,
            SRCCOPY | CAPTUREBLT,
        ):
            raise RuntimeError("Unable to capture image")

        bitmap_info = BITMAPINFO()
        bitmap_info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
        bitmap_info.bmiHeader.biWidth = width
        bitmap_info.bmiHeader.biHeight = -height
        bitmap_info.bmiHeader.biPlanes = 1
        bitmap_info.bmiHeader.biBitCount = 32
        bitmap_info.bmiHeader.biCompression = BI_RGB
        bitmap_info.bmiHeader.biSizeImage = width * height * 4

        pixels = create_string_buffer(width * height * 4)
        scan_lines = GetDIBits(
            memory_dc,
            bitmap,
            0,
            height,
            pixels,
            byref(bitmap_info),
            DIB_RGB_COLORS,
        )
        if scan_lines != height:
            raise RuntimeError("Unable to read image pixels")

        return png_from_bgra(width, height, pixels.raw)
    finally:
        SelectObject(memory_dc, previous_bitmap)
        DeleteObject(bitmap)
        DeleteDC(memory_dc)
        ReleaseDC(hwnd, source_dc)


def png_from_bgra(width, height, bgra):
    rgba = bytearray(len(bgra))
    for offset in range(0, len(bgra), 4):
        rgba[offset] = bgra[offset + 2]
        rgba[offset + 1] = bgra[offset + 1]
        rgba[offset + 2] = bgra[offset]
        rgba[offset + 3] = 255

    return png_from_rgba(width, height, rgba)
