import socketio
from aiohttp import web
import ssl
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

app = web.Application()

sio.attach(app)


async def index(request):
    return web.Response(text="Hello", content_type='text/html')


@sio.on('getNotification')
async def print_message(sid, message):
    print("Server message", message)
    
    await sio.emit(
        "getNotification", {
            "message": "message received.",
            "sid": sid,
            "msg": message,
            "disconnect": False
        })


@sio.on('connect')
async def connect(sid, message):
    await sio.emit("getNotification", {"message": "Welcome", "sid": sid, "disconnect": False})


app.router.add_get('/', index)


if __name__ == '__main__':
    web.run_app(app, port=5000, host="0.0.0.0")
