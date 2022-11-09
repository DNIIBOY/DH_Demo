import threading
import time

response = None


def get_response():
    global response
    response = input("Do you wish to reconnect? ")
    print('As you wish')


thread = threading.Thread(target=get_response, daemon=True)
thread.start()
time.sleep(4)
thread.join(2)

if response is None:
    print('Exiting')
