# modules/reporting.py
"""
Reporting Module
Handles report generation for the Pool Chemistry Manager
"""

import logging
from datetime import datetime

class ReportGenerator:
    """Report generator for the Pool Chemistry Manager"""
    
    def __init__(self, db_manager):
        """Initialize the report generator"""
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
    
    def generate_customer_summary_report(self):
        """Generate customer summary report"""
        try:
            report = []
            report.append("CUSTOMER SUMMARY REPORT")
            report.append("=" * 50)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Get customer data
            customers = self.db_manager.get_all_customers()
            
            report.append(f"Total Customers: {len(customers)}")
            report.append("")
            
            if customers:
                report.append("Customer List:")
                report.append("-" * 30)
                for customer in customers:
                    report.append(f"Name: {customer['name']}")
                    report.append(f"Phone: {customer['phone']}")
                    report.append(f"Pool Size: {customer['pool_size']} gallons")
                    report.append(f"Pool Type: {customer['pool_type']}")
                    report.append("")
            else:
                report.append("No customers found.")
            
            return "\n".join(report)
        except Exception as e:
            self.logger.error(f"Error generating customer summary report: {e}")
            return f"Error generating report: {e}"
    
    def generate_test_history_report(self, customer_id=None):
        """Generate test history report"""
        try:
            report = []
            report.append("WATER TEST HISTORY REPORT")
            report.append("=" * 50)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Get test data
            tests = self.db_manager.get_water_tests(customer_id)
            
            # If customer_id is provided, include customer info
            if customer_id:
                customer = self.db_manager.get_customer(customer_id)
                if customer:
                    report.append(f"Customer: {customer['name']}")
                    report.append(f"Pool Size: {customer['pool_size']} gallons")
                    report.append(f"Pool Type: {customer['pool_type']}")
                    report.append("")
            
            report.append(f"Total Tests: {len(tests)}")
            report.append("")
            
            if tests:
                report.append("Test Results:")
                report.append("-" * 30)
                for test in tests:
                    report.append(f"Date/Time: {test['date_time']}")
                    report.append(f"pH: {test['ph']}")
                    report.append(f"Free Chlorine: {test['chlorine']} ppm")
                    report.append(f"Total Alkalinity: {test['alkalinity']} ppm")
                    report.append(f"Calcium Hardness: {test['hardness']} ppm")
                    report.append(f"Cyanuric Acid: {test['cyanuric_acid']} ppm")
                    if test['notes']:
                        report.append(f"Notes: {test['notes']}")
                    report.append("")
            else:
                report.append("No test results found.")
            
            return "\n".join(report)
        except Exception as e:
            self.logger.error(f"Error generating test history report: {e}")
            return f"Error generating report: {e}"
    
    def generate_chemical_usage_report(self, customer_id=None):
        """Generate chemical usage report"""
        try:
            report = []
            report.append("CHEMICAL USAGE REPORT")
            report.append("=" * 50)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Get chemical addition data
            additions = self.db_manager.get_chemical_additions(customer_id)
            
            # If customer_id is provided, include customer info
            if customer_id:
                customer = self.db_manager.get_customer(customer_id)
                if customer:
                    report.append(f"Customer: {customer['name']}")
                    report.append(f"Pool Size: {customer['pool_size']} gallons")
                    report.append(f"Pool Type: {customer['pool_type']}")
                    report.append("")
            
            report.append(f"Total Chemical Additions: {len(additions)}")
            report.append("")
            
            if additions:
                report.append("Chemical Addition History:")
                report.append("-" * 30)
                
                # Group by chemical type
                chemical_types = {}
                for addition in additions:
                    chem_type = addition['chemical_type']
                    if chem_type not in chemical_types:
                        chemical_types[chem_type] = []
                    chemical_types[chem_type].append(addition)
                
                # Report by chemical type
                for chem_type, items in chemical_types.items():
                    report.append(f"{chem_type}:")
                    total_amount = sum(item['amount'] for item in items)
                    unit = items[0]['unit'] if items else ""
                    report.append(f"Total Used: {total_amount:.2f} {unit}")
                    report.append("Addition History:")
                    for item in items:
                        report.append(f"  {item['date_time']}: {item['amount']} {item['unit']}")
                    report.append("")
            else:
                report.append("No chemical additions found.")
            
            return "\n".join(report)
        except Exception as e:
            self.logger.error(f"Error generating chemical usage report: {e}")
            return f"Error generating report: {e}"
    
    def generate_monthly_report(self, month=None, year=None):
        """Generate monthly report"""
        try:
            # If month/year not provided, use current month/year
            if month is None or year is None:
                now = datetime.now()
                month = month or now.month
                year = year or now.year
            
            month_name = datetime(year, month, 1).strftime("%B")
            
            report = []
            report.append(f"MONTHLY REPORT - {month_name} {year}")
            report.append("=" * 50)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # This would be expanded in a real implementation to include:
            # - Customer activity summary
            # - Water test statistics
            # - Chemical usage summary
            # - Service appointments
            # - Financial summary
            
            report.append(f"Monthly summary for {month_name} {year}")
            report.append("This feature will be expanded in future versions.")
            
            return "\n".join(report)
        except Exception as e:
            self.logger.error(f"Error generating monthly report: {e}")
            return f"Error generating report: {e}"
    
    def generate_service_schedule_report(self):
        """Generate service schedule report"""
        try:
            report = []
            report.append("SERVICE SCHEDULE REPORT")
            report.append("=" * 50)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # This would be expanded in a real implementation to include:
            # - Upcoming service appointments
            # - Service history
            # - Recurring service schedules
            
            report.append("Service Schedule")
            report.append("This feature will be expanded in future versions.")
            
            return "\n".join(report)
        except Exception as e:
            self.logger.error(f"Error generating service schedule report: {e}")
            return f"Error generating report: {e}"
    
    def generate_water_quality_trends_report(self, customer_id=None):
        """Generate water quality trends report"""
        try:
            report = []
            report.append("WATER QUALITY TRENDS REPORT")
            report.append("=" * 50)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Get test data
            tests = self.db_manager.get_water_tests(customer_id)
            
            # If customer_id is provided, include customer info
            if customer_id:
                customer = self.db_manager.get_customer(customer_id)
                if customer:
                    report.append(f"Customer: {customer['name']}")
                    report.append(f"Pool Size: {customer['pool_size']} gallons")
                    report.append(f"Pool Type: {customer['pool_type']}")
                    report.append("")
            
            if tests:
                # In a real implementation, this would include statistical analysis
                # and possibly generate charts/graphs
                report.append("Water Quality Trends")
                report.append("This feature will include statistical analysis and trends in future versions.")
                report.append("")
                report.append(f"Number of tests analyzed: {len(tests)}")
            else:
                report.append("No test data available for trend analysis.")
            
            return "\n".join(report)
        except Exception as e:
            self.logger.error(f"Error generating water quality trends report: {e}")
            return f"Error generating report: {e}"