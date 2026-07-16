from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from src.core.torque import TorqueCurveGenerator
from src.core.gears import GearRatioCalculator

class XMLGenerator:
    """
    Handles generation of XML configuration files for FS25.
    Creates properly formatted XML for engines and transmissions.
    """
    
    @staticmethod
    def format_xml(xml_string: str) -> str:
        """
        Format XML string with proper indentation for better readability.
        
        Args:
            xml_string: Raw XML string
            
        Returns:
            Formatted XML string with proper indentation
        """
        import re
        
        # Remove existing whitespace and newlines
        xml_string = re.sub(r'\s+', ' ', xml_string.strip())
        
        # Split into lines and format
        lines = []
        indent_level = 0
        
        # Split by tags
        parts = re.split(r'(<[^>]+>)', xml_string)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if part.startswith('<?xml'):
                # XML declaration
                lines.append(part)
            elif part.startswith('<!--'):
                # Comments
                lines.append(' ' * indent_level + part)
            elif part.startswith('</'):
                # Closing tag
                indent_level = max(0, indent_level - 1)
                lines.append(' ' * indent_level + part)
            elif part.startswith('<') and not part.endswith('/>'):
                # Opening tag
                lines.append(' ' * indent_level + part)
                indent_level += 1
            else:
                # Self-closing tag or text content
                lines.append(' ' * indent_level + part)
        
        return '\n'.join(lines)
    
    @staticmethod
    def generate_engine_xml(engine_data: Dict) -> str:
        """
        Generate XML for engine configuration in FS25 format.
        
        Args:
            engine_data: Dictionary containing engine specifications
            
        Returns:
            Formatted XML string
        """
        torque_curve = TorqueCurveGenerator.generate_torque_curve(
            engine_data['horsepower'],
            engine_data['min_rpm'],
            engine_data['max_rpm'],
            engine_data['turbocharged']
        )
        
        # Convert normalized RPM back to actual RPM for FS25 format
        actual_rpm_torque = []
        for norm_rpm, torque in torque_curve:
            actual_rpm = norm_rpm * engine_data['max_rpm']
            # Convert torque to scale (0-1 range)
            torque_scale = torque / max(torque for _, torque in torque_curve)
            actual_rpm_torque.append((actual_rpm, torque_scale))
        
        xml = f'''<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<motorConfigurations>
    <motorConfiguration name="{engine_data['name']}" hp="{engine_data['horsepower']}" price="{engine_data['cost']}">
        <motor torqueScale="{engine_data['fuel_usage_scale']}" minRpm="{engine_data['min_rpm']}" maxRpm="{engine_data['max_rpm']}" maxForwardSpeed="120" maxBackwardSpeed="22" brakeForce="2" lowBrakeForceScale="0.1" dampingRateScale="0.2">
'''
        
        for rpm, torque_scale in actual_rpm_torque:
            xml += f'            <torque rpm="{rpm:.0f}" torque="{torque_scale:.2f}"/>\n'
        
        xml += '''        </motor>
    </motorConfiguration>
</motorConfigurations>'''
        
        # Format the XML for better readability
        return XMLGenerator.format_xml(xml)
    
    @staticmethod
    def generate_transmission_xml(transmission_data: Dict) -> str:
        """
        Generate XML for transmission configuration in FS25 format.
        
        Args:
            transmission_data: Dictionary containing transmission specifications
            
        Returns:
            Formatted XML string
        """
        gear_ratios = GearRatioCalculator.calculate_gear_ratios(
            transmission_data['type'],
            transmission_data['num_forward'],
            transmission_data['num_reverse'],
            transmission_data['top_speed'],
            transmission_data.get('enable_low_gearing', False),
            transmission_data.get('low_gear_boost', 25.0)
        )
        
        # Determine transmission type for FS25
        if transmission_data['type'].lower() == 'automatic':
            auto_gear_change_time = "1"
            gear_change_time = "0.3"
        else:
            auto_gear_change_time = "0"
            gear_change_time = "0.3"
        
        xml = f'''<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<motorConfigurations>
    <motorConfiguration name="{transmission_data['name']}" hp="0" price="{transmission_data['cost']}">
        <motor torqueScale="1.0" minRpm="1000" maxRpm="6000" maxForwardSpeed="{transmission_data['top_speed']}" maxBackwardSpeed="22" brakeForce="2" lowBrakeForceScale="0.1" dampingRateScale="0.2">
            <torque rpm="1000" torque="1.0"/>
            <torque rpm="6000" torque="1.0"/>
        </motor>
        <transmission autoGearChangeTime="{auto_gear_change_time}" gearChangeTime="{gear_change_time}" name="{transmission_data['name']}" axleRatio="25" startGearThreshold="0.3">
            <directionChange useGear="true"/>
'''
        
        # Add reverse gears
        for i, ratio in enumerate(gear_ratios['reverse']):
            xml += f'            <backwardGear gearRatio="{ratio:.3f}" name="R{i+1 if len(gear_ratios["reverse"]) > 1 else ""}"/>\n'
        
        # Add forward gears
        for i, ratio in enumerate(gear_ratios['forward']):
            xml += f'            <forwardGear gearRatio="{ratio:.3f}"/>\n'
        
        xml += '''        </transmission>
    </motorConfiguration>
</motorConfigurations>'''
        
        # Format the XML for better readability
        return XMLGenerator.format_xml(xml)
    
    @staticmethod
    def generate_combined_fs25_xml(engine_data: Dict, transmission_data: Dict) -> str:
        """
        Generate combined engine and transmission XML in FS25 format.
        
        Args:
            engine_data: Dictionary containing engine specifications
            transmission_data: Dictionary containing transmission specifications
            
        Returns:
            Formatted XML string
        """
        torque_curve = TorqueCurveGenerator.generate_torque_curve(
            engine_data['horsepower'],
            engine_data['min_rpm'],
            engine_data['max_rpm'],
            engine_data['turbocharged']
        )
        
        # Convert normalized RPM back to actual RPM for FS25 format
        actual_rpm_torque = []
        for norm_rpm, torque in torque_curve:
            actual_rpm = norm_rpm * engine_data['max_rpm']
            # Convert torque to scale (0-1 range)
            torque_scale = torque / max(torque for _, torque in torque_curve)
            actual_rpm_torque.append((actual_rpm, torque_scale))
        
        gear_ratios = GearRatioCalculator.calculate_gear_ratios(
            transmission_data['type'],
            transmission_data['num_forward'],
            transmission_data['num_reverse'],
            transmission_data['top_speed'],
            transmission_data.get('enable_low_gearing', False),
            transmission_data.get('low_gear_boost', 25.0)
        )
        
        # Determine transmission type for FS25
        if transmission_data['type'].lower() == 'automatic':
            auto_gear_change_time = "1"
            gear_change_time = "0.3"
        else:
            auto_gear_change_time = "0"
            gear_change_time = "0.3"
        
        xml = f'''<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<motorConfigurations>
    <motorConfiguration name="{engine_data['name']} - {transmission_data['name']}" hp="{engine_data['horsepower']}" price="{engine_data['cost'] + transmission_data['cost']}">
        <motor torqueScale="{engine_data['fuel_usage_scale']}" minRpm="{engine_data['min_rpm']}" maxRpm="{engine_data['max_rpm']}" maxForwardSpeed="{transmission_data['top_speed']}" maxBackwardSpeed="22" brakeForce="2" lowBrakeForceScale="0.1" dampingRateScale="0.2">
'''
        
        for rpm, torque_scale in actual_rpm_torque:
            xml += f'            <torque rpm="{rpm:.0f}" torque="{torque_scale:.2f}"/>\n'
        
        xml += f'''        </motor>
        <transmission autoGearChangeTime="{auto_gear_change_time}" gearChangeTime="{gear_change_time}" name="{transmission_data['name']}" axleRatio="25" startGearThreshold="0.3">
            <directionChange useGear="true"/>
'''
        
        # Add reverse gears
        for i, ratio in enumerate(gear_ratios['reverse']):
            xml += f'            <backwardGear gearRatio="{ratio:.3f}" name="R{i+1 if len(gear_ratios["reverse"]) > 1 else ""}"/>\n'
        
        # Add forward gears
        for i, ratio in enumerate(gear_ratios['forward']):
            xml += f'            <forwardGear gearRatio="{ratio:.3f}"/>\n'
        
        xml += '''        </transmission>
    </motorConfiguration>
</motorConfigurations>'''
        
        # Format the XML for better readability
        return XMLGenerator.format_xml(xml)


