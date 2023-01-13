#Creates a savestate for the frame that a run starts on
from dolphin import event, memory, savestate

def pointer_chase(address, *chase_offsets):
        val = memory.read_u32(address)
        for offset in chase_offsets[:-1]:
            val = memory.read_u32(val + offset)
        return val+chase_offsets[-1]

while True:
    await event.frameadvance()
    if (memory.read_u32(pointer_chase(0x809BD730, 0x28)) == 1):
       savestate.save_to_file('/home/brian/Documents/startstate.sav')
       savestate.save_to_slot(1)
       break