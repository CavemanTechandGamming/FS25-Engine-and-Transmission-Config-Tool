from __future__ import annotations

from typing import Dict, List, Optional, Tuple

class PresetManager:
    """
    Manages engine and transmission presets.
    Handles saving and loading of configuration presets.
    """
    
    # Thread lock for preset operations
    _preset_lock = None
    
    @classmethod
    def _get_lock(cls):
        """Get thread lock for preset operations."""
        if cls._preset_lock is None:
            import threading
            cls._preset_lock = threading.Lock()
        return cls._preset_lock
    
    # Engine presets
    ENGINE_PRESETS = {
        "7.3 Powerstroke": {
            "name": "7.3 Powerstroke",
            "cost": 8500,
            "horsepower": 275,
            "min_rpm": 600,
            "max_rpm": 3500,
            "fuel_usage_scale": 1.0,
            "turbocharged": True
        },
        "6.0 Powerstroke": {
            "name": "6.0 Powerstroke",
            "cost": 12000,
            "horsepower": 325,
            "min_rpm": 650,
            "max_rpm": 3500,
            "fuel_usage_scale": 1.1,
            "turbocharged": True
        },
        "6.7 Powerstroke": {
            "name": "6.7 Powerstroke",
            "cost": 18000,
            "horsepower": 475,
            "min_rpm": 650,
            "max_rpm": 3500,
            "fuel_usage_scale": 1.3,
            "turbocharged": True
        },
        "5.9 Cummins": {
            "name": "5.9 Cummins",
            "cost": 11000,
            "horsepower": 325,
            "min_rpm": 700,
            "max_rpm": 3500,
            "fuel_usage_scale": 1.0,
            "turbocharged": True
        },
        "6.7 Cummins": {
            "name": "6.7 Cummins",
            "cost": 15000,
            "horsepower": 400,
            "min_rpm": 700,
            "max_rpm": 3500,
            "fuel_usage_scale": 1.2,
            "turbocharged": True
        }
    }
    
    # Transmission presets
    TRANSMISSION_PRESETS = {
        "10-speed Allison Automatic": {
            "name": "10-speed Allison Automatic",
            "cost": 8000,
            "type": "Automatic",
            "top_speed": 120,
            "num_forward": 10,
            "num_reverse": 2,
            "enable_low_gearing": False,
            "low_gear_boost": 25.0
        },
        "13-speed Eaton Fuller": {
            "name": "13-speed Eaton Fuller",
            "cost": 12000,
            "type": "Manual",
            "top_speed": 140,
            "num_forward": 13,
            "num_reverse": 2,
            "enable_low_gearing": False,
            "low_gear_boost": 25.0
        },
        "4-speed with Granny Gear": {
            "name": "4-speed with Granny Gear",
            "cost": 5000,
            "type": "Manual",
            "top_speed": 80,
            "num_forward": 5,
            "num_reverse": 1,
            "enable_low_gearing": True,
            "low_gear_boost": 50.0
        },
        "18-speed Eaton Fuller": {
            "name": "18-speed Eaton Fuller",
            "cost": 15000,
            "type": "Manual",
            "top_speed": 160,
            "num_forward": 18,
            "num_reverse": 2,
            "enable_low_gearing": False,
            "low_gear_boost": 25.0
        }
    }
    
    @staticmethod
    def save_preset(data: Dict, filename: str):
        """
        Save configuration preset to JSON file.
        
        Args:
            data: Configuration data to save
            filename: Name of the file to save to
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Success", f"Preset saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preset: {str(e)}")
    
    @staticmethod
    def load_preset(filename: str) -> Optional[Dict]:
        """
        Load configuration preset from JSON file.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Configuration data dictionary or None if failed
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset: {str(e)}")
            return None
    
    @classmethod
    def add_engine_preset(cls, name: str, data: Dict):
        """Thread-safe method to add engine preset."""
        with cls._get_lock():
            cls.ENGINE_PRESETS[name] = data
    
    @classmethod
    def add_transmission_preset(cls, name: str, data: Dict):
        """Thread-safe method to add transmission preset."""
        with cls._get_lock():
            cls.TRANSMISSION_PRESETS[name] = data
    
    @classmethod
    def get_engine_presets(cls) -> Dict:
        """Thread-safe method to get engine presets."""
        with cls._get_lock():
            return cls.ENGINE_PRESETS.copy()
    
    @classmethod
    def get_transmission_presets(cls) -> Dict:
        """Thread-safe method to get transmission presets."""
        with cls._get_lock():
            return cls.TRANSMISSION_PRESETS.copy()


