#Replays a ghost on Dolphin
from dolphin import event, controller, savestate, memory

def pointer_chase(address, *chase_offsets):
        val = memory.read_u32(address)
        for offset in chase_offsets[:-1]:
            val = memory.read_u32(val + offset)
        return val+chase_offsets[-1]

#load savestate
while True:
    await event.frameadvance()
    if (memory.read_u32(pointer_chase(0x809BD730, 0x28)) == 0):
        savestate.load_from_file('/home/brian/Documents/startstate.sav')
        break

#load ghost
with open('/home/brian/Downloads/01m08s7737161 Kasey.rkg', 'rb') as f:
    ghostdata = bytearray(f.read())
    print(ghostdata[12] & 0x08)
    print(ghostdata[136] << 0x08)
    print(ghostdata[137])
    face_button_inputs = (ghostdata[136] << 0x08) | ghostdata[137]
    print(face_button_inputs)
    directional_inputs = (ghostdata[138] << 0x08) | ghostdata[139]
    print(directional_inputs)
    trick_inputs = (ghostdata[140] << 0x08) | ghostdata[141]
    print(trick_inputs)

    current_byte = 8
    endFrame = 0

'''
#play back ghost
while True:
    await event.frameadvance()
    if (memory.read_u32(pointer_chase(0x809BD730, 0x28)) == 4):
        break
'''