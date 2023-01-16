import socketio
from flask import Flask
import time



sio = socketio.Server(async_mode='threading', cors_allowed_origins="*")
app = Flask(__name__)

app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

rooms =  {}

@sio.on("joinRoom")
def joinRoom(sid, data):
    room = int(data["room"])
    roomString = str(room)
    if type(room) != int:
        sio.emit("invalidRoom", "room must be a number")
        return
    name = data["name"]
    print("joinRoom")
    if room in rooms:
        for client in rooms[roomString]:
            if sid in client:
                sio.emit("clientInRoom", "in room")
            else:
                rooms[roomString].append([sid, name])
    else:
        rooms[roomString] = [[sid, name]]  
    sio.enter_room(sid, room)
    sio.emit("joinRoom", {"room":room, "names": rooms[roomString]}, room=room)
    print(rooms)

@sio.on("addTimer")
def addTimer(sid, data):
    print("addTimer")
    print(data)
    sio.emit("addTimer", {"data":data["timer"]}, room=int(data["room"]))

@sio.on("resetRoom")
def resetRoom(sid, data):
    print("resetRoom")
    print(data)
    sio.emit("resetRoom", {}, room=data["room"])

@sio.on("startRoom")
def startRoom(sid, data):
    print(data)
    print("startRoom")
    room = int(data["room"])
    data["timer"]["startTime"] = data["startTime"]
    print(data["timer"])
    data["timer"]["status"] = "started"
    sio.emit("startRoom", {"startTime": data["startTime"], "timerid":int(data["timer"]["id"]), "timername":data["timer"]["name"], "timer":data["timer"], "listElement":data["listElement"]},  room=room)

@sio.on("stopRoom")
def stopRoom(sid, data):
    room = int(data["room"])
    print("stopRoom")
    print(data)
    sio.emit("stopRoom", {"stopTime": data["stopTime"], "timer":data["timer"]}, room=room)

@sio.on("leaveRoom")
def leaveRoom(sid, data):
    room = int(data["room"])
    roomString = str(room)
    print("leaveRoom")
    print(data)
    sio.leave_room(sid, data["room"])
    sio.emit("leaveRoomClient", data["room"])
    for person in rooms[roomString]:
        if sid in person:
            rooms[roomString].remove(person)
    sio.emit("leaveRoom", {"rooms":rooms[roomString]}, room=room)
    print(rooms[roomString])
@sio.event
def connect(sid, environ, auth):
    print("connect ", sid)

#run the server
if __name__ == '__main__':
    app.run()