#Gathers data for the four different kinds of chains
from dolphin import event, controller, savestate, memory
from PIL import Image, ImageDraw

forward = {
            'Left': False,
            'Right': False,
            'Down': False,
            'Up': False,
            'Z': False,
            'R': False,
            'A': True,
            'L': False,
            'B': False,
            'X': False,
            'Y': False,
            'Start': False,
            'StickX': 128,
            'StickY': 128,
            'CStickX': 128,
            'CStickY': 128,
            'TriggerLeft': 0,
            'TriggerRight': 0,
            'AnalogA': 0,
            'AnalogB': 0,
            'Connected': True
        }

wheelie = {
            'Left': False,
            'Right': False,
            'Down': False,
            'Up': True,
            'Z': False,
            'R': False,
            'A': True,
            'L': False,
            'B': False,
            'X': False,
            'Y': False,
            'Start': False,
            'StickX': 128,
            'StickY': 128,
            'CStickX': 128,
            'CStickY': 128,
            'TriggerLeft': 0,
            'TriggerRight': 0,
            'AnalogA': 0,
            'AnalogB': 0,
            'Connected': True
        }

def pointer_chase(address, *chase_offsets):
        val = memory.read_u32(address)
        for offset in chase_offsets[:-1]:
            val = memory.read_u32(val + offset)
        return val+chase_offsets[-1]

await event.frameadvance()
savestate.load_from_file('/home/brian/Documents/chainstate.sav')
for i in range(25):
    controller.set_gc_buttons(0, forward)
    if i==2:
        controller.set_gc_buttons(0, wheelie)

    width, height, data = await event.framedrawn()

    img = Image.frombytes('RGBA', (width, height), data, 'raw')
    img = img.crop((350, 220, 832-350, 456-50))
    imgdraw = ImageDraw.Draw(img)
    imgdraw.text((0, 0), f'Wheelie timer: {memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x2A8))}', fill=(255, 0, 0))
    imgdraw.text((0, 20), f'Speed: {memory.read_f32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x20))}', fill=(255, 0, 0))
    img.save(f'/home/brian/Documents/Frames/full{i}.png')

await event.frameadvance()
savestate.load_from_file('/home/brian/Documents/chainstate.sav')
for i in range(25):
    controller.set_gc_buttons(0, forward)
    if i==3:
        controller.set_gc_buttons(0, wheelie)

    width, height, data = await event.framedrawn()

    img = Image.frombytes('RGBA', (width, height), data, 'raw')
    img = img.crop((350, 220, 832-350, 456-50))
    imgdraw = ImageDraw.Draw(img)
    imgdraw.text((0, 0), f'Wheelie timer: {memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x2A8))}', fill=(255, 0, 0))
    imgdraw.text((0, 20), f'Speed: {memory.read_f32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x20))}', fill=(255, 0, 0))
    img.save(f'/home/brian/Documents/Frames/half{i}.png')

await event.frameadvance()
savestate.load_from_file('/home/brian/Documents/chainstate.sav')
for i in range(25):
    controller.set_gc_buttons(0, forward)
    if i==4:
        controller.set_gc_buttons(0, wheelie)

    width, height, data = await event.framedrawn()

    img = Image.frombytes('RGBA', (width, height), data, 'raw')
    img = img.crop((350, 220, 832-350, 456-50))
    imgdraw = ImageDraw.Draw(img)
    imgdraw.text((0, 0), f'Wheelie timer: {memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x2A8))}', fill=(255, 0, 0))
    imgdraw.text((0, 20), f'Speed: {memory.read_f32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x20))}', fill=(255, 0, 0))
    img.save(f'/home/brian/Documents/Frames/weak{i}.png')

await event.frameadvance()
savestate.load_from_file('/home/brian/Documents/chainstate.sav')
for i in range(25):
    controller.set_gc_buttons(0, forward)
    if i==5:
        controller.set_gc_buttons(0, wheelie)

    width, height, data = await event.framedrawn()

    img = Image.frombytes('RGBA', (width, height), data, 'raw')
    img = img.crop((350, 220, 832-350, 456-50))
    imgdraw = ImageDraw.Draw(img)
    imgdraw.text((0, 0), f'Wheelie timer: {memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x2A8))}', fill=(255, 0, 0))
    imgdraw.text((0, 20), f'Speed: {memory.read_f32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x20))}', fill=(255, 0, 0))
    img.save(f'/home/brian/Documents/Frames/drop{i}.png')