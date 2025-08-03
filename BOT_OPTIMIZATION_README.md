# Bot Optimization Guide

## Issues Fixed

Your bot was experiencing responsiveness issues due to several factors:

### 1. **Long Sleep Operations**
- **Problem**: The `check_premium` function was sleeping for 20 minutes (1200 seconds)
- **Solution**: Reduced to 5 minutes (300 seconds) with better error handling

### 2. **Memory Leaks from Database Connections**
- **Problem**: MongoDB connections without proper pooling and timeout settings
- **Solution**: Added connection pooling with `maxPoolSize=10` and timeout settings

### 3. **Long Auto-Delete Operations**
- **Problem**: Bot was sleeping for 1 hour (3600 seconds) during auto-delete operations
- **Solution**: Changed to check every minute instead of one long sleep

### 4. **Poor Error Handling**
- **Problem**: Silent exceptions that could cause the bot to hang
- **Solution**: Added comprehensive error logging and recovery mechanisms

## Changes Made

### 1. **utils.py**
- ✅ Reduced `check_premium` sleep time from 1200s to 300s
- ✅ Added error handling and logging
- ✅ Added recovery mechanism for failed operations

### 2. **bot.py**
- ✅ Improved error handling in startup process
- ✅ Removed hard exit on LOG_CHANNEL errors
- ✅ Added better logging for debugging

### 3. **database/users_chats_db.py**
- ✅ Added connection pooling (`maxPoolSize=10`)
- ✅ Added timeout settings (`serverSelectionTimeoutMS=5000`)
- ✅ Added error handling for database connections

### 4. **plugins/pm_filter.py**
- ✅ Optimized auto-delete operations to check every minute
- ✅ Reduced sleep times in spell check functions
- ✅ Added proper error handling for message deletions

### 5. **plugins/commands.py**
- ✅ Reduced sticker deletion sleep from 3s to 1s
- ✅ Optimized PM file deletion operations
- ✅ Added error handling for file operations

## Monitoring Tools Added

### 1. **monitor.py**
A comprehensive monitoring script that checks:
- Bot responsiveness
- Memory usage
- Database connections
- Response times

**Usage:**
```bash
python monitor.py
```

### 2. **restart_bot.py**
An auto-restart script that:
- Monitors bot responsiveness
- Automatically restarts if unresponsive for 5 minutes
- Sends notifications about restarts
- Limits restarts to prevent infinite loops

**Usage:**
```bash
python restart_bot.py
```

## Environment Variables

Add these to your environment for monitoring:

```bash
export BOT_TOKEN="your_bot_token"
export MONITOR_CHAT_ID="your_admin_chat_id"
```

## Performance Improvements

### Before:
- Bot could become unresponsive for 20+ minutes
- Long sleep operations blocking other tasks
- Silent failures causing hangs
- No monitoring or recovery mechanisms

### After:
- Maximum sleep time reduced to 5 minutes
- Regular health checks every minute
- Comprehensive error logging
- Automatic restart capability
- Memory and database monitoring

## Monitoring Commands

### Check Bot Health:
```bash
python monitor.py
```

### Auto-Restart Bot:
```bash
python restart_bot.py
```

### View Logs:
```bash
tail -f bot_monitor.log
tail -f bot_restart.log
```

## Additional Recommendations

### 1. **Set up Cron Jobs**
Add to your crontab for automatic monitoring:
```bash
# Check bot every 5 minutes
*/5 * * * * cd /path/to/bot && python monitor.py

# Auto-restart if needed
0 */6 * * * cd /path/to/bot && python restart_bot.py
```

### 2. **Database Optimization**
Consider adding these MongoDB indexes:
```javascript
// Users collection
db.Users.createIndex({"id": 1})

// Groups collection  
db.Groups.createIndex({"id": 1})

// Files collection
db.Telegram_files.createIndex({"file_name": "text"})
```

### 3. **Memory Monitoring**
Install `psutil` for memory monitoring:
```bash
pip install psutil
```

### 4. **Log Rotation**
Add log rotation to prevent disk space issues:
```bash
# Add to crontab
0 0 * * * find /path/to/bot -name "*.log" -mtime +7 -delete
```

## Troubleshooting

### If Bot Still Becomes Unresponsive:

1. **Check Logs:**
   ```bash
   tail -f bot_monitor.log
   ```

2. **Check Memory Usage:**
   ```bash
   ps aux | grep python
   ```

3. **Check Database Connections:**
   ```bash
   python -c "from database.users_chats_db import data_db_client; print(data_db_client.admin.command('ping'))"
   ```

4. **Manual Restart:**
   ```bash
   pkill -f bot.py
   python bot.py
   ```

## Expected Results

After implementing these changes:

- ✅ Bot should respond within 1-2 seconds
- ✅ No more 10+ minute delays
- ✅ Automatic recovery from failures
- ✅ Better error visibility through logs
- ✅ Reduced memory usage
- ✅ More stable database connections

## Support

If you continue to experience issues:

1. Check the monitoring logs for specific errors
2. Verify database connectivity
3. Monitor memory usage
4. Check for network connectivity issues
5. Review the auto-restart logs for patterns

The monitoring tools will help identify the root cause of any remaining issues.