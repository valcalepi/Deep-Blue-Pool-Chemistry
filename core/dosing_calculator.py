def calculate_volume(length_ft, width_ft, avg_depth_ft):
    return length_ft * width_ft * avg_depth_ft * 7.48  # gallons

def recommend_dose(volume_gal, chemical_type):
    doses = {
        'chlorine': 0.00013,  # gallons per gallon of pool water
        'stabilizer': 0.00005,
        'shock': 0.0002
    }
    if chemical_type not in doses:
        return "Unknown chemical type."
    return round(volume_gal * doses[chemical_type], 2)
