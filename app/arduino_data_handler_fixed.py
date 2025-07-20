
"""
Arduino Data Handler for Deep Blue Pool Chemistry Application
This module contains the functions for handling and parsing Arduino data.
"""

import re
import json
import logging

logger = logging.getLogger("DeepBluePoolApp")

def handle_arduino_data(self, data):
    """
    Handle data received from Arduino.
    
    Args:
        data: Data string from Arduino
    """
    self.arduino_data_var.set(data)
    
    # Log the received data
    logger.info(f"Arduino data received: {data}")
    
    # Parse data
    try:
        # Try to parse data in different formats
        
        # Format 1: "pH:7.2,Temp:78.5,ORP:650"
        if ":" in data and "," in data:
            values = {}
            for item in data.split(','):
                if ":" in item:
                    key, value = item.split(':')
                    values[key] = float(value)
            
            # Update chemical parameters if available
            if 'pH' in values:
                self.chemical_vars['ph'].set(str(values['pH']))
            
            if 'Temp' in values:
                self.chemical_vars['temperature'].set(str(values['Temp']))
            
            # ORP can be used to estimate free chlorine
            if 'ORP' in values:
                # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                free_chlorine = (values['ORP'] - 600) / 50
                if free_chlorine < 0:
                    free_chlorine = 0
                self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
        
        # Format 2: JSON-like format
        elif "{" in data and "}" in data:
            # Extract JSON part
            json_str = data[data.find("{"):data.find("}")+1]
            # Try to parse as JSON
            try:
                # Replace single quotes with double quotes for proper JSON
                json_str = json_str.replace("'", '"')
                values = json.loads(json_str)
                
                # Update chemical parameters if available
                if 'pH' in values:
                    self.chemical_vars['ph'].set(str(values['pH']))
                
                if 'Temp' in values:
                    self.chemical_vars['temperature'].set(str(values['Temp']))
                
                if 'ORP' in values:
                    # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                    free_chlorine = (values['ORP'] - 600) / 50
                    if free_chlorine < 0:
                        free_chlorine = 0
                    self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON: {e}")
        
        # Format 3: Simple number (likely ORP value)
        elif data.strip().isdigit() or (data.strip().replace('.', '', 1).isdigit() and data.strip().count('.') <= 1):
            try:
                orp = float(data.strip())
                # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                free_chlorine = (orp - 600) / 50
                if free_chlorine < 0:
                    free_chlorine = 0
                self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
            except ValueError as e:
                logger.error(f"Error parsing numeric value: {e}")
        
        # Format 4: Try to extract numbers using regex
        else:
            # Look for patterns like "ORP: 650" or "pH: 7.2"
            orp_match = re.search(r'ORP[:\s]+(\d+)', data)
            if orp_match:
                orp = float(orp_match.group(1))
                # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                free_chlorine = (orp - 600) / 50
                if free_chlorine < 0:
                    free_chlorine = 0
                self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
            
            ph_match = re.search(r'pH[:\s]+(\d+\.\d+)', data)
            if ph_match:
                ph = float(ph_match.group(1))
                self.chemical_vars['ph'].set(str(ph))
            
            temp_match = re.search(r'[Tt]emp(?:erature)?[:\s]+(\d+\.\d+)', data)
            if temp_match:
                temp = float(temp_match.group(1))
                self.chemical_vars['temperature'].set(str(temp))
    
    except Exception as e:
        logger.error(f"Error parsing Arduino data: {e}")
