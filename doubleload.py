from dolphin import event, savestate

await event.frameadvance()
savestate.load_from_file('/home/brian/Documents/chainstate.sav')
for i in range(60):
    await event.frameadvance()
savestate.load_from_file('/home/brian/Documents/chainstate.sav')
await event.frameadvance()