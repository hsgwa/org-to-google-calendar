from script.event_manager import EventManager
import json

if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    event_manager = EventManager(config)
    event_manager.clear()
    event_manager.update()
