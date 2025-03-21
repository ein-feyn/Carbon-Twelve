"""
Configuration module for the Digital Notebook.

This module provides functionality for saving and loading user preferences.
"""
import json
import os
from pathlib import Path


class Config:
    """
    Manages application configuration and preferences.
    
    This class provides methods for saving and loading user preferences,
    such as the default storage location for notebooks.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file. If None, a default
                         location in the user's home directory is used.
        """
        if config_file is None:
            # Use a default location in the user's home directory
            self.config_file = os.path.join(str(Path.home()), '.digital_notebook', 'config.json')
        else:
            self.config_file = config_file
        
        # Make sure the directory exists
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Load the configuration
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load the configuration from the file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If there's an error reading the file, return an empty dict
                return {}
        return {}
    
    def save_config(self) -> None:
        """Save the configuration to the file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving configuration: {str(e)}")
    
    def get(self, key: str, default=None):
        """
        Get a configuration value.
        
        Args:
            key: The key to retrieve
            default: The default value to return if the key doesn't exist
            
        Returns:
            The configuration value or the default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value) -> None:
        """
        Set a configuration value and save the configuration.
        
        Args:
            key: The key to set
            value: The value to store
        """
        self.config[key] = value
        self.save_config()
    
    def get_default_storage_dir(self) -> str:
        """
        Get the default storage directory for notebooks.
        
        Returns:
            The configured storage directory or the default
        """
        default_dir = os.path.join(str(Path.home()), '.digital_notebook')
        return self.get('storage_dir', default_dir)
    
    def set_default_storage_dir(self, directory: str) -> None:
        """
        Set the default storage directory for notebooks.
        
        Args:
            directory: The directory to use for storing notebooks
        """
        self.set('storage_dir', directory) 