from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from .jobs import scheduled_dispatch, wb_update_prices_auto, wb_synchronize_orders_with_ozon

def start():
	
	scheduler = BackgroundScheduler(max_instances=1)
	#scheduler = BlockingScheduler()#blocks all the process
	#scheduler.add_job(scheduled_dispatch, 'interval', seconds=10)
	#updates prices at wb every 6 hours. Otherwize wb reduces prices on its own
	#scheduler.add_job(wb_update_prices_auto, 'interval', hours=2)
	#receives list of orders from wb every hour & synchronizes erms db remainders & remainders at ozon
	#scheduler.add_job(wb_synchronize_orders_with_ozon, 'interval', minutes=5, max_instances=1)
	scheduler.add_job(wb_synchronize_orders_with_ozon, 'interval', minutes=5)
	#scheduler.add_job(scheduled_dispatch, 'interval', minutes=10)
	#scheduler.add_job(scheduled_dispatch, 'interval', seconds=5)
	scheduler.start()
	