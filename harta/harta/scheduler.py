from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from django.conf import settings
from maps.views import aula_scheduler, primaria_scheduler, cinema_city_scheduler, teatru_scheduler
from apscheduler.executors.pool import ProcessPoolExecutor
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


executors = {
    'default': ProcessPoolExecutor(5)
}
def start():
    executors = {
        'default': ThreadPoolExecutor(20)
    }
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE, executors=executors)
    
    scheduler.add_job(aula_scheduler, 'interval', hours=24, id='extract_aula')
    scheduler.add_job(primaria_scheduler, 'interval', hours=24, id='extract_primaria')
    scheduler.add_job(cinema_city_scheduler, 'interval', hours=12, id='extract_cinema_city')
    scheduler.add_job(teatru_scheduler, 'interval', hours=24, id='extract_teatru')
    
    scheduler.start()
    logger.info("Scheduler has been started")