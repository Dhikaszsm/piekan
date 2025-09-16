# Test Redis connection dari Python
import redis
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_redis_connection():
    """
    Test Redis connection step by step
    Fungsi: Verify Redis connection dari Python ke WSL Ubuntu
    """
    print("🔍 Testing Redis Connection...")
    print("=" * 50)
    
    # Get Redis settings dari .env
    host = os.environ.get('REDIS_HOST', '127.0.0.1')
    port = int(os.environ.get('REDIS_PORT', 6379))
    password = os.environ.get('REDIS_PASSWORD', 'fisheries2024')
    
    print(f"📍 Host: {host}")
    print(f"🚪 Port: {port}")
    print(f"🔑 Password: {password}")
    print()
    
    try:
        # Test connection
        print("1️⃣ Creating Redis connection...")
        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=0,
            decode_responses=True  # Auto decode bytes to string
        )
        
        # Test ping
        print("2️⃣ Testing PING...")
        result = r.ping()
        print(f"   Result: {result}")  # Should be True
        
        # Test SET operation
        print("3️⃣ Testing SET operation...")
        r.set('fisheries:test', 'Connection successful!')
        print("   ✅ SET successful")
        
        # Test GET operation
        print("4️⃣ Testing GET operation...")
        value = r.get('fisheries:test')
        print(f"   Retrieved: {value}")
        
        # Test counter
        print("5️⃣ Testing COUNTER operations...")
        counter = r.incr('fisheries:test_counter')
        print(f"   Counter value: {counter}")
        
        # Test JSON operations
        print("6️⃣ Testing JSON operations...")
        test_data = {
            'user': 'test_user',
            'role': 'budidaya',
            'timestamp': '2024-08-30 13:30:00'
        }
        r.set('fisheries:json_test', json.dumps(test_data))
        retrieved = json.loads(r.get('fisheries:json_test'))
        print(f"   JSON test: {retrieved}")
        
        # Test hash operations
        print("7️⃣ Testing HASH operations...")
        r.hset('fisheries:user:test', 'name', 'Test User')
        r.hset('fisheries:user:test', 'role', 'budidaya')
        r.hset('fisheries:user:test', 'login_count', 5)
        
        user_data = r.hgetall('fisheries:user:test')
        print(f"   Hash data: {user_data}")
        
        # Show all keys
        print("8️⃣ All Redis keys:")
        keys = r.keys('fisheries:*')
        for key in keys:
            print(f"   - {key}")
        
        print()
        print("✅ Redis connection test SUCCESSFUL!")
        print("🚀 Ready to integrate with Flask app")
        
        return True
        
    except redis.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("💡 Check Redis password configuration")
        return False
        
    except redis.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("💡 Check if Redis service is running in WSL")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = test_redis_connection()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Run Flask app: python app.py")
        print("2. Login to test Redis integration")
        print("3. Check /redis/status endpoint")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check WSL Redis: sudo systemctl status redis-server")
        print("2. Check password: redis-cli -a fisheries2024 ping")
        print("3. Check config: sudo nano /etc/redis/redis.conf")
