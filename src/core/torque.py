from __future__ import annotations

from typing import Dict, List, Optional, Tuple

class TorqueCurveGenerator:
    """
    Handles automatic generation of torque curves for engines.
    Supports both naturally aspirated and turbocharged engines.
    """
    
    @staticmethod
    def generate_torque_curve(hp: float, min_rpm: float, max_rpm: float, 
                             turbocharged: bool = False) -> List[Tuple[float, float]]:
        """
        Generate a torque curve based on engine specifications.
        
        Args:
            hp: Engine horsepower
            min_rpm: Minimum RPM
            max_rpm: Maximum RPM
            turbocharged: Whether engine is turbocharged
            
        Returns:
            List of (normalized_rpm, torque) tuples
        """
        # Validate input parameters
        if hp <= 0:
            raise ValueError("Horsepower must be greater than 0")
        if min_rpm < 0:
            raise ValueError("Minimum RPM cannot be negative")
        if max_rpm <= min_rpm:
            raise ValueError("Maximum RPM must be greater than minimum RPM")
        
        # Calculate peak RPM (approximately 65% of max RPM)
        peak_rpm = min_rpm + (max_rpm - min_rpm) * 0.65
        
        # Prevent division by zero
        if peak_rpm <= 0:
            raise ValueError("Peak RPM calculation resulted in zero or negative value")
        
        # Base torque calculation: Torque = (HP × 9549) / Peak RPM
        base_torque = (hp * 9549) / peak_rpm
        
        # Generate 10 evenly spaced RPM points
        rpm_points = []
        for i in range(10):
            rpm = min_rpm + (max_rpm - min_rpm) * (i / 9.0)
            rpm_points.append(rpm)
        
        # Generate torque values
        torque_points = []
        for rpm in rpm_points:
            if turbocharged:
                # Turbocharged engines have flatter, higher mid-range curves
                if rpm < peak_rpm * 0.8:
                    # Below peak: gradual rise
                    factor = (rpm / (peak_rpm * 0.8)) ** 0.7
                else:
                    # Above peak: gradual decline
                    factor = 1.0 - ((rpm - peak_rpm * 0.8) / (max_rpm - peak_rpm * 0.8)) ** 0.5
                    factor = max(0.7, factor)
            else:
                # Naturally aspirated: more traditional curve
                if rpm < peak_rpm:
                    # Below peak: gradual rise
                    factor = (rpm / peak_rpm) ** 0.8
                else:
                    # Above peak: steeper decline
                    factor = 1.0 - ((rpm - peak_rpm) / (max_rpm - peak_rpm)) ** 0.3
                    factor = max(0.5, factor)
            
            torque = base_torque * factor
            # Normalize RPM for XML: normRpm = RPM / maxRPM
            norm_rpm = rpm / max_rpm
            
            torque_points.append((norm_rpm, torque))
        
        return torque_points


