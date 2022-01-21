import threading
import sniper
import chat

# sniper.run( )
threading.Thread(target=sniper.run, daemon=True).start()

print('hello UWUW UW UWU')


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(chat.app, host='0.0.0.0', port=80)