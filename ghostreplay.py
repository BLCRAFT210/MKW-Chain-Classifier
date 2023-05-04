# Replays a ghost on Dolphin
from dolphin import event, controller, savestate, memory
from libyaz0 import decompress
from PIL import Image
import time
import json
import os
import shutil


def mkdir(path):
    try:
        os.mkdir(path)
    except:
        pass


def pointer_chase(address, *chase_offsets):
    val = memory.read_u32(address)
    for offset in chase_offsets[:-1]:
        val = memory.read_u32(val + offset)
    return val+chase_offsets[-1]


def save_screenshot(width, height, data):
    img = Image.frombytes('RGBA', (width, height), data, 'raw')
    img = img.crop((355, 220, 832-355, 456-50))
    img = img.convert('L')
    global framenumber
    img.save(f'/home/brian/Documents/Frames/{framenumber}.png')
    framenumber += 1


STICK_MAP = [0, 65, 70, 80, 90, 100, 110,
             128, 155, 165, 175, 185, 195, 200, 255]
runhash = ''
framenumber = 0
event.on_framedrawn(save_screenshot)
TRAINING_DIR = '/home/brian/Documents/TrainingData'
mkdir('/home/brian/Documents/Frames')
mkdir(f'{TRAINING_DIR}')
mkdir(f'{TRAINING_DIR}/F')
mkdir(f'{TRAINING_DIR}/H')
mkdir(f'{TRAINING_DIR}/W')
mkdir(f'{TRAINING_DIR}/D')

with open('/home/brian/MKW-Chain-Classifier/leaderboard.json', 'r+') as leaderboardfile, open('/home/brian/Documents/log.txt', 'a') as out:
    out.write(
        f'\n\nScript started at {time.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    leaderboard = json.load(leaderboardfile)
    for run in leaderboard.values():
        runhash = run['hash']
        if run['replayed']:
            out.write(f'Skipped replayed run {runhash}\n')
            continue
        out.write(f'Replaying run {runhash}\n')
        framenumber = 0
        with open(f'/home/brian/MKW-Chain-Classifier/ghosts/{runhash}.rkg', 'rb') as f:
            ghostdata = f.read()
            inputdata = ghostdata[140:]
            if (ghostdata[12] & 0x08) != 0:
                inputdata = decompress(inputdata)
            # accelerate, drift, shroom
            faceInputCount = (inputdata[0] << 0x08) | inputdata[1]
            directionalInputCount = (
                inputdata[2] << 0x08) | inputdata[3]  # joystick
            trickInputCount = (inputdata[4] << 0x08) | inputdata[5]  # dpad

            faceInputs, directionalInputs, trickInputs = [], [], []
            currentByte = 8

            for i in range(faceInputCount):
                inputs = inputdata[currentByte]
                duration = inputdata[currentByte+1]
                accelerator = (inputs & 0x01) != 0
                drift = (inputs & 0x02) != 0
                item = (inputs & 0x04) != 0
                faceInputs.extend([(accelerator, drift, item)] * duration)
                currentByte += 2

            for i in range(directionalInputCount):
                inputs = inputdata[currentByte]
                duration = inputdata[currentByte+1]
                vertical = inputs & 0x0F
                horizontal = (inputs >> 4) & 0x0F
                directionalInputs.extend([(horizontal, vertical)] * duration)
                currentByte += 2

            for i in range(trickInputCount):
                inputs = inputdata[currentByte]
                duration = inputdata[currentByte+1]
                trick = (inputs & 0x70) // 16
                fullBytePresses = inputs & 0x0F
                trickInputs.extend([0]*fullBytePresses*256 + [trick]*duration)
                currentByte += 2

            inputList = []
            for i in range(len(faceInputs)):
                inputList.append({
                    'Left': trickInputs[i] == 3,
                    'Right': trickInputs[i] == 4,
                    'Down': trickInputs[i] == 2,
                    'Up': trickInputs[i] == 1,
                    'Z': False,
                    'R': False,
                    'L': faceInputs[i][2],
                    'A': faceInputs[i][0],
                    'B': faceInputs[i][1],
                    'X': False,
                    'Y': False,
                    'Start': False,
                    'StickX': STICK_MAP[directionalInputs[i][0]],
                    'StickY': STICK_MAP[directionalInputs[i][1]],
                    'CStickX': 128,
                    'CStickY': 128,
                    'TriggerLeft': 0,
                    'TriggerRight': 0,
                    'AnalogA': 0,
                    'AnalogB': 0,
                    'Connected': True
                })

        # load savestate
        await event.frameadvance()
        time.sleep(1)
        savestate.load_from_file('/home/brian/Documents/startstate.sav')

        # play back ghost
        wheelieTimerSeq = []
        for i, inputs in enumerate(inputList):
            # out.write(f'{i}: {memory.read_u32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x2A8))}, {memory.read_f32(pointer_chase(0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x20))}\n')
            wheelieTimerSeq.append(memory.read_u32(pointer_chase(
                0x809C18F8, 0xC, 0x10, 0x0, 0x10, 0x10, 0x2A8)))
            controller.set_gc_buttons(0, inputs)
            await event.frameadvance()

        # create training data
        for i, c in enumerate(wheelieTimerSeq):
            out.write(f'{i}: {c}\n')
        out.write('\nCreating training data...\n\n')
        chains = []
        streak = 0
        start = 0
        for i in range(len(wheelieTimerSeq)):
            if wheelieTimerSeq[i] == 181:
                if streak == 0:
                    start = i
                streak += 1
            elif wheelieTimerSeq[i-1] == 181:
                if wheelieTimerSeq[i+25-streak] == 26-streak:
                    chains.append((start, streak))
                streak = 0

        out.write(str(chains)+'\n')

        for chain in chains:
            label = ''
            match chain[1]:
                case 1:
                    label = 'F'
                case 2:
                    label = 'H'
                case 3:
                    label = 'W'
                case _:
                    label = 'D'
            dataCount = len(os.listdir(f'{TRAINING_DIR}/{label}'))
            mkdir(f'{TRAINING_DIR}/{label}/{dataCount}')

            for i in range(25):
                shutil.copyfile(
                    f'/home/brian/Documents/Frames/{chain[0]-1+i}.png', f'{TRAINING_DIR}/{label}/{dataCount}/{i}.png')
            out.write(f'Saved {label} chain #{dataCount}\n')

        out.flush()

        leaderboard[runhash]['replayed'] = True
        leaderboardfile.seek(0)
        json.dump(leaderboard, leaderboardfile)
        leaderboardfile.truncate()

    out.write('Complete!')
