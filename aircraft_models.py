import numpy as np

def create_f22_model(scale=1.0):
    """
    Create a detailed F-22 Raptor stealth fighter model.
    Characteristics: Faceted design, internal weapon bays, angled surfaces.
    """
    s = scale
    vertices = np.array([
        # Nose cone (pointed)
        [3.0*s, 0, 0.15*s],      # 0: Nose tip
        [2.5*s, 0.3*s, 0.1*s],   # 1: Right nose
        [2.5*s, -0.3*s, 0.1*s],  # 2: Left nose
        
        # Forward fuselage (diamond cross-section)
        [1.5*s, 0.5*s, 0.2*s],   # 3: Right forward
        [1.5*s, -0.5*s, 0.2*s],  # 4: Left forward
        [1.5*s, 0, 0.4*s],       # 5: Top forward
        [1.5*s, 0, -0.1*s],      # 6: Bottom forward
        
        # Mid fuselage (wider)
        [0.5*s, 0.8*s, 0.25*s],  # 7: Right mid
        [0.5*s, -0.8*s, 0.25*s], # 8: Left mid
        [0.5*s, 0, 0.5*s],       # 9: Top mid
        [0.5*s, 0, -0.15*s],     # 10: Bottom mid
        
        # Wings (delta-canard style)
        [0.8*s, 1.5*s, 0.1*s],   # 11: Right wing tip
        [0.8*s, -1.5*s, 0.1*s],  # 12: Left wing tip
        
        # Vertical stabilizers (angled for stealth)
        [-0.5*s, 0.6*s, 0.6*s],  # 13: Right vertical stab
        [-0.5*s, -0.6*s, 0.6*s], # 14: Left vertical stab
        
        # Tail fuselage
        [-1.0*s, 0.3*s, 0.2*s],  # 15: Right tail
        [-1.0*s, -0.3*s, 0.2*s], # 16: Left tail
        [-1.0*s, 0, 0.35*s],     # 17: Top tail
        [-1.0*s, 0, -0.1*s],     # 18: Bottom tail
        
        # Tail cone
        [-1.8*s, 0, 0.15*s],     # 19: Tail tip
    ])
    
    faces = np.array([
        # Nose cone facets
        [0, 1, 5], [0, 2, 5], [0, 1, 6], [0, 2, 6],
        
        # Forward fuselage
        [1, 3, 5], [2, 4, 5], [1, 3, 6], [2, 4, 6],
        [3, 5, 9], [4, 5, 9], [3, 6, 10], [4, 6, 10],
        
        # Wings
        [3, 11, 7], [4, 12, 8], [5, 11, 9], [5, 12, 9],
        [7, 11, 9], [8, 12, 9],
        
        # Vertical stabilizers
        [9, 13, 17], [9, 14, 17], [10, 13, 18], [10, 14, 18],
        
        # Tail fuselage
        [15, 17, 19], [16, 17, 19], [15, 18, 19], [16, 18, 19],
    ])
    
    return vertices, faces

def create_f16_model(scale=1.0):
    """
    Create a detailed F-16 Fighting Falcon conventional fighter model.
    Characteristics: Large vertical tail, rounded intake, more reflective surfaces.
    """
    s = scale
    vertices = np.array([
        # Nose cone (rounded)
        [3.0*s, 0, 0.25*s],      # 0: Nose tip
        [2.8*s, 0.2*s, 0.2*s],   # 1: Right nose
        [2.8*s, -0.2*s, 0.2*s],  # 2: Left nose
        [2.6*s, 0.4*s, 0.15*s],  # 3: Right nose lower
        [2.6*s, -0.4*s, 0.15*s], # 4: Left nose lower
        
        # Intake (large, prominent)
        [2.0*s, 0.5*s, -0.1*s],  # 5: Right intake
        [2.0*s, -0.5*s, -0.1*s], # 6: Left intake
        [2.0*s, 0, 0.3*s],       # 7: Top intake
        
        # Forward fuselage
        [1.2*s, 0.6*s, 0.3*s],   # 8: Right forward
        [1.2*s, -0.6*s, 0.3*s],  # 9: Left forward
        [1.2*s, 0, 0.6*s],       # 10: Top forward
        [1.2*s, 0, -0.2*s],      # 11: Bottom forward
        
        # Mid fuselage (wider)
        [0.4*s, 1.0*s, 0.35*s],  # 12: Right mid
        [0.4*s, -1.0*s, 0.35*s], # 13: Left mid
        [0.4*s, 0, 0.7*s],       # 14: Top mid
        [0.4*s, 0, -0.2*s],      # 15: Bottom mid
        
        # Wings (swept)
        [0.6*s, 2.0*s, 0.2*s],   # 16: Right wing tip
        [0.6*s, -2.0*s, 0.2*s],  # 17: Left wing tip
        
        # Large vertical tail (prominent feature)
        [-0.8*s, 0, 1.2*s],      # 18: Vertical tail top
        [-0.8*s, 0.3*s, 0.3*s],  # 19: Vertical tail right
        [-0.8*s, -0.3*s, 0.3*s], # 20: Vertical tail left
        
        # Tail fuselage
        [-1.2*s, 0.4*s, 0.3*s],  # 21: Right tail
        [-1.2*s, -0.4*s, 0.3*s], # 22: Left tail
        [-1.2*s, 0, 0.6*s],      # 23: Top tail
        [-1.2*s, 0, -0.2*s],     # 24: Bottom tail
        
        # Tail cone
        [-2.0*s, 0, 0.25*s],     # 25: Tail tip
    ])
    
    faces = np.array([
        # Nose cone
        [0, 1, 7], [0, 2, 7], [0, 3, 11], [0, 4, 11],
        [1, 3, 7], [2, 4, 7],
        
        # Intake (large)
        [5, 6, 7], [5, 6, 11],
        
        # Forward fuselage
        [1, 8, 10], [2, 9, 10], [3, 8, 11], [4, 9, 11],
        [8, 10, 14], [9, 10, 14], [8, 11, 15], [9, 11, 15],
        
        # Wings
        [8, 16, 12], [9, 17, 13], [10, 16, 14], [10, 17, 14],
        [12, 16, 14], [13, 17, 14],
        
        # Large vertical tail (prominent)
        [14, 18, 19], [14, 18, 20], [15, 18, 19], [15, 18, 20],
        [19, 20, 18],
        
        # Tail fuselage
        [21, 23, 25], [22, 23, 25], [21, 24, 25], [22, 24, 25],
    ])
    
    return vertices, faces

def create_drone_model(scale=1.0):
    """
    Create a detailed MQ-9 Reaper-style military drone model.
    Characteristics: Slender fuselage, high-mounted wings, small cross-section.
    """
    s = scale
    vertices = np.array([
        # Nose cone (pointed, small)
        [2.5*s, 0, 0.08*s],      # 0: Nose tip
        [2.3*s, 0.1*s, 0.06*s],  # 1: Right nose
        [2.3*s, -0.1*s, 0.06*s], # 2: Left nose
        
        # Forward fuselage (very slender)
        [1.5*s, 0.15*s, 0.1*s],  # 3: Right forward
        [1.5*s, -0.15*s, 0.1*s], # 4: Left forward
        [1.5*s, 0, 0.2*s],       # 5: Top forward
        [1.5*s, 0, -0.05*s],     # 6: Bottom forward
        
        # Mid fuselage (payload bay)
        [0.5*s, 0.2*s, 0.12*s],  # 7: Right mid
        [0.5*s, -0.2*s, 0.12*s], # 8: Left mid
        [0.5*s, 0, 0.25*s],      # 9: Top mid
        [0.5*s, 0, -0.08*s],     # 10: Bottom mid
        
        # High-mounted wings (inverted gull)
        [0.7*s, 1.8*s, 0.35*s],  # 11: Right wing tip
        [0.7*s, -1.8*s, 0.35*s], # 12: Left wing tip
        
        # Tail boom (very thin)
        [-1.0*s, 0.1*s, 0.1*s],  # 13: Right tail boom
        [-1.0*s, -0.1*s, 0.1*s], # 14: Left tail boom
        [-1.0*s, 0, 0.2*s],      # 15: Top tail boom
        [-1.0*s, 0, -0.05*s],    # 16: Bottom tail boom
        
        # V-tail (characteristic of drones)
        [-1.8*s, 0.3*s, 0.3*s],  # 17: Right V-tail
        [-1.8*s, -0.3*s, 0.3*s], # 18: Left V-tail
        [-1.8*s, 0, -0.1*s],     # 19: Bottom V-tail
    ])
    
    faces = np.array([
        # Nose cone
        [0, 1, 5], [0, 2, 5], [0, 1, 6], [0, 2, 6],
        
        # Forward fuselage
        [1, 3, 5], [2, 4, 5], [1, 3, 6], [2, 4, 6],
        [3, 5, 9], [4, 5, 9], [3, 6, 10], [4, 6, 10],
        
        # High-mounted wings
        [3, 11, 7], [4, 12, 8], [5, 11, 9], [5, 12, 9],
        [7, 11, 9], [8, 12, 9],
        
        # Tail boom
        [13, 15, 17], [14, 15, 18], [13, 16, 19], [14, 16, 19],
        
        # V-tail
        [15, 17, 19], [15, 18, 19],
    ])
    
    return vertices, faces

def get_aircraft_model(aircraft_name, scale=1.0):
    """Get the 3D facet model for a specified aircraft."""
    models = {
        "F-22 Raptor (Stealth)": create_f22_model,
        "F-16 Fighting Falcon": create_f16_model,
        "MQ-9 Reaper Drone": create_drone_model,
    }
    
    if aircraft_name in models:
        return models[aircraft_name](scale)
    else:
        raise ValueError(f"Aircraft model '{aircraft_name}' not found.")

def get_aircraft_info(aircraft_name):
    """Get realistic RCS information for each aircraft."""
    info = {
        "F-22 Raptor (Stealth)": {
            "description": "5th-gen stealth fighter with faceted design and internal weapon bays",
            "typical_rcs_dbsm": -40,
            "typical_rcs_m2": 0.0001,
            "color": "red"
        },
        "F-16 Fighting Falcon": {
            "description": "4th-gen conventional fighter with large vertical tail and rounded fuselage",
            "typical_rcs_dbsm": 10,
            "typical_rcs_m2": 10.0,
            "color": "blue"
        },
        "MQ-9 Reaper Drone": {
            "description": "High-altitude long-endurance drone with slender fuselage and high-mounted wings",
            "typical_rcs_dbsm": -5,
            "typical_rcs_m2": 0.316,
            "color": "green"
        },
    }
    
    return info.get(aircraft_name, {})
