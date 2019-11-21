from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import time
import subprocess


class KWHandler(PatternMatchingEventHandler):
    patterns = ['*.sh']

    def process(self, event):
        print(f'Running {event.src_path}')
        p = subprocess.Popen('python3 /home/dominouzu/.kappc/app/app.py', shell=True)
        # p.communicate()

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)


if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(KWHandler(), path=args[0] if args else '.')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
