
#!/usr/bin/env python3
"""
Script to update the pool_app.py file to use the new tab-based UI.

This script reads the original pool_app.py file, finds the run_gui method,
and replaces it with a new implementation that uses the tab-based UI.
"""

import os
import sys

def update_pool_app():
    """Update the pool_app.py file to use the tab-based UI."""
    
    # Find the pool_app.py file
    possible_paths = [
        'pool_app.py',
        'Deep-Blue-Pool-Chemistry/pool_app.py',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pool_app.py'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Deep-Blue-Pool-Chemistry', 'pool_app.py')
    ]
    
    pool_app_path = None
    for path in possible_paths:
        if os.path.exists(path):
            pool_app_path = path
            break
    
    if not pool_app_path:
        print("Could not find pool_app.py. Please specify the correct path.")
        return False
    
    print(f"Found pool_app.py at: {pool_app_path}")
    
    # Read the original file
    with open(pool_app_path, 'r') as f:
        content = f.read()
    
    # Find the run_gui method
    start_marker = "    def run_gui(self) -> None:"
    end_marker = "    def _show_test_strip_analyzer(self, parent: tk.Tk) -> None:"
    
    start_index = content.find(start_marker)
    end_index = content.find(end_marker)
    
    if start_index == -1 or end_index == -1:
        print("Could not find the run_gui method in the file.")
        return False
    
    # Extract the method content
    method_content = content[start_index:end_index]
    
    # Create the new method content
    new_method_content = """    def run_gui(self) -> None:
        \"\"\"
        Run the GUI application.
        
        Raises:
            RuntimeError: If the GUI fails to initialize
        \"\"\"
        try:
            logger.info("Starting GUI application")
            
            # Create the main window
            root = tk.Tk()
            
            # Import the tab-based UI
            try:
                from tab_based_ui import TabBasedUI
                
                # Initialize the tab-based UI
                ui = TabBasedUI(
                    root=root,
                    db_service=self.db_service,
                    chemical_safety_db=self.chemical_safety_db,
                    test_strip_analyzer=self.test_strip_analyzer,
                    weather_service=self.weather_service,
                    controller=self.controller
                )
                
                logger.info("Tab-based UI initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing tab-based UI: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
                # Fall back to basic UI
                root.title("Deep Blue Pool Chemistry")
                root.geometry("1000x700")
                
                # Set icon if available
                icon_path = os.path.join("assests", "chemistry.png")
                if os.path.exists(icon_path):
                    try:
                        icon = tk.PhotoImage(file=icon_path)
                        root.iconphoto(True, icon)
                    except Exception as e:
                        logger.warning(f"Failed to load icon: {e}")
                
                # Create notebook for tabs
                notebook = ttk.Notebook(root)
                notebook.pack(fill=tk.BOTH, expand=True)
                
                # Create main dashboard tab
                dashboard_frame = ttk.Frame(notebook, padding=20)
                notebook.add(dashboard_frame, text="Dashboard")
                
                # Add title to dashboard
                title = ttk.Label(dashboard_frame, text="Deep Blue Pool Chemistry", font=("Arial", 24))
                title.pack(pady=20)
                
                # Add subtitle
                subtitle = ttk.Label(dashboard_frame, text="Pool Chemistry Management System with Arduino Integration", font=("Arial", 14))
                subtitle.pack(pady=10)
                
                # Add buttons
                ttk.Button(dashboard_frame, text="Test Strip Analysis", 
                          command=lambda: self._show_test_strip_analyzer(root)).pack(pady=5)
                
                ttk.Button(dashboard_frame, text="Chemical Safety Information", 
                          command=lambda: self._show_chemical_safety(root)).pack(pady=5)
                
                ttk.Button(dashboard_frame, text="Weather Impact", 
                          command=lambda: self._show_weather_info(root)).pack(pady=5)
                
                ttk.Button(dashboard_frame, text="Calculate Chemicals", 
                          command=lambda: self._show_chemical_calculator(root)).pack(pady=5)
                
                # Create Arduino Monitor tab
                try:
                    # Import the Arduino Monitor
                    # Import our simplified ArduinoMonitorApp
                    from arduino_monitor_app import ArduinoMonitorApp
                    
                    # Create Arduino Monitor tab
                    arduino_frame = ttk.Frame(notebook)
                    notebook.add(arduino_frame, text="Arduino Sensors")
                    
                    # Initialize Arduino Monitor in the tab
                    arduino_monitor = ArduinoMonitorApp(arduino_frame)
                    
                    logger.info("Arduino Monitor initialized successfully")
                except Exception as e:
                    logger.error(f"Error initializing Arduino Monitor: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    
                    # Create a placeholder frame with error message
                    arduino_frame = ttk.Frame(notebook, padding=20)
                    notebook.add(arduino_frame, text="Arduino Sensors")
                    
                    ttk.Label(arduino_frame, text="Arduino Monitor could not be initialized", 
                             font=("Arial", 16)).pack(pady=20)
                    ttk.Label(arduino_frame, text=f"Error: {str(e)}").pack(pady=10)
                
                # Create exit button at the bottom
                exit_frame = ttk.Frame(root)
                exit_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
                ttk.Button(exit_frame, text="Exit", command=root.destroy).pack(side=tk.RIGHT)
            
            # Start the main loop
            root.mainloop()
            
        except Exception as e:
            logger.error(f"Error in GUI application: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise RuntimeError(f"GUI application failed: {e}")
"""
    
    # Replace the method content
    new_content = content.replace(method_content, new_method_content)
    
    # Write the updated content back to the file
    with open(pool_app_path, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully updated {pool_app_path}")
    return True

def create_integration_file():
    """Create a file to integrate the enhanced chemical calculator and history visualizer."""
    
    # Determine the directory to save the integration file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if Deep-Blue-Pool-Chemistry directory exists
    deep_blue_dir = os.path.join(base_dir, 'Deep-Blue-Pool-Chemistry')
    if os.path.exists(deep_blue_dir) and os.path.isdir(deep_blue_dir):
        save_dir = deep_blue_dir
    else:
        save_dir = base_dir
    
    integration_file_path = os.path.join(save_dir, 'integrate_enhancements.py')
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(save_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    integration_code = """#!/usr/bin/env python3
\"\"\"
Integration script for enhanced chemical calculator and history visualizer.

This script integrates the enhanced chemical calculator and history visualizer
into the main application.
\"\"\"

import os
import sys
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Integration")

def integrate_enhancements():
    \"\"\"Integrate enhanced chemical calculator and history visualizer.\"\"\"
    logger.info("Integrating enhanced chemical calculator and history visualizer")
    
    try:
        # Import the enhanced chemical calculator
        from enhanced_chemical_calculator import EnhancedChemicalCalculator
        logger.info("Successfully imported EnhancedChemicalCalculator")
        
        # Import the chemical history visualizer
        from chemical_history_visualizer import ChemicalHistoryVisualizer
        logger.info("Successfully imported ChemicalHistoryVisualizer")
        
        # Import the database service
        from database_service import DatabaseService
        
        # Import the chemical safety database
        from chemical_safety_database import ChemicalSafetyDatabase
        
        # Create instances for testing
        db_service = DatabaseService("data/pool_data.db")
        chemical_safety_db = ChemicalSafetyDatabase()
        
        # Create enhanced chemical calculator
        calculator = EnhancedChemicalCalculator(db_service, chemical_safety_db)
        
        # Test the calculator with sample data
        test_data = {
            "pool_size": "10000",
            "pool_type": "Concrete/Gunite",
            "ph": "7.8",
            "chlorine": "1.0",
            "alkalinity": "80",
            "calcium_hardness": "200",
            "temperature": "78"
        }
        
        result = calculator.calculate_chemicals(test_data)
        
        logger.info("Chemical calculation result:")
        logger.info(f"Adjustments: {result.get('adjustments', {})}")
        logger.info(f"Water Balance: {result.get('water_balance', 0)}")
        logger.info(f"Recommendations: {result.get('recommendations', {})}")
        logger.info(f"Warnings: {result.get('warnings', [])}")
        logger.info(f"Precautions: {result.get('precautions', {})}")
        logger.info(f"Instructions: {len(result.get('instructions', []))} steps")
        
        # Test the history visualizer
        logger.info("Testing chemical history visualizer")
        
        # Get historical data
        historical_data = calculator.get_historical_data(days=30)
        
        logger.info(f"Historical data: {len(historical_data.get('dates', []))} data points")
        
        # Test data export
        export_path = calculator.export_data(format="csv", days=30)
        
        if export_path:
            logger.info(f"Data exported to {export_path}")
        else:
            logger.warning("Data export failed")
        
        logger.info("Integration test completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Add the current directory to the Python path
    sys.path.insert(0, os.getcwd())
    
    # Run the integration
    success = integrate_enhancements()
    
    if success:
        print("Integration completed successfully")
        sys.exit(0)
    else:
        print("Integration failed")
        sys.exit(1)
"""
    
    # Write the integration file
    with open(integration_file_path, 'w') as f:
        f.write(integration_code)
    
    print(f"Created integration file: {integration_file_path}")
    return True

if __name__ == "__main__":
    print("Starting update process...")
    
    # Update the pool_app.py file
    update_success = update_pool_app()
    
    # Create the integration file
    integration_success = create_integration_file()
    
    if update_success and integration_success:
        print("All updates completed successfully")
        sys.exit(0)
    else:
        print("Some updates failed")
        sys.exit(1)
