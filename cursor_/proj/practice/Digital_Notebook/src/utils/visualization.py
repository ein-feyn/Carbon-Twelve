"""
Visualization module for the Digital Notebook.

This module provides visualization capabilities for text analysis and word count tracking.
"""
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.figure
import numpy as np
from io import BytesIO


class Visualizer:
    """
    Provides visualization tools for text analysis.
    
    This class creates plots and charts for text metrics and progress tracking.
    """
    
    def __init__(self):
        """Initialize the visualizer with default settings."""
        self.theme = "default"
        self.figure_size = (10, 6)
        self.dpi = 100
    
    def plot_word_count_progress(
        self, 
        x_values: List[int], 
        y_values: List[float], 
        title: str = "Word Count Progress",
        save_path: Optional[str] = None
    ) -> Optional[matplotlib.figure.Figure]:
        """
        Plot the word count progress.
        
        Args:
            x_values: X-axis values (typically word positions)
            y_values: Y-axis values (cumulative word count)
            title: Title for the plot
            save_path: Path to save the plot (if None, the plot is displayed)
            
        Returns:
            The matplotlib Figure object if not saved to file, otherwise None
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Plot the actual word count progress
        ax.plot(x_values, y_values, 'b-', linewidth=2, label="Word Count")
        
        # Plot the ideal slope = 1 line
        max_x = max(x_values) if x_values else 1
        ax.plot([0, max_x], [0, max_x], 'r--', linewidth=1, label="Ideal (slope = 1)")
        
        # Add labels and title
        ax.set_xlabel("Word Position")
        ax.set_ylabel("Cumulative Count")
        ax.set_title(title)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Ensure the axes start at 0
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        
        # Save or return the figure
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close(fig)
            return None
        else:
            plt.tight_layout()
            return fig
    
    def plot_character_distribution(
        self, 
        char_counts: Dict[str, int],
        title: str = "Character Distribution",
        save_path: Optional[str] = None
    ) -> Optional[matplotlib.figure.Figure]:
        """
        Plot the distribution of character types.
        
        Args:
            char_counts: Dictionary mapping character types to counts
            title: Title for the plot
            save_path: Path to save the plot (if None, the plot is displayed)
            
        Returns:
            The matplotlib Figure object if not saved to file, otherwise None
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Extract the data
        labels = list(char_counts.keys())
        values = list(char_counts.values())
        
        # Sort by value (descending)
        sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
        labels = [item[0] for item in sorted_data]
        values = [item[1] for item in sorted_data]
        
        # Plot bar chart
        ax.bar(labels, values, color='skyblue')
        
        # Add labels and title
        ax.set_xlabel("Character Type")
        ax.set_ylabel("Count")
        ax.set_title(title)
        
        # Format the axes
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Save or return the figure
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close(fig)
            return None
        else:
            plt.tight_layout()
            return fig
    
    def plot_readability_metrics(
        self, 
        readability: Dict[str, float],
        title: str = "Readability Metrics",
        save_path: Optional[str] = None
    ) -> Optional[matplotlib.figure.Figure]:
        """
        Plot readability metrics.
        
        Args:
            readability: Dictionary with readability metrics
            title: Title for the plot
            save_path: Path to save the plot (if None, the plot is displayed)
            
        Returns:
            The matplotlib Figure object if not saved to file, otherwise None
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Extract the data
        labels = list(readability.keys())
        values = list(readability.values())
        
        # Plot horizontal bar chart
        ax.barh(labels, values, color='lightgreen')
        
        # Add labels and title
        ax.set_xlabel("Value")
        ax.set_ylabel("Metric")
        ax.set_title(title)
        
        # Format the axes
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # Save or return the figure
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close(fig)
            return None
        else:
            plt.tight_layout()
            return fig
    
    def plot_writing_progress(
        self, 
        history: Dict[str, List[Any]],
        title: str = "Writing Progress Over Time",
        save_path: Optional[str] = None
    ) -> Optional[matplotlib.figure.Figure]:
        """
        Plot writing progress over time.
        
        Args:
            history: Dictionary with progress metrics
            title: Title for the plot
            save_path: Path to save the plot (if None, the plot is displayed)
            
        Returns:
            The matplotlib Figure object if not saved to file, otherwise None
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Extract the data
        cumulative = history.get("cumulative_counts", [])
        deltas = history.get("word_deltas", [])
        
        # Create x-axis values (assuming these are version numbers)
        x_values = list(range(1, len(cumulative) + 1))
        
        # Plot cumulative word count
        ax.plot(x_values, cumulative, 'b-', marker='o', linewidth=2, label="Total Words")
        
        # Plot word count changes as a bar chart
        ax2 = ax.twinx()
        ax2.bar(x_values, deltas, alpha=0.3, color='green', label="Words Added")
        
        # Add labels and title
        ax.set_xlabel("Version")
        ax.set_ylabel("Total Word Count", color='blue')
        ax2.set_ylabel("Words Added/Changed", color='green')
        ax.set_title(title)
        
        # Format the axes
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.tick_params(axis='y', labelcolor='blue')
        ax2.tick_params(axis='y', labelcolor='green')
        
        # Add legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Save or return the figure
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close(fig)
            return None
        else:
            plt.tight_layout()
            return fig
    
    def figure_to_bytes(self, fig: matplotlib.figure.Figure) -> bytes:
        """
        Convert a matplotlib figure to bytes.
        
        This is useful for displaying the figure in a GUI without saving to disk.
        
        Args:
            fig: The matplotlib Figure object
            
        Returns:
            Bytes representation of the figure
        """
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=self.dpi)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
    
    def plot_keyword_cloud(
        self, 
        keywords: Dict[str, int],
        title: str = "Keyword Cloud",
        save_path: Optional[str] = None
    ) -> Optional[matplotlib.figure.Figure]:
        """
        Plot a simple keyword representation (not a true word cloud).
        
        Args:
            keywords: Dictionary mapping keywords to frequency
            title: Title for the plot
            save_path: Path to save the plot (if None, the plot is displayed)
            
        Returns:
            The matplotlib Figure object if not saved to file, otherwise None
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Extract the data
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        words = [item[0] for item in sorted_keywords[:15]]  # Top 15 words
        frequencies = [item[1] for item in sorted_keywords[:15]]
        
        # Plot horizontal bar chart
        y_pos = np.arange(len(words))
        ax.barh(y_pos, frequencies, color='skyblue')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(words)
        
        # Add labels and title
        ax.set_xlabel("Frequency")
        ax.set_title(title)
        
        # Format the axes
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        ax.invert_yaxis()  # Display highest frequency at the top
        
        # Save or return the figure
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close(fig)
            return None
        else:
            plt.tight_layout()
            return fig
    
    def set_theme(self, theme: str) -> None:
        """
        Set the visualization theme.
        
        Args:
            theme: Name of the theme to use
        """
        self.theme = theme
        
        # Apply the theme to matplotlib
        if theme == "dark":
            plt.style.use('dark_background')
        elif theme == "light":
            plt.style.use('default')
        elif theme == "seaborn":
            try:
                plt.style.use('seaborn')
            except:
                plt.style.use('default')
        else:
            plt.style.use('default')
