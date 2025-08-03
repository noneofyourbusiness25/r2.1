#!/usr/bin/env python3
"""
Bot Auto-Restart Script
This script monitors the bot and automatically restarts it if it becomes unresponsive.
"""

import asyncio
import logging
import subprocess
import time
import os
import signal
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_restart.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotRestarter:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.bot_process = None
        self.restart_count = 0
        self.max_restarts = 5  # Maximum restarts per hour
        
    async def check_bot_responsiveness(self):
        """Check if bot is responding to commands"""
        try:
            import requests
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": "🤖 Bot Health Check"
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error checking bot responsiveness: {e}")
            return False
    
    def start_bot(self):
        """Start the bot process"""
        try:
            logger.info("Starting bot process...")
            self.bot_process = subprocess.Popen(
                [sys.executable, "bot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"Bot process started with PID: {self.bot_process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            return False
    
    def stop_bot(self):
        """Stop the bot process gracefully"""
        if self.bot_process:
            try:
                logger.info(f"Stopping bot process (PID: {self.bot_process.pid})...")
                self.bot_process.terminate()
                # Wait for graceful shutdown
                try:
                    self.bot_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning("Bot didn't stop gracefully, forcing kill...")
                    self.bot_process.kill()
                logger.info("Bot process stopped")
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")
    
    async def send_restart_notification(self, reason):
        """Send notification about bot restart"""
        try:
            import requests
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": f"🔄 Bot Restart\n\n📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📝 Reason: {reason}\n🔄 Restart Count: {self.restart_count}"
            }
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send restart notification: {e}")
    
    async def monitor_and_restart(self, check_interval=60, max_unresponsive_time=300):
        """Monitor bot and restart if needed"""
        logger.info("Starting bot monitoring and auto-restart...")
        
        unresponsive_start = None
        
        while True:
            try:
                # Check if bot is responsive
                is_responsive = await self.check_bot_responsiveness()
                
                if is_responsive:
                    if unresponsive_start:
                        logger.info("Bot is responsive again")
                        unresponsive_start = None
                    logger.info("Bot is healthy")
                else:
                    if not unresponsive_start:
                        unresponsive_start = time.time()
                        logger.warning("Bot became unresponsive")
                    
                    # Check if bot has been unresponsive for too long
                    if time.time() - unresponsive_start > max_unresponsive_time:
                        logger.error(f"Bot has been unresponsive for {max_unresponsive_time} seconds")
                        
                        # Check restart limit
                        if self.restart_count >= self.max_restarts:
                            logger.error("Maximum restart limit reached. Stopping auto-restart.")
                            await self.send_restart_notification("Maximum restart limit reached")
                            break
                        
                        # Restart bot
                        self.restart_count += 1
                        logger.info(f"Restarting bot (attempt {self.restart_count})")
                        
                        self.stop_bot()
                        await asyncio.sleep(5)  # Wait before restart
                        
                        if self.start_bot():
                            await self.send_restart_notification("Bot was unresponsive")
                            # Wait for bot to start up
                            await asyncio.sleep(30)
                        else:
                            logger.error("Failed to restart bot")
                            await self.send_restart_notification("Failed to restart bot")
                
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(check_interval)
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_bot()

async def main():
    """Main function"""
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('MONITOR_CHAT_ID', '1710896723')
    
    if not bot_token:
        logger.error("BOT_TOKEN environment variable not set")
        return
    
    restarter = BotRestarter(bot_token, chat_id)
    
    try:
        # Start bot initially
        if not restarter.start_bot():
            logger.error("Failed to start bot initially")
            return
        
        # Wait for bot to start
        await asyncio.sleep(10)
        
        # Start monitoring
        await restarter.monitor_and_restart()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        restarter.cleanup()

if __name__ == "__main__":
    asyncio.run(main())