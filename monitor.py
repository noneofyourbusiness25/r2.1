#!/usr/bin/env python3
"""
Bot Performance Monitor
This script helps monitor the bot's responsiveness and performance.
"""

import asyncio
import logging
import time
from datetime import datetime
import requests
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotMonitor:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.last_response_time = None
        self.response_times = []
        
    async def send_test_message(self):
        """Send a test message to check if bot is responsive"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": f"🤖 Bot Health Check\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ Bot is responsive"
            }
            start_time = time.time()
            response = requests.post(url, data=data, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.last_response_time = response_time
                self.response_times.append(response_time)
                # Keep only last 10 response times
                if len(self.response_times) > 10:
                    self.response_times.pop(0)
                
                logger.info(f"Bot is responsive. Response time: {response_time:.2f}s")
                return True
            else:
                logger.error(f"Bot not responding. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking bot responsiveness: {e}")
            return False
    
    async def check_memory_usage(self):
        """Check memory usage of the bot process"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB ({memory_percent:.1f}%)")
            
            # Alert if memory usage is high
            if memory_percent > 80:
                logger.warning(f"High memory usage detected: {memory_percent:.1f}%")
                return False
            return True
            
        except ImportError:
            logger.warning("psutil not available, skipping memory check")
            return True
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
            return True
    
    async def check_database_connection(self):
        """Check if database connections are healthy"""
        try:
            from database.users_chats_db import data_db_client, files_db_client
            
            # Test data database connection
            data_db_client.admin.command('ping')
            logger.info("Data database connection: OK")
            
            # Test files database connection
            files_db_client.admin.command('ping')
            logger.info("Files database connection: OK")
            
            return True
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    async def get_average_response_time(self):
        """Calculate average response time"""
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)
    
    async def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        logger.info("Starting monitoring cycle...")
        
        # Check bot responsiveness
        bot_ok = await self.send_test_message()
        
        # Check memory usage
        memory_ok = await self.check_memory_usage()
        
        # Check database connections
        db_ok = await self.check_database_connection()
        
        # Calculate average response time
        avg_response_time = await self.get_average_response_time()
        
        # Log summary
        status = "✅" if all([bot_ok, memory_ok, db_ok]) else "❌"
        logger.info(f"{status} Monitoring Summary:")
        logger.info(f"  Bot Responsive: {'✅' if bot_ok else '❌'}")
        logger.info(f"  Memory OK: {'✅' if memory_ok else '❌'}")
        logger.info(f"  Database OK: {'✅' if db_ok else '❌'}")
        logger.info(f"  Avg Response Time: {avg_response_time:.2f}s")
        
        return all([bot_ok, memory_ok, db_ok])
    
    async def start_monitoring(self, interval=300):
        """Start continuous monitoring"""
        logger.info(f"Starting bot monitoring with {interval}s intervals...")
        
        while True:
            try:
                await self.run_monitoring_cycle()
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

async def main():
    """Main function to start monitoring"""
    # Get configuration from environment variables
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('MONITOR_CHAT_ID', '1710896723')  # Default to admin chat
    
    if not bot_token:
        logger.error("BOT_TOKEN environment variable not set")
        return
    
    monitor = BotMonitor(bot_token, chat_id)
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())