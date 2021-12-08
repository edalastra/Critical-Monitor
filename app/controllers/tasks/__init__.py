import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from app.models.Inference import Inference


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=, trigger="interval", seconds=60)
# scheduler.start()

# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())