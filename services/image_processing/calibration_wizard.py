import cv2
import json

PAD_ZONES_FILE = "services/image_processing/pad_zones.json"

def draw_zones(image, zones):
    for chem, (x, y, w, h) in zones.items():
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, chem, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def calibrate_zones(image_path, brand="default"):
    image = cv2.imread(image_path)
    clone = image.copy()
    zones = {}
    current_chem = ""

    def click(event, x, y, flags, param):
        nonlocal current_chem
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Clicked at ({x}, {y}) for {current_chem}")
            zones[current_chem] = [x, y, 40, 40]

    cv2.namedWindow("Calibration Wizard")
    cv2.setMouseCallback("Calibration Wizard", click)

    chemicals = ["pH", "free_chlorine", "total_chlorine", "alkalinity", "calcium", "cyanuric_acid", "bromine", "salt"]
    for chem in chemicals:
        current_chem = chem
        while True:
            temp = clone.copy()
            draw_zones(temp, zones)
            cv2.imshow("Calibration Wizard", temp)
            key = cv2.waitKey(0)
            if key == ord("n"):
                break
            elif key == 27:
                cv2.destroyAllWindows()
                return

    cv2.destroyAllWindows()
    try:
        with open(PAD_ZONES_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    data[brand] = zones
    with open(PAD_ZONES_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved pad zones for brand '{brand}'")
