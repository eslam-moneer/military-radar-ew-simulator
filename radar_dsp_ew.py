import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq

# ============================================================================
# DOPPLER PROCESSING
# ============================================================================

def calculate_doppler_shift(target_velocity_mps, radar_frequency_hz):
    """
    Calculate the Doppler shift for a moving target.
    
    Doppler shift formula: f_d = (2 * v * f) / c
    where:
        v: target velocity (m/s)
        f: radar frequency (Hz)
        c: speed of light (3e8 m/s)
    """
    c = 3e8
    doppler_shift = (2 * target_velocity_mps * radar_frequency_hz) / c
    return doppler_shift

def generate_doppler_spectrum(target_velocity_mps, radar_frequency_hz, num_samples=1024, snr_db=20):
    """
    Generate a simulated Doppler spectrum with noise.
    """
    doppler_shift = calculate_doppler_shift(target_velocity_mps, radar_frequency_hz)
    
    # Create time vector
    time = np.linspace(0, 1, num_samples)
    
    # Generate the Doppler signal (sinusoid at Doppler frequency)
    signal_power = 10 ** (snr_db / 10)
    target_signal = np.sqrt(signal_power) * np.sin(2 * np.pi * doppler_shift * time)
    
    # Add Gaussian white noise
    noise = np.random.randn(num_samples)
    received_signal = target_signal + noise
    
    # Compute FFT
    fft_result = fft(received_signal)
    freqs = fftfreq(num_samples, time[1] - time[0])
    
    # Only positive frequencies
    positive_freqs = freqs[:num_samples // 2]
    magnitude = np.abs(fft_result[:num_samples // 2])
    
    return positive_freqs, magnitude, doppler_shift

def estimate_target_velocity(doppler_shift_hz, radar_frequency_hz):
    """
    Estimate target velocity from Doppler shift.
    
    Inverse formula: v = (c * f_d) / (2 * f)
    """
    c = 3e8
    velocity = (c * doppler_shift_hz) / (2 * radar_frequency_hz)
    return velocity

# ============================================================================
# FREQUENCY SWEEP ANALYSIS
# ============================================================================

def calculate_rcs_vs_frequency(vertices, faces, freq_array_hz, incident_angle_deg):
    """
    Calculate RCS across a range of frequencies.
    """
    rcs_values = []
    
    for freq in freq_array_hz:
        c = 3e8
        wavelength = c / freq
        k = 2 * np.pi / wavelength
        
        phi_rad = np.radians(incident_angle_deg)
        incident_vector = np.array([np.cos(phi_rad), np.sin(phi_rad), 0])
        
        total_scattered_field = 0 + 0j
        
        for face_indices in faces:
            v1, v2, v3 = vertices[face_indices]
            
            # Calculate normal
            vec1 = v2 - v1
            vec2 = v3 - v1
            normal = np.cross(vec1, vec2)
            norm_mag = np.linalg.norm(normal)
            if norm_mag < 1e-10:
                normal = np.array([0, 0, 1])
            else:
                normal = normal / norm_mag
            
            if np.dot(normal, incident_vector) < 0:
                continue
            
            centroid = (v1 + v2 + v3) / 3.0
            area = 0.5 * np.linalg.norm(np.cross(v2 - v1, v3 - v1))
            projected_area = area * np.abs(np.dot(normal, incident_vector))
            phase_term = np.exp(1j * 2 * k * np.dot(incident_vector, centroid))
            
            total_scattered_field += projected_area * phase_term
        
        rcs = (4 * np.pi / wavelength**2) * np.abs(total_scattered_field)**2
        rcs_values.append(rcs)
    
    return np.array(rcs_values)

# ============================================================================
# JAMMING SIMULATION (DRFM - Digital Radio Frequency Memory)
# ============================================================================

class DRFMJammer:
    """
    Digital Radio Frequency Memory (DRFM) Jammer simulation.
    """
    
    def __init__(self, jammer_power_mw=10.0, jammer_type='noise'):
        """
        Initialize DRFM jammer.
        
        jammer_type: 'noise' (Noise Jamming) or 'deception' (False Targets)
        """
        self.jammer_power = jammer_power_mw * 1e6  # Convert to Watts
        self.jammer_type = jammer_type
    
    def noise_jamming(self, radar_signal, snr_db=10):
        """
        Noise Jamming: Transmit broadband noise to mask target returns.
        """
        jammer_signal = np.sqrt(self.jammer_power) * np.random.randn(len(radar_signal))
        combined_signal = radar_signal + jammer_signal
        return combined_signal
    
    def deception_jamming(self, radar_signal, num_false_targets=3, velocity_spread_mps=100):
        """
        Deception Jamming: Create false targets at different velocities.
        """
        false_target_signals = np.zeros_like(radar_signal)
        
        for i in range(num_false_targets):
            # Random velocity for false target
            false_velocity = np.random.uniform(-velocity_spread_mps, velocity_spread_mps)
            
            # Generate false target signal (similar to real target but at different velocity)
            false_signal = np.sqrt(self.jammer_power / num_false_targets) * np.sin(
                2 * np.pi * (i + 1) * 100 * np.linspace(0, 1, len(radar_signal))
            )
            false_target_signals += false_signal
        
        combined_signal = radar_signal + false_target_signals
        return combined_signal
    
    def calculate_sjr(self, target_power_dbm, radar_frequency_hz, range_km):
        """
        Calculate Signal-to-Jammer Ratio (SJR).
        
        SJR = Target Power / Jammer Power
        """
        target_power = 10 ** (target_power_dbm / 10)  # Convert from dBm to mW
        sjr_linear = target_power / (self.jammer_power / 1e-3)  # Normalize jammer to mW
        sjr_db = 10 * np.log10(sjr_linear)
        return sjr_db

def simulate_radar_with_jamming(target_rcs_m2, target_velocity_mps, radar_params, jammer_params):
    """
    Simulate complete radar system with jamming.
    
    Returns: detected_signal, doppler_spectrum, sjr_db
    """
    c = 3e8
    freq = radar_params['frequency']
    wavelength = c / freq
    
    # Generate target signal
    time = np.linspace(0, 1, 1024)
    doppler_shift = calculate_doppler_shift(target_velocity_mps, freq)
    target_signal = np.sqrt(target_rcs_m2) * np.sin(2 * np.pi * doppler_shift * time)
    
    # Apply jamming
    jammer = DRFMJammer(jammer_params['power_mw'], jammer_params['type'])
    
    if jammer_params['enabled']:
        if jammer_params['type'] == 'noise':
            received_signal = jammer.noise_jamming(target_signal)
        else:
            received_signal = jammer.deception_jamming(target_signal, num_false_targets=3)
    else:
        received_signal = target_signal + np.random.randn(len(target_signal)) * 0.1
    
    # Compute Doppler spectrum
    fft_result = np.fft.fft(received_signal)
    freqs = np.fft.fftfreq(len(received_signal), time[1] - time[0])
    positive_freqs = freqs[:len(received_signal) // 2]
    magnitude = np.abs(fft_result[:len(received_signal) // 2])
    
    # Calculate SJR
    target_power_dbm = 10 * np.log10(target_rcs_m2 * 1000)  # Convert to dBm
    sjr_db = jammer.calculate_sjr(target_power_dbm, freq, radar_params.get('range_km', 100))
    
    return received_signal, (positive_freqs, magnitude), sjr_db, doppler_shift

# ============================================================================
# RADAR RANGE EQUATION WITH JAMMING
# ============================================================================

def radar_range_with_jamming(Pt, G, freq, sigma, Pr_min, jammer_power_mw=0, jammer_enabled=False):
    """
    Calculate detection range considering jamming.
    
    With jamming, the effective noise power increases:
    P_n_eff = P_n + P_jammer
    """
    c = 3e8
    wavelength = c / freq
    
    if jammer_enabled and jammer_power_mw > 0:
        # Jammer increases effective noise floor
        jammer_power_watts = jammer_power_mw * 1e6
        effective_noise = Pr_min + (jammer_power_watts * 1e-12)
    else:
        effective_noise = Pr_min
    
    numerator = Pt * (G**2) * (wavelength**2) * sigma
    denominator = ((4 * np.pi)**3) * effective_noise
    
    try:
        max_range = (numerator / denominator)**0.25
    except:
        max_range = 0
    
    return max_range

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def m2_to_dbsm(sigma):
    """Convert square meters to dBsm."""
    sigma = np.maximum(sigma, 1e-10)
    return 10 * np.log10(sigma)

def dbsm_to_m2(dbsm):
    """Convert dBsm to square meters."""
    return 10 ** (dbsm / 10)

def generate_frequency_array(start_ghz=1, end_ghz=40, num_points=100):
    """Generate frequency array for sweep analysis."""
    return np.linspace(start_ghz * 1e9, end_ghz * 1e9, num_points)

def classify_frequency_band(frequency_hz):
    """Classify frequency into radar band."""
    freq_ghz = frequency_hz / 1e9
    
    if freq_ghz < 0.5:
        return "VHF"
    elif freq_ghz < 2:
        return "UHF"
    elif freq_ghz < 4:
        return "L-Band"
    elif freq_ghz < 8:
        return "S-Band"
    elif freq_ghz < 12:
        return "C-Band"
    elif freq_ghz < 18:
        return "X-Band"
    elif freq_ghz < 27:
        return "Ku-Band"
    else:
        return "Ka-Band"
