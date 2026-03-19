import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from aircraft_models import get_aircraft_model, get_aircraft_info
from radar_dsp_ew import (
    calculate_doppler_shift, generate_doppler_spectrum, estimate_target_velocity,
    calculate_rcs_vs_frequency, DRFMJammer, simulate_radar_with_jamming,
    radar_range_with_jamming, m2_to_dbsm, generate_frequency_array,
    classify_frequency_band
)

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="Military Radar & EW Simulator PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛰️ Military Radar & Electronic Warfare (EW) Simulator PRO")
st.markdown("""
Advanced simulation of radar systems with **Frequency Sweeping**, **Doppler Processing**, and **Electronic Warfare (DRFM Jamming)**.
This professional-grade tool demonstrates real-world radar signal processing and counter-measures.
""")

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

st.sidebar.header("⚙️ RADAR CONFIGURATION")
freq_ghz = st.sidebar.slider("Radar Frequency (GHz)", 1.0, 40.0, 10.0, 0.5)
freq = freq_ghz * 1e9

st.sidebar.header("🛩️ TARGET SELECTION")
aircraft_type = st.sidebar.selectbox(
    "Select Aircraft",
    ["F-22 Raptor (Stealth)", "F-16 Fighting Falcon", "MQ-9 Reaper Drone"]
)

st.sidebar.header("📡 TRANSMITTER PARAMETERS")
Pt_mw = st.sidebar.slider("Transmit Power (MW)", 0.1, 10.0, 1.0, 0.1)
Pt = Pt_mw * 1e6
G_db = st.sidebar.slider("Antenna Gain (dB)", 20, 50, 40, 2)
G = 10**(G_db/10)
Pr_min = 1e-13

st.sidebar.header("🎯 TARGET DYNAMICS")
target_velocity_mps = st.sidebar.slider("Target Velocity (m/s)", -500, 500, 100, 10)
incident_angle = st.sidebar.slider("Incident Angle (degrees)", 0, 360, 0, 5)

st.sidebar.header("🚨 JAMMING PARAMETERS")
jamming_enabled = st.sidebar.checkbox("Enable Jamming", value=False)
if jamming_enabled:
    jammer_type = st.sidebar.radio("Jammer Type", ["Noise Jamming", "Deception Jamming"])
    jammer_power_mw = st.sidebar.slider("Jammer Power (MW)", 0.1, 50.0, 5.0, 0.5)
else:
    jammer_type = "Noise Jamming"
    jammer_power_mw = 0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_facet_normal(v1, v2, v3):
    """Calculate normal vector of a triangular facet."""
    vec1 = v2 - v1
    vec2 = v3 - v1
    normal = np.cross(vec1, vec2)
    norm_mag = np.linalg.norm(normal)
    if norm_mag < 1e-10:
        return np.array([0, 0, 1])
    return normal / norm_mag

def physical_optics_rcs(vertices, faces, freq, incident_angle_deg):
    """Calculate RCS using Physical Optics approximation."""
    c = 3e8
    wavelength = c / freq
    k = 2 * np.pi / wavelength
    
    phi_rad = np.radians(incident_angle_deg)
    incident_vector = np.array([np.cos(phi_rad), np.sin(phi_rad), 0])
    
    total_scattered_field = 0 + 0j
    
    for face_indices in faces:
        v1, v2, v3 = vertices[face_indices]
        normal = calculate_facet_normal(v1, v2, v3)
        
        if np.dot(normal, incident_vector) < 0:
            continue
        
        centroid = (v1 + v2 + v3) / 3.0
        area = 0.5 * np.linalg.norm(np.cross(v2 - v1, v3 - v1))
        projected_area = area * np.abs(np.dot(normal, incident_vector))
        phase_term = np.exp(1j * 2 * k * np.dot(incident_vector, centroid))
        
        total_scattered_field += projected_area * phase_term
    
    rcs = (4 * np.pi / wavelength**2) * np.abs(total_scattered_field)**2
    return rcs

def plot_3d_model(vertices, faces, title, color='cyan'):
    """Create a 3D plot of the aircraft model."""
    fig = go.Figure()
    
    for face in faces:
        v = vertices[face]
        fig.add_trace(go.Scatter3d(
            x=v[:, 0], y=v[:, 1], z=v[:, 2],
            mode='lines',
            line=dict(color=color, width=2),
            hoverinfo='skip',
            showlegend=False
        ))
    
    fig.update_layout(
        title=title,
        scene=dict(xaxis_title='X (m)', yaxis_title='Y (m)', zaxis_title='Z (m)', aspectmode='data'),
        height=500,
        showlegend=False
    )
    return fig

# ============================================================================
# CREATE TABS FOR DIFFERENT ANALYSES
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 RCS & Detection",
    "📈 Frequency Sweep",
    "🚁 Doppler Analysis",
    "⚔️ Jamming & EW"
])

# ============================================================================
# TAB 1: RCS & DETECTION RANGE
# ============================================================================

with tab1:
    st.header("Radar Cross Section & Detection Range Analysis")
    
    vertices, faces = get_aircraft_model(aircraft_type, scale=1.0)
    aircraft_info = get_aircraft_info(aircraft_type)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("3D Aircraft Model")
        fig_3d = plot_3d_model(vertices, faces, f"{aircraft_type}", color=aircraft_info.get('color', 'cyan'))
        st.plotly_chart(fig_3d, use_container_width=True)
    
    with col2:
        st.subheader("📊 RCS Metrics")
        rcs = physical_optics_rcs(vertices, faces, freq, incident_angle)
        rcs_dbsm = m2_to_dbsm(rcs)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("RCS (m²)", f"{rcs:.6f}")
        with col_m2:
            st.metric("RCS (dBsm)", f"{rcs_dbsm:.2f}")
        
        sigma_linear = np.maximum(rcs, 1e-10)
        max_range = radar_range_with_jamming(Pt, G, freq, sigma_linear, Pr_min, jammer_power_mw, jamming_enabled)
        st.metric("Max Detection Range", f"{max_range/1000:.2f} km")
        
        st.info(f"""
        **{aircraft_type}**
        
        {aircraft_info.get('description', '')}
        
        **Typical RCS (head-on):**
        - {aircraft_info.get('typical_rcs_dbsm', 'N/A')} dBsm
        - {aircraft_info.get('typical_rcs_m2', 'N/A')} m²
        
        **Current Radar Configuration:**
        - Frequency: {freq_ghz} GHz (λ = {3e8/freq*100:.2f} cm)
        - Band: {classify_frequency_band(freq)}
        - Transmit Power: {Pt_mw} MW
        - Antenna Gain: {G_db} dB
        - Incident Angle: {incident_angle}°
        - Target Velocity: {target_velocity_mps} m/s
        """)
    
    # Polar plot
    st.subheader("📡 360° Radar Signature")
    with st.spinner("Computing RCS signature..."):
        angles = np.linspace(0, 360, 360)
        rcs_values = [m2_to_dbsm(physical_optics_rcs(vertices, faces, freq, a)) for a in angles]
    
    fig_polar = go.Figure()
    fig_polar.add_trace(go.Scatterpolar(
        r=rcs_values, theta=angles, fill='toself',
        line=dict(color=aircraft_info.get('color', 'red'), width=2)
    ))
    fig_polar.update_layout(
        title=f"RCS Signature - {aircraft_type}",
        height=600,
        polar=dict(radialaxis=dict(visible=True, range=[min(rcs_values), max(rcs_values)]))
    )
    st.plotly_chart(fig_polar, use_container_width=True)

# ============================================================================
# TAB 2: FREQUENCY SWEEP ANALYSIS
# ============================================================================

with tab2:
    st.header("Frequency Sweep Analysis (1-40 GHz)")
    st.markdown("""
    This analysis shows how RCS varies across the radar spectrum. Different frequency bands interact differently with target features:
    - **Low Frequencies (VHF/UHF)**: Stealth is harder; larger wavelengths "see through" shaping.
    - **High Frequencies (X/Ku/Ka-Band)**: Stealth is more effective; smaller wavelengths are absorbed by RAM.
    """)
    
    vertices, faces = get_aircraft_model(aircraft_type, scale=1.0)
    
    with st.spinner("Sweeping frequencies (1-40 GHz)..."):
        freq_array = generate_frequency_array(start_ghz=1, end_ghz=40, num_points=100)
        rcs_sweep = calculate_rcs_vs_frequency(vertices, faces, freq_array, incident_angle)
        rcs_sweep_dbsm = m2_to_dbsm(rcs_sweep)
    
    # Create frequency sweep plot
    fig_sweep = go.Figure()
    fig_sweep.add_trace(go.Scatter(
        x=freq_array / 1e9,
        y=rcs_sweep_dbsm,
        mode='lines+markers',
        name=aircraft_type,
        line=dict(color=aircraft_info.get('color', 'blue'), width=3)
    ))
    
    # Add frequency band markers
    bands = [
        (1, 2, "L-Band", "lightyellow"),
        (2, 4, "S-Band", "lightblue"),
        (4, 8, "C-Band", "lightgreen"),
        (8, 12, "X-Band", "lightcoral"),
        (12, 18, "Ku-Band", "lightsalmon"),
        (18, 27, "K-Band", "lightpink"),
    ]
    
    for start, end, label, color in bands:
        fig_sweep.add_vrect(x0=start, x1=end, fillcolor=color, opacity=0.2, layer="below", line_width=0)
    
    fig_sweep.update_layout(
        title="RCS vs. Frequency (1-40 GHz)",
        xaxis_title="Frequency (GHz)",
        yaxis_title="RCS (dBsm)",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig_sweep, use_container_width=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Min RCS (dBsm)", f"{min(rcs_sweep_dbsm):.2f}")
    with col2:
        st.metric("Max RCS (dBsm)", f"{max(rcs_sweep_dbsm):.2f}")
    with col3:
        st.metric("Mean RCS (dBsm)", f"{np.mean(rcs_sweep_dbsm):.2f}")
    with col4:
        st.metric("Std Dev (dBsm)", f"{np.std(rcs_sweep_dbsm):.2f}")

# ============================================================================
# TAB 3: DOPPLER ANALYSIS
# ============================================================================

with tab3:
    st.header("Doppler Velocity Detection")
    st.markdown("""
    Doppler radar measures the velocity of moving targets by detecting the frequency shift of reflected signals.
    The Doppler shift is: **f_d = (2 × v × f) / c**
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Doppler Spectrum")
        
        vertices, faces = get_aircraft_model(aircraft_type, scale=1.0)
        
        with st.spinner("Computing Doppler spectrum..."):
            freqs, magnitude, doppler_shift = generate_doppler_spectrum(
                target_velocity_mps, freq, num_samples=1024, snr_db=15
            )
        
        fig_doppler = go.Figure()
        fig_doppler.add_trace(go.Scatter(
            x=freqs, y=magnitude,
            mode='lines',
            name='Doppler Spectrum',
            line=dict(color='red', width=2)
        ))
        fig_doppler.update_layout(
            title="FFT Doppler Spectrum",
            xaxis_title="Frequency (Hz)",
            yaxis_title="Magnitude",
            height=400
        )
        st.plotly_chart(fig_doppler, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Velocity Estimation")
        
        estimated_velocity = estimate_target_velocity(doppler_shift, freq)
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.metric("Doppler Shift (Hz)", f"{doppler_shift:.2f}")
        with col_v2:
            st.metric("Estimated Velocity (m/s)", f"{estimated_velocity:.2f}")
        
        st.metric("Target Velocity (Actual)", f"{target_velocity_mps} m/s")
        
        error = abs(estimated_velocity - target_velocity_mps)
        error_percent = (error / abs(target_velocity_mps)) * 100 if target_velocity_mps != 0 else 0
        st.metric("Estimation Error", f"{error:.2f} m/s ({error_percent:.1f}%)")
        
        st.info(f"""
        **Doppler Processing Details:**
        - Wavelength: {3e8/freq*100:.2f} cm
        - Doppler Shift: {doppler_shift:.2f} Hz
        - SNR: 15 dB
        - Velocity Accuracy: ±{error:.2f} m/s
        """)

# ============================================================================
# TAB 4: JAMMING & ELECTRONIC WARFARE
# ============================================================================

with tab4:
    st.header("Electronic Warfare (EW) - DRFM Jamming Simulation")
    st.markdown("""
    **Digital Radio Frequency Memory (DRFM)** is an advanced jamming technique that:
    - **Noise Jamming**: Transmits broadband noise to increase the radar's noise floor.
    - **Deception Jamming**: Creates false targets to confuse radar operators.
    """)
    
    vertices, faces = get_aircraft_model(aircraft_type, scale=1.0)
    rcs = physical_optics_rcs(vertices, faces, freq, incident_angle)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📡 Received Signal")
        
        with st.spinner("Simulating radar with jamming..."):
            radar_params = {
                'frequency': freq,
                'range_km': 100
            }
            jammer_params = {
                'enabled': jamming_enabled,
                'power_mw': jammer_power_mw,
                'type': 'noise' if jammer_type == "Noise Jamming" else 'deception'
            }
            
            received_signal, doppler_spec, sjr_db, doppler_shift = simulate_radar_with_jamming(
                rcs, target_velocity_mps, radar_params, jammer_params
            )
        
        # Plot received signal
        time = np.linspace(0, 1, len(received_signal))
        fig_signal = go.Figure()
        fig_signal.add_trace(go.Scatter(
            x=time, y=received_signal,
            mode='lines',
            name='Received Signal',
            line=dict(color='blue', width=1)
        ))
        fig_signal.update_layout(
            title="Received Radar Signal (Time Domain)",
            xaxis_title="Time (s)",
            yaxis_title="Amplitude",
            height=400
        )
        st.plotly_chart(fig_signal, use_container_width=True)
    
    with col2:
        st.subheader("⚔️ Jamming Metrics")
        
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            st.metric("Jammer Status", "ACTIVE" if jamming_enabled else "INACTIVE")
        with col_j2:
            st.metric("Jammer Type", jammer_type)
        
        st.metric("Signal-to-Jammer Ratio (SJR)", f"{sjr_db:.2f} dB")
        
        # Detection range with jamming
        sigma_linear = np.maximum(rcs, 1e-10)
        range_no_jam = radar_range_with_jamming(Pt, G, freq, sigma_linear, Pr_min, 0, False)
        range_with_jam = radar_range_with_jamming(Pt, G, freq, sigma_linear, Pr_min, jammer_power_mw, jamming_enabled)
        
        st.metric("Detection Range (No Jamming)", f"{range_no_jam/1000:.2f} km")
        st.metric("Detection Range (With Jamming)", f"{range_with_jam/1000:.2f} km")
        
        if jamming_enabled:
            range_reduction = ((range_no_jam - range_with_jam) / range_no_jam) * 100
            st.metric("Range Reduction", f"{range_reduction:.1f}%")
        
        st.info(f"""
        **Jamming Analysis:**
        - Jammer Power: {jammer_power_mw} MW
        - Target RCS: {m2_to_dbsm(rcs):.2f} dBsm
        - SJR: {sjr_db:.2f} dB
        - Jamming Effectiveness: {'HIGH' if sjr_db < 0 else 'MEDIUM' if sjr_db < 10 else 'LOW'}
        """)
    
    # Doppler spectrum with jamming
    st.subheader("📊 Doppler Spectrum (With/Without Jamming)")
    
    freqs_doppler, magnitude_doppler = doppler_spec
    
    fig_jam_doppler = go.Figure()
    fig_jam_doppler.add_trace(go.Scatter(
        x=freqs_doppler, y=magnitude_doppler,
        mode='lines',
        name='Doppler Spectrum',
        line=dict(color='red', width=2)
    ))
    fig_jam_doppler.update_layout(
        title="Doppler Spectrum (Jamming Enabled)" if jamming_enabled else "Doppler Spectrum (Clean)",
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        height=400
    )
    st.plotly_chart(fig_jam_doppler, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**About this PRO Simulator:**
This advanced tool demonstrates professional-grade radar signal processing and electronic warfare concepts:
- **Physical Optics (PO)**: 3D facet-based RCS calculation
- **Frequency Analysis**: RCS behavior across 1-40 GHz spectrum
- **Doppler Processing**: FFT-based velocity estimation
- **DRFM Jamming**: Noise and deception jamming simulation
- **Signal-to-Jammer Ratio**: Real-time EW effectiveness metrics

**Educational Use:** Designed for ECE students studying radar systems, signal processing, and electronic warfare.
""")
