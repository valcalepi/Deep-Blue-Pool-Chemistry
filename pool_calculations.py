def manage_pool(pool_type, pool_size, pH, chlorine, bromine, alkalinity, cyanuric_acid, calcium_hardness, stabilizer, salt):
    """
    Calculate chemical adjustments needed based on current pool parameters
    
    Args:
        pool_type (str): Type of pool (e.g., "Chlorine", "Bromine", "Saltwater")
        pool_size (float): Size of pool in gallons
        pH (float): Current pH level
        chlorine (float): Current chlorine level in ppm
        bromine (float): Current bromine level in ppm
        alkalinity (float): Current alkalinity level in ppm
        cyanuric_acid (float): Current cyanuric acid level in ppm
        calcium_hardness (float): Current calcium hardness level in ppm
        stabilizer (float): Current stabilizer level in ppm (same as cyanuric acid)
        salt (float): Current salt level in ppm
    
    Returns:
        dict: Dictionary containing chemical adjustment recommendations
    """
    pool_factor = pool_size / 10000
    recommendations = {}
    
    # Define ideal ranges based on pool type
    ideal_ranges = {
        "pH": {"min": 7.4, "max": 7.6, "ideal": 7.5},
        "chlorine": {"min": 1.0, "max": 5.0, "ideal": 3.0},
        "bromine": {"min": 2.0, "max": 6.0, "ideal": 4.0},
        "alkalinity": {"min": 80, "max": 120, "ideal": 100},
        "calcium_hardness": {"min": 200, "max": 400, "ideal": 300},
        "cyanuric_acid": {"min": 30, "max": 50, "ideal": 40},
    }
    
    # Adjust ideal ranges based on pool type
    if pool_type.lower() == "saltwater":
        ideal_ranges["salt"] = {"min": 3000, "max": 3900, "ideal": 3400}
        ideal_ranges["chlorine"]["ideal"] = 2.0  # Saltwater pools often operate at lower chlorine levels
    else:
        ideal_ranges["salt"] = {"min": 0, "max": 0, "ideal": 0}
    
    # Note: stabilizer and cyanuric acid are the same thing
    if cyanuric_acid != stabilizer:
        # Use the higher value if they differ
        cyanuric_acid = max(cyanuric_acid, stabilizer)
        stabilizer = cyanuric_acid
        recommendations["note"] = "Stabilizer and cyanuric acid are the same chemical. The higher value has been used for calculations."
    
    # Calculate chemical adjustments in the recommended order
    
    # 1. Calcium Hardness
    if calcium_hardness < ideal_ranges["calcium_hardness"]["min"]:
        change_needed = ideal_ranges["calcium_hardness"]["ideal"] - calcium_hardness
        calcium_to_add = (change_needed / 30) * 3.6 * pool_factor
        recommendations["calcium_hardness"] = {
            "status": "low", 
            "current": calcium_hardness, 
            "ideal": ideal_ranges["calcium_hardness"]["ideal"],
            "change_needed": change_needed,
            "calcium_chloride_to_add_lbs": round(calcium_to_add, 2)
        }
    elif calcium_hardness > ideal_ranges["calcium_hardness"]["max"]:
        recommendations["calcium_hardness"] = {
            "status": "high", 
            "current": calcium_hardness, 
            "ideal": ideal_ranges["calcium_hardness"]["ideal"],
            "action": "Partially drain and refill pool with fresh water to dilute"
        }
    else:
        recommendations["calcium_hardness"] = {"status": "ok", "current": calcium_hardness}
    
    # 2. Chlorine/Bromine (based on pool type)
    if pool_type.lower() in ["chlorine", "saltwater"]:
        # Chlorine adjustment
        if chlorine < ideal_ranges["chlorine"]["min"]:
            change_needed = ideal_ranges["chlorine"]["ideal"] - chlorine
            if change_needed < 5:
                chlorine_to_add = ((change_needed / 1) * 2 * pool_factor) / 16
            else:
                chlorine_to_add = ((change_needed / 5) * 10 * pool_factor) / 16
            recommendations["chlorine"] = {
                "status": "low", 
                "current": chlorine, 
                "ideal": ideal_ranges["chlorine"]["ideal"],
                "change_needed": change_needed,
                "calcium_hypochlorite_to_add_lbs": round(chlorine_to_add, 2)
            }
        elif chlorine > ideal_ranges["chlorine"]["max"]:
            change_needed = chlorine - ideal_ranges["chlorine"]["ideal"]
            if change_needed < 5:
                neutralizer_to_add = change_needed * 2.6 * pool_factor / 16
            else:
                neutralizer_to_add = (change_needed / 5) * 13 * pool_factor / 16
            recommendations["chlorine"] = {
                "status": "high", 
                "current": chlorine, 
                "ideal": ideal_ranges["chlorine"]["ideal"],
                "change_needed": change_needed,
                "sodium_thiosulfate_to_add_lbs": round(neutralizer_to_add, 2)
            }
        else:
            recommendations["chlorine"] = {"status": "ok", "current": chlorine}
    elif pool_type.lower() == "bromine":
        # Bromine adjustment
        if bromine < ideal_ranges["bromine"]["min"]:
            change_needed = ideal_ranges["bromine"]["ideal"] - bromine
            bromine_to_add = change_needed * 2.0 * pool_factor / 16
            recommendations["bromine"] = {
                "status": "low", 
                "current": bromine, 
                "ideal": ideal_ranges["bromine"]["ideal"],
                "change_needed": change_needed,
                "bromine_tablets_lbs": round(bromine_to_add, 2)
            }
        elif bromine > ideal_ranges["bromine"]["max"]:
            recommendations["bromine"] = {
                "status": "high", 
                "current": bromine, 
                "ideal": ideal_ranges["bromine"]["ideal"],
                "action": "Stop adding bromine and allow levels to naturally decrease"
            }
        else:
            recommendations["bromine"] = {"status": "ok", "current": bromine}
    
    # 3. Cyanuric Acid/Stabilizer
    if cyanuric_acid < ideal_ranges["cyanuric_acid"]["min"]:
        change_needed = ideal_ranges["cyanuric_acid"]["ideal"] - cyanuric_acid
        if change_needed < 30:
            cya_to_add = (change_needed / 10) * 13 * pool_factor / 16
        else:
            cya_to_add = (change_needed / 30) * 2.5 * pool_factor
        recommendations["cyanuric_acid"] = {
            "status": "low", 
            "current": cyanuric_acid, 
            "ideal": ideal_ranges["cyanuric_acid"]["ideal"],
            "change_needed": change_needed,
            "cyanuric_acid_to_add_lbs": round(cya_to_add, 2)
        }
    elif cyanuric_acid > ideal_ranges["cyanuric_acid"]["max"]:
        recommendations["cyanuric_acid"] = {
            "status": "high", 
            "current": cyanuric_acid, 
            "ideal": ideal_ranges["cyanuric_acid"]["ideal"],
            "action": "Partially drain and refill pool with fresh water to dilute"
        }
    else:
        recommendations["cyanuric_acid"] = {"status": "ok", "current": cyanuric_acid}
    
    # 4. Alkalinity
    if alkalinity < ideal_ranges["alkalinity"]["min"]:
        change_needed = ideal_ranges["alkalinity"]["ideal"] - alkalinity
        if change_needed < 30:
            sodium_bicarb_to_add = (change_needed / 10) * 1.4 * pool_factor
        else:
            sodium_bicarb_to_add = (change_needed / 30) * 4.2 * pool_factor
        recommendations["alkalinity"] = {
            "status": "low", 
            "current": alkalinity, 
            "ideal": ideal_ranges["alkalinity"]["ideal"],
            "change_needed": change_needed,
            "sodium_bicarbonate_to_add_lbs": round(sodium_bicarb_to_add, 2)
        }
    elif alkalinity > ideal_ranges["alkalinity"]["max"]:
        change_needed = alkalinity - ideal_ranges["alkalinity"]["ideal"]
        if change_needed < 30:
            acid_to_add = (change_needed / 10) * 26 * pool_factor / 128
        else:
            acid_to_add = (change_needed / 30) * 76.8 * pool_factor / 128
        recommendations["alkalinity"] = {
            "status": "high", 
            "current": alkalinity, 
            "ideal": ideal_ranges["alkalinity"]["ideal"],
            "change_needed": change_needed,
            "muriatic_acid_to_add_gallons": round(acid_to_add, 2)
        }
    else:
        recommendations["alkalinity"] = {"status": "ok", "current": alkalinity}
    
    # 5. pH
    if pH < ideal_ranges["pH"]["min"]:
        change_needed = ideal_ranges["pH"]["ideal"] - pH
        # For a rough approximation: 1 lb soda ash per 10,000 gallons raises pH by ~0.2
        soda_ash_to_add = (change_needed / 0.2) * pool_factor
        recommendations["pH"] = {
            "status": "low", 
            "current": pH, 
            "ideal": ideal_ranges["pH"]["ideal"],
            "change_needed": change_needed,
            "soda_ash_to_add_lbs": round(soda_ash_to_add, 2)
        }
    elif pH > ideal_ranges["pH"]["max"]:
        change_needed = pH - ideal_ranges["pH"]["ideal"]
        # For a rough approximation: 1 qt acid per 10,000 gallons lowers pH by ~0.2
        acid_to_add = (change_needed / 0.2) * pool_factor
        recommendations["pH"] = {
            "status": "high", 
            "current": pH, 
            "ideal": ideal_ranges["pH"]["ideal"],
            "change_needed": change_needed,
            "muriatic_acid_to_add_quarts": round(acid_to_add, 2)
        }
    else:
        recommendations["pH"] = {"status": "ok", "current": pH}
    
    # 6. Salt (for saltwater pools)
    if pool_type.lower() == "saltwater":
        if salt < ideal_ranges["salt"]["min"]:
            change_needed = ideal_ranges["salt"]["ideal"] - salt
            # Approximately 8.3 pounds of salt raises the level by 1000 ppm in 10,000 gallons
            salt_to_add = (change_needed / 1000) * 8.3 * pool_factor
            recommendations["salt"] = {
                "status": "low", 
                "current": salt, 
                "ideal": ideal_ranges["salt"]["ideal"],
                "change_needed": change_needed,
                "salt_to_add_lbs": round(salt_to_add, 2)
            }
        elif salt > ideal_ranges["salt"]["max"]:
            recommendations["salt"] = {
                "status": "high", 
                "current": salt, 
                "ideal": ideal_ranges["salt"]["ideal"],
                "action": "Partially drain and refill pool with fresh water to dilute"
            }
        else:
            recommendations["salt"] = {"status": "ok", "current": salt}
    
    # Calculate Saturation Index (LSI)
    # This is a simplified calculation and would need more factors for complete accuracy
    # Temperature factor (assuming 78F)
    tf = 0.6
    
    # Calcium hardness factor
    if calcium_hardness < 37:
        cf = 0.1
    elif calcium_hardness < 64:
        cf = 1.3
    elif calcium_hardness < 88:
        cf = 1.5
    elif calcium_hardness < 114:
        cf = 1.6
    elif calcium_hardness < 139:
        cf = 1.7
    elif calcium_hardness < 164:
        cf = 1.8
    elif calcium_hardness < 226:
        cf = 1.9
    elif calcium_hardness < 276:
        cf = 2.0
    elif calcium_hardness < 351:
        cf = 2.1
    elif calcium_hardness < 601:
        cf = 2.2
    else:
        cf = 2.5
    
    # Alkalinity factor
    if alkalinity < 37:
        af = 1.4
    elif alkalinity < 64:
        af = 1.7
    elif alkalinity < 88:
        af = 1.9
    elif alkalinity < 114:
        af = 2.0
    elif alkalinity < 139:
        af = 2.1
    elif alkalinity < 164:
        af = 2.2
    elif alkalinity < 226:
        af = 2.3
    elif alkalinity < 276:
        af = 2.4
    elif alkalinity < 351:
        af = 2.5
    elif alkalinity < 601:
        af = 2.6
    else:
        af = 2.9
    
    # Calculate LSI
    lsi = pH + tf + cf + af - 12.1
    recommendations["lsi"] = {
        "value": round(lsi, 2),
        "status": "balanced" if -0.3 <= lsi <= 0.3 else "unbalanced"
    }
    
    # Add customer name and pool information
    recommendations["pool_info"] = {
        "pool_type": pool_type,
        "pool_size_gallons": pool_size
    }
    
    return recommendations
