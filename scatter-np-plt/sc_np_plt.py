#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scatter Plot Visualization Script
Generates a random scatter plot from CSV data with hex values
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog as fd
import sys
import argparse


def select_file(title="Select CSV file"):
    """Open a file dialog to select a CSV file"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)  # Ensure dialog appears on top

    file_path = fd.askopenfilename(title=title, filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])

    root.destroy()

    if not file_path:
        print("No file selected. Exiting.")
        sys.exit(1)

    return file_path


def read_and_process_csv(file_path):
    """Read CSV file and process the data"""
    try:
        # Read CSV with specific columns
        # Handle different pandas versions
        try:
            df = pd.read_csv(file_path, on_bad_lines="skip", header=None, usecols=[0, 1])
        except TypeError:
            # Older pandas version
            df = pd.read_csv(file_path, error_bad_lines=False, header=None, usecols=[0, 1])

        # Extract hex values from second column
        df["value"] = df[1].apply(lambda x: x.split()[1]).apply(lambda x: int(x, 16))

        # Shuffle the dataframe
        df = df.sample(frac=1).reset_index(drop=True)

        return df
    except Exception as e:
        print(f"Error reading/processing CSV: {e}")
        sys.exit(1)


def rand_num():
    """Generate a random number between 0 and 1"""
    # Generate a random normal distribution value
    number = np.abs(np.random.normal(0, 1))
    if number > 1:
        number = number - np.floor(number)
    return number


def create_scatter_plot(df, sample_size=750, figure_size=(15, 10)):
    """Create a random scatter plot from the dataframe"""
    # Sample data
    dfs = df.sample(min(sample_size, len(df))).copy()
    len_df = len(dfs.index)

    # Add random x and y coordinates
    dfs["x"] = np.random.randn(len_df) * np.exp(np.pi**2)
    dfs["y"] = np.random.rand(len_df) ** np.log(np.pi)

    # Choose random style - use available styles
    available_styles = plt.style.available
    # Filter to commonly available styles
    preferred_styles = ["dark_background", "ggplot", "fivethirtyeight", "bmh", "grayscale"]
    valid_styles = [s for s in preferred_styles if s in available_styles]

    if valid_styles:
        style = np.random.choice(valid_styles)
        plt.style.use(style)
    else:
        # Fallback to default
        plt.style.use("default")

    # Create figure
    plt.figure(figsize=figure_size)
    plt.axis("off")

    # Plot each point with random characteristics
    markers = [
        ".",
        ",",
        "o",
        "v",
        "^",
        "<",
        ">",
        "1",
        "2",
        "3",
        "4",
        "8",
        "s",
        "p",
        "P",
        "*",
        "h",
        "H",
        "+",
        "x",
        "X",
        "d",
        "D",
        "|",
        "_",
    ]

    for i in dfs.index:
        marker = np.random.choice(markers)
        rgba = [np.random.random() for _ in range(4)]
        colour = np.array([rgba])
        alpha = rand_num()

        # Calculate size with bounds
        rand_divisor = np.random.randint(1, 501)
        denominator = np.abs(rand_divisor / np.random.normal(-1, 1))
        if denominator < 1:
            denominator = 1  # Prevent division by very small numbers

        size = min(dfs.loc[i, "value"] / denominator, 5000)  # Cap maximum size
        size = max(size, 1)  # Ensure minimum size

        plt.scatter(dfs.loc[i, "x"], dfs.loc[i, "y"], marker=marker, color=colour, s=size, alpha=alpha)

    return plt


def save_plot(plt_obj, default_filename="scatter_plot.svg"):
    """Save the plot as SVG file"""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = fd.asksaveasfilename(
        title="Save plot as SVG",
        initialfile=default_filename,
        defaultextension=".svg",
        filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
    )

    root.destroy()

    if file_path:
        plt_obj.savefig(file_path, format="svg", bbox_inches="tight")
        print(f"Plot saved to: {file_path}")
        return True
    else:
        print("Save cancelled.")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate scatter plot from CSV with hex values")
    parser.add_argument("-f", "--file", type=str, help="CSV file path (optional, will prompt if not provided)")
    parser.add_argument("-s", "--samples", type=int, default=750, help="Number of samples to plot (default: 750)")
    parser.add_argument("-o", "--output", type=str, help="Output SVG file path (optional, will prompt if not provided)")
    parser.add_argument("--no-show", action="store_true", help="Don't display the plot")

    args = parser.parse_args()

    # Get input file
    if args.file:
        file_path = args.file
    else:
        file_path = select_file()

    # Read and process data
    print(f"Reading file: {file_path}")
    df = read_and_process_csv(file_path)
    print(f"Loaded {len(df)} rows")

    # Create plot
    print("Creating scatter plot...")
    plt_obj = create_scatter_plot(df, sample_size=args.samples)

    # Save plot
    if args.output:
        plt_obj.savefig(args.output, format="svg", bbox_inches="tight")
        print(f"Plot saved to: {args.output}")
    else:
        save_plot(plt_obj)

    # Show plot
    if not args.no_show:
        plt.show()

    plt.close()


if __name__ == "__main__":
    main()
