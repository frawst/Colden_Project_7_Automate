import os
import re
import glob
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

def process_idstv_file(idstv_file):
    while True:
        try:
            with open(idstv_file, 'r') as file:
                content = file.read()

            content = re.sub(r'(<Name>).*?W_(.*?</Name>)', r'\1\2', content)
            content = re.sub(r'(<Name>).*?C_(.*?</Name>)', r'\1\2', content)
            content = re.sub(r'(<Name>).*?HSS_(.*?</Name>)', r'\1\2', content)
            content = re.sub(r'<RemnantLocation>.*?</RemnantLocation>', '<RemnantLocation>v</RemnantLocation>', content)

            with open(idstv_file, 'w') as file:
                file.write(content)
            break  
        except PermissionError:
            print(f"Waiting for file {idstv_file} to be released")
            time.sleep(1)  

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        file = event.src_path
        if file.endswith(".nc1"):
            remove_SI_block(file)
        elif file.endswith(".idstv"):
            process_idstv_file(file)

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()

    folders_to_track = ['N:\\Production\\PEDDINGHAUS IDSTV\\W8722', 
                        'N:\\Production\\PEDDINGHAUS IDSTV\\W8733',
                        'N:\\Production\\PEDDINGHAUS IDSTV\\W8736',
                        'N:\\Production\\PEDDINGHAUS IDSTV\\W8745',
                        ]
    for folder in folders_to_track:
        observer.schedule(event_handler, folder, recursive=True)

    observer.start()

    # Keep the script running indefinitely
    while True:
        time.sleep(1)
