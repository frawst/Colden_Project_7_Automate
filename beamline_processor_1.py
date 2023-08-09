import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# remove_SI_block function is used to remove the SI block from the .nc1 file, thus removing unwanted scribing information from the .nc1 file
def remove_SI_block(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    new_lines = []
    skip = False
    for line in lines:
        if line.strip().startswith("SI"):
            skip = True
        elif len(line.strip()) == 2 and not line.strip().startswith('  '):
            skip = False
        if not skip:
            new_lines.append(line)

    with open(filepath, 'w') as file:
        file.writelines(new_lines)
#  process_idstv_file function is used to process the .idstv file, thus removing unwanted information from the .idstv file
def process_idstv_file(idstv_file):
    while True:
        try:
            with open(idstv_file, 'r') as file:
                content = file.read()

            # Existing processing
            content = re.sub(r'(<Name>).*?W_(.*?</Name>)', r'\1\2', content)
            content = re.sub(r'(<Name>).*?C_(.*?</Name>)', r'\1\2', content)
            content = re.sub(r'(<Name>).*?HSS_(.*?</Name>)', r'\1\2', content)
            content = re.sub(r'(<Name>).*?L_(.*?</Name>)', r'\1\2', content)
            content = re.sub(r'<RemnantLocation>.*?</RemnantLocation>', '<RemnantLocation>v</RemnantLocation>', content)

            # Trim the first 10 characters for the specified tags only if content is 25+ characters long
            for tag in ['Filename', 'DrawingIdentification', 'PieceIdentification']:
                pattern = fr'(<{tag}>)(.{{25,}})(</{tag}>)'
                content = re.sub(pattern, lambda m: m.group(1) + m.group(2)[10:] + m.group(3), content)

            with open(idstv_file, 'w') as file:
                file.write(content)
            break  
        except PermissionError:
            print(f"Waiting for file {idstv_file} to be released")
            time.sleep(1)



#  process_and_rename_file function checks the lines 4 and 5 
#  of the .nc1 file and if the length of the lines is greater than 25 characters, it removes the first 12 characters of the lines,
#  which include the 2 spaces and the 10 characters of the filename
def process_and_rename_file(file_path):
    if not os.path.exists(file_path):
        return

    filename = os.path.basename(file_path)
    directory = os.path.dirname(file_path)
    
    if file_path.endswith(".nc1") and len(filename) >= 25:
        new_file_path = os.path.join(directory, filename[10:])
        
        with open(file_path, "r") as file_obj:
            lines = file_obj.readlines()

                # Modify lines 4 and 5 based on their length
        if len(lines) >= 5:  # Ensure the file has at least 5 lines to avoid index errors
            for i in [3, 4]:  # Lines 4 and 5 have indices 3 and 4
                if len(lines[i].strip()) >= 25:
                    lines[i] = lines[i][12:]


        with open(file_path, "w") as file_obj:
            file_obj.writelines(lines)

        os.rename(file_path, new_file_path)
        print(f"{filename} has been modified and saved as {filename[10:]}.")


class CombinedHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        file = event.src_path
        if file.endswith(".nc1"):
            remove_SI_block(file)
        elif file.endswith(".idstv"):
            process_idstv_file(file)

    def on_modified(self, event):
        if not event.is_directory:
            process_and_rename_file(event.src_path)

if __name__ == "__main__":
    event_handler = CombinedHandler()
    observer = Observer()

    folders_to_track = ['N:\\Production\\PEDDINGHAUS IDSTV\\W8722', 
                        'N:\\Production\\PEDDINGHAUS IDSTV\\W8733',
                        'N:\\Production\\PEDDINGHAUS IDSTV\\W8736',
                        'N:\\Production\\PEDDINGHAUS IDSTV\\W8745',
                        ]

    for folder in folders_to_track:
        if not os.path.exists(folder):
            print(f"ERROR: Cannot access path {folder}")
            continue
        observer.schedule(event_handler, folder, recursive=True)

    print("Waiting for 6 seconds before starting monitoring...")
    time.sleep(6)

    observer.start()
    print(f"Monitoring started on folders: {', '.join(folders_to_track)}...")

    # Keep the script running indefinitely
    while True:
        time.sleep(1)
