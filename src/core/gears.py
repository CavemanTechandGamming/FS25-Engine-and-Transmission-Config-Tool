from __future__ import annotations

from typing import Dict, List, Optional, Tuple

class GearRatioCalculator:
    """
    Handles gear ratio calculations for transmissions.
    Supports low gearing options for enhanced torque output.
    """
    
    @staticmethod
    def calculate_gear_ratios(transmission_type: str, num_forward: int, 
                             num_reverse: int, top_speed: float,
                             enable_low_gearing: bool = False, 
                             low_gear_boost: float = 25.0) -> Dict[str, List[float]]:
        """
        Calculate gear ratios for transmission.
        
        Args:
            transmission_type: Type of transmission (Manual, Automatic, etc.)
            num_forward: Number of forward gears
            num_reverse: Number of reverse gears
            top_speed: Top speed in km/h
            enable_low_gearing: Whether to enable low gearing
            low_gear_boost: Percentage boost for low gears
            
        Returns:
            Dictionary with 'forward' and 'reverse' gear ratios
        """
        # Validate input parameters to prevent division by zero
        if num_forward <= 0:
            raise ValueError("Number of forward gears must be greater than 0")
        if num_reverse < 0:
            raise ValueError("Number of reverse gears cannot be negative")
        if top_speed <= 0:
            raise ValueError("Top speed must be greater than 0")
        
        # Base gear ratios based on transmission type
        forward_ratios = []
        reverse_ratios = []
        
        # Calculate forward gear ratios based on FS25 example
        for i in range(num_forward):
            if transmission_type == "CVT":
                # CVT has continuous ratios with smooth progression
                if num_forward == 1:
                    ratio = 4.2  # Single gear CVT
                else:
                    ratio = 4.2 - (3.0 * i / (num_forward - 1))
            elif transmission_type == "Automatic":
                # Automatic has closer ratios for smooth shifting
                if num_forward == 1:
                    ratio = 4.5  # Single gear automatic
                else:
                    ratio = 4.5 - (3.2 * i / (num_forward - 1))
            elif transmission_type == "PowerShift":
                # PowerShift has very close ratios for performance
                if num_forward == 1:
                    ratio = 4.8  # Single gear PowerShift
                else:
                    ratio = 4.8 - (3.5 * i / (num_forward - 1))
            else:
                # Manual transmission ratios based on FS25 example
                # Example: 4.784, 2.423, 1.443, 1.000, 0.826, 0.643
                if num_forward == 1:
                    ratio = 4.784  # Single gear manual
                elif num_forward == 6:
                    ratios = [4.784, 2.423, 1.443, 1.000, 0.826, 0.643]
                    ratio = ratios[i] if i < len(ratios) else 4.0 - (3.0 * i / (num_forward - 1))
                elif num_forward == 7:
                    ratios = [5.0, 2.8, 1.8, 1.2, 1.000, 0.8, 0.6]
                    ratio = ratios[i] if i < len(ratios) else 4.0 - (3.0 * i / (num_forward - 1))
                else:
                    # Generic manual ratios
                    ratio = 4.8 - (3.5 * i / (num_forward - 1))
            
            # Apply low gearing if enabled
            if enable_low_gearing and i < num_forward * 0.25:
                boost_factor = 1.0 + (low_gear_boost / 100.0)
                ratio *= boost_factor
            
            forward_ratios.append(round(ratio, 3))
        
        # Calculate reverse gear ratios (typically higher than 1st gear)
        for i in range(num_reverse):
            ratio = forward_ratios[0] * (1.2 + i * 0.3)
            reverse_ratios.append(round(ratio, 3))
        
        return {
            'forward': forward_ratios,
            'reverse': reverse_ratios
        }


