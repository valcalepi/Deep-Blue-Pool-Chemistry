import argparse
import os
from core.analyzer import TestStripAnalyzer
from core.sensor import SensorManager
from data.logger import log_chemistry_data

def run_test_strip_analysis(image_path):
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        return

    analyzer = TestStripAnalyzer()
    hsv_image = analyzer.preprocess_image(image_path)
    zones = analyzer.extract_color_zones(hsv_image)
    results = analyzer.interpret_zones(zones)

    print("\n🧪 Test Strip Results:")
    for zone, result in results.items():
        print(f"{zone}: {result}")

    log_chemistry_data(results)

def run_sensor_reading(port='COM3', baudrate=9600):
    sensor = SensorManager(port=port, baudrate=baudrate)
    try:
        sensor.connect()
        data = sensor.read_data()
        if data:
            print("\n📟 Sensor Readings:")
            for key, value in data.items():
                print(f"{key}: {value}")
            log_chemistry_data(data)
        else:
            print("No sensor data received.")
    except Exception as e:
        print(f"Sensor error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Deep Blue Pool Chemistry Manager")
    parser.add_argument('--image', type=str, help='Path to test strip image')
    parser.add_argument('--sensor', action='store_true', help='Enable sensor reading')
    parser.add_argument('--port', type=str, default='COM3', help='Serial port for sensor')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baudrate for sensor')

    args = parser.parse_args()

    if args.image:
        run_test_strip_analysis(args.image)

    if args.sensor:
        run_sensor_reading(port=args.port, baudrate=args.baudrate)

    if not args.image and not args.sensor:
        print("No input provided. Use --image or --sensor to run analysis.")

if __name__ == "__main__":
    main()

