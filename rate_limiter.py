import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_requests=1, time_window=1):
        """
        Simple rate limiter
        max_requests: Maximum requests allowed in time_window
        time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
    
    def is_allowed(self, key="default"):
        """Check if request is allowed for given key"""
        now = time.time()
        request_times = self.requests[key]
        
        # Remove old requests outside time window
        while request_times and request_times[0] <= now - self.time_window:
            request_times.popleft()
        
        # Check if we can make another request
        if len(request_times) < self.max_requests:
            request_times.append(now)
            return True
        
        return False
    
    def wait_time(self, key="default"):
        """Get time to wait before next request is allowed"""
        now = time.time()
        request_times = self.requests[key]
        
        if not request_times:
            return 0
        
        oldest_request = request_times[0]
        wait_time = max(0, self.time_window - (now - oldest_request))
        return wait_time

# Usage example for Bedrock Agent
bedrock_rate_limiter = RateLimiter(max_requests=1, time_window=2)  # 1 request per 2 seconds
