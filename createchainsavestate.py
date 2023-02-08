#Creates a savestate for the frame on which a drop occurs
from dolphin import event, memory, savestate

def pointer_chase(address, *chase_offsets):
        val = memory.read_u32(address)
        for offset in chase_offsets[:-1]:
            val = memory.read_u32(val + offset)
        return val+chase_offsets[-1]

while True:
    await event.frameadvance()
    if (memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x2A8)) == 178):
       savestate.save_to_file('/home/brian/Documents/chainstate.sav')
       break