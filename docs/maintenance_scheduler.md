# Maintenance Scheduler

The Maintenance Scheduler helps you keep track of regular pool maintenance tasks.

## Features

- Schedule recurring maintenance tasks
- Track task completion
- View upcoming and overdue tasks
- Calendar view for task scheduling
- Statistics on maintenance history
- Task categories and priorities

## Task Properties

- **Name**: Task name
- **Description**: Task description
- **Frequency**: How often the task should be performed (in days)
- **Last Completed**: When the task was last completed
- **Next Due**: When the task is next due
- **Priority**: Task priority (low, medium, high)
- **Category**: Task category (chemical, equipment, cleaning, inspection, general)
- **Notes**: Additional notes about the task

## Configuration

The Maintenance Scheduler can be configured by editing the `config/maintenance_config.json` file.

Available settings:
- `data_file`: File where maintenance tasks are stored
- `default_categories`: Default task categories
- `default_priorities`: Default task priorities
- `default_frequencies`: Default task frequencies
- `reminder_days`: Days before due date to send reminders
- `auto_suggest`: Whether to auto-suggest tasks based on pool type
- `enable_notifications`: Whether to send notifications for due tasks
