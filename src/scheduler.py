import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any, Tuple, Union
from pathlib import Path
import json
import os
from enum import Enum

logger = logging.getLogger(__name__)

class ScheduleType(Enum):
    """Enumeration of schedule types"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class Priority(Enum):
    """Enumeration of task priorities"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class TaskScheduler:
    """Manages scheduled tasks for the pool chemistry application"""
    
    def __init__(self):
        """Initialize the task scheduler"""
        logger.info("Initializing TaskScheduler")
        try:
            self.tasks = {}
            self.task_history = []
            self.stop_event = threading.Event()
            self.scheduler_thread = None
            self.task_file = Path("data/tasks.json")
            self.history_file = Path("data/task_history.json")
            
            # Create data directory if it doesn't exist
            self.task_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing tasks
            self._load_tasks()
            self._load_task_history()
            
            logger.info("TaskScheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing TaskScheduler: {str(e)}")
            raise
    
    def _load_tasks(self):
        """Load tasks from file"""
        try:
            if self.task_file.exists():
                with open(self.task_file, 'r') as f:
                    tasks_data = json.load(f)
                    
                # Convert stored tasks to proper format
                for task_id, task_info in tasks_data.items():
                    # Convert string dates back to datetime objects
                    if 'next_run' in task_info and task_info['next_run']:
                        task_info['next_run'] = datetime.fromisoformat(task_info['next_run'])
                    self.tasks[task_id] = task_info
                    
                logger.info(f"Loaded {len(self.tasks)} tasks from {self.task_file}")
            else:
                logger.info(f"No tasks file found at {self.task_file}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Error loading tasks: {str(e)}")
            # Continue with empty tasks rather than crash
            self.tasks = {}
    
    def _load_task_history(self):
        """Load task execution history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.task_history = json.load(f)
                logger.info(f"Loaded {len(self.task_history)} task history entries")
            else:
                logger.info(f"No task history file found at {self.history_file}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Error loading task history: {str(e)}")
            # Continue with empty history rather than crash
            self.task_history = []
    
    def _save_tasks(self):
        """Save tasks to file"""
        try:
            # Convert datetime objects to strings for serialization
            serializable_tasks = {}
            for task_id, task_info in self.tasks.items():
                task_copy = task_info.copy()
                if 'next_run' in task_copy and isinstance(task_copy['next_run'], datetime):
                    task_copy['next_run'] = task_copy['next_run'].isoformat()
                # Remove callback as it's not serializable
                if 'callback' in task_copy:
                    del task_copy['callback']
                serializable_tasks[task_id] = task_copy
                
            with open(self.task_file, 'w') as f:
                json.dump(serializable_tasks, f, indent=2)
                
            logger.debug(f"Saved {len(self.tasks)} tasks to {self.task_file}")
            
        except Exception as e:
            logger.error(f"Error saving tasks: {str(e)}")
    
    def _save_task_history(self):
        """Save task execution history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.task_history, f, indent=2)
                
            logger.debug(f"Saved {len(self.task_history)} task history entries")
            
        except Exception as e:
            logger.error(f"Error saving task history: {str(e)}")
    
    def add_task(self, task_id: str, description: str, schedule_type: ScheduleType, 
                priority: Priority = Priority.MEDIUM, 
                callback: Optional[Callable] = None, 
                start_time: Optional[datetime] = None,
                parameters: Optional[Dict] = None) -> bool:
        """
        Add a new scheduled task
        
        Args:
            task_id (str): Unique identifier for the task
            description (str): Description of the task
            schedule_type (ScheduleType): Type of schedule (ONCE, DAILY, WEEKLY, MONTHLY, CUSTOM)
            priority (Priority, optional): Priority of the task. Defaults to Priority.MEDIUM.
            callback (Optional[Callable], optional): Function to call when task is due
            start_time (Optional[datetime], optional): When to start the task (default: now)
            parameters (Optional[Dict], optional): Parameters to pass to the callback
            
        Returns:
            bool: True if task was added successfully
        """
        try:
            if task_id in self.tasks:
                logger.warning(f"Task {task_id} already exists")
                return False
                
            if not start_time:
                start_time = datetime.now()
                
            task = {
                'description': description,
                'schedule_type': schedule_type,
                'priority': priority,
                'next_run': start_time,
                'last_run': None,
                'enabled': True,
                'callback': callback,
                'parameters': parameters or {}
            }
            
            self.tasks[task_id] = task
            self._save_tasks()
            
            logger.info(f"Added task {task_id}: {description}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding task {task_id}: {str(e)}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a scheduled task
        
        Args:
            task_id (str): Unique identifier for the task
            
        Returns:
            bool: True if task was removed successfully
        """
        try:
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} not found")
                return False
                
            del self.tasks[task_id]
            self._save_tasks()
            
            logger.info(f"Removed task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing task {task_id}: {str(e)}")
            return False
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """
        Update a scheduled task
        
        Args:
            task_id (str): Unique identifier for the task
            **kwargs: Task properties to update
            
        Returns:
            bool: True if task was updated successfully
        """
        try:
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} not found")
                return False
                
            for key, value in kwargs.items():
                if key in self.tasks[task_id]:
                    self.tasks[task_id][key] = value
                    
            self._save_tasks()
            
            logger.info(f"Updated task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        Get a task by ID
        
        Args:
            task_id (str): Unique identifier for the task
            
        Returns:
            Optional[Dict]: Task information if found, otherwise None
        """
        try:
            return self.tasks.get(task_id)
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {str(e)}")
            return None
    
    def start(self):
        """Start the task scheduler"""
        try:
            self.scheduler_thread = threading.Thread(target=self._run_scheduler)
            self.scheduler_thread.start()
            logger.info("Task scheduler started")
        except Exception as e:
            logger.error(f"Error starting task scheduler: {str(e)}")
    
    def stop(self):
        """Stop the task scheduler"""
        try:
            self.stop_event.set()
            if self.scheduler_thread:
                self.scheduler_thread.join()
            logger.info("Task scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping task scheduler: {str(e)}")
    
    def _run_scheduler(self):
        """Run the task scheduler loop"""
        try:
            while not self.stop_event.is_set():
                current_time = datetime.now()
                for task_id, task in self.tasks.items():
                    if task['enabled'] and task['next_run'] <= current_time:
                        # Execute the task
                        task['callback'](**task['parameters'])
                        # Update the task's next run time
                        if task['schedule_type'] == ScheduleType.ONCE:
                            task['enabled'] = False
                        elif task['schedule_type'] == ScheduleType.DAILY:
                            task['next_run'] = current_time + timedelta(days=1)
                        elif task['schedule_type'] == ScheduleType.WEEKLY:
                            task['next_run'] = current_time + timedelta(weeks=1)
                        elif task['schedule_type'] == ScheduleType.MONTHLY:
                            task['next_run'] = current_time.replace(day=1) + timedelta(months=1)
                        elif task['schedule_type'] == ScheduleType.CUSTOM:
                            # For custom intervals, the interval is stored in the task's data
                            task['next_run'] = current_time + timedelta(seconds=task.get('interval', 0))
                        # Save the updated task
                        self._save_tasks()
                        # Log the task execution
                        logger.info(f"Executed task {task_id}: {task['description']}")
                # Sleep for 1 second before checking again
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error running task scheduler: {str(e)}")

# Example usage:
if __name__ == "__main__":
    scheduler = TaskScheduler()
    scheduler.add_task("task1", "Task 1", ScheduleType.DAILY, 
                       callback=lambda: print("Task 1 executed"))
    scheduler.start()
    time.sleep(30)
    scheduler.stop()
