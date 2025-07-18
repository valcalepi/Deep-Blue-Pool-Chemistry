# Notification System

The Notification System provides alerts for important events in the Deep Blue Pool Chemistry application.

## Features

- Chemical alerts when pool chemistry is out of balance
- Maintenance reminders for scheduled tasks
- System notifications for application events
- Weather alerts for conditions affecting pool chemistry
- Custom notifications for user-defined events

## Notification Levels

- **Info**: General information
- **Warning**: Potential issues that should be addressed
- **Alert**: Important issues that require attention
- **Critical**: Urgent issues that require immediate attention

## Configuration

The Notification System can be configured by editing the `config/notification_config.json` file.

Available settings:
- `enabled`: Whether notifications are enabled
- `display_time`: How long notifications are displayed (in seconds)
- `max_notifications`: Maximum number of notifications to store
- `auto_cleanup_days`: Number of days after which old notifications are automatically deleted
- `notification_sound`: Whether to play a sound when a notification is received
- `desktop_notifications`: Whether to show desktop notifications
- `email_notifications`: Whether to send email notifications
- `email_settings`: Email notification settings
- `notification_levels`: Which notification levels are enabled
- `notification_categories`: Which notification categories are enabled
