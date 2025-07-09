import os
import datetime
import logging
import re
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cache_cleanup.log"),
        logging.StreamHandler()
    ]
)

def clean_cache_by_age(directory, max_age_days=30):
    """
    Remove cache files older than the specified maximum age.

    Args:
        directory (str): Path to the cache directory.
        max_age_days (int): Maximum age of cache files in days.
    
    Returns:
        tuple: (bytes_removed, files_removed) - Total bytes and count of files removed
    """
    now = datetime.datetime.now()
    max_age = datetime.timedelta(days=max_age_days)
    bytes_removed = 0
    files_removed = 0
    
    logging.info(f"Cleaning files older than {max_age_days} days in {directory}")
    
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            try:
                if os.path.isfile(filepath):
                    file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                    if now - file_mtime > max_age:
                        file_size = os.path.getsize(filepath)
                        os.remove(filepath)
                        bytes_removed += file_size
                        files_removed += 1
                        logging.info(f"Removed old cache file: {filename} (Age: {(now - file_mtime).days} days)")
            except (OSError, PermissionError) as e:
                logging.error(f"Error processing {filepath}: {str(e)}")
    except Exception as e:
        logging.error(f"Error accessing directory {directory}: {str(e)}")
    
    logging.info(f"Age-based cleanup completed. Removed {files_removed} files ({bytes_removed / (1024*1024):.2f} MB)")
    return bytes_removed, files_removed

def clean_cache_by_size(directory, max_size_mb=100):
    """
    Remove cache files larger than the specified maximum size.

    Args:
        directory (str): Path to the cache directory.
        max_size_mb (int): Maximum size of cache files in MB.
    
    Returns:
        tuple: (bytes_removed, files_removed) - Total bytes and count of files removed
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    bytes_removed = 0
    files_removed = 0
    
    logging.info(f"Cleaning files larger than {max_size_mb} MB in {directory}")
    
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            try:
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    if file_size > max_size_bytes:
                        os.remove(filepath)
                        bytes_removed += file_size
                        files_removed += 1
                        logging.info(f"Removed large cache file: {filename} (Size: {file_size / (1024*1024):.2f} MB)")
            except (OSError, PermissionError) as e:
                logging.error(f"Error processing {filepath}: {str(e)}")
    except Exception as e:
        logging.error(f"Error accessing directory {directory}: {str(e)}")
    
    logging.info(f"Size-based cleanup completed. Removed {files_removed} files ({bytes_removed / (1024*1024):.2f} MB)")
    return bytes_removed, files_removed

def enforce_directory_quota(directory, max_dir_size_gb=5):
    """
    Enforce a maximum directory size by removing oldest files first.

    Args:
        directory (str): Path to the cache directory.
        max_dir_size_gb (int): Maximum allowed directory size in GB.
    
    Returns:
        tuple: (bytes_removed, files_removed) - Total bytes and count of files removed
    """
    max_size_bytes = max_dir_size_gb * 1024 * 1024 * 1024
    bytes_removed = 0
    files_removed = 0
    
    logging.info(f"Enforcing directory quota of {max_dir_size_gb} GB on {directory}")
    
    try:
        # Get all files with their modification times
        files_with_time = []
        total_size = 0
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            try:
                if os.path.isfile(filepath):
                    file_mtime = os.path.getmtime(filepath)
                    file_size = os.path.getsize(filepath)
                    total_size += file_size
                    files_with_time.append((filepath, filename, file_mtime, file_size))
            except (OSError, PermissionError) as e:
                logging.error(f"Error processing {filepath}: {str(e)}")
        
        # If total size exceeds quota, delete oldest files until under quota
        if total_size > max_size_bytes:
            # Sort by modification time (oldest first)
            files_with_time.sort(key=lambda x: x[2])
            
            size_to_remove = total_size - max_size_bytes
            removed_size = 0
            
            for filepath, filename, _, file_size in files_with_time:
                try:
                    os.remove(filepath)
                    removed_size += file_size
                    bytes_removed += file_size
                    files_removed += 1
                    logging.info(f"Removed to meet quota: {filename} (Size: {file_size / (1024*1024):.2f} MB)")
                    
                    if removed_size >= size_to_remove:
                        break
                except (OSError, PermissionError) as e:
                    logging.error(f"Error removing {filepath}: {str(e)}")
    except Exception as e:
        logging.error(f"Error enforcing directory quota: {str(e)}")
    
    logging.info(f"Quota enforcement completed. Removed {files_removed} files ({bytes_removed / (1024*1024):.2f} MB)")
    return bytes_removed, files_removed

def clean_cache_with_pattern(directory, pattern=None, exclude=False):
    """
    Clean cache files matching (or not matching) a specific pattern.

    Args:
        directory (str): Path to the cache directory.
        pattern (str): Regex pattern to match filenames.
        exclude (bool): If True, exclude files matching the pattern instead.
    
    Returns:
        tuple: (bytes_removed, files_removed) - Total bytes and count of files removed
    """
    if not pattern:
        return 0, 0
        
    bytes_removed = 0
    files_removed = 0
    regex = re.compile(pattern)
    
    action = "excluding" if exclude else "targeting"
    logging.info(f"Cleaning cache with pattern ({action} '{pattern}') in {directory}")
    
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            try:
                if os.path.isfile(filepath):
                    matches = bool(regex.search(filename))
                    if (matches and not exclude) or (not matches and exclude):
                        file_size = os.path.getsize(filepath)
                        os.remove(filepath)
                        bytes_removed += file_size
                        files_removed += 1
                        logging.info(f"Removed pattern-matched file: {filename} (Size: {file_size / (1024*1024):.2f} MB)")
            except (OSError, PermissionError) as e:
                logging.error(f"Error processing {filepath}: {str(e)}")
    except Exception as e:
        logging.error(f"Error cleaning with pattern: {str(e)}")
    
    logging.info(f"Pattern-based cleanup completed. Removed {files_removed} files ({bytes_removed / (1024*1024):.2f} MB)")
    return bytes_removed, files_removed

def cleanup_empty_dirs(directory):
    """
    Remove empty subdirectories in the cache directory.

    Args:
        directory (str): Path to the cache directory.
    
    Returns:
        int: Number of directories removed
    """
    dirs_removed = 0
    
    logging.info(f"Cleaning empty directories in {directory}")
    
    try:
        for root, dirs, files in os.walk(directory, topdown=False):
            # Skip the main directory
            if root == directory:
                continue
                
            if not os.listdir(root):
                try:
                    os.rmdir(root)
                    dirs_removed += 1
                    logging.info(f"Removed empty directory: {root}")
                except OSError as e:
                    logging.error(f"Error removing directory {root}: {str(e)}")
    except Exception as e:
        logging.error(f"Error cleaning empty directories: {str(e)}")
    
    logging.info(f"Empty directory cleanup completed. Removed {dirs_removed} directories")
    return dirs_removed

def main():
    """Main function that runs the cache cleanup with configurable parameters."""
    # Default configuration
    config = {
        'cache_directory': "/path/to/cache/directory",  # Replace with actual path
        'max_age_days': 30,
        'max_size_mb': 100,
        'max_dir_size_gb': 5,
        'cleanup_patterns': {
            'temp_files': r'.*\.tmp$',
            'log_files': r'.*\.log$'
        },
        'exclude_patterns': [r'\.keep$$', r'important_.*\.data$$ ']
    }
    
    # Parse command line arguments to override default config
    if len(sys.argv) > 1:
        config['cache_directory'] = sys.argv[1]
    if len(sys.argv) > 2:
        config['max_age_days'] = int(sys.argv[2])
    
    # Validate directory exists
    if not os.path.isdir(config['cache_directory']):
        logging.error(f"Directory does not exist: {config['cache_directory']}")
        return
    
    logging.info(f"Starting cache cleanup for: {config['cache_directory']}")
    
    # Track total statistics
    total_bytes_removed = 0
    total_files_removed = 0
    
    # 1. Age-based cleanup
    bytes_removed, files_removed = clean_cache_by_age(
        config['cache_directory'], 
        config['max_age_days']
    )
    total_bytes_removed += bytes_removed
    total_files_removed += files_removed
    
    # 2. Size-based cleanup
    bytes_removed, files_removed = clean_cache_by_size(
        config['cache_directory'], 
        config['max_size_mb']
    )
    total_bytes_removed += bytes_removed
    total_files_removed += files_removed
    
    # 3. Pattern-based cleanup
    for pattern_name, pattern in config['cleanup_patterns'].items():
        bytes_removed, files_removed = clean_cache_with_pattern(
            config['cache_directory'], 
            pattern
        )
        total_bytes_removed += bytes_removed
        total_files_removed += files_removed
    
    # 4. Exclude patterns
    for pattern in config['exclude_patterns']:
        bytes_removed, files_removed = clean_cache_with_pattern(
            config['cache_directory'], 
            pattern, 
            exclude=True
        )
        total_bytes_removed += bytes_removed
        total_files_removed += files_removed
    
    # 5. Clean empty directories
    dirs_removed = cleanup_empty_dirs(config['cache_directory'])
    
    # 6. Directory quota enforcement (as the final step)
    bytes_removed, files_removed = enforce_directory_quota(
        config['cache_directory'], 
        config['max_dir_size_gb']
    )
    total_bytes_removed += bytes_removed
    total_files_removed += files_removed
    
    # Log summary
    logging.info(f"Cache cleanup complete!")
    logging.info(f"Total removed: {total_files_removed} files, {total_bytes_removed / (1024*1024):.2f} MB, {dirs_removed} empty directories")

if __name__ == "__main__":
    main()
