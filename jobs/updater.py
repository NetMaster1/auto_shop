from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import scheduled_dispatch, wb_update_prices_auto, wb_synchronize_orders_with_ozon

def start():
	scheduler = BackgroundScheduler()
	scheduler.add_job(wb_update_prices_auto, 'interval', hours=6)
	#scheduler.add_job(wb_synchronize_orders_with_ozon, 'interval', hours=1)
	#scheduler.add_job(scheduled_dispatch, 'interval', seconds=3)
	#scheduler.add_job(scheduled_dispatch, 'interval', minutes=10)
	#scheduler.add_job(scheduled_dispatch, 'interval', seconds=5)
	scheduler.start()