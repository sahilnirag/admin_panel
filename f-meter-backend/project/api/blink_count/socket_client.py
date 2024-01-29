import asyncio
import socketio
import threading

my_local = threading.local()
sio = socketio.AsyncClient(logger=False)


@sio.event
async def connect():
    print('connection established')
    await sio.emit('getNotification', my_local.send_data)
    print('data send to socket', my_local.send_data)


@sio.event
async def getNotification(data):
    print('message received form server ', data)


    
    
    if data.get("disconnect"):
        await sio.disconnect()


@sio.event
async def disconnect():
    print('disconnected from server')



async def main():
    await sio.connect("http://0.0.0.0:5500")
    await sio.wait()
    await sio.wait()


def send_data(data):
    my_local.send_data = data
    try:
        asyncio.run(main())
    except:
        pass
    return True, my_local.send_data


if __name__ == '__main__':
    send_data({'id': 46, 'user': {'id': 289, 'email': 'work.bhupender@gmail.com', 'first_name': 'Bhupender', 'last_name': 'Jangra'}, 'symbol': 'A', 'cond_name': 'cci', 'cond_value': 133, 'cond_check': 'crossingdown', 'web_hook_url': None, 'option': 'once', 'action_method': 'popup', 'is_mail': False, 'is_popup': True, 'is_web_hook_url': False, 'time_stamp': 1655376840.0, 'expiry_date': '2022-06-16T10:54:00+00:00', 'alert_name': 'Testing alert', 'alert_msg': 'Message will go here', 'is_notify': True, 'calculated_value': 10})
