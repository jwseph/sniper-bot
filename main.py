import threading
import sniper

# sniper.run()
threading.Thread(target=sniper.run, daemon=True).start()


import chat
app = chat.app

print('hello UWUW UW UWU')