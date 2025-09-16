# Redis Configuration untuk Fisheries System
import redis 
import json
import os
from functools import wraps

class RedisManager:
    """
    Redis Manager Class untuk handle semua operasi Redis
    """
    
    def __init__(self):
        """
        Inisiasi koneksi ke Redis
        Fungsi: Setup connection ke Redis server
        """
        # Redis connection settings
        self.host = os.environ.get('REDIS_HOST', 'localhost')  # Redis server host
        self.port = int(os.environ.get('REDIS_PORT', 6379))    # Redis port (default 6379)
        self.password = os.environ.get('REDIS_PASSWORD', 'fisheries2024')  # Redis password
        self.db = int(os.environ.get('REDIS_DB', 0))           # Redis database number (0-15)
        
        # Create Redis connection
        self.redis_client = redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            decode_responses=True  # Auto-decode bytes ke string
        )
        
        # Test connection
        try:
            self.redis_client.ping()
            print(f"[OK] Redis connected: {self.host}:{self.port}")
        except redis.ConnectionError as e:
            print(f"[ERROR] Redis connection failed: {e}")
            self.redis_client = None
    
    def set_data(self, key, value, expire_time=None):
        """
        Simpan data ke Redis
        
        Args:
            key (str): Key untuk data
            value (any): Data yang akan disimpan (akan diconvert ke JSON)
            expire_time (int): Waktu expire dalam detik (None = permanent)
        
        Fungsi: Simpan data dengan auto-serialization ke JSON
        """
        if not self.redis_client:
            return False
            
        try:
            # Convert data ke JSON string
            json_value = json.dumps(value) if not isinstance(value, str) else value
            
            # Set data dengan expire time
            if expire_time:
                return self.redis_client.setex(key, expire_time, json_value)
            else:
                return self.redis_client.set(key, json_value)
                
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def get_data(self, key):
        """
        Ambil data dari Redis
        
        Args:
            key (str): Key untuk data yang mau diambil
            
        Returns:
            any: Data yang diambil (auto-parse dari JSON)
            
        Fungsi: Ambil data dengan auto-deserialization dari JSON
        """
        if not self.redis_client:
            return None
            
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
                
            # Try parse as JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    def delete_data(self, key):
        """
        Hapus data dari Redis
        
        Args:
            key (str): Key yang mau dihapus
            
        Fungsi: Delete data dari Redis
        """
        if not self.redis_client:
            return False
            
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    def get_all_keys(self, pattern="*"):
        """
        Get semua keys dengan pattern
        
        Args:
            pattern (str): Pattern untuk filter keys (default: semua)
            
        Fungsi: List semua keys yang match pattern
        """
        if not self.redis_client:
            return []
            
        try:
            return self.redis_client.keys(pattern)
        except Exception as e:
            print(f"Redis KEYS error: {e}")
            return []
    
    def increment_counter(self, key, increment=1):
        """
        Increment counter value
        
        Args:
            key (str): Key untuk counter
            increment (int): Jumlah increment (default 1)
            
        Fungsi: Menambah nilai counter, useful untuk statistics
        """
        if not self.redis_client:
            return 0
            
        try:
            return self.redis_client.incrby(key, increment)
        except Exception as e:
            print(f"Redis INCR error: {e}")
            return 0
    
    def set_hash(self, hash_key, field, value):
        """
        Set hash field value
        
        Args:
            hash_key (str): Hash key name
            field (str): Field name dalam hash
            value (any): Value untuk field
            
        Fungsi: Simpan data dalam format hash (seperti object/dictionary)
        """
        if not self.redis_client:
            return False
            
        try:
            json_value = json.dumps(value) if not isinstance(value, str) else value
            return self.redis_client.hset(hash_key, field, json_value)
        except Exception as e:
            print(f"Redis HSET error: {e}")
            return False
    
    def get_hash(self, hash_key, field=None):
        """
        Get hash field value atau semua hash
        
        Args:
            hash_key (str): Hash key name
            field (str): Field name (None = get all fields)
            
        Fungsi: Ambil data dari hash structure
        """
        if not self.redis_client:
            return None
            
        try:
            if field:
                # Get specific field
                value = self.redis_client.hget(hash_key, field)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
            else:
                # Get all hash fields
                hash_data = self.redis_client.hgetall(hash_key)
                result = {}
                for key, value in hash_data.items():
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        result[key] = value
                return result
                
        except Exception as e:
            print(f"Redis HGET error: {e}")
            return None

# Global Redis instance
redis_manager = RedisManager()

def cache_result(expire_time=300):
    """
    Decorator untuk cache function results ke Redis
    
    Args:
        expire_time (int): Cache expire time dalam detik (default 5 menit)
        
    Fungsi: Decorator yang otomatis cache hasil function ke Redis
    Usage:
        @cache_result(expire_time=600)  # Cache 10 menit
        def expensive_function():
            return "hasil yang membutuhkan waktu lama"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key dari function name dan arguments
            cache_key = f"cache:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try get from cache first
            cached_result = redis_manager.get_data(cache_key)
            if cached_result is not None:
                print(f"Cache HIT: {func.__name__}")
                return cached_result
            
            # Execute function dan cache result
            result = func(*args, **kwargs)
            redis_manager.set_data(cache_key, result, expire_time)
            print(f"Cache SET: {func.__name__}")
            return result
            
        return wrapper
    return decorator
