bind = "0.0.0.0:5004"
workers = 1  # 512MB RAM için worker sayısını azalttık (2'den 1'e)
worker_class = "sync"
worker_connections = 500  # Connection sayısını azalttık (1000'den 500'e)
max_requests = 500  # Request limit'i azalttık (1000'den 500'e)
max_requests_jitter = 50  # Jitter'ı azalttık (100'den 50'ye)
timeout = 30
keepalive = 2
preload_app = True
worker_memory_limit = 400 * 1024 * 1024  # 400MB worker memory limit

# Memory optimization settings
max_worker_memory = 400  # MB - worker restarts if exceeds
graceful_timeout = 10  # Graceful shutdown timeout
worker_tmp_dir = "/dev/shm"  # Use memory for temp files if available
