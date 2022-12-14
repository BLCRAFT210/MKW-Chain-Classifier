#To be used in Felk's Dolphin scripting branch.

from dolphin import gui, event, memory
import sys
sys.path.append('/usr/lib/python3/dist-packages')
from PIL import Image

white = 0xffffffff
black = 0xff000000

framecounter = 0

def pointer_chase(address, *chase_offsets):
        val = memory.read_u32(address)
        for offset in chase_offsets[:-1]:
            val = memory.read_u32(val + offset)
        return val+chase_offsets[-1]

def show_screenshot(width: int, height: int, data: bytes):
    gui.draw_rect_filled((8, 10), (180, 75), black)

    wheelietimer = memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x2A8))
    gui.draw_text((10, 10), white, f'Wheelie timer: {wheelietimer}')

    grounded = bool(memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x1C, 0x4)) & 0x40000)
    gui.draw_text((10, 20), white, f'Grounded: {grounded}')

    inwheelie = bool(memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x1C, 0x4)) & 0x20000000)
    gui.draw_text((10, 30), white, f'In Wheelie: {inwheelie}')

    speed = memory.read_f32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x20))
    gui.draw_text((10, 40), white, f'Speed: {speed}')

    gui.draw_text((10, 50), white, f'Dimensions: {width}x{height}')

    global framecounter
    #if framecounter%60 == 0:
    #    img = Image.frombytes('RGBA', (width, height), data, 'raw')
    #    img.save(f'/home/brian/Documents/Frames/frame{framecounter}.png')

    framecounter += 1

await event.on_framedrawn(show_screenshot)