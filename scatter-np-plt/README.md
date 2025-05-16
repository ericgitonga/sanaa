# Scatter Plot Visualization Script

A Python script that generates random scatter plots from CSV data containing hexadecimal values. The script creates visually diverse scatter plots with random styling, colors, shapes, and sizes.

## Features

- Interactive file selection via GUI dialog
- CSV parsing with hex value extraction
- Random scatter plot generation with:
  - Multiple marker types
  - Random colors and transparency
  - Variable point sizes based on data values
  - Multiple matplotlib styling options
- SVG output format
- Command-line interface support

## Requirements

```bash
pip install pandas numpy matplotlib tkinter
```

## Usage

### Basic Usage (Interactive)
```bash
python sc_np_plt.py
```
This will open file dialogs for input CSV selection and output SVG saving.

### Command Line Options
```bash
python sc_np_plt.py -f input.csv -s 1000 -o output.svg --no-show
```

Options:
- `-f, --file`: Input CSV file path (optional, prompts if not provided)
- `-s, --samples`: Number of samples to plot (default: 750)
- `-o, --output`: Output SVG file path (optional, prompts if not provided)
- `--no-show`: Don't display the plot window

## Input File Format

The script expects a CSV file with at least two columns:
- Column 1: Any data (not used)
- Column 2: String containing hex values in format "text 0xHEXVALUE"

Example:
```
id1,data 0x1A2B3C
id2,info 0x4D5E6F
```

## Output

The script generates:
- An SVG file containing the scatter plot
- Console output showing progress and file paths

## Example

```bash
# Run with defaults
python sc_np_plt.py

# Specify all parameters
python sc_np_plt.py -f data.csv -s 500 -o plot.svg

# Batch processing without display
python sc_np_plt.py -f data.csv -o plot.svg --no-show
```

## Notes

- The script randomly samples data points for better performance with large datasets
- Plot styling is randomly selected from available matplotlib styles
- Point sizes are calculated based on hex values with random scaling
- GUI dialogs require a display environment (use command-line args for headless systems)
