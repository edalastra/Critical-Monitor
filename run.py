from app import app, socketio

if __name__ == '__main__':
    socketio.run(app)
    #app.run(host='localhost', port=5000, debug=True)