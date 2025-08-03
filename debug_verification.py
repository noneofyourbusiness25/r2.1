#!/usr/bin/env python3
"""
Debug script for verification and shortlink issues
"""

import asyncio
import logging
from database.users_chats_db import db
from utils import get_verify_status, update_verify_status, get_shortlink, is_premium
from info import IS_VERIFY, SHORTLINK_URL, SHORTLINK_API, VERIFY_EXPIRE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_verification():
    """Test verification functionality"""
    print("=== Testing Verification ===")
    
    # Test user ID (replace with actual user ID)
    test_user_id = 123456789  # Replace with actual user ID
    
    print(f"1. Testing verification status for user {test_user_id}")
    verify_status = await get_verify_status(test_user_id)
    print(f"   Current status: {verify_status}")
    
    print(f"2. Testing IS_VERIFY setting")
    print(f"   IS_VERIFY = {IS_VERIFY}")
    
    print(f"3. Testing premium status")
    # Note: This requires a bot instance, so we'll skip for now
    # is_premium_status = await is_premium(test_user_id, bot)
    # print(f"   Is premium: {is_premium_status}")
    
    print(f"4. Testing verification update")
    test_token = "test_token_123"
    await update_verify_status(test_user_id, verify_token=test_token, is_verified=True)
    updated_status = await get_verify_status(test_user_id)
    print(f"   Updated status: {updated_status}")

async def test_shortlink():
    """Test shortlink functionality"""
    print("\n=== Testing Shortlink ===")
    
    print(f"1. Testing shortlink settings")
    print(f"   SHORTLINK_URL = {SHORTLINK_URL}")
    print(f"   SHORTLINK_API = {SHORTLINK_API}")
    
    print(f"2. Testing shortlink creation")
    test_link = "https://t.me/test_bot?start=test"
    try:
        shortlink = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, test_link)
        print(f"   Original link: {test_link}")
        print(f"   Shortlink: {shortlink}")
    except Exception as e:
        print(f"   Error creating shortlink: {e}")

async def test_database_settings():
    """Test database settings"""
    print("\n=== Testing Database Settings ===")
    
    # Test group settings
    test_group_id = -1001234567890  # Replace with actual group ID
    
    print(f"1. Testing group settings for group {test_group_id}")
    try:
        settings = await db.get_settings(test_group_id)
        print(f"   Settings: {settings}")
        print(f"   Shortlink enabled: {settings.get('shortlink', False)}")
        print(f"   Shortlink URL: {settings.get('url', 'Not set')}")
        print(f"   Shortlink API: {settings.get('api', 'Not set')}")
    except Exception as e:
        print(f"   Error getting settings: {e}")

async def check_environment_variables():
    """Check environment variables"""
    print("\n=== Environment Variables ===")
    
    import os
    env_vars = [
        'IS_VERIFY',
        'SHORTLINK',
        'SHORTLINK_URL', 
        'SHORTLINK_API',
        'VERIFY_EXPIRE',
        'VERIFY_TUTORIAL'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        print(f"   {var} = {value}")

async def main():
    """Main test function"""
    print("Starting verification and shortlink debug tests...")
    
    await check_environment_variables()
    await test_verification()
    await test_shortlink()
    await test_database_settings()
    
    print("\n=== Debug Summary ===")
    print("1. Check if IS_VERIFY is set to True")
    print("2. Check if SHORTLINK is set to True")
    print("3. Verify SHORTLINK_URL and SHORTLINK_API are correct")
    print("4. Check database settings for groups")
    print("5. Monitor bot logs for verification and shortlink errors")

if __name__ == "__main__":
    asyncio.run(main())