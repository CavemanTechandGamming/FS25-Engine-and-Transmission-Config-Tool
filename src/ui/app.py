#!/usr/bin/env python3
"""FS25 Engine and Transmission Config Tool — main window and UI."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk
from typing import Dict, List, Optional, Tuple

try:
    import customtkinter as ctk

    CUSTOM_TKINTER_AVAILABLE = True
except ImportError:
    CUSTOM_TKINTER_AVAILABLE = False
    print("CustomTkinter not available, using standard Tkinter")

from src import __version__
from src.core.presets import PresetManager
from src.core.xml_gen import XMLGenerator
from src.ui.about import show_about

class Tooltip:
    """
    Simple tooltip widget for providing help text on hover.
    Displays descriptive text when hovering over widgets.
    """
    
    def __init__(self, widget: tk.Widget, text: str):
        """
        Initialize tooltip for a widget.
        
        Args:
            widget: The widget to attach tooltip to
            text: The tooltip text to display
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Display tooltip when mouse enters widget."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip_window, text=self.text, 
                        justify=tk.LEFT, background="#2d2d2d", 
                        foreground="#ffffff", relief=tk.SOLID, 
                        borderwidth=1, font=("Arial", 8))
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide tooltip when mouse leaves widget."""
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except tk.TclError:
                # Window was already destroyed
                pass
            finally:
                self.tooltip_window = None



class FS25ConfigTool:
    """
    Main application class for the FS25 Engine and Transmission Config Tool.
    Handles GUI creation, event handling, and application logic.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main application.
        
        Args:
            root: The main Tkinter window
        """
        self.root = root
        self.root.title(f"FS25 Engine and Transmission Config Tool v{__version__}")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)
        
        # Configure custom styling
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_tkinter()
        else:
            self.setup_standard_tkinter()
        
        # Initialize variables
        self.engine_data = {
            'name': tk.StringVar(value="Custom Engine"),
            'cost': tk.StringVar(value="10000"),
            'horsepower': tk.StringVar(value="300"),
            'min_rpm': tk.StringVar(value="600"),
            'max_rpm': tk.StringVar(value="3500"),
            'fuel_usage_scale': tk.StringVar(value="1.0"),
            'turbocharged': tk.BooleanVar(value=False)
        }
        
        self.transmission_data = {
            'name': tk.StringVar(value="Custom Transmission"),
            'cost': tk.StringVar(value="8000"),
            'type': tk.StringVar(value="Manual"),
            'top_speed': tk.StringVar(value="120"),
            'num_forward': tk.StringVar(value="6"),
            'num_reverse': tk.StringVar(value="1"),
            'enable_low_gearing': tk.BooleanVar(value=False),
            'low_gear_boost': tk.StringVar(value="25.0")
        }
        
        # Store dropdown references for refresh functionality
        self.engine_preset_dropdown = None
        self.transmission_preset_dropdown = None
        
        self.setup_gui()
    
    def setup_custom_tkinter(self):
        """Set up CustomTkinter styling."""
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure custom colors
        self.colors = {
            'bg': "#1a1a1a",
            'fg': "#ffffff",
            'secondary_fg': "#cccccc",
            'input_bg': "#2d2d2d",
            'button_bg': "#1f538d",
            'button_hover': "#14375e",
            'border': "#555555",
            'accent': "#007acc",
            'success': "#28a745",
            'warning': "#ffc107",
            'error': "#dc3545"
        }
        
        self.root.configure(bg=self.colors['bg'])
    
    def setup_standard_tkinter(self):
        """Set up standard Tkinter styling."""
        self.root.configure(bg="#1e1e1e")
        
        # Configure dark theme colors
        self.colors = {
            'bg': "#1e1e1e",
            'fg': "#ffffff",
            'secondary_fg': "#cccccc",
            'input_bg': "#2d2d2d",
            'button_bg': "#3d3d3d",
            'button_hover': "#4d4d4d",
            'border': "#555555",
            'accent': "#007acc",
            'success': "#28a745",
            'warning': "#ffc107",
            'error': "#dc3545"
        }
        
        self.setup_gui()
        self.apply_dark_theme()
    
    def setup_gui(self):
        """Set up the main GUI layout with all components."""
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_gui()
        else:
            self.setup_standard_gui()
    
    def setup_custom_gui(self):
        """Set up a single-page GUI: engine | transmission, XML output below."""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=2)  # config panels
        main_frame.grid_rowconfigure(2, weight=3)  # XML output

        # Title row with About
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
        header.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header,
            text="FS25 Engine and Transmission Config Tool",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.grid(row=0, column=0, sticky="w")

        about_btn = ctk.CTkButton(
            header,
            text="About",
            width=80,
            command=lambda: show_about(self.root),
        )
        about_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))
        Tooltip(about_btn, "About this app and support links")

        # Engine (left) + Transmission (right)
        config_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        config_row.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        config_row.grid_columnconfigure(0, weight=1)
        config_row.grid_columnconfigure(1, weight=1)
        config_row.grid_rowconfigure(0, weight=1)

        engine_panel = ctk.CTkScrollableFrame(config_row, label_text="Engine")
        engine_panel.grid(row=0, column=0, sticky="nsew", padx=(4, 4), pady=4)
        self.setup_engine_tab(engine_panel)

        transmission_panel = ctk.CTkScrollableFrame(config_row, label_text="Transmission")
        transmission_panel.grid(row=0, column=1, sticky="nsew", padx=(4, 4), pady=4)
        self.setup_transmission_tab(transmission_panel)

        # Generated XML + actions (bottom)
        output_panel = ctk.CTkFrame(main_frame)
        output_panel.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.setup_output_tab(output_panel)

    def setup_standard_gui(self):
        """Set up a single-page GUI using standard Tkinter widgets."""
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=2)
        main_frame.grid_rowconfigure(2, weight=3)

        header = tk.Frame(main_frame, bg=self.colors['bg'])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        title_label = tk.Label(
            header,
            text="FS25 Engine and Transmission Config Tool",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
        )
        title_label.pack(side=tk.LEFT)

        about_btn = tk.Button(
            header,
            text="About",
            command=lambda: show_about(self.root),
            bg=self.colors.get('button', '#404040'),
            fg=self.colors['fg'],
        )
        about_btn.pack(side=tk.RIGHT)
        Tooltip(about_btn, "About this app and support links")

        config_row = tk.Frame(main_frame, bg=self.colors['bg'])
        config_row.grid(row=1, column=0, sticky="nsew", pady=(0, 6))
        config_row.grid_columnconfigure(0, weight=1)
        config_row.grid_columnconfigure(1, weight=1)
        config_row.grid_rowconfigure(0, weight=1)

        engine_panel = tk.LabelFrame(
            config_row,
            text="Engine",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        engine_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        self.setup_engine_tab(engine_panel)

        transmission_panel = tk.LabelFrame(
            config_row,
            text="Transmission",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        transmission_panel.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        self.setup_transmission_tab(transmission_panel)

        output_panel = tk.Frame(main_frame, bg=self.colors['bg'])
        output_panel.grid(row=2, column=0, sticky="nsew")
        self.setup_output_tab(output_panel)
    
    def setup_engine_tab(self, parent):
        """Set up the engine configuration tab."""
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_engine_tab(parent)
        else:
            self.setup_standard_engine_tab(parent)
    
    def setup_custom_engine_tab(self, parent):
        """Set up engine panel using CustomTkinter widgets."""
        preset_frame = ctk.CTkFrame(parent)
        preset_frame.pack(fill=tk.X, padx=6, pady=5)

        preset_label = ctk.CTkLabel(
            preset_frame,
            text="Presets",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        preset_label.pack(anchor="w", padx=8, pady=(6, 2))

        preset_row = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_row.pack(fill=tk.X, padx=6, pady=(0, 6))

        preset_combo = ctk.CTkOptionMenu(
            preset_row,
            values=list(PresetManager.get_engine_presets().keys()),
            command=self.load_engine_preset,
        )
        preset_combo.pack(side=tk.LEFT, padx=(2, 6), pady=4)
        self.engine_preset_dropdown = preset_combo

        load_preset_btn = ctk.CTkButton(
            preset_row,
            text="Load",
            width=70,
            command=lambda: self.load_engine_preset(preset_combo.get()),
        )
        load_preset_btn.pack(side=tk.LEFT, padx=2, pady=4)

        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=5)

        settings_label = ctk.CTkLabel(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        settings_label.pack(anchor="w", padx=8, pady=(8, 4))

        fields = ctk.CTkFrame(settings_frame, fg_color="transparent")
        fields.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.create_custom_input_field(
            fields, "Engine Name:", self.engine_data['name'],
            "Enter the name of the engine",
        )
        self.create_custom_input_field(
            fields, "Engine Cost ($):", self.engine_data['cost'],
            "Enter the cost of the engine in dollars",
        )
        self.create_custom_input_field(
            fields, "Horsepower (HP):", self.engine_data['horsepower'],
            "Enter the engine's rated horsepower. Used to calculate torque curve",
        )
        self.create_custom_input_field(
            fields, "Minimum RPM:", self.engine_data['min_rpm'],
            "Enter the minimum RPM of the engine",
        )
        self.create_custom_input_field(
            fields, "Maximum RPM:", self.engine_data['max_rpm'],
            "Enter the maximum RPM of the engine (default: 3500)",
        )
        self.create_custom_input_field(
            fields, "Fuel Usage Scale:", self.engine_data['fuel_usage_scale'],
            "Enter the fuel usage scale factor (default: 1.0)",
        )

        turbo_check = ctk.CTkCheckBox(
            fields,
            text="Turbocharged",
            variable=self.engine_data['turbocharged'],
        )
        turbo_check.pack(anchor="w", pady=8)
        Tooltip(turbo_check, "Check if the engine is turbocharged. Affects torque curve generation")
    
    def setup_standard_engine_tab(self, parent):
        """Set up engine panel using standard Tkinter widgets."""
        preset_frame = tk.LabelFrame(
            parent, text="Presets",
            bg=self.colors['bg'], fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        preset_frame.pack(fill=tk.X, padx=6, pady=5)

        preset_var = tk.StringVar()
        preset_combo = ttk.Combobox(
            preset_frame, textvariable=preset_var,
            values=list(PresetManager.get_engine_presets().keys()),
            state="readonly", width=28,
        )
        preset_combo.pack(side=tk.LEFT, padx=8, pady=8)
        preset_combo.bind(
            '<<ComboboxSelected>>',
            lambda e: self.load_engine_preset(preset_var.get()),
        )
        self.engine_preset_dropdown = preset_combo

        load_preset_btn = tk.Button(
            preset_frame, text="Load",
            command=lambda: self.load_engine_preset(preset_var.get()),
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            relief=tk.RAISED, borderwidth=1,
        )
        load_preset_btn.pack(side=tk.LEFT, padx=5, pady=8)

        settings_frame = tk.LabelFrame(
            parent, text="Settings",
            bg=self.colors['bg'], fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=5)

        fields = tk.Frame(settings_frame, bg=self.colors['bg'])
        fields.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.create_input_field(
            fields, "Engine Name:", self.engine_data['name'],
            "Enter the name of the engine",
        )
        self.create_input_field(
            fields, "Engine Cost ($):", self.engine_data['cost'],
            "Enter the cost of the engine in dollars",
        )
        self.create_input_field(
            fields, "Horsepower (HP):", self.engine_data['horsepower'],
            "Enter the engine's rated horsepower. Used to calculate torque curve",
        )
        self.create_input_field(
            fields, "Minimum RPM:", self.engine_data['min_rpm'],
            "Enter the minimum RPM of the engine",
        )
        self.create_input_field(
            fields, "Maximum RPM:", self.engine_data['max_rpm'],
            "Enter the maximum RPM of the engine (default: 3500)",
        )
        self.create_input_field(
            fields, "Fuel Usage Scale:", self.engine_data['fuel_usage_scale'],
            "Enter the fuel usage scale factor (default: 1.0)",
        )

        turbo_frame = tk.Frame(fields, bg=self.colors['bg'])
        turbo_frame.pack(fill=tk.X, pady=5)

        turbo_label = tk.Label(
            turbo_frame, text="Turbocharged:",
            bg=self.colors['bg'], fg=self.colors['fg'],
        )
        turbo_label.pack(side=tk.LEFT)

        turbo_check = tk.Checkbutton(
            turbo_frame, variable=self.engine_data['turbocharged'],
            bg=self.colors['bg'], fg=self.colors['fg'],
            selectcolor=self.colors['input_bg'],
        )
        turbo_check.pack(side=tk.LEFT, padx=5)
        Tooltip(turbo_check, "Check if the engine is turbocharged. Affects torque curve generation")
    
    def setup_transmission_tab(self, parent):
        """Set up the transmission configuration tab."""
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_transmission_tab(parent)
        else:
            self.setup_standard_transmission_tab(parent)
    
    def setup_custom_transmission_tab(self, parent):
        """Set up transmission panel using CustomTkinter widgets."""
        preset_frame = ctk.CTkFrame(parent)
        preset_frame.pack(fill=tk.X, padx=6, pady=5)

        preset_label = ctk.CTkLabel(
            preset_frame,
            text="Presets",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        preset_label.pack(anchor="w", padx=8, pady=(6, 2))

        preset_row = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_row.pack(fill=tk.X, padx=6, pady=(0, 6))

        preset_combo = ctk.CTkOptionMenu(
            preset_row,
            values=list(PresetManager.get_transmission_presets().keys()),
            command=self.load_transmission_preset,
        )
        preset_combo.pack(side=tk.LEFT, padx=(2, 6), pady=4)
        self.transmission_preset_dropdown = preset_combo

        load_preset_btn = ctk.CTkButton(
            preset_row,
            text="Load",
            width=70,
            command=lambda: self.load_transmission_preset(preset_combo.get()),
        )
        load_preset_btn.pack(side=tk.LEFT, padx=2, pady=4)

        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=5)

        settings_label = ctk.CTkLabel(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        settings_label.pack(anchor="w", padx=8, pady=(8, 4))

        fields = ctk.CTkFrame(settings_frame, fg_color="transparent")
        fields.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.create_custom_input_field(
            fields, "Transmission Name:", self.transmission_data['name'],
            "Enter the name of the transmission",
        )
        self.create_custom_input_field(
            fields, "Transmission Cost ($):", self.transmission_data['cost'],
            "Enter the cost of the transmission in dollars",
        )

        type_frame = ctk.CTkFrame(fields, fg_color="transparent")
        type_frame.pack(fill=tk.X, pady=5)
        type_label = ctk.CTkLabel(type_frame, text="Transmission Type:")
        type_label.pack(side=tk.LEFT, padx=(0, 8))
        type_combo = ctk.CTkOptionMenu(
            type_frame,
            values=["Manual", "Automatic", "CVT", "PowerShift"],
            variable=self.transmission_data['type'],
        )
        type_combo.pack(side=tk.LEFT)
        Tooltip(type_combo, "Select the type of transmission")

        self.create_custom_input_field(
            fields, "Top Speed (km/h):", self.transmission_data['top_speed'],
            "Enter the maximum speed of the vehicle in km/h",
        )
        self.create_custom_input_field(
            fields, "Forward Gears:", self.transmission_data['num_forward'],
            "Enter the number of forward gears",
        )
        self.create_custom_input_field(
            fields, "Reverse Gears:", self.transmission_data['num_reverse'],
            "Enter the number of reverse gears",
        )

        low_gear_check = ctk.CTkCheckBox(
            fields,
            text="Enable Low Gearing",
            variable=self.transmission_data['enable_low_gearing'],
        )
        low_gear_check.pack(anchor="w", pady=(8, 4))
        Tooltip(
            low_gear_check,
            "Enable low gearing for enhanced torque output in first 25% of gears",
        )

        boost_frame = ctk.CTkFrame(fields, fg_color="transparent")
        boost_frame.pack(fill=tk.X, pady=5)
        boost_label = ctk.CTkLabel(boost_frame, text="Low Gear Boost (%):")
        boost_label.pack(side=tk.LEFT, padx=(0, 8))
        boost_entry = ctk.CTkEntry(
            boost_frame,
            textvariable=self.transmission_data['low_gear_boost'],
            width=100,
        )
        boost_entry.pack(side=tk.LEFT)
        Tooltip(boost_entry, "Percentage boost for low gears (e.g., 25 for 25% boost)")
    
    def setup_standard_transmission_tab(self, parent):
        """Set up transmission panel using standard Tkinter widgets."""
        preset_frame = tk.LabelFrame(
            parent, text="Presets",
            bg=self.colors['bg'], fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        preset_frame.pack(fill=tk.X, padx=6, pady=5)

        preset_var = tk.StringVar()
        preset_combo = ttk.Combobox(
            preset_frame, textvariable=preset_var,
            values=list(PresetManager.get_transmission_presets().keys()),
            state="readonly", width=28,
        )
        preset_combo.pack(side=tk.LEFT, padx=8, pady=8)
        self.transmission_preset_dropdown = preset_combo

        load_preset_btn = tk.Button(
            preset_frame, text="Load",
            command=lambda: self.load_transmission_preset(preset_var.get()),
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            relief=tk.RAISED, borderwidth=1,
        )
        load_preset_btn.pack(side=tk.LEFT, padx=5, pady=8)

        settings_frame = tk.LabelFrame(
            parent, text="Settings",
            bg=self.colors['bg'], fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=5)

        fields = tk.Frame(settings_frame, bg=self.colors['bg'])
        fields.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.create_input_field(
            fields, "Transmission Name:", self.transmission_data['name'],
            "Enter the name of the transmission",
        )
        self.create_input_field(
            fields, "Transmission Cost ($):", self.transmission_data['cost'],
            "Enter the cost of the transmission in dollars",
        )

        type_frame = tk.Frame(fields, bg=self.colors['bg'])
        type_frame.pack(fill=tk.X, pady=5)
        type_label = tk.Label(
            type_frame, text="Transmission Type:",
            bg=self.colors['bg'], fg=self.colors['fg'],
        )
        type_label.pack(side=tk.LEFT)
        type_combo = ttk.Combobox(
            type_frame, textvariable=self.transmission_data['type'],
            values=["Manual", "Automatic", "CVT", "PowerShift"],
            state="readonly", width=15,
        )
        type_combo.pack(side=tk.LEFT, padx=5)
        Tooltip(type_combo, "Select the type of transmission")

        self.create_input_field(
            fields, "Top Speed (km/h):", self.transmission_data['top_speed'],
            "Enter the maximum speed of the vehicle in km/h",
        )
        self.create_input_field(
            fields, "Forward Gears:", self.transmission_data['num_forward'],
            "Enter the number of forward gears",
        )
        self.create_input_field(
            fields, "Reverse Gears:", self.transmission_data['num_reverse'],
            "Enter the number of reverse gears",
        )

        low_gear_frame = tk.Frame(fields, bg=self.colors['bg'])
        low_gear_frame.pack(fill=tk.X, pady=5)
        low_gear_check = tk.Checkbutton(
            low_gear_frame, text="Enable Low Gearing",
            variable=self.transmission_data['enable_low_gearing'],
            bg=self.colors['bg'], fg=self.colors['fg'],
            selectcolor=self.colors['input_bg'],
        )
        low_gear_check.pack(side=tk.LEFT)
        Tooltip(
            low_gear_check,
            "Enable low gearing for enhanced torque output in first 25% of gears",
        )

        boost_frame = tk.Frame(fields, bg=self.colors['bg'])
        boost_frame.pack(fill=tk.X, pady=5)
        boost_label = tk.Label(
            boost_frame, text="Low Gear Boost (%):",
            bg=self.colors['bg'], fg=self.colors['fg'],
        )
        boost_label.pack(side=tk.LEFT)
        boost_entry = tk.Entry(
            boost_frame, textvariable=self.transmission_data['low_gear_boost'],
            bg=self.colors['input_bg'], fg=self.colors['fg'],
            relief=tk.SOLID, borderwidth=1, width=10,
        )
        boost_entry.pack(side=tk.LEFT, padx=5)
        Tooltip(boost_entry, "Percentage boost for low gears (e.g., 25 for 25% boost)")
    
    def setup_output_tab(self, parent):
        """Set up the output tab with XML preview and action buttons."""
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_output_tab(parent)
        else:
            self.setup_standard_output_tab(parent)
    
    def setup_custom_output_tab(self, parent):
        """Set up output tab using CustomTkinter widgets."""
        # Action buttons frame - Compact Layout
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Top row - Engine and Transmission
        top_row = ctk.CTkFrame(button_frame)
        top_row.pack(fill=tk.X, padx=5, pady=2)
        
        # Engine Actions
        engine_label = ctk.CTkLabel(top_row, text="Engine:", 
                                   font=ctk.CTkFont(size=11, weight="bold"))
        engine_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        ctk.CTkButton(top_row, text="Generate",
                     command=self.generate_engine_xml, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        ctk.CTkButton(top_row, text="Copy",
                     command=self.copy_engine_xml, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        ctk.CTkButton(top_row, text="Save",
                     command=self.save_engine_xml, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        # Transmission Actions
        trans_label = ctk.CTkLabel(top_row, text="Transmission:", 
                                  font=ctk.CTkFont(size=11, weight="bold"))
        trans_label.pack(side=tk.LEFT, padx=(20, 5), pady=5)
        
        ctk.CTkButton(top_row, text="Generate",
                     command=self.generate_transmission_xml, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        ctk.CTkButton(top_row, text="Copy",
                     command=self.copy_transmission_xml, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        ctk.CTkButton(top_row, text="Save",
                     command=self.save_transmission_xml, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        # Bottom row - Presets and Combined
        bottom_row = ctk.CTkFrame(button_frame)
        bottom_row.pack(fill=tk.X, padx=5, pady=2)
        
        # Preset Actions
        preset_label = ctk.CTkLabel(bottom_row, text="Presets:", 
                                   font=ctk.CTkFont(size=11, weight="bold"))
        preset_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        ctk.CTkButton(bottom_row, text="Save",
                     command=self.save_current_preset, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        ctk.CTkButton(bottom_row, text="Load",
                     command=self.load_current_preset, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        ctk.CTkButton(bottom_row, text="Add",
                     command=self.add_to_presets, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        # Combined Actions
        combined_label = ctk.CTkLabel(bottom_row, text="Combined:", 
                                     font=ctk.CTkFont(size=11, weight="bold"))
        combined_label.pack(side=tk.LEFT, padx=(20, 5), pady=5)
        
        ctk.CTkButton(bottom_row, text="Generate",
                     command=self.generate_both_xml, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        ctk.CTkButton(bottom_row, text="Save",
                     command=self.save_both_xml, width=70).pack(side=tk.LEFT, padx=2, pady=5)
        
        # XML preview frame
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        preview_label = ctk.CTkLabel(preview_frame, text="XML Preview",
                                    font=ctk.CTkFont(size=14, weight="bold"))
        preview_label.pack(pady=5)
        
        # Create a frame for the text area with scrollbars
        text_frame = ctk.CTkFrame(preview_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create line numbers widget
        self.line_numbers = tk.Text(text_frame, 
                                   bg=self.colors['bg'],
                                   fg=self.colors['secondary_fg'],
                                   font=("Consolas", 9),
                                   width=4,
                                   padx=5,
                                   pady=5,
                                   relief=tk.FLAT,
                                   state=tk.DISABLED)
        
        # XML text area with both scrollbars
        self.xml_text = tk.Text(text_frame, 
                               bg=self.colors['input_bg'],
                               fg=self.colors['fg'],
                               font=("Consolas", 9),
                               wrap=tk.NONE,
                               insertbackground=self.colors['fg'],
                               padx=5,
                               pady=5)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self._on_scroll)
        h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.xml_text.xview)
        self.xml_text.configure(yscrollcommand=self._on_scroll, xscrollcommand=h_scrollbar.set)
        
        # Pack the text area and scrollbars
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.xml_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure XML syntax highlighting
        self.setup_xml_syntax_highlighting()
    
    def setup_standard_output_tab(self, parent):
        """Set up output tab using standard Tkinter widgets."""
        # Action buttons frame
        button_frame = tk.Frame(parent, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Top row - Engine and Transmission
        top_row = tk.Frame(button_frame, bg=self.colors['bg'])
        top_row.pack(fill=tk.X, padx=5, pady=2)
        
        # Engine Actions
        engine_label = tk.Label(top_row, text="Engine:", 
                               bg=self.colors['bg'], fg=self.colors['fg'],
                               font=("Arial", 10, "bold"))
        engine_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        tk.Button(top_row, text="Generate",
                 command=self.generate_engine_xml,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(top_row, text="Copy",
                 command=self.copy_engine_xml,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(top_row, text="Save",
                 command=self.save_engine_xml,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        # Transmission Actions
        trans_label = tk.Label(top_row, text="Transmission:", 
                              bg=self.colors['bg'], fg=self.colors['fg'],
                              font=("Arial", 10, "bold"))
        trans_label.pack(side=tk.LEFT, padx=(20, 5), pady=5)
        
        tk.Button(top_row, text="Generate",
                 command=self.generate_transmission_xml,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(top_row, text="Copy",
                 command=self.copy_transmission_xml,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(top_row, text="Save",
                 command=self.save_transmission_xml,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        # Bottom row - Presets and Combined
        bottom_row = tk.Frame(button_frame, bg=self.colors['bg'])
        bottom_row.pack(fill=tk.X, padx=5, pady=2)
        
        # Preset Actions
        preset_label = tk.Label(bottom_row, text="Presets:", 
                               bg=self.colors['bg'], fg=self.colors['fg'],
                               font=("Arial", 10, "bold"))
        preset_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        tk.Button(bottom_row, text="Save",
                 command=self.save_current_preset,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(bottom_row, text="Load",
                 command=self.load_current_preset,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(bottom_row, text="Add",
                 command=self.add_to_presets,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        # Combined Actions
        combined_label = tk.Label(bottom_row, text="Combined:", 
                                 bg=self.colors['bg'], fg=self.colors['fg'],
                                 font=("Arial", 10, "bold"))
        combined_label.pack(side=tk.LEFT, padx=(20, 5), pady=5)
        
        tk.Button(bottom_row, text="Generate",
                 command=self.generate_both_xml,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(bottom_row, text="Save",
                 command=self.save_both_xml,
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief=tk.RAISED, borderwidth=1, width=8).pack(side=tk.LEFT, padx=2, pady=5)
        
        # XML preview frame
        preview_frame = tk.LabelFrame(parent, text="XML Preview",
                                    bg=self.colors['bg'], fg=self.colors['fg'],
                                    font=("Arial", 10, "bold"))
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create a frame for the text area with scrollbars
        text_frame = tk.Frame(preview_frame, bg=self.colors['input_bg'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create line numbers widget
        self.line_numbers = tk.Text(text_frame, 
                                   bg=self.colors['bg'],
                                   fg=self.colors['secondary_fg'],
                                   font=("Consolas", 9),
                                   width=4,
                                   padx=5,
                                   pady=5,
                                   relief=tk.FLAT,
                                   state=tk.DISABLED)
        
        # XML text area with both scrollbars
        self.xml_text = tk.Text(text_frame, 
                               bg=self.colors['input_bg'],
                               fg=self.colors['fg'],
                               font=("Consolas", 9),
                               wrap=tk.NONE,
                               insertbackground=self.colors['fg'],
                               padx=5,
                               pady=5)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self._on_scroll)
        h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.xml_text.xview)
        self.xml_text.configure(yscrollcommand=self._on_scroll, xscrollcommand=h_scrollbar.set)
        
        # Pack the text area and scrollbars
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.xml_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure XML syntax highlighting
        self.setup_xml_syntax_highlighting()
    
    def create_input_field(self, parent, label_text, variable, tooltip_text):
        """
        Create a labeled input field with tooltip.
        
        Args:
            parent: Parent widget
            label_text: Text for the label
            variable: Tkinter variable to bind to
            tooltip_text: Tooltip text for the field
        """
        frame = tk.Frame(parent, bg=self.colors['bg'])
        frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(frame, text=label_text, 
                        bg=self.colors['bg'], fg=self.colors['fg'])
        label.pack(side=tk.LEFT)
        
        entry = tk.Entry(frame, textvariable=variable,
                        bg=self.colors['input_bg'], fg=self.colors['fg'],
                        relief=tk.SOLID, borderwidth=1)
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        Tooltip(entry, tooltip_text)
    
    def create_custom_input_field(self, parent, label_text, variable, tooltip_text):
        """
        Create a labeled input field with tooltip using CustomTkinter.
        
        Args:
            parent: Parent widget
            label_text: Text for the label
            variable: Tkinter variable to bind to
            tooltip_text: Tooltip text for the field
        """
        frame = ctk.CTkFrame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        label = ctk.CTkLabel(frame, text=label_text)
        label.pack(side=tk.LEFT, padx=5)
        
        entry = ctk.CTkEntry(frame, textvariable=variable)
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        Tooltip(entry, tooltip_text)
    
    def apply_dark_theme(self):
        """Apply dark theme styling to the application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure ttk styles for dark theme
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['button_bg'],
                       foreground=self.colors['fg'], padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', self.colors['button_hover'])])
        
        style.configure('TCombobox', fieldbackground=self.colors['input_bg'],
                       background=self.colors['input_bg'], foreground=self.colors['fg'])
        style.map('TCombobox', fieldbackground=[('readonly', self.colors['input_bg'])])
    
    def setup_xml_syntax_highlighting(self):
        """Set up XML syntax highlighting tags and colors."""
        # Define XML syntax highlighting colors
        xml_colors = {
            'tag': '#4EC9B0',      # Light blue-green for tags
            'attribute': '#9CDCFE', # Light blue for attributes
            'value': '#CE9178',     # Light orange for values
            'comment': '#6A9955',   # Green for comments
            'text': '#D4D4D4',      # Light gray for text content
            'declaration': '#569CD6' # Blue for XML declaration
        }
        
        # Configure text widget tags for syntax highlighting
        self.xml_text.tag_configure('xml_tag', foreground=xml_colors['tag'])
        self.xml_text.tag_configure('xml_attribute', foreground=xml_colors['attribute'])
        self.xml_text.tag_configure('xml_value', foreground=xml_colors['value'])
        self.xml_text.tag_configure('xml_comment', foreground=xml_colors['comment'])
        self.xml_text.tag_configure('xml_text', foreground=xml_colors['text'])
        self.xml_text.tag_configure('xml_declaration', foreground=xml_colors['declaration'])
    
    def highlight_xml_syntax(self, xml_content):
        """
        Apply syntax highlighting to XML content.
        
        Args:
            xml_content: The XML string to highlight
        """
        # Clear existing content and tags
        self.xml_text.delete(1.0, tk.END)
        self.xml_text.insert(1.0, xml_content)
        
        # Remove all existing tags to prevent memory leaks
        for tag in self.xml_text.tag_names():
            if tag != 'sel':
                self.xml_text.tag_remove(tag, 1.0, tk.END)
                # Delete the tag completely to free memory
                try:
                    self.xml_text.tag_delete(tag)
                except tk.TclError:
                    # Tag might already be deleted
                    pass
        
        # Apply syntax highlighting
        self._highlight_xml_tags(xml_content)
        
        # Update line numbers
        self._update_line_numbers()
    
    def _highlight_xml_tags(self, xml_content):
        """Internal method to highlight XML syntax."""
        import re
        
        # Ensure tags are configured before applying them
        xml_colors = {
            'tag': '#4EC9B0',      # Light blue-green for tags
            'attribute': '#9CDCFE', # Light blue for attributes
            'value': '#CE9178',     # Light orange for values
            'comment': '#6A9955',   # Green for comments
            'text': '#D4D4D4',      # Light gray for text content
            'declaration': '#569CD6' # Blue for XML declaration
        }
        
        # Configure text widget tags for syntax highlighting
        self.xml_text.tag_configure('xml_tag', foreground=xml_colors['tag'])
        self.xml_text.tag_configure('xml_attribute', foreground=xml_colors['attribute'])
        self.xml_text.tag_configure('xml_value', foreground=xml_colors['value'])
        self.xml_text.tag_configure('xml_comment', foreground=xml_colors['comment'])
        self.xml_text.tag_configure('xml_text', foreground=xml_colors['text'])
        self.xml_text.tag_configure('xml_declaration', foreground=xml_colors['declaration'])
        
        # XML declaration
        decl_pattern = r'<\?xml[^>]*\?>'
        for match in re.finditer(decl_pattern, xml_content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.xml_text.tag_add('xml_declaration', start, end)
        
        # Comments
        comment_pattern = r'<!--[^>]*-->'
        for match in re.finditer(comment_pattern, xml_content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.xml_text.tag_add('xml_comment', start, end)
        
        # Tags
        tag_pattern = r'<[^>]+>'
        for match in re.finditer(tag_pattern, xml_content):
            tag_content = match.group()
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            
            # Skip if it's a comment or declaration
            if tag_content.startswith('<!--') or tag_content.startswith('<?'):
                continue
            
            # Highlight the tag
            self.xml_text.tag_add('xml_tag', start, end)
            
            # Highlight attributes within the tag
            attr_pattern = r'(\w+)="([^"]*)"'
            for attr_match in re.finditer(attr_pattern, tag_content):
                attr_start = match.start() + attr_match.start()
                attr_end = match.start() + attr_match.end()
                
                # Attribute name
                attr_name_start = f"1.0+{attr_start}c"
                attr_name_end = f"1.0+{attr_start + attr_match.group(1).__len__()}c"
                self.xml_text.tag_add('xml_attribute', attr_name_start, attr_name_end)
                
                # Attribute value
                attr_value_start = f"1.0+{attr_start + attr_match.group(1).__len__() + 2}c"  # +2 for ="
                attr_value_end = f"1.0+{attr_end - 1}c"  # -1 for closing quote
                self.xml_text.tag_add('xml_value', attr_value_start, attr_value_end)
    
    def _update_line_numbers(self):
        """Update the line numbers display."""
        try:
            # Get the number of lines
            line_count = int(self.xml_text.index('end-1c').split('.')[0])
            
            # Clear existing line numbers
            self.line_numbers.config(state=tk.NORMAL)
            self.line_numbers.delete(1.0, tk.END)
            
            # Add line numbers
            for i in range(1, line_count + 1):
                self.line_numbers.insert(tk.END, f"{i}\n")
            
            self.line_numbers.config(state=tk.DISABLED)
            
            # Sync scrolling
            self.xml_text.yview_moveto(0)
            self.line_numbers.yview_moveto(0)
            
        except Exception:
            pass
    
    def _on_scroll(self, *args):
        """Handle scrolling synchronization between text and line numbers."""
        try:
            # Update both text widgets
            self.xml_text.yview(*args)
            self.line_numbers.yview(*args)
        except Exception:
            pass
    
    def load_engine_preset(self, preset_name):
        """Load engine preset data into the form."""
        engine_presets = PresetManager.get_engine_presets()
        if preset_name in engine_presets:
            preset = engine_presets[preset_name]
            self.engine_data['name'].set(preset['name'])
            self.engine_data['cost'].set(str(preset['cost']))
            self.engine_data['horsepower'].set(str(preset['horsepower']))
            self.engine_data['min_rpm'].set(str(preset['min_rpm']))
            self.engine_data['max_rpm'].set(str(preset['max_rpm']))
            self.engine_data['fuel_usage_scale'].set(str(preset['fuel_usage_scale']))
            self.engine_data['turbocharged'].set(preset['turbocharged'])
    
    def load_transmission_preset(self, preset_name):
        """Load transmission preset data into the form."""
        transmission_presets = PresetManager.get_transmission_presets()
        if preset_name in transmission_presets:
            preset = transmission_presets[preset_name]
            self.transmission_data['name'].set(preset['name'])
            self.transmission_data['cost'].set(str(preset['cost']))
            self.transmission_data['type'].set(preset['type'])
            self.transmission_data['top_speed'].set(str(preset['top_speed']))
            self.transmission_data['num_forward'].set(str(preset['num_forward']))
            self.transmission_data['num_reverse'].set(str(preset['num_reverse']))
            self.transmission_data['enable_low_gearing'].set(preset['enable_low_gearing'])
            self.transmission_data['low_gear_boost'].set(str(preset['low_gear_boost']))
    
    def get_engine_data(self):
        """Get current engine data from form variables."""
        try:
            # Get raw values
            name = self.engine_data['name'].get().strip()
            cost = int(self.engine_data['cost'].get())
            horsepower = float(self.engine_data['horsepower'].get())
            min_rpm = float(self.engine_data['min_rpm'].get())
            max_rpm = float(self.engine_data['max_rpm'].get())
            fuel_usage_scale = float(self.engine_data['fuel_usage_scale'].get())
            turbocharged = self.engine_data['turbocharged'].get()
            
            # Validate input values
            if not name:
                raise ValueError("Engine name cannot be empty")
            if cost < 0:
                raise ValueError("Engine cost cannot be negative")
            if horsepower <= 0:
                raise ValueError("Horsepower must be greater than 0")
            if min_rpm < 0:
                raise ValueError("Minimum RPM cannot be negative")
            if max_rpm <= min_rpm:
                raise ValueError("Maximum RPM must be greater than minimum RPM")
            if fuel_usage_scale <= 0:
                raise ValueError("Fuel usage scale must be greater than 0")
            
            return {
                'name': name,
                'cost': cost,
                'horsepower': horsepower,
                'min_rpm': min_rpm,
                'max_rpm': max_rpm,
                'fuel_usage_scale': fuel_usage_scale,
                'turbocharged': turbocharged
            }
        except ValueError as e:
            raise ValueError(f"Invalid numeric input in engine data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error retrieving engine data: {str(e)}")
    
    def get_transmission_data(self):
        """Get current transmission data from form variables."""
        try:
            # Get raw values
            name = self.transmission_data['name'].get().strip()
            trans_type = self.transmission_data['type'].get()
            cost = int(self.transmission_data['cost'].get())
            top_speed = float(self.transmission_data['top_speed'].get())
            num_forward = int(self.transmission_data['num_forward'].get())
            num_reverse = int(self.transmission_data['num_reverse'].get())
            enable_low_gearing = self.transmission_data['enable_low_gearing'].get()
            low_gear_boost = float(self.transmission_data['low_gear_boost'].get())
            
            # Validate input values
            if not name:
                raise ValueError("Transmission name cannot be empty")
            if trans_type not in ["Manual", "Automatic", "CVT", "PowerShift"]:
                raise ValueError("Invalid transmission type")
            if cost < 0:
                raise ValueError("Transmission cost cannot be negative")
            if top_speed <= 0:
                raise ValueError("Top speed must be greater than 0")
            if num_forward <= 0:
                raise ValueError("Number of forward gears must be greater than 0")
            if num_reverse < 0:
                raise ValueError("Number of reverse gears cannot be negative")
            if low_gear_boost < 0:
                raise ValueError("Low gear boost cannot be negative")
            
            return {
                'name': name,
                'type': trans_type,
                'cost': cost,
                'top_speed': top_speed,
                'num_forward': num_forward,
                'num_reverse': num_reverse,
                'enable_low_gearing': enable_low_gearing,
                'low_gear_boost': low_gear_boost
            }
        except ValueError as e:
            raise ValueError(f"Invalid numeric input in transmission data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error retrieving transmission data: {str(e)}")
    
    def generate_engine_xml(self):
        """Generate and display engine XML."""
        try:
            engine_data = self.get_engine_data()
            xml = XMLGenerator.generate_engine_xml(engine_data)
            self.highlight_xml_syntax(xml)
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid input data: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate engine XML: {str(e)}")
    
    def generate_transmission_xml(self):
        """Generate and display transmission XML."""
        try:
            transmission_data = self.get_transmission_data()
            xml = XMLGenerator.generate_transmission_xml(transmission_data)
            self.highlight_xml_syntax(xml)
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid input data: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate transmission XML: {str(e)}")
    
    def generate_both_xml(self):
        """Generate and display both engine and transmission XML in FS25 format."""
        try:
            engine_data = self.get_engine_data()
            transmission_data = self.get_transmission_data()
            
            # Generate combined XML in FS25 format
            combined_xml = XMLGenerator.generate_combined_fs25_xml(engine_data, transmission_data)
            
            self.highlight_xml_syntax(combined_xml)
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid input data: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate combined XML: {str(e)}")
    
    def save_both_xml(self):
        """Save both engine and transmission XML to separate files."""
        try:
            # Get base filename
            base_filename = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Save Engine XML (Base Name)"
            )
            if not base_filename:
                return
            
            # Remove extension for base name
            base_name = os.path.splitext(base_filename)[0]
            
            # Generate XML
            engine_data = self.get_engine_data()
            transmission_data = self.get_transmission_data()
            
            # Generate combined FS25 XML
            combined_xml = XMLGenerator.generate_combined_fs25_xml(engine_data, transmission_data)
            
            # Save combined XML
            combined_filename = f"{base_name}_fs25.xml"
            with open(combined_filename, 'w', encoding='utf-8') as f:
                f.write(combined_xml)
            
            # Also save separate files for reference
            engine_xml = XMLGenerator.generate_engine_xml(engine_data)
            transmission_xml = XMLGenerator.generate_transmission_xml(transmission_data)
            
            engine_filename = f"{base_name}_engine.xml"
            with open(engine_filename, 'w', encoding='utf-8') as f:
                f.write(engine_xml)
            
            transmission_filename = f"{base_name}_transmission.xml"
            with open(transmission_filename, 'w', encoding='utf-8') as f:
                f.write(transmission_xml)
            
            messagebox.showinfo("Success", 
                              f"Files saved:\n{combined_filename}\n{engine_filename}\n{transmission_filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save XML files: {str(e)}")
    
    def copy_engine_xml(self):
        """Copy engine XML to clipboard."""
        try:
            engine_data = self.get_engine_data()
            xml = XMLGenerator.generate_engine_xml(engine_data)
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(xml)
                messagebox.showinfo("Success", "Engine XML copied to clipboard")
            except tk.TclError as e:
                messagebox.showerror("Clipboard Error", f"Failed to access clipboard: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy engine XML: {str(e)}")
    
    def copy_transmission_xml(self):
        """Copy transmission XML to clipboard."""
        try:
            transmission_data = self.get_transmission_data()
            xml = XMLGenerator.generate_transmission_xml(transmission_data)
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(xml)
                messagebox.showinfo("Success", "Transmission XML copied to clipboard")
            except tk.TclError as e:
                messagebox.showerror("Clipboard Error", f"Failed to access clipboard: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy transmission XML: {str(e)}")
    
    def save_engine_xml(self):
        """Save engine XML to file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Save Engine XML"
            )
            if filename:
                # Validate filename
                if not filename.strip():
                    messagebox.showerror("Error", "Invalid filename provided")
                    return
                
                # Get and validate data before saving
                try:
                    engine_data = self.get_engine_data()
                except ValueError as e:
                    messagebox.showerror("Validation Error", f"Invalid engine data: {str(e)}")
                    return
                except Exception as e:
                    messagebox.showerror("Data Error", f"Failed to retrieve engine data: {str(e)}")
                    return
                
                # Generate XML
                try:
                    xml = XMLGenerator.generate_engine_xml(engine_data)
                except Exception as e:
                    messagebox.showerror("XML Generation Error", f"Failed to generate XML: {str(e)}")
                    return
                
                # Save file with specific error handling
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(xml)
                    messagebox.showinfo("Success", f"Engine XML saved to {filename}")
                except PermissionError:
                    messagebox.showerror("Permission Error", f"Cannot save to {filename}. Check file permissions.")
                except OSError as e:
                    messagebox.showerror("File System Error", f"Failed to save file: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Unexpected error while saving: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save engine XML: {str(e)}")
    
    def save_transmission_xml(self):
        """Save transmission XML to file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Save Transmission XML"
            )
            if filename:
                # Validate filename
                if not filename.strip():
                    messagebox.showerror("Error", "Invalid filename provided")
                    return
                
                # Get and validate data before saving
                try:
                    transmission_data = self.get_transmission_data()
                except ValueError as e:
                    messagebox.showerror("Validation Error", f"Invalid transmission data: {str(e)}")
                    return
                except Exception as e:
                    messagebox.showerror("Data Error", f"Failed to retrieve transmission data: {str(e)}")
                    return
                
                # Generate XML
                try:
                    xml = XMLGenerator.generate_transmission_xml(transmission_data)
                except Exception as e:
                    messagebox.showerror("XML Generation Error", f"Failed to generate XML: {str(e)}")
                    return
                
                # Save file with specific error handling
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(xml)
                    messagebox.showinfo("Success", f"Transmission XML saved to {filename}")
                except PermissionError:
                    messagebox.showerror("Permission Error", f"Cannot save to {filename}. Check file permissions.")
                except OSError as e:
                    messagebox.showerror("File System Error", f"Failed to save file: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Unexpected error while saving: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transmission XML: {str(e)}")
    
    def save_current_preset(self):
        """Save current configuration as a preset."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Configuration Preset"
            )
            if filename:
                # Validate filename
                if not filename.strip():
                    messagebox.showerror("Error", "Invalid filename provided")
                    return
                
                # Get and validate data before saving
                try:
                    engine_data = self.get_engine_data()
                    transmission_data = self.get_transmission_data()
                except ValueError as e:
                    messagebox.showerror("Validation Error", f"Invalid configuration data: {str(e)}")
                    return
                except Exception as e:
                    messagebox.showerror("Data Error", f"Failed to retrieve configuration data: {str(e)}")
                    return
                
                preset_data = {
                    'engine': engine_data,
                    'transmission': transmission_data
                }
                
                # Save with specific error handling
                try:
                    PresetManager.save_preset(preset_data, filename)
                except PermissionError:
                    messagebox.showerror("Permission Error", f"Cannot save to {filename}. Check file permissions.")
                except OSError as e:
                    messagebox.showerror("File System Error", f"Failed to save file: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Unexpected error while saving: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preset: {str(e)}")
    
    def load_current_preset(self):
        """Load configuration from a preset file."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Configuration Preset"
            )
            if filename:
                preset_data = PresetManager.load_preset(filename)
                if preset_data:
                    # Load engine data with error handling
                    if 'engine' in preset_data:
                        try:
                            engine = preset_data['engine']
                            # Validate engine data structure
                            required_engine_fields = ['name', 'cost', 'horsepower', 'min_rpm', 'max_rpm', 'fuel_usage_scale', 'turbocharged']
                            for field in required_engine_fields:
                                if field not in engine:
                                    raise ValueError(f"Missing required engine field: {field}")
                            
                            self.engine_data['name'].set(str(engine['name']))
                            self.engine_data['cost'].set(str(engine['cost']))
                            self.engine_data['horsepower'].set(str(engine['horsepower']))
                            self.engine_data['min_rpm'].set(str(engine['min_rpm']))
                            self.engine_data['max_rpm'].set(str(engine['max_rpm']))
                            self.engine_data['fuel_usage_scale'].set(str(engine['fuel_usage_scale']))
                            self.engine_data['turbocharged'].set(bool(engine['turbocharged']))
                        except (KeyError, ValueError, TypeError) as e:
                            messagebox.showerror("Error", f"Invalid engine data in preset: {str(e)}")
                            return
                    
                    # Load transmission data with error handling
                    if 'transmission' in preset_data:
                        try:
                            trans = preset_data['transmission']
                            # Validate transmission data structure
                            required_trans_fields = ['name', 'cost', 'type', 'top_speed', 'num_forward', 'num_reverse', 'enable_low_gearing', 'low_gear_boost']
                            for field in required_trans_fields:
                                if field not in trans:
                                    raise ValueError(f"Missing required transmission field: {field}")
                            
                            self.transmission_data['name'].set(str(trans['name']))
                            self.transmission_data['cost'].set(str(trans['cost']))
                            self.transmission_data['type'].set(str(trans['type']))
                            self.transmission_data['top_speed'].set(str(trans['top_speed']))
                            self.transmission_data['num_forward'].set(str(trans['num_forward']))
                            self.transmission_data['num_reverse'].set(str(trans['num_reverse']))
                            self.transmission_data['enable_low_gearing'].set(bool(trans['enable_low_gearing']))
                            self.transmission_data['low_gear_boost'].set(str(trans['low_gear_boost']))
                        except (KeyError, ValueError, TypeError) as e:
                            messagebox.showerror("Error", f"Invalid transmission data in preset: {str(e)}")
                            return
                    
                    messagebox.showinfo("Success", "Preset loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset: {str(e)}")
    
    def add_to_presets(self):
        """Add current configuration to the preset lists."""
        try:
            # Get current configuration
            try:
                engine_data = self.get_engine_data()
                transmission_data = self.get_transmission_data()
            except ValueError as e:
                messagebox.showerror("Validation Error", f"Invalid configuration data: {str(e)}")
                return
            except Exception as e:
                messagebox.showerror("Data Error", f"Failed to retrieve configuration data: {str(e)}")
                return
            
            # Ask user for preset name
            preset_name = tk.simpledialog.askstring("Add Preset", 
                                                   "Enter a name for this preset:")
            if not preset_name:
                return
            
            # Validate preset name
            preset_name = preset_name.strip()
            if not preset_name:
                messagebox.showerror("Error", "Preset name cannot be empty")
                return
            
            # Check for invalid characters
            import re
            invalid_chars = re.findall(r'[<>:"/\\|?*]', preset_name)
            if invalid_chars:
                messagebox.showerror("Error", f"Preset name contains invalid characters: {', '.join(set(invalid_chars))}")
                return
            
            # Check length limits
            if len(preset_name) > 50:
                messagebox.showerror("Error", "Preset name must be 50 characters or less")
                return
            
            # Check for duplicates
            if preset_name in PresetManager.get_engine_presets():
                result = messagebox.askyesno("Duplicate Preset", 
                                           f"Preset '{preset_name}' already exists. Do you want to overwrite it?")
                if not result:
                    return
            
            # Add to engine presets (thread-safe)
            PresetManager.add_engine_preset(preset_name, engine_data)
            
            # Add to transmission presets (thread-safe)
            PresetManager.add_transmission_preset(preset_name, transmission_data)
            
            messagebox.showinfo("Success", f"Preset '{preset_name}' added successfully!")
            
            # Refresh preset dropdowns
            self.refresh_preset_dropdowns()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add preset: {str(e)}")
    
    def refresh_preset_dropdowns(self):
        """Refresh the preset dropdown lists."""
        try:
            # Get thread-safe copies of preset lists
            engine_presets = PresetManager.get_engine_presets()
            transmission_presets = PresetManager.get_transmission_presets()
            
            # Refresh engine preset dropdown
            if self.engine_preset_dropdown:
                if CUSTOM_TKINTER_AVAILABLE:
                    # For CustomTkinter OptionMenu
                    self.engine_preset_dropdown.configure(values=list(engine_presets.keys()))
                else:
                    # For standard Tkinter Combobox
                    self.engine_preset_dropdown['values'] = list(engine_presets.keys())
            
            # Refresh transmission preset dropdown
            if self.transmission_preset_dropdown:
                if CUSTOM_TKINTER_AVAILABLE:
                    # For CustomTkinter OptionMenu
                    self.transmission_preset_dropdown.configure(values=list(transmission_presets.keys()))
                else:
                    # For standard Tkinter Combobox
                    self.transmission_preset_dropdown['values'] = list(transmission_presets.keys())
                    
        except Exception as e:
            print(f"Error refreshing preset dropdowns: {str(e)}")


def run_app() -> None:
    """
    Main entry point for the application.
    Creates the main window and starts the application.
    """
    if CUSTOM_TKINTER_AVAILABLE:
        root = ctk.CTk()
    else:
        root = tk.Tk()
    
    app = FS25ConfigTool(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()

