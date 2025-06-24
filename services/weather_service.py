# services/weather_service.py
import threading
import time
from queue import Queue
import logging
from config import Config

class WeatherService:
    """Service for fetching and processing weather data."""
    
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.request_queue = Queue()
        self.results = {}
        self.worker_thread = None
        self.last_request_time = 0
        self.rate_limit_delay = 60 / Config.MAX_REQUESTS_PER_MINUTE  # seconds
        
    def start_worker(self):
        """Start the worker thread to process weather requests."""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(
                target=self._process_requests, 
                daemon=True
            )
            self.worker_thread.start()
            
    def request_forecast(self, zip_code, callback=None):
        """
        Queue a request for weather forecast by zip code.
        
        Args:
            zip_code (str): The ZIP code to get forecast for
            callback (callable, optional): Function to call with results
        """
        request_id = f"{zip_code}_{time.time()}"
        self.request_queue.put((request_id, zip_code, callback))
        self.start_worker()
        return request_id
        
    def _process_requests(self):
        """Worker thread to process queued weather requests."""
        while True:
            try:
                request_id, zip_code, callback = self.request_queue.get(timeout=1)
                
                # Apply rate limiting
                time_since_last = time.time() - self.last_request_time
                if time_since_last < self.rate_limit_delay:
                    time.sleep(self.rate_limit_delay - time_since_last)
                
                result = self._fetch_forecast(zip_code)
                self.results[request_id] = result
                
                if callback:
                    callback(result)
                    
                self.last_request_time = time.time()
                self.request_queue.task_done()
                
            except queue.Empty:
                # No more requests in queue
                pass
                
            except Exception as e:
                logging.error(f"Error processing weather request: {e}", exc_info=True)
                
    def _fetch_forecast(self, zip_code):
        """Fetch forecast data from the weather API."""
        # Implementation with proper error handling and timeouts
