from app import app, socketio

if __name__ == '__main__':
    socketio.run(app, port=5000, host='0.0.0.0')
    #app.run(host='localhost', port=5000, debug=True)