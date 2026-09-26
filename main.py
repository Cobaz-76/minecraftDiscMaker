import PySimpleGUI as sg
import os, random, zipfile, json, base64, sys
from PIL import Image
from io import BytesIO
import numpy as np

# can we get pydub to fricken work
if getattr(sys, "frozen", False):
    os.environ["PATH"] = sys._MEIPASS + os.pathsep + os.environ["PATH"] # HOLY CRAP IT ACTULLY WORKS
from pydub import AudioSegment

def discGuiAddition(): # add more rows to our gui, and give them unique ids
    global discCount
    discCount += 1
    validDiscs.append(str(discCount))
    return [
            [sg.pin(
                sg.Column([[sg.Image(emptyImage, key=f"Image{discCount}", zoom=4),
                sg.Column([
                    [sg.Text("Disc Name"), sg.Input(key=f'Name{discCount}', expand_x=True), sg.Input("1 False", visible=False, enable_events=True, key=f"DiscSettings{discCount}"), sg.Button("⚙️", tooltip="Edit animated disc settings for this disc", key=f"SettingsButton{discCount}"), sg.Button("Remove Disc", key=f"RemoveDisc{discCount}", button_color=("white", "red"))],
                    [sg.Text("Song file path"), sg.Input(key=f'Song{discCount}', expand_x=True), sg.FileBrowse("Browse", file_types=(("Sound Files", ".mp3 .wav .flac .ogg"),))],
                    [sg.Text("Disc texture path"), sg.Input(enable_events=True, key=f'Texture{discCount}', expand_x=True), sg.FileBrowse("Browse", file_types=(("PNG files", ".png"),))]
                ], key=f'Inputs{discCount}')], [sg.HorizontalSeparator(key=f"Separator{discCount}")]], key=f"DiscEntry{discCount}"))]]

def makeGif(PILimage, delay=1):
    frames = []
    for frameCount in range(int((PILimage.size[1])/16)):
        currentFrame = PILimage.crop((0, 16*frameCount, 16, 16*(frameCount+1)))
        currentPixels = currentFrame.load()
        tintedPixels = []
        if frameCount % 2 == 0: # for some reason it'll only display the difference from last frame, so we just gonna make it tinted different every frame lol
            for i in range(currentFrame.height):
                l = []
                for j in range(currentFrame.width):
                    px = [value + (1 if value != 255 and value != 0 else 0) for value in currentPixels[i, j]]
                    l.append(px)
                tintedPixels.append(l)
        else:
            for i in range(currentFrame.height):
                l = []
                for j in range(currentFrame.width):
                    px = [value - (1 if value != 0 else 0) for value in currentPixels[i, j]]
                    l.append(px)
                tintedPixels.append(l)
        array = np.array(tintedPixels, dtype=np.uint8)
        frames.append(Image.fromarray(array))
    
    # y tf does it display rotated and reversed? guess we'll just .rotate(-90) and reverse the order
    frames = [frame.resize((64, 64), Image.NEAREST).rotate(-90) for frame in frames][::-1]
    gif = BytesIO()
    frames[0].save(gif, format='GIF', save_all=True, append_images=frames[1:], delay=delay, loop=0)
    return base64.b64encode(gif.getvalue())

def reset_image(imageNum):
    global GIFdata
    try:
        del GIFdata[imageNum]
    except KeyError:
        pass
    window[f'Image{imageNum}'].update(filename=emptyImage, zoom=4)

discCount = 0
validDiscs = []
GIFdata = {}
emptyImage = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAASSURBVDhPY2AYBaNgFIwCCAAABBAAAUy7RlUAAAAASUVORK5CYII='
creeperLootTable = {
  "type": "minecraft:entity",
  "pools": [
    {
      "bonus_rolls": 0.0,
      "entries": [
        {
          "type": "minecraft:item",
          "functions": [
            {
              "add": False,
              "count": {
                "type": "minecraft:uniform",
                "max": 2.0,
                "min": 0.0
              },
              "function": "minecraft:set_count"
            },
            {
              "count": {
                "type": "minecraft:uniform",
                "max": 1.0,
                "min": 0.0
              },
              "enchantment": "minecraft:looting",
              "function": "minecraft:enchanted_count_increase"
            }
          ],
          "name": "minecraft:gunpowder"
        }
      ],
      "rolls": 1.0
    },
    {
      "bonus_rolls": 0.0,
      "conditions": [
        {
          "condition": "minecraft:entity_properties",
          "entity": "attacker",
          "predicate": {
            "type": "#minecraft:skeletons"
          }
        }
      ],
      "entries": [
        {
          "type": "minecraft:tag",
          "expand": True,
            "weight": 1,
          "name": "minecraft:creeper_drop_music_discs"
        }
      ],
      "rolls": 1.0
    }
  ],
  "random_sequence": "minecraft:entities/creeper"
}

sg.theme('Dark Brown 1') # maybe add a theme selector at some point...?
winLayout = [[sg.Push(), sg.Text("Minecraft Custom Music Disc Pack Generator", font="30"), sg.Push()],
             [sg.Push(), sg.Text("Input each disc name, sound file path, and disc texture path. Make sure the disc textures are 16x16."), sg.Push()],
             [sg.Text("Pack name"), sg.Input(expand_x=True, key="PackName")],
             [sg.HorizontalSeparator()],
             [sg.Column(discGuiAddition(), key="discList", scrollable=True, vertical_scroll_only=True, size=(None, 500))],
             [sg.Push(), sg.Button("Add music disc"), sg.VerticalSeparator(), sg.Button("Export"), sg.Button("Import", button_color=("white", "gray")), sg.Push()],
             [sg.Push(), sg.Text("If you find any bugs, please report them to https://github.com/Cobaz-76/minecraftDiscMaker"), sg.Push()]
             ]
window = sg.Window('Disc Pack Generator', winLayout, icon="favicon.ico")

# HOLY CRAP WHY CAN'T PYDUB JUST ACCESS FFMPEG FROM INSIDE THE EXE IT'S NOT THAT HARD MAN FOR THE LOVE OF POATOES
# SHOULDN'T THERE BE A WAY TO JUST TELL IT WHERE IT IS IN THERE?!
# WHY DO NONE OF THE OTHER SOUND LIBRARIES ALLOW FOR MP3s OR SOMETHING DUMB LIKE THAT
# i have like 50 tabs open and no answers. it works here in the ide but it won't after i package it into an exe. unless i put ffmpeg
# into the folder the exe is in. why. why won't it work. it's 1:27 AM. just do what your supposed to please

while True: # the HOLY FRICK MAIN LOOP lol
    event, values = window.read(timeout=50)
    if event != "__TIMEOUT__":
        print(event, values)

    if event == sg.WINDOW_CLOSED: # gracefully close the program
        break
    
    # update gifs
    for key in GIFdata:
        window[f'Image{key}'].update_animation(GIFdata[key], time_between_frames=float(values[f'DiscSettings{key}'].split()[0]) * 50)

    if event == "Add music disc": # add a new disc section
        window.extend_layout(window['discList'], discGuiAddition())
        window['discList'].contents_changed()
        window['discList'].Widget.canvas.yview_moveto(1.0)

    if "RemoveDisc" in event: # remove a disc section
        window[f'DiscEntry{event[10:]}'].update(visible=False)
        validDiscs.remove(event[10:])

    if "SettingsButton" in event:
        settingsWinLayout = [
            [sg.Push(), sg.T("Disc Settings"), sg.Push()],
            [sg.Push(), sg.Column([[sg.T("Frame Time")], [sg.Spin([i for i in range(1,100)], initial_value=int(values[f'DiscSettings{event[14]}'].split()[0]), key=f"FrameRate", size=(2, 1))], [sg.Checkbox("Fade", key="Fade")]]), sg.Push()],
            [sg.Push(), sg.Button("Done"), sg.Push()]
        ]
        
        settingsWindow = sg.Window(f"Disc Settings", settingsWinLayout, modal=True, icon="favicon.ico")
        
        while True:
            Sevent, Svalues = settingsWindow.read()
            print(Sevent, Svalues)
            
            if Sevent == sg.WINDOW_CLOSED or Sevent == "Done":
                break
        settingsWindow.close()
        
        if Svalues['FrameRate'] is None:
            Svalues['FrameRate'] = 1
        if Svalues['Fade'] is None:
            Svalues['Fade'] = False
        window[f"DiscSettings{event[14]}"].update(f"{Svalues["FrameRate"]} {Svalues['Fade']}")
            

    if "Texture" in event: # The input for the disc texture section was updated, so we should try and display the new image
        # first let's access it with pillow and check it's dimensions.
        if os.path.isfile(values[event]):
            tempDiscImage = Image.open(values[event])
            if tempDiscImage.size[0] == 16:
                if tempDiscImage.size[1] == 16:
                    # normal disc texture file
                    try:
                        del GIFdata[event[7]]
                    except KeyError:
                        pass
                    window[f'Image{event[7]}'].update(filename=values[event], zoom=4)
                elif tempDiscImage.size[1] % 16 == 0:
                    # oh hey this is a gif
                    GIFdata[event[7]] = makeGif(tempDiscImage)
                    window[f'Image{event[7]}'].update(filename=GIFdata[event[7]], zoom=1)
                else:
                    reset_image(event[7])
            else:
                reset_image(event[7])
        else:
            reset_image(event[7])

    if event == "Import":
        # should probably open a new window for this
        # whatever the case we can probably yoink details to add to
        pass

    if event == "Export": # it's time to lock in and make the final packs
        # open up a new window here for where we gonna save the files and such
        exportWinLayout = [
            [sg.Push(), sg.T("Input file path for exported packs"), sg.Push()],
            [sg.Input("", expand_x=True, key='savePath'), sg.FolderBrowse("Browse")],
            [sg.Push(), sg.Button("Cancel"), sg.Button("Export")],
            [sg.Multiline("", autoscroll=True, autoscroll_only_at_bottom=True, expand_x=True, key="log", size=(1, 10), write_only=True)]
            ]

        exportWindow = sg.Window("Export Packs", exportWinLayout, modal=True, icon="favicon.ico")

        while True:
            # X is for Xport!
            Xevent, Xvalues = exportWindow.read()

            if Xevent == sg.WINDOW_CLOSED or Xevent == "Cancel":
                break

            if Xevent == "Export":
                if os.path.isdir(Xvalues['savePath']):
                    def log(string, color="white"):
                        global exportWindow
                        exportWindow['log'].update(f"{string}\n", text_color=color, append=True)
                        print(string)
                        window.refresh()
                    try:
                        log('Creating temporary folder\nPreparing zip files')
                        ## setup zipfile for data and resource packs ##
                        soundsJson = {}
                        disc11Json = {"model":{"type":"minecraft:select","property":"minecraft:component","component":"minecraft:jukebox_playable","cases":[],"fallback":{"type":"minecraft:model","model":"minecraft:item/music_disc_11"}}}
                        giveAllDiscsString = ""
                        
                        extraPath = ""
                        while True:
                            try:
                                os.makedirs(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}")
                                break
                            except WindowsError:
                                extraPath += "-"
                        
                        with zipfile.ZipFile(f"{Xvalues['savePath']}/{values['PackName']}-datapack.zip", "w") as datapack:
                            with zipfile.ZipFile(f"{Xvalues['savePath']}/{values['PackName']}-resourcepack.zip", "w") as resourcepack:
                                # add normal pack stuff #
                                datapack.writestr("pack.mcmeta", '{"pack": {"pack_format": 61,"description": "§aAdds custom music discs. Made with Cobaz\'s disc generator."}}')
                                resourcepack.writestr("pack.mcmeta", '{"pack": {"description": "§aAdds custom music discs. Made with Cobaz\'s disc generator.","pack_format": 61}}')
                                
                                ## loop through each disc ##
                                for discNum in validDiscs:
                                    # print and set some basic information
                                    print("")
                                    print("Name:", values[f'Name{discNum}'])
                                    songName = values[f'Name{discNum}'].replace(' ', '_').lower()
                                    print("Song path:", values[f'Song{discNum}'])
                                    print("Texture path:", values[f'Texture{discNum}'])
                                    
                                    log(f'Processing {values[f'Name{discNum}']}')
                                    
                                    # extract data from the sound file
                                    song = AudioSegment.from_file(values[f'Song{discNum}'])
                                    songLength = song.duration_seconds
                                    print(f"Length in seconds: {songLength}")
                                    
                                    # generate the song's json file
                                    datapack.writestr(f"data/custom_discs/jukebox_song/{songName}.json", f'{{"comparator_output": {random.randint(1, 15)}, "description": "{values[f'Name{discNum}']}", "length_in_seconds": {songLength}, "sound_event": {{"sound_id": "custom_discs:music_disc.{songName}"}}}}')
                                    log(f'Created {songName}.json in datapack')
                                    resourcepack.writestr(f"assets/custom_discs/models/item/{songName}.json", f'{{"parent":"minecraft:item/generated","textures":{{"layer0":"custom_discs:item/{songName}"}}}}')
                                    
                                    # save image to resource pack
                                    discImage = Image.open(values[f'Texture{discNum}'])
                                    resourcepack.write(values[f'Texture{discNum}'], f"assets/custom_discs/textures/item/{songName}.png")
                                    log(f"Placed {songName}.png in resource pack")
                                    if discImage.size[0] / discImage.size[1] != 1:
                                        resourcepack.writestr(f"assets/custom_discs/textures/item/{songName}.png.mcmeta", f'{{"animation":{{"frametime":{values[f'DiscSettings{discNum}'].split()[0]}}},"interpolate":{values[f'DiscSettings{discNum}'].split()[1].lower()}}}}}')
                                        log(f"Animated disc texture detected, created {songName}.png.mcmeta")
                                    
                                    # add disc to creeper loot table dict for later
                                    creeperLootTable['pools'][1]['entries'].append({"type": "minecraft:item","weight": 1,"name": "minecraft:music_disc_11","functions": [{"function": "minecraft:set_components","components": {"minecraft:jukebox_playable": {"song": f"infinite_music_discs:{songName}"}}}]})
                                    
                                    # generate the song's give function file and add to the give all discs string
                                    datapack.writestr(f"data/custom_discs/function/give/{songName}.mcfunction", f"give @s minecraft:music_disc_11[minecraft:jukebox_playable='custom_discs:{songName}']")
                                    giveAllDiscsString += f"execute at @s run function custom_discs:give/{songName}\n"
                                    log(f"Created give function for {songName}")
                                    
                                    # add details for sounds.json and music_disc_11.json later
                                    soundsJson[f'music_disc.{songName}'] = {"sounds":[{"name": f"custom_discs:records/{songName}", "stream": True}]}
                                    disc11Json["model"]["cases"].append({"when": f"custom_discs:{songName}","model": {"type": "model","model": f"custom_discs:item/{songName}"}})
                                    
                                    # use a temp file to convert to ogg then drop it into the resource pack
                                    song.export(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}/{songName}.ogg", format="ogg")
                                    resourcepack.write(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}/{songName}.ogg", f"assets/custom_discs/sounds/records/{songName}.ogg")
                                    log(f'Converted {songName} to .ogg')
                                
                                # create sounds.json
                                soundsJson = json.dumps(soundsJson)
                                resourcepack.writestr("assets/custom_discs/sounds.json", soundsJson)
                                log('Created sounds.json')
                                
                                # create the creeper loot table
                                creeperLootTable = json.dumps(creeperLootTable)
                                datapack.writestr("assets/minecraft/loot_table/entities/creeper.json", creeperLootTable)
                                log("Created creeper loot table in creeper.json")
                                
                                # create music_disc_11.json
                                disc11Json = json.dumps(disc11Json)
                                resourcepack.writestr("assets/minecraft/items/music_disc_11.json", disc11Json)
                                log("Created music_disc_11.json")
                                
                                # create give all discs function
                                datapack.writestr("data/custom_discs/function/give_all_discs.mcfunction", giveAllDiscsString)
                                log("Created give all discs function.")
                                
                                # delete the temp folder
                                for fileToRemove in os.listdir(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}"):
                                    os.remove(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}/{fileToRemove}")
                                os.rmdir(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}")
                                log(f'Deleted temp folder')
                            
                            resourcepack.close()
                        datapack.close()
                        log("Successfully created resource and datapack!", "yellow")
                    except Exception as e: # change this to Exception before releasing it on github etc so ppl can tell me what went wrong
                        exportWindow['log'].update(f'{type(e)}: {e}\n', text_color="red", append=True)
                        window.refresh()

                else:
                    exportWindow['log'].update('Error: Invalid path\n', text_color="red", append=True)
                    window.refresh()
        exportWindow.close()

window.close()

# if i live to see pydub actually working when the program is .exe form, imma make some well deserved potato soupimport PySimpleGUI as sg
import os, random, zipfile, json, base64, sys
from PIL import Image
from io import BytesIO
import numpy as np

# can we get pydub to fricken work
if getattr(sys, "frozen", False):
    os.environ["PATH"] = sys._MEIPASS + os.pathsep + os.environ["PATH"] # HOLY CRAP IT ACTULLY WORKS
from pydub import AudioSegment

def discGuiAddition(): # add more rows to our gui, and give them unique ids
    global discCount
    discCount += 1
    validDiscs.append(str(discCount))
    return [
            [sg.pin(
                sg.Column([[sg.Image(emptyImage, key=f"Image{discCount}", zoom=4),
                sg.Column([
                    [sg.Text("Disc Name"), sg.Input(key=f'Name{discCount}', expand_x=True), sg.Input("1 True", visible=False, enable_events=True, key=f"DiscSettings{discCount}"), sg.Button("⚙️", tooltip="Edit animated disc settings for this disc", key=f"SettingsButton{discCount}"), sg.Button("Remove Disc", key=f"RemoveDisc{discCount}", button_color=("white", "red"))],
                    [sg.Text("Song file path"), sg.Input(key=f'Song{discCount}', expand_x=True), sg.FileBrowse("Browse", file_types=(("Sound Files", ".mp3 .wav .flac .ogg"),))],
                    [sg.Text("Disc texture path"), sg.Input(enable_events=True, key=f'Texture{discCount}', expand_x=True), sg.FileBrowse("Browse", file_types=(("PNG files", ".png"),))]
                ], key=f'Inputs{discCount}')], [sg.HorizontalSeparator(key=f"Separator{discCount}")]], key=f"DiscEntry{discCount}"))]]

def makeGif(PILimage, delay=1):
    frames = []
    for frameCount in range(int((PILimage.size[1])/16)):
        currentFrame = PILimage.crop((0, 16*frameCount, 16, 16*(frameCount+1)))
        currentPixels = currentFrame.load()
        tintedPixels = []
        if frameCount % 2 == 0: # for some reason it'll only display the difference from last frame, so we just gonna make it tinted different every frame lol
            for i in range(currentFrame.height):
                l = []
                for j in range(currentFrame.width):
                    px = [value + (1 if value != 255 and value != 0 else 0) for value in currentPixels[i, j]]
                    l.append(px)
                tintedPixels.append(l)
        else:
            for i in range(currentFrame.height):
                l = []
                for j in range(currentFrame.width):
                    px = [value - (1 if value != 0 else 0) for value in currentPixels[i, j]]
                    l.append(px)
                tintedPixels.append(l)
        array = np.array(tintedPixels, dtype=np.uint8)
        frames.append(Image.fromarray(array))
    
    # y tf does it display rotated and reversed? guess we'll just .rotate(-90) and reverse the order
    frames = [frame.resize((64, 64), Image.NEAREST).rotate(-90) for frame in frames][::-1]
    gif = BytesIO()
    frames[0].save(gif, format='GIF', save_all=True, append_images=frames[1:], delay=delay, loop=0)
    return base64.b64encode(gif.getvalue())

def reset_image(imageNum):
    global GIFdata
    try:
        del GIFdata[imageNum]
    except KeyError:
        pass
    window[f'Image{imageNum}'].update(filename=emptyImage, zoom=4)

discCount = 0
validDiscs = []
GIFdata = {}
emptyImage = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAASSURBVDhPY2AYBaNgFIwCCAAABBAAAUy7RlUAAAAASUVORK5CYII='
creeperLootTable = {
  "type": "minecraft:entity",
  "pools": [
    {
      "bonus_rolls": 0.0,
      "entries": [
        {
          "type": "minecraft:item",
          "functions": [
            {
              "add": False,
              "count": {
                "type": "minecraft:uniform",
                "max": 2.0,
                "min": 0.0
              },
              "function": "minecraft:set_count"
            },
            {
              "count": {
                "type": "minecraft:uniform",
                "max": 1.0,
                "min": 0.0
              },
              "enchantment": "minecraft:looting",
              "function": "minecraft:enchanted_count_increase"
            }
          ],
          "name": "minecraft:gunpowder"
        }
      ],
      "rolls": 1.0
    },
    {
      "bonus_rolls": 0.0,
      "conditions": [
        {
          "condition": "minecraft:entity_properties",
          "entity": "attacker",
          "predicate": {
            "type": "#minecraft:skeletons"
          }
        }
      ],
      "entries": [
        {
          "type": "minecraft:tag",
          "expand": True,
            "weight": 1,
          "name": "minecraft:creeper_drop_music_discs"
        }
      ],
      "rolls": 1.0
    }
  ],
  "random_sequence": "minecraft:entities/creeper"
}

sg.theme('Dark Brown 1') # maybe add a theme selector at some point...?
winLayout = [[sg.Push(), sg.Text("Minecraft Custom Music Disc Pack Generator", font="30"), sg.Push()],
             [sg.Push(), sg.Text("Input each disc name, sound file path, and disc texture path. Make sure the disc textures are 16x16."), sg.Push()],
             [sg.Text("Pack name"), sg.Input(expand_x=True, key="PackName")],
             [sg.HorizontalSeparator()],
             [sg.Column(discGuiAddition(), key="discList", scrollable=True, vertical_scroll_only=True, size=(None, 500))],
             [sg.Push(), sg.Button("Add music disc"), sg.VerticalSeparator(), sg.Button("Export"), sg.Button("Import", button_color=("white", "gray")), sg.Push()],
             [sg.Push(), sg.Text("If you find any bugs, please report them to https://github.com/Cobaz-76/minecraftDiscMaker"), sg.Push()]
             ]
window = sg.Window('Disc Pack Generator', winLayout, icon="favicon.ico")

# HOLY CRAP WHY CAN'T PYDUB JUST ACCESS FFMPEG FROM INSIDE THE EXE IT'S NOT THAT HARD MAN FOR THE LOVE OF POATOES
# SHOULDN'T THERE BE A WAY TO JUST TELL IT WHERE IT IS IN THERE?!
# WHY DO NONE OF THE OTHER SOUND LIBRARIES ALLOW FOR MP3s OR SOMETHING DUMB LIKE THAT
# i have like 50 tabs open and no answers. it works here in the ide but it won't after i package it into an exe. unless i put ffmpeg
# into the folder the exe is in. why. why won't it work. it's 1:27 AM. just do what your supposed to please

while True: # the HOLY FRICK MAIN LOOP lol
    event, values = window.read(timeout=50)
    if event != "__TIMEOUT__":
        print(event, values)

    if event == sg.WINDOW_CLOSED: # gracefully close the program
        break
    
    # update gifs
    for key in GIFdata:
        window[f'Image{key}'].update_animation(GIFdata[key], time_between_frames=float(values[f'DiscSettings{key}'].split()[0]) * 50)

    if event == "Add music disc": # add a new disc section
        window.extend_layout(window['discList'], discGuiAddition())
        window['discList'].contents_changed()
        window['discList'].Widget.canvas.yview_moveto(1.0)

    if "RemoveDisc" in event: # remove a disc section
        window[f'DiscEntry{event[10:]}'].update(visible=False)
        validDiscs.remove(event[10:])

    if "SettingsButton" in event:
        settingsWinLayout = [
            [sg.Push(), sg.T("Disc Settings"), sg.Push()],
            [sg.Push(), sg.Column([[sg.T("Frame Time")], [sg.Spin([i for i in range(1,100)], initial_value=int(values[f'DiscSettings{event[14]}'].split()[0]), key=f"FrameRate", size=(2, 1))], [sg.Checkbox("Fade", key="Fade")]]), sg.Push()],
            [sg.Push(), sg.Button("Done"), sg.Push()]
        ]
        
        settingsWindow = sg.Window(f"Disc Settings", settingsWinLayout, modal=True, icon="favicon.ico")
        
        while True:
            Sevent, Svalues = settingsWindow.read()
            print(Sevent, Svalues)
            
            if Sevent == sg.WINDOW_CLOSED or Sevent == "Done":
                break
        settingsWindow.close()
        
        window[f"DiscSettings{event[14]}"].update(f"{Svalues["FrameRate"]} {Svalues['Fade']}")
            

    if "Texture" in event: # The input for the disc texture section was updated, so we should try and display the new image
        # first let's access it with pillow and check it's dimensions.
        if os.path.isfile(values[event]):
            tempDiscImage = Image.open(values[event])
            if tempDiscImage.size[0] == 16:
                if tempDiscImage.size[1] == 16:
                    # normal disc texture file
                    try:
                        del GIFdata[event[7]]
                    except KeyError:
                        pass
                    window[f'Image{event[7]}'].update(filename=values[event], zoom=4)
                elif tempDiscImage.size[1] % 16 == 0:
                    # oh hey this is a gif
                    GIFdata[event[7]] = makeGif(tempDiscImage)
                    window[f'Image{event[7]}'].update(filename=GIFdata[event[7]], zoom=1)
                else:
                    reset_image(event[7])
            else:
                reset_image(event[7])
        else:
            reset_image(event[7])

    if event == "Import":
        # should probably open a new window for this
        # whatever the case we can probably yoink details to add to
        pass

    if event == "Export": # it's time to lock in and make the final packs
        # open up a new window here for where we gonna save the files and such
        exportWinLayout = [
            [sg.Push(), sg.T("Input file path for exported packs"), sg.Push()],
            [sg.Input("", expand_x=True, key='savePath'), sg.FolderBrowse("Browse")],
            [sg.Push(), sg.Button("Cancel"), sg.Button("Export")],
            [sg.Multiline("", autoscroll=True, autoscroll_only_at_bottom=True, expand_x=True, key="log", size=(1, 10), write_only=True)]
            ]

        exportWindow = sg.Window("Export Packs", exportWinLayout, modal=True, icon="favicon.ico")

        while True:
            # X is for Xport!
            Xevent, Xvalues = exportWindow.read()

            if Xevent == sg.WINDOW_CLOSED or Xevent == "Cancel":
                break

            if Xevent == "Export":
                if os.path.isdir(Xvalues['savePath']):
                    def log(string, color="white"):
                        global exportWindow
                        exportWindow['log'].update(f"{string}\n", text_color=color, append=True)
                        print(string)
                        window.refresh()
                    try:
                        log('Creating temporary folder\nPreparing zip files')
                        ## setup zipfile for data and resource packs ##
                        soundsJson = {}
                        disc11Json = {"model":{"type":"minecraft:select","property":"minecraft:component","component":"minecraft:jukebox_playable","cases":[],"fallback":{"type":"minecraft:model","model":"minecraft:item/music_disc_11"}}}
                        giveAllDiscsString = ""
                        
                        extraPath = ""
                        while True:
                            try:
                                os.makedirs(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}")
                                break
                            except WindowsError:
                                extraPath += "-"
                        
                        with zipfile.ZipFile(f"{Xvalues['savePath']}/{values['PackName']}-datapack.zip", "w") as datapack:
                            with zipfile.ZipFile(f"{Xvalues['savePath']}/{values['PackName']}-resourcepack.zip", "w") as resourcepack:
                                # add normal pack stuff #
                                datapack.writestr("pack.mcmeta", '{"pack": {"pack_format": 61,"description": "§aAdds custom music discs. Made with Cobaz\'s disc generator."}}')
                                resourcepack.writestr("pack.mcmeta", '{"pack": {"description": "§aAdds custom music discs. Made with Cobaz\'s disc generator.","pack_format": 61}}')
                                
                                ## loop through each disc ##
                                for discNum in validDiscs:
                                    # print and set some basic information
                                    print("")
                                    print("Name:", values[f'Name{discNum}'])
                                    songName = values[f'Name{discNum}'].replace(' ', '_').lower()
                                    print("Song path:", values[f'Song{discNum}'])
                                    print("Texture path:", values[f'Texture{discNum}'])
                                    
                                    log(f'Processing {values[f'Name{discNum}']}')
                                    
                                    # extract data from the sound file
                                    song = AudioSegment.from_file(values[f'Song{discNum}'])
                                    songLength = song.duration_seconds
                                    print(f"Length in seconds: {songLength}")
                                    
                                    # generate the song's json file
                                    datapack.writestr(f"data/custom_discs/jukebox_song/{songName}.json", f'{{"comparator_output": {random.randint(1, 15)}, "description": "{values[f'Name{discNum}']}", "length_in_seconds": {songLength}, "sound_event": {{"sound_id": "custom_discs:music_disc.{songName}"}}}}')
                                    log(f'Created {songName}.json in datapack')
                                    resourcepack.writestr(f"assets/custom_discs/models/item/{songName}.json", f'{{"parent":"minecraft:item/generated","textures":{{"layer0":"custom_discs:item/{songName}"}}}}')
                                    
                                    # save image to resource pack
                                    discImage = Image.open(values[f'Texture{discNum}'])
                                    resourcepack.write(values[f'Texture{discNum}'], f"assets/custom_discs/textures/item/{songName}.png")
                                    log(f"Placed {songName}.png in resource pack")
                                    if discImage.size[0] / discImage.size[1] != 1:
                                        resourcepack.writestr(f"assets/custom_discs/textures/item/{songName}.png.mcmeta", f'{{"animation":{{"frametime":{values[f'DiscSettings{discNum}'].split()[0]}}},"interpolate":{values[f'DiscSettings{discNum}'].split()[1].lower()}}}}}')
                                        log(f"Animated disc texture detected, created {songName}.png.mcmeta")
                                    
                                    # add disc to creeper loot table dict for later
                                    creeperLootTable['pools'][1]['entries'].append({"type": "minecraft:item","weight": 1,"name": "minecraft:music_disc_11","functions": [{"function": "minecraft:set_components","components": {"minecraft:jukebox_playable": {"song": f"infinite_music_discs:{songName}"}}}]})
                                    
                                    # generate the song's give function file and add to the give all discs string
                                    datapack.writestr(f"data/custom_discs/function/give/{songName}.mcfunction", f"give @s minecraft:music_disc_11[minecraft:jukebox_playable='custom_discs:{songName}']")
                                    giveAllDiscsString += f"execute at @s run function custom_discs:give/{songName}\n"
                                    log(f"Created give function for {songName}")
                                    
                                    # add details for sounds.json and music_disc_11.json later
                                    soundsJson[f'music_disc.{songName}'] = {"sounds":[{"name": f"custom_discs:records/{songName}", "stream": True}]}
                                    disc11Json["model"]["cases"].append({"when": f"custom_discs:{songName}","model": {"type": "model","model": f"custom_discs:item/{songName}"}})
                                    
                                    # use a temp file to convert to ogg then drop it into the resource pack
                                    song.export(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}/{songName}.ogg", format="ogg")
                                    resourcepack.write(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}/{songName}.ogg", f"assets/custom_discs/sounds/records/{songName}.ogg")
                                    log(f'Converted {songName} to .ogg')
                                
                                # create sounds.json
                                soundsJson = json.dumps(soundsJson)
                                resourcepack.writestr("assets/custom_discs/sounds.json", soundsJson)
                                log('Created sounds.json')
                                
                                # create the creeper loot table
                                creeperLootTable = json.dumps(creeperLootTable)
                                datapack.writestr("assets/minecraft/loot_table/entities/creeper.json", creeperLootTable)
                                log("Created creeper loot table in creeper.json")
                                
                                # create music_disc_11.json
                                disc11Json = json.dumps(disc11Json)
                                resourcepack.writestr("assets/minecraft/items/music_disc_11.json", disc11Json)
                                log("Created music_disc_11.json")
                                
                                # create give all discs function
                                datapack.writestr("data/custom_discs/function/give_all_discs.mcfunction", giveAllDiscsString)
                                log("Created give all discs function.")
                                
                                # delete the temp folder
                                for fileToRemove in os.listdir(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}"):
                                    os.remove(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}/{fileToRemove}")
                                os.rmdir(f"{Xvalues['savePath']}/customDiscTempDir{extraPath}")
                                log(f'Deleted temp folder')
                            
                            resourcepack.close()
                        datapack.close()
                        log("Successfully created resource and datapack!", "yellow")
                    except Exception as e: # change this to Exception before releasing it on github etc so ppl can tell me what went wrong
                        exportWindow['log'].update(f'{type(e)}: {e}\n', text_color="red", append=True)
                        window.refresh()

                else:
                    exportWindow['log'].update('Error: Invalid path\n', text_color="red", append=True)
                    window.refresh()
        exportWindow.close()

window.close()

# if i live to see pydub actually working when the program is .exe form, imma make some well deserved potato soup
