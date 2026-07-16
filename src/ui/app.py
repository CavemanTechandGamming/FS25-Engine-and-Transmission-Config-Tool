#!/usr/bin/env python3
"""FS25 Engine and Transmission Config Tool — main window and UI."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from typing import Dict, List, Optional, Tuple

try:
    import customtkinter as ctk

    CUSTOM_TKINTER_AVAILABLE = True
except ImportError:
    CUSTOM_TKINTER_AVAILABLE = False
    print("CustomTkinter not available, using standard Tkinter")

from src import __version__
from src.core.logging_setup import setup_logging
from src.core.paths import app_icon_ico, app_icon_png
from src.core.presets import PresetManager
from src.core import settings as app_settings
from src.core.xml_gen import XMLGenerator
from src.ui.about import show_about
from src.ui.dialogs import (
    ask_string,
    ask_yes_no,
    set_dialog_parent,
    show_error,
    show_info,
)
from src.ui.settings_dialog import show_settings

import logging
import sys

logger = logging.getLogger("fs25config.app")

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
        set_dialog_parent(self.root)
        self.apply_window_icon()

        setup_logging()
        app_settings.load_settings()
        PresetManager.reload_custom_presets()
        
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
        self.apply_startup_default_presets()
        self.root.after(50, self.center_main_window)
        logger.info("UI ready")

    def apply_window_icon(self) -> None:
        """Apply the pixel-art app icon to the window (and taskbar where supported)."""
        try:
            ico = app_icon_ico()
            png = app_icon_png()
            if sys.platform.startswith("win") and ico is not None:
                try:
                    self.root.iconbitmap(default=str(ico))
                except Exception:
                    self.root.iconbitmap(str(ico))
            if png is not None:
                # Keep a reference so Tk does not garbage-collect the image
                self._window_icon = tk.PhotoImage(file=str(png))
                self.root.iconphoto(True, self._window_icon)
            elif ico is not None and not sys.platform.startswith("win"):
                try:
                    self.root.iconbitmap(str(ico))
                except Exception:
                    pass
        except Exception as e:
            logger.warning("Could not apply window icon: %s", e)

    def center_main_window(self, width: int = 1400, height: int = 900) -> None:
        """Place the main window near the center of the primary screen."""
        try:
            self.root.update_idletasks()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            # Keep size within the screen (taskbar / small displays)
            w = min(width, max(800, sw - 40))
            h = min(height, max(600, sh - 80))
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass
    
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
        
        self.apply_dark_theme()
    
    def setup_gui(self):
        """Set up the main GUI layout with all components."""
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_gui()
        else:
            self.setup_standard_gui()
    
    def setup_custom_gui(self):
        """Set up a single-page GUI: engine/transmission stacked left, XML right."""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=2, minsize=420)  # forms
        main_frame.grid_columnconfigure(1, weight=3)  # XML
        main_frame.grid_rowconfigure(1, weight=1)

        # Title row with About (spans both columns)
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 8))
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

        settings_btn = ctk.CTkButton(
            header,
            text="Settings",
            width=90,
            fg_color=("gray70", "gray35"),
            hover_color=("gray60", "gray30"),
            command=self.open_settings,
        )
        settings_btn.grid(row=0, column=2, sticky="e", padx=(8, 0))
        Tooltip(settings_btn, "Custom preset folder, defaults, and log location")

        # Left: Engine (top) + Transmission (bottom)
        left_col = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_col.grid(row=1, column=0, sticky="nsew", padx=(6, 4), pady=(0, 6))
        left_col.grid_columnconfigure(0, weight=1)
        left_col.grid_rowconfigure(0, weight=1)
        left_col.grid_rowconfigure(1, weight=1)

        engine_panel = ctk.CTkFrame(left_col)
        engine_panel.grid(row=0, column=0, sticky="nsew", padx=4, pady=(4, 4))
        engine_label = ctk.CTkLabel(
            engine_panel,
            text="Engine",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        engine_label.pack(anchor="w", padx=12, pady=(10, 0))
        engine_body = ctk.CTkFrame(engine_panel, fg_color="transparent")
        engine_body.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
        self.setup_engine_tab(engine_body)

        transmission_panel = ctk.CTkFrame(left_col)
        transmission_panel.grid(row=1, column=0, sticky="nsew", padx=4, pady=(4, 4))
        transmission_label = ctk.CTkLabel(
            transmission_panel,
            text="Transmission",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        transmission_label.pack(anchor="w", padx=12, pady=(10, 0))
        transmission_body = ctk.CTkFrame(transmission_panel, fg_color="transparent")
        transmission_body.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
        self.setup_transmission_tab(transmission_body)

        # Right: Generated XML + actions
        output_panel = ctk.CTkFrame(main_frame)
        output_panel.grid(row=1, column=1, sticky="nsew", padx=(4, 6), pady=(0, 6))
        self.setup_output_tab(output_panel)

    def setup_standard_gui(self):
        """Set up a single-page GUI using standard Tkinter widgets."""
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=2, minsize=420)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(1, weight=1)

        header = tk.Frame(main_frame, bg=self.colors['bg'])
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

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

        settings_btn = tk.Button(
            header,
            text="Settings",
            command=self.open_settings,
            bg=self.colors.get('button', '#404040'),
            fg=self.colors['fg'],
        )
        settings_btn.pack(side=tk.RIGHT, padx=(0, 8))
        Tooltip(settings_btn, "Custom preset folder, defaults, and log location")

        left_col = tk.Frame(main_frame, bg=self.colors['bg'])
        left_col.grid(row=1, column=0, sticky="nsew", padx=(0, 4))
        left_col.grid_columnconfigure(0, weight=1)
        left_col.grid_rowconfigure(0, weight=1)
        left_col.grid_rowconfigure(1, weight=1)

        engine_panel = tk.LabelFrame(
            left_col,
            text="Engine",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        engine_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        self.setup_engine_tab(engine_panel)

        transmission_panel = tk.LabelFrame(
            left_col,
            text="Transmission",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        transmission_panel.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.setup_transmission_tab(transmission_panel)

        output_panel = tk.Frame(main_frame, bg=self.colors['bg'])
        output_panel.grid(row=1, column=1, sticky="nsew", padx=(4, 0))
        self.setup_output_tab(output_panel)
    
    def setup_engine_tab(self, parent):
        """Set up the engine configuration tab."""
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_engine_tab(parent)
        else:
            self.setup_standard_engine_tab(parent)
    
    def setup_custom_engine_tab(self, parent):
        """Set up engine panel using CustomTkinter widgets (compact paired fields)."""
        preset_row = ctk.CTkFrame(parent, fg_color="transparent")
        preset_row.pack(fill=tk.X, padx=8, pady=(6, 4))

        preset_combo = ctk.CTkOptionMenu(
            preset_row,
            values=list(PresetManager.get_engine_presets().keys()),
            command=self.load_engine_preset,
            width=220,
        )
        preset_combo.pack(side=tk.LEFT, padx=(0, 6))
        self.engine_preset_dropdown = preset_combo

        load_preset_btn = ctk.CTkButton(
            preset_row,
            text="Load",
            width=64,
            command=lambda: self.load_engine_preset(preset_combo.get()),
        )
        load_preset_btn.pack(side=tk.LEFT, padx=(0, 6))
        Tooltip(load_preset_btn, "Load the selected engine preset into the form")

        save_preset_btn = ctk.CTkButton(
            preset_row,
            text="Save",
            width=64,
            command=self.save_custom_engine_preset,
        )
        save_preset_btn.pack(side=tk.LEFT)
        Tooltip(save_preset_btn, "Save current engine settings as a custom preset (Engine presets folder)")

        fields = ctk.CTkFrame(parent, fg_color="transparent")
        fields.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2, 6))

        self.create_custom_input_field(
            fields, "Name:", self.engine_data['name'],
            "Enter the name of the engine",
        )
        self._ctk_field_row(
            fields,
            ("Cost ($):", self.engine_data['cost'],
             "Enter the cost of the engine in dollars", 90),
            ("HP:", self.engine_data['horsepower'],
             "Enter the engine's rated horsepower. Used to calculate torque curve", 80),
        )
        self._ctk_field_row(
            fields,
            ("Min RPM:", self.engine_data['min_rpm'],
             "Enter the minimum RPM of the engine", 90),
            ("Max RPM:", self.engine_data['max_rpm'],
             "Enter the maximum RPM of the engine (default: 3500)", 90),
        )
        fuel_row = ctk.CTkFrame(fields, fg_color="transparent")
        fuel_row.pack(fill=tk.X, pady=3)
        fuel_row.grid_columnconfigure(0, weight=1)
        fuel_row.grid_columnconfigure(1, weight=0)

        fuel_cell = self._ctk_field_cell(
            fuel_row, "Fuel Scale:", self.engine_data['fuel_usage_scale'],
            "Enter the fuel usage scale factor (default: 1.0)", entry_width=90,
        )
        fuel_cell.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        turbo_check = ctk.CTkCheckBox(
            fuel_row,
            text="Turbocharged",
            variable=self.engine_data['turbocharged'],
        )
        turbo_check.grid(row=0, column=1, sticky="w")
        Tooltip(turbo_check, "Check if the engine is turbocharged. Affects torque curve generation")
    
    def setup_standard_engine_tab(self, parent):
        """Set up engine panel using standard Tkinter widgets (compact paired fields)."""
        preset_row = tk.Frame(parent, bg=self.colors['bg'])
        preset_row.pack(fill=tk.X, padx=8, pady=(6, 4))

        preset_var = tk.StringVar()
        preset_combo = ttk.Combobox(
            preset_row, textvariable=preset_var,
            values=list(PresetManager.get_engine_presets().keys()),
            state="readonly", width=28,
        )
        preset_combo.pack(side=tk.LEFT, padx=(0, 6))
        preset_combo.bind(
            '<<ComboboxSelected>>',
            lambda e: self.load_engine_preset(preset_var.get()),
        )
        self.engine_preset_dropdown = preset_combo

        load_preset_btn = tk.Button(
            preset_row, text="Load",
            command=lambda: self.load_engine_preset(preset_var.get()),
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            relief=tk.RAISED, borderwidth=1,
        )
        load_preset_btn.pack(side=tk.LEFT, padx=(0, 6))
        Tooltip(load_preset_btn, "Load the selected engine preset into the form")

        save_preset_btn = tk.Button(
            preset_row, text="Save",
            command=self.save_custom_engine_preset,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            relief=tk.RAISED, borderwidth=1,
        )
        save_preset_btn.pack(side=tk.LEFT)
        Tooltip(save_preset_btn, "Save current engine settings as a custom preset (Engine presets folder)")

        fields = tk.Frame(parent, bg=self.colors['bg'])
        fields.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2, 6))

        self.create_input_field(
            fields, "Name:", self.engine_data['name'],
            "Enter the name of the engine",
        )
        self._tk_field_row(
            fields,
            ("Cost ($):", self.engine_data['cost'],
             "Enter the cost of the engine in dollars", 10),
            ("HP:", self.engine_data['horsepower'],
             "Enter the engine's rated horsepower. Used to calculate torque curve", 8),
        )
        self._tk_field_row(
            fields,
            ("Min RPM:", self.engine_data['min_rpm'],
             "Enter the minimum RPM of the engine", 10),
            ("Max RPM:", self.engine_data['max_rpm'],
             "Enter the maximum RPM of the engine (default: 3500)", 10),
        )
        fuel_row = tk.Frame(fields, bg=self.colors['bg'])
        fuel_row.pack(fill=tk.X, pady=3)

        self.create_input_field(
            fuel_row, "Fuel Scale:", self.engine_data['fuel_usage_scale'],
            "Enter the fuel usage scale factor (default: 1.0)",
            entry_width=10, expand=False, fill_row=False,
        )
        turbo_check = tk.Checkbutton(
            fuel_row, text="Turbocharged",
            variable=self.engine_data['turbocharged'],
            bg=self.colors['bg'], fg=self.colors['fg'],
            selectcolor=self.colors['input_bg'],
        )
        turbo_check.pack(side=tk.LEFT, padx=(12, 0))
        Tooltip(turbo_check, "Check if the engine is turbocharged. Affects torque curve generation")
    
    def setup_transmission_tab(self, parent):
        """Set up the transmission configuration tab."""
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_transmission_tab(parent)
        else:
            self.setup_standard_transmission_tab(parent)
    
    def setup_custom_transmission_tab(self, parent):
        """Set up transmission panel using CustomTkinter widgets (compact paired fields)."""
        preset_row = ctk.CTkFrame(parent, fg_color="transparent")
        preset_row.pack(fill=tk.X, padx=8, pady=(6, 4))

        preset_combo = ctk.CTkOptionMenu(
            preset_row,
            values=list(PresetManager.get_transmission_presets().keys()),
            command=self.load_transmission_preset,
            width=220,
        )
        preset_combo.pack(side=tk.LEFT, padx=(0, 6))
        self.transmission_preset_dropdown = preset_combo

        load_preset_btn = ctk.CTkButton(
            preset_row,
            text="Load",
            width=64,
            command=lambda: self.load_transmission_preset(preset_combo.get()),
        )
        load_preset_btn.pack(side=tk.LEFT, padx=(0, 6))
        Tooltip(load_preset_btn, "Load the selected transmission preset into the form")

        save_preset_btn = ctk.CTkButton(
            preset_row,
            text="Save",
            width=64,
            command=self.save_custom_transmission_preset,
        )
        save_preset_btn.pack(side=tk.LEFT)
        Tooltip(save_preset_btn, "Save current transmission settings as a custom preset (Transmission presets folder)")

        fields = ctk.CTkFrame(parent, fg_color="transparent")
        fields.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2, 6))

        self.create_custom_input_field(
            fields, "Name:", self.transmission_data['name'],
            "Enter the name of the transmission",
        )
        cost_type = ctk.CTkFrame(fields, fg_color="transparent")
        cost_type.pack(fill=tk.X, pady=3)
        cost_type.grid_columnconfigure(0, weight=1)
        cost_type.grid_columnconfigure(1, weight=1)

        cost_cell = self._ctk_field_cell(
            cost_type, "Cost ($):", self.transmission_data['cost'],
            "Enter the cost of the transmission in dollars", entry_width=90,
        )
        cost_cell.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        type_cell = ctk.CTkFrame(cost_type, fg_color="transparent")
        type_cell.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        type_label = ctk.CTkLabel(type_cell, text="Type:")
        type_label.pack(side=tk.LEFT, padx=(0, 6))
        type_combo = ctk.CTkOptionMenu(
            type_cell,
            values=["Manual", "Automatic", "CVT", "PowerShift"],
            variable=self.transmission_data['type'],
            width=120,
        )
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        Tooltip(type_combo, "Select the type of transmission")

        self._ctk_field_row(
            fields,
            ("Top Speed:", self.transmission_data['top_speed'],
             "Enter the maximum speed of the vehicle in km/h", 90),
            ("Fwd Gears:", self.transmission_data['num_forward'],
             "Enter the number of forward gears", 70),
        )
        gear_row = ctk.CTkFrame(fields, fg_color="transparent")
        gear_row.pack(fill=tk.X, pady=3)
        gear_row.grid_columnconfigure(0, weight=1)
        gear_row.grid_columnconfigure(1, weight=1)

        rev_cell = self._ctk_field_cell(
            gear_row, "Rev Gears:", self.transmission_data['num_reverse'],
            "Enter the number of reverse gears", entry_width=70,
        )
        rev_cell.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        boost_cell = ctk.CTkFrame(gear_row, fg_color="transparent")
        boost_cell.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        low_gear_check = ctk.CTkCheckBox(
            boost_cell,
            text="Low Gearing",
            variable=self.transmission_data['enable_low_gearing'],
            width=110,
        )
        low_gear_check.pack(side=tk.LEFT, padx=(0, 8))
        Tooltip(
            low_gear_check,
            "Enable low gearing for enhanced torque output in first 25% of gears",
        )
        boost_label = ctk.CTkLabel(boost_cell, text="Boost %:")
        boost_label.pack(side=tk.LEFT, padx=(0, 6))
        boost_entry = ctk.CTkEntry(
            boost_cell,
            textvariable=self.transmission_data['low_gear_boost'],
            width=70,
        )
        boost_entry.pack(side=tk.LEFT)
        Tooltip(boost_entry, "Percentage boost for low gears (e.g., 25 for 25% boost)")
    
    def setup_standard_transmission_tab(self, parent):
        """Set up transmission panel using standard Tkinter widgets (compact paired fields)."""
        preset_row = tk.Frame(parent, bg=self.colors['bg'])
        preset_row.pack(fill=tk.X, padx=8, pady=(6, 4))

        preset_var = tk.StringVar()
        preset_combo = ttk.Combobox(
            preset_row, textvariable=preset_var,
            values=list(PresetManager.get_transmission_presets().keys()),
            state="readonly", width=28,
        )
        preset_combo.pack(side=tk.LEFT, padx=(0, 6))
        self.transmission_preset_dropdown = preset_combo

        load_preset_btn = tk.Button(
            preset_row, text="Load",
            command=lambda: self.load_transmission_preset(preset_var.get()),
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            relief=tk.RAISED, borderwidth=1,
        )
        load_preset_btn.pack(side=tk.LEFT, padx=(0, 6))
        Tooltip(load_preset_btn, "Load the selected transmission preset into the form")

        save_preset_btn = tk.Button(
            preset_row, text="Save",
            command=self.save_custom_transmission_preset,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            relief=tk.RAISED, borderwidth=1,
        )
        save_preset_btn.pack(side=tk.LEFT)
        Tooltip(save_preset_btn, "Save current transmission settings as a custom preset (Transmission presets folder)")

        fields = tk.Frame(parent, bg=self.colors['bg'])
        fields.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2, 6))

        self.create_input_field(
            fields, "Name:", self.transmission_data['name'],
            "Enter the name of the transmission",
        )
        cost_type = tk.Frame(fields, bg=self.colors['bg'])
        cost_type.pack(fill=tk.X, pady=3)

        self.create_input_field(
            cost_type, "Cost ($):", self.transmission_data['cost'],
            "Enter the cost of the transmission in dollars",
            entry_width=10, expand=False, fill_row=False,
        )
        type_label = tk.Label(
            cost_type, text="Type:",
            bg=self.colors['bg'], fg=self.colors['fg'],
        )
        type_label.pack(side=tk.LEFT, padx=(12, 4))
        type_combo = ttk.Combobox(
            cost_type, textvariable=self.transmission_data['type'],
            values=["Manual", "Automatic", "CVT", "PowerShift"],
            state="readonly", width=12,
        )
        type_combo.pack(side=tk.LEFT)
        Tooltip(type_combo, "Select the type of transmission")

        self._tk_field_row(
            fields,
            ("Top Speed:", self.transmission_data['top_speed'],
             "Enter the maximum speed of the vehicle in km/h", 10),
            ("Fwd Gears:", self.transmission_data['num_forward'],
             "Enter the number of forward gears", 6),
        )
        gear_row = tk.Frame(fields, bg=self.colors['bg'])
        gear_row.pack(fill=tk.X, pady=3)

        self.create_input_field(
            gear_row, "Rev Gears:", self.transmission_data['num_reverse'],
            "Enter the number of reverse gears",
            entry_width=6, expand=False, fill_row=False,
        )
        low_gear_check = tk.Checkbutton(
            gear_row, text="Low Gearing",
            variable=self.transmission_data['enable_low_gearing'],
            bg=self.colors['bg'], fg=self.colors['fg'],
            selectcolor=self.colors['input_bg'],
        )
        low_gear_check.pack(side=tk.LEFT, padx=(12, 6))
        Tooltip(
            low_gear_check,
            "Enable low gearing for enhanced torque output in first 25% of gears",
        )
        boost_label = tk.Label(
            gear_row, text="Boost %:",
            bg=self.colors['bg'], fg=self.colors['fg'],
        )
        boost_label.pack(side=tk.LEFT)
        boost_entry = tk.Entry(
            gear_row, textvariable=self.transmission_data['low_gear_boost'],
            bg=self.colors['input_bg'], fg=self.colors['fg'],
            relief=tk.SOLID, borderwidth=1, width=6,
        )
        boost_entry.pack(side=tk.LEFT, padx=4)
        Tooltip(boost_entry, "Percentage boost for low gears (e.g., 25 for 25% boost)")
    
    def setup_output_tab(self, parent):
        """Set up the output tab with XML preview and action buttons."""
        if CUSTOM_TKINTER_AVAILABLE:
            self.setup_custom_output_tab(parent)
        else:
            self.setup_standard_output_tab(parent)
    
    def setup_custom_output_tab(self, parent):
        """Set up output panel: clean action bar + XML preview."""
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill=tk.X, padx=10, pady=(8, 4))
        toolbar.grid_columnconfigure(0, weight=1)
        toolbar.grid_columnconfigure(1, weight=0)

        primary = ctk.CTkFrame(toolbar, fg_color="transparent")
        primary.grid(row=0, column=0, sticky="w")

        generate_btn = ctk.CTkButton(
            primary,
            text="Generate XML",
            width=130,
            command=self.generate_both_xml,
        )
        generate_btn.pack(side=tk.LEFT, padx=(0, 8))
        Tooltip(generate_btn, "Generate combined FS25 engine + transmission XML")

        copy_btn = ctk.CTkButton(
            primary,
            text="Copy",
            width=90,
            fg_color=("gray70", "gray35"),
            hover_color=("gray60", "gray30"),
            command=self.copy_generated_xml,
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 8))
        Tooltip(copy_btn, "Copy the combined FS25 XML to the clipboard")

        save_btn = ctk.CTkButton(
            primary,
            text="Save…",
            width=90,
            fg_color=("gray70", "gray35"),
            hover_color=("gray60", "gray30"),
            command=self.save_both_xml,
        )
        save_btn.pack(side=tk.LEFT)
        Tooltip(save_btn, "Save combined FS25 XML (and separate engine/transmission files)")

        presets = ctk.CTkFrame(toolbar, fg_color="transparent")
        presets.grid(row=0, column=1, sticky="e")

        preset_label = ctk.CTkLabel(
            presets,
            text="Presets",
            font=ctk.CTkFont(size=12),
            text_color="gray65",
        )
        preset_label.pack(side=tk.LEFT, padx=(0, 8))

        save_preset_btn = ctk.CTkButton(
            presets,
            text="Export",
            width=70,
            fg_color=("gray70", "gray35"),
            hover_color=("gray60", "gray30"),
            command=self.save_current_preset,
        )
        save_preset_btn.pack(side=tk.LEFT, padx=(0, 6))
        Tooltip(save_preset_btn, "Export engine + transmission settings to a JSON file")

        load_preset_btn = ctk.CTkButton(
            presets,
            text="Import",
            width=70,
            fg_color=("gray70", "gray35"),
            hover_color=("gray60", "gray30"),
            command=self.load_current_preset,
        )
        load_preset_btn.pack(side=tk.LEFT)
        Tooltip(load_preset_btn, "Import engine + transmission settings from a JSON file")

        preview_frame = ctk.CTkFrame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 8))

        preview_header = ctk.CTkFrame(preview_frame, fg_color="transparent")
        preview_header.pack(fill=tk.X, padx=10, pady=(8, 0))
        preview_label = ctk.CTkLabel(
            preview_header,
            text="XML Preview",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        preview_label.pack(side=tk.LEFT)

        text_frame = ctk.CTkFrame(preview_frame, fg_color=self.colors['input_bg'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._build_xml_preview_area(text_frame, use_ctk=True)
        self.setup_xml_syntax_highlighting()

    def setup_standard_output_tab(self, parent):
        """Set up output panel using standard Tkinter widgets."""
        toolbar = tk.Frame(parent, bg=self.colors['bg'])
        toolbar.pack(fill=tk.X, padx=10, pady=(8, 4))

        primary = tk.Frame(toolbar, bg=self.colors['bg'])
        primary.pack(side=tk.LEFT)

        generate_btn = tk.Button(
            primary,
            text="Generate XML",
            command=self.generate_both_xml,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            relief=tk.RAISED,
            borderwidth=1,
            font=("Arial", 10, "bold"),
            padx=10,
        )
        generate_btn.pack(side=tk.LEFT, padx=(0, 8))
        Tooltip(generate_btn, "Generate combined FS25 engine + transmission XML")

        copy_btn = tk.Button(
            primary,
            text="Copy",
            command=self.copy_generated_xml,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            relief=tk.RAISED,
            borderwidth=1,
            width=10,
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 8))
        Tooltip(copy_btn, "Copy the combined FS25 XML to the clipboard")

        save_btn = tk.Button(
            primary,
            text="Save…",
            command=self.save_both_xml,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            relief=tk.RAISED,
            borderwidth=1,
            width=10,
        )
        save_btn.pack(side=tk.LEFT)
        Tooltip(save_btn, "Save combined FS25 XML (and separate engine/transmission files)")

        presets = tk.Frame(toolbar, bg=self.colors['bg'])
        presets.pack(side=tk.RIGHT)

        tk.Label(
            presets,
            text="Presets",
            bg=self.colors['bg'],
            fg=self.colors['secondary_fg'],
            font=("Arial", 9),
        ).pack(side=tk.LEFT, padx=(0, 8))

        for text, cmd, tip in (
            ("Export", self.save_current_preset, "Export engine + transmission settings to a JSON file"),
            ("Import", self.load_current_preset, "Import engine + transmission settings from a JSON file"),
        ):
            btn = tk.Button(
                presets,
                text=text,
                command=cmd,
                bg=self.colors['button_bg'],
                fg=self.colors['fg'],
                relief=tk.RAISED,
                borderwidth=1,
                width=8,
            )
            btn.pack(side=tk.LEFT, padx=(0, 6))
            Tooltip(btn, tip)

        preview_frame = tk.LabelFrame(
            parent,
            text="XML Preview",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=("Arial", 10, "bold"),
        )
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 8))

        text_frame = tk.Frame(preview_frame, bg=self.colors['input_bg'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._build_xml_preview_area(text_frame, use_ctk=False)
        self.setup_xml_syntax_highlighting()
    
    def _build_xml_preview_area(self, text_frame, *, use_ctk: bool) -> None:
        """Build themed XML preview with word wrap, line numbers, and auto-hiding v-scrollbar."""
        self._xml_preview_frame = text_frame
        self._v_scrollbar_visible = False
        self._h_scrollbar_visible = False
        self.h_scrollbar = None

        # Grid keeps a reserved gutter so showing/hiding the vertical scrollbar doesn't jump text.
        gutter = 16
        text_frame.grid_columnconfigure(0, weight=0)  # line numbers
        text_frame.grid_columnconfigure(1, weight=1)  # XML text
        text_frame.grid_columnconfigure(2, weight=0, minsize=gutter)  # vertical scrollbar gutter
        text_frame.grid_rowconfigure(0, weight=1)

        self.line_numbers = tk.Text(
            text_frame,
            bg=self.colors['bg'],
            fg=self.colors['secondary_fg'],
            font=("Consolas", 9),
            width=4,
            padx=5,
            pady=5,
            wrap=tk.NONE,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            state=tk.DISABLED,
        )
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        self.xml_text = tk.Text(
            text_frame,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=("Consolas", 9),
            wrap=tk.WORD,
            insertbackground=self.colors['fg'],
            padx=5,
            pady=5,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
        )
        self.xml_text.grid(row=0, column=1, sticky="nsew")

        if use_ctk and CUSTOM_TKINTER_AVAILABLE:
            self.v_scrollbar = ctk.CTkScrollbar(
                text_frame,
                orientation="vertical",
                command=self._scroll_y,
                width=gutter,
            )
        else:
            self.v_scrollbar = ttk.Scrollbar(
                text_frame,
                orient=tk.VERTICAL,
                command=self._scroll_y,
                style="Preview.Vertical.TScrollbar",
            )

        self.xml_text.configure(yscrollcommand=self._on_yview_changed)
        self.xml_text.bind("<Configure>", self._on_preview_configure, add="+")
        # Mouse wheel still works when scrollbars are hidden
        self.xml_text.bind("<MouseWheel>", self._on_mousewheel, add="+")
        self.xml_text.bind("<Button-4>", self._on_mousewheel, add="+")
        self.xml_text.bind("<Button-5>", self._on_mousewheel, add="+")

    def _scroll_y(self, *args) -> None:
        """Scrollbar/thumb command: scroll preview + line numbers together."""
        try:
            self.xml_text.yview(*args)
            self.line_numbers.yview(*args)
        except Exception:
            pass

    def _on_yview_changed(self, first: str, last: str) -> None:
        """Update vertical scrollbar thumb and visibility from Text widget."""
        try:
            self.v_scrollbar.set(first, last)
            self.line_numbers.yview_moveto(float(first))
        except Exception:
            pass
        need = float(first) > 0.001 or float(last) < 0.999
        self._set_v_scrollbar_visible(need)

    def _on_xview_changed(self, first: str, last: str) -> None:
        """Horizontal overflow callback (unused with word wrap)."""
        return

    def _set_v_scrollbar_visible(self, visible: bool) -> None:
        if visible == self._v_scrollbar_visible:
            return
        self._v_scrollbar_visible = visible
        if visible:
            self.v_scrollbar.grid(row=0, column=2, sticky="ns")
        else:
            self.v_scrollbar.grid_remove()

    def _set_h_scrollbar_visible(self, visible: bool) -> None:
        """No horizontal scrollbar when word wrap is enabled."""
        self._h_scrollbar_visible = False

    def _refresh_scrollbar_visibility(self) -> None:
        """Re-evaluate vertical scrollbar need after content or size changes."""
        try:
            self.xml_text.update_idletasks()
            y0, y1 = self.xml_text.yview()
            self._on_yview_changed(str(y0), str(y1))
        except Exception:
            pass

    def _on_preview_configure(self, _event=None) -> None:
        # Re-wrap can change display-line count; refresh gutter + scrollbar.
        if getattr(self, "_updating_line_numbers", False):
            return
        self._update_line_numbers(preserve_scroll=True)

    def _update_line_numbers(self, preserve_scroll: bool = False):
        """Update line numbers; pad blank rows so wrapped display lines stay aligned."""
        if getattr(self, "_updating_line_numbers", False):
            return
        self._updating_line_numbers = True
        try:
            y0, _y1 = self.xml_text.yview() if preserve_scroll else (0.0, 1.0)
            line_count = int(self.xml_text.index('end-1c').split('.')[0])

            self.line_numbers.config(state=tk.NORMAL)
            self.line_numbers.delete(1.0, tk.END)

            parts = []
            for i in range(1, line_count + 1):
                if i < line_count:
                    result = self.xml_text.count(f"{i}.0", f"{i + 1}.0", "displaylines")
                else:
                    result = self.xml_text.count(f"{i}.0", "end", "displaylines")
                display_lines = 1
                if result is not None:
                    display_lines = result[0] if isinstance(result, tuple) else int(result)
                if display_lines < 1:
                    display_lines = 1
                parts.append(str(i))
                for _ in range(display_lines - 1):
                    parts.append("")

            self.line_numbers.insert(tk.END, "\n".join(parts) + ("\n" if parts else ""))
            self.line_numbers.config(state=tk.DISABLED)

            if preserve_scroll:
                self.xml_text.yview_moveto(y0)
                self.line_numbers.yview_moveto(y0)
            else:
                self.xml_text.yview_moveto(0)
                self.line_numbers.yview_moveto(0)
            self._refresh_scrollbar_visibility()
        except Exception:
            pass
        finally:
            self._updating_line_numbers = False

    def _on_mousewheel(self, event) -> None:
        """Scroll XML preview with the mouse wheel (and keep line numbers synced)."""
        try:
            if getattr(event, "num", None) == 4:  # Linux scroll up
                delta = -1
            elif getattr(event, "num", None) == 5:  # Linux scroll down
                delta = 1
            else:
                delta = -1 if event.delta > 0 else 1
            self.xml_text.yview_scroll(delta, "units")
            self.line_numbers.yview_scroll(delta, "units")
            self._refresh_scrollbar_visibility()
        except Exception:
            pass
        return "break"

    def create_input_field(
        self, parent, label_text, variable, tooltip_text,
        *, entry_width=None, expand=True, fill_row=True, pady=3,
    ):
        """Create a labeled input field with tooltip (standard Tkinter)."""
        frame = tk.Frame(parent, bg=self.colors['bg'])
        if fill_row:
            frame.pack(fill=tk.X, pady=pady)
        else:
            frame.pack(side=tk.LEFT, pady=pady)

        label = tk.Label(
            frame, text=label_text,
            bg=self.colors['bg'], fg=self.colors['fg'],
        )
        label.pack(side=tk.LEFT)

        entry = tk.Entry(
            frame, textvariable=variable,
            bg=self.colors['input_bg'], fg=self.colors['fg'],
            relief=tk.SOLID, borderwidth=1,
            width=entry_width if entry_width is not None else 20,
        )
        if expand and entry_width is None:
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        else:
            entry.pack(side=tk.LEFT, padx=5)

        Tooltip(entry, tooltip_text)
        return frame

    def create_custom_input_field(
        self, parent, label_text, variable, tooltip_text,
        *, entry_width=None, expand=True, pady=3,
    ):
        """Create a labeled input field with tooltip (CustomTkinter)."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill=tk.X, pady=pady)

        label = ctk.CTkLabel(frame, text=label_text)
        label.pack(side=tk.LEFT, padx=(0, 6))

        entry_kwargs = {"textvariable": variable}
        if entry_width is not None:
            entry_kwargs["width"] = entry_width
        entry = ctk.CTkEntry(frame, **entry_kwargs)
        if expand and entry_width is None:
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            entry.pack(side=tk.LEFT)

        Tooltip(entry, tooltip_text)
        return frame

    def _ctk_field_cell(self, parent, label_text, variable, tooltip_text, *, entry_width=90):
        """Build an unplaced labeled entry cell for grid layouts."""
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        label = ctk.CTkLabel(cell, text=label_text)
        label.pack(side=tk.LEFT, padx=(0, 6))
        entry = ctk.CTkEntry(cell, textvariable=variable, width=entry_width)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        Tooltip(entry, tooltip_text)
        return cell

    def _ctk_field_row(self, parent, left_spec, right_spec=None):
        """Pack a one- or two-column compact field row (CustomTkinter)."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill=tk.X, pady=3)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1 if right_spec else 0)

        left_label, left_var, left_tip, left_width = left_spec
        left_cell = self._ctk_field_cell(
            row, left_label, left_var, left_tip, entry_width=left_width,
        )
        left_cell.grid(row=0, column=0, sticky="ew", padx=(0, 8 if right_spec else 0))

        if right_spec is not None:
            right_label, right_var, right_tip, right_width = right_spec
            right_cell = self._ctk_field_cell(
                row, right_label, right_var, right_tip, entry_width=right_width,
            )
            right_cell.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _tk_field_row(self, parent, left_spec, right_spec=None):
        """Pack a one- or two-column compact field row (standard Tkinter)."""
        row = tk.Frame(parent, bg=self.colors['bg'])
        row.pack(fill=tk.X, pady=3)

        left_label, left_var, left_tip, left_width = left_spec
        self.create_input_field(
            row, left_label, left_var, left_tip,
            entry_width=left_width, expand=False, fill_row=False,
        )
        if right_spec is not None:
            right_label, right_var, right_tip, right_width = right_spec
            spacer = tk.Frame(row, bg=self.colors['bg'], width=16)
            spacer.pack(side=tk.LEFT)
            self.create_input_field(
                row, right_label, right_var, right_tip,
                entry_width=right_width, expand=False, fill_row=False,
            )

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

        # Themed preview scrollbars (Tk fallback path)
        style.configure(
            "Preview.Vertical.TScrollbar",
            background=self.colors['button_bg'],
            troughcolor=self.colors['input_bg'],
            bordercolor=self.colors['border'],
            arrowcolor=self.colors['fg'],
            relief="flat",
        )
        style.map(
            "Preview.Vertical.TScrollbar",
            background=[("active", self.colors['button_hover'])],
        )
        style.configure(
            "Preview.Horizontal.TScrollbar",
            background=self.colors['button_bg'],
            troughcolor=self.colors['input_bg'],
            bordercolor=self.colors['border'],
            arrowcolor=self.colors['fg'],
            relief="flat",
        )
        style.map(
            "Preview.Horizontal.TScrollbar",
            background=[("active", self.colors['button_hover'])],
        )
    
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
            show_error("Validation Error", f"Invalid input data: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to generate engine XML: {str(e)}")
    
    def generate_transmission_xml(self):
        """Generate and display transmission XML."""
        try:
            transmission_data = self.get_transmission_data()
            xml = XMLGenerator.generate_transmission_xml(transmission_data)
            self.highlight_xml_syntax(xml)
        except ValueError as e:
            show_error("Validation Error", f"Invalid input data: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to generate transmission XML: {str(e)}")
    
    def generate_both_xml(self):
        """Generate and display both engine and transmission XML in FS25 format."""
        try:
            engine_data = self.get_engine_data()
            transmission_data = self.get_transmission_data()
            
            # Generate combined XML in FS25 format
            combined_xml = XMLGenerator.generate_combined_fs25_xml(engine_data, transmission_data)
            
            self.highlight_xml_syntax(combined_xml)
        except ValueError as e:
            show_error("Validation Error", f"Invalid input data: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to generate combined XML: {str(e)}")

    def copy_generated_xml(self):
        """Copy combined FS25 XML to the clipboard (same output as Generate XML)."""
        try:
            engine_data = self.get_engine_data()
            transmission_data = self.get_transmission_data()
            xml = XMLGenerator.generate_combined_fs25_xml(engine_data, transmission_data)
            self.highlight_xml_syntax(xml)
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(xml)
                show_info("Success", "FS25 XML copied to clipboard")
            except tk.TclError as e:
                show_error("Error", f"Failed to access clipboard: {str(e)}")
        except ValueError as e:
            show_error("Validation Error", f"Invalid input data: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to copy XML: {str(e)}")
    
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
            
            show_info("Success", 
                              f"Files saved:\n{combined_filename}\n{engine_filename}\n{transmission_filename}")
            
        except Exception as e:
            show_error("Error", f"Failed to save XML files: {str(e)}")
    
    def copy_engine_xml(self):
        """Copy engine XML to clipboard."""
        try:
            engine_data = self.get_engine_data()
            xml = XMLGenerator.generate_engine_xml(engine_data)
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(xml)
                show_info("Success", "Engine XML copied to clipboard")
            except tk.TclError as e:
                show_error("Clipboard Error", f"Failed to access clipboard: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to copy engine XML: {str(e)}")
    
    def copy_transmission_xml(self):
        """Copy transmission XML to clipboard."""
        try:
            transmission_data = self.get_transmission_data()
            xml = XMLGenerator.generate_transmission_xml(transmission_data)
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(xml)
                show_info("Success", "Transmission XML copied to clipboard")
            except tk.TclError as e:
                show_error("Clipboard Error", f"Failed to access clipboard: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to copy transmission XML: {str(e)}")
    
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
                    show_error("Error", "Invalid filename provided")
                    return
                
                # Get and validate data before saving
                try:
                    engine_data = self.get_engine_data()
                except ValueError as e:
                    show_error("Validation Error", f"Invalid engine data: {str(e)}")
                    return
                except Exception as e:
                    show_error("Data Error", f"Failed to retrieve engine data: {str(e)}")
                    return
                
                # Generate XML
                try:
                    xml = XMLGenerator.generate_engine_xml(engine_data)
                except Exception as e:
                    show_error("XML Generation Error", f"Failed to generate XML: {str(e)}")
                    return
                
                # Save file with specific error handling
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(xml)
                    show_info("Success", f"Engine XML saved to {filename}")
                except PermissionError:
                    show_error("Permission Error", f"Cannot save to {filename}. Check file permissions.")
                except OSError as e:
                    show_error("File System Error", f"Failed to save file: {str(e)}")
                except Exception as e:
                    show_error("Save Error", f"Unexpected error while saving: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to save engine XML: {str(e)}")
    
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
                    show_error("Error", "Invalid filename provided")
                    return
                
                # Get and validate data before saving
                try:
                    transmission_data = self.get_transmission_data()
                except ValueError as e:
                    show_error("Validation Error", f"Invalid transmission data: {str(e)}")
                    return
                except Exception as e:
                    show_error("Data Error", f"Failed to retrieve transmission data: {str(e)}")
                    return
                
                # Generate XML
                try:
                    xml = XMLGenerator.generate_transmission_xml(transmission_data)
                except Exception as e:
                    show_error("XML Generation Error", f"Failed to generate XML: {str(e)}")
                    return
                
                # Save file with specific error handling
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(xml)
                    show_info("Success", f"Transmission XML saved to {filename}")
                except PermissionError:
                    show_error("Permission Error", f"Cannot save to {filename}. Check file permissions.")
                except OSError as e:
                    show_error("File System Error", f"Failed to save file: {str(e)}")
                except Exception as e:
                    show_error("Save Error", f"Unexpected error while saving: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to save transmission XML: {str(e)}")
    
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
                    show_error("Error", "Invalid filename provided")
                    return
                
                # Get and validate data before saving
                try:
                    engine_data = self.get_engine_data()
                    transmission_data = self.get_transmission_data()
                except ValueError as e:
                    show_error("Validation Error", f"Invalid configuration data: {str(e)}")
                    return
                except Exception as e:
                    show_error("Data Error", f"Failed to retrieve configuration data: {str(e)}")
                    return
                
                preset_data = {
                    'engine': engine_data,
                    'transmission': transmission_data
                }
                
                # Save with specific error handling
                try:
                    PresetManager.save_preset(preset_data, filename)
                    show_info("Success", f"Preset saved to {filename}")
                except PermissionError:
                    show_error("Permission Error", f"Cannot save to {filename}. Check file permissions.")
                except OSError as e:
                    show_error("File System Error", f"Failed to save file: {str(e)}")
                except Exception as e:
                    show_error("Save Error", f"Unexpected error while saving: {str(e)}")
        except Exception as e:
            show_error("Error", f"Failed to save preset: {str(e)}")
    
    def load_current_preset(self):
        """Load configuration from a preset file."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Configuration Preset"
            )
            if filename:
                try:
                    preset_data = PresetManager.load_preset(filename)
                except Exception as e:
                    show_error("Error", f"Failed to load preset: {str(e)}")
                    return
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
                            show_error("Error", f"Invalid engine data in preset: {str(e)}")
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
                            show_error("Error", f"Invalid transmission data in preset: {str(e)}")
                            return
                    
                    show_info("Success", "Preset loaded successfully!")
        except Exception as e:
            show_error("Error", f"Failed to load preset: {str(e)}")
    
    def open_settings(self):
        """Open Settings (preset folder, defaults, log path)."""
        show_settings(self.root, on_saved=self.on_settings_saved)

    def on_settings_saved(self):
        """Reload custom presets and refresh UI after Settings save."""
        try:
            PresetManager.reload_custom_presets()
            self.refresh_preset_dropdowns()
            self.apply_startup_default_presets()
            logger.info("Applied settings changes")
        except Exception as e:
            logger.exception("Failed after settings save: %s", e)
            show_error("Settings", f"Settings saved, but refresh failed:\n{e}")

    def apply_startup_default_presets(self):
        """Load configured default engine/transmission presets into the form."""
        try:
            engine_name = app_settings.get_default_engine_preset()
            trans_name = app_settings.get_default_transmission_preset()
            if engine_name:
                self.load_engine_preset(engine_name)
                self._set_dropdown_value(self.engine_preset_dropdown, engine_name)
                logger.info("Applied default engine preset: %s", engine_name)
            if trans_name:
                self.load_transmission_preset(trans_name)
                self._set_dropdown_value(self.transmission_preset_dropdown, trans_name)
                logger.info("Applied default transmission preset: %s", trans_name)
        except Exception as e:
            logger.exception("Failed to apply default presets: %s", e)

    def _set_dropdown_value(self, dropdown, value: str) -> None:
        if not dropdown or not value:
            return
        try:
            if CUSTOM_TKINTER_AVAILABLE:
                dropdown.set(value)
            else:
                dropdown.set(value)
        except Exception:
            pass

    def _ask_custom_preset_name(self, kind: str) -> Optional[str]:
        """Ask for a custom preset name and validate it. Returns None if cancelled/invalid."""
        import re

        preset_name = ask_string(
            f"Save {kind} Preset",
            f"Enter a name for this custom {kind.lower()} preset:",
            parent=self.root,
        )
        if preset_name is None:
            return None

        preset_name = preset_name.strip()
        if not preset_name:
            show_error("Error", "Preset name cannot be empty")
            return None

        invalid_chars = re.findall(r'[<>:"/\\|?*]', preset_name)
        if invalid_chars:
            show_error(
                "Error",
                f"Preset name contains invalid characters: {', '.join(set(invalid_chars))}",
            )
            return None

        if len(preset_name) > 50:
            show_error("Error", "Preset name must be 50 characters or less")
            return None

        return preset_name

    def save_custom_engine_preset(self):
        """Save current engine settings into Custom Presets / Engine presets."""
        try:
            try:
                engine_data = self.get_engine_data()
            except ValueError as e:
                show_error("Validation Error", f"Invalid engine data: {str(e)}")
                return
            except Exception as e:
                show_error("Data Error", f"Failed to retrieve engine data: {str(e)}")
                return

            preset_name = self._ask_custom_preset_name("Engine")
            if not preset_name:
                return

            if PresetManager.is_builtin_engine(preset_name):
                show_error(
                    "Error",
                    f"'{preset_name}' is a built-in engine preset. Choose a different name.",
                )
                return

            if preset_name in PresetManager.get_engine_presets():
                if not ask_yes_no(
                    "Duplicate Preset",
                    f"Custom engine preset '{preset_name}' already exists. Overwrite?",
                ):
                    return

            PresetManager.add_engine_preset(preset_name, engine_data, persist=True)
            self.refresh_preset_dropdowns()
            self._set_dropdown_value(self.engine_preset_dropdown, preset_name)
            show_info(
                "Success",
                f"Engine preset '{preset_name}' saved to Custom Presets / Engine presets.",
            )
            logger.info("Saved custom engine preset: %s", preset_name)
        except Exception as e:
            logger.exception("Failed to save engine preset: %s", e)
            show_error("Error", f"Failed to save engine preset: {str(e)}")

    def save_custom_transmission_preset(self):
        """Save current transmission settings into Custom Presets / Transmission presets."""
        try:
            try:
                transmission_data = self.get_transmission_data()
            except ValueError as e:
                show_error(
                    "Validation Error", f"Invalid transmission data: {str(e)}"
                )
                return
            except Exception as e:
                show_error(
                    "Data Error", f"Failed to retrieve transmission data: {str(e)}"
                )
                return

            preset_name = self._ask_custom_preset_name("Transmission")
            if not preset_name:
                return

            if PresetManager.is_builtin_transmission(preset_name):
                show_error(
                    "Error",
                    f"'{preset_name}' is a built-in transmission preset. Choose a different name.",
                )
                return

            if preset_name in PresetManager.get_transmission_presets():
                if not ask_yes_no(
                    "Duplicate Preset",
                    f"Custom transmission preset '{preset_name}' already exists. Overwrite?",
                ):
                    return

            PresetManager.add_transmission_preset(
                preset_name, transmission_data, persist=True
            )
            self.refresh_preset_dropdowns()
            self._set_dropdown_value(self.transmission_preset_dropdown, preset_name)
            show_info(
                "Success",
                f"Transmission preset '{preset_name}' saved to Custom Presets / Transmission presets.",
            )
            logger.info("Saved custom transmission preset: %s", preset_name)
        except Exception as e:
            logger.exception("Failed to save transmission preset: %s", e)
            show_error("Error", f"Failed to save transmission preset: {str(e)}")

    def refresh_preset_dropdowns(self):
        """Refresh the preset dropdown lists."""
        try:
            engine_presets = PresetManager.get_engine_presets()
            transmission_presets = PresetManager.get_transmission_presets()

            if self.engine_preset_dropdown:
                values = list(engine_presets.keys())
                if CUSTOM_TKINTER_AVAILABLE:
                    self.engine_preset_dropdown.configure(values=values)
                else:
                    self.engine_preset_dropdown['values'] = values

            if self.transmission_preset_dropdown:
                values = list(transmission_presets.keys())
                if CUSTOM_TKINTER_AVAILABLE:
                    self.transmission_preset_dropdown.configure(values=values)
                else:
                    self.transmission_preset_dropdown['values'] = values

        except Exception as e:
            logger.exception("Error refreshing preset dropdowns: %s", e)
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

