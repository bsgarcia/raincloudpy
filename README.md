# raincloudpy 🌧️☁️

[![PyPI version](https://badge.fury.io/py/raincloudpy.svg)](https://badge.fury.io/py/raincloudpy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Beautiful **raincloud plots** for Python, combining boxplots, half-violin plots, and density-aligned scatter plots to create comprehensive and visually appealing data visualizations.

## What is a Raincloud Plot?

Raincloud plots are a hybrid visualization that combines:
- 📊 **Box plots** - showing quartiles and outliers
- 🎻 **Half-violin plots** - displaying the probability density
- 🔴 **Scatter plots** - showing individual data points aligned by density

This creates a "rain cloud" effect that provides maximum information about your data distribution.

## Example
![raincloud plot](https://raw.githubusercontent.com/bsgarcia/raincloudpy/refs/heads/master/examples/example.png)

## Installation

```bash
pip install raincloudpy
```

## Quick Start

### basic 
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from raincloudpy import raincloudplot
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# Create sample data
df = pd.DataFrame({
    'group': ['A'] * 50 + ['B'] * 50 + ['C'] * 50,
    'value': np.concatenate([
        np.random.randn(50) + 2,
        np.random.randn(50) + 3,
        np.random.randn(50) + 2.5
    ])
})

# Create raincloud plot
# fig, ax = plt.subplots(figsize=(10, 6))
plt.figure(figsize=(10, 6))
sns.set_context('talk')
raincloudplot(data=df, x='group', y='value', palette='Set2')
plt.title('basic raincloud plot example')
plt.ylabel('value')
plt.xlabel('group')
plt.tight_layout()
plt.show()
```

### advanced
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# Create sample data mimicking value comparison
N = 150
df_fit = pd.DataFrame({
    'group': ['group 1'] * N + ['group 2'] * N + ['group 3'] * N,
    'value': np.concatenate([
        np.random.normal(loc=300, scale=20, size=N),
        np.random.normal(loc=250, scale=20, size=N),
        np.random.normal(loc=200, scale=20, size=N)
    ])
})

sns.set_style("ticks")
sns.set_context("notebook")

# Create customized raincloud plot
plt.figure(figsize=(6, 5), dpi=300)
raincloudplot(
    data=df_fit, 
    x='group', 
    y='value',
    order=['group 1', 'group 2', 'group 3'],
    palette=['#3498db', '#e74c3c', '#2ecc71'],
    box_width=0.14,
    violin_width=0.4,
    dot_size=10,
    dot_spacing=0.04,
    y_threshold=3,
    box_kwargs={'linewidth': 3},
    scatter_kwargs={'alpha': 0.9, 'edgecolor': 'black', 'linewidth': 0.5},
    violin_kwargs={'alpha': 0.25},
)


plt.title('group comparison using raincloudpy', fontweight='bold')
plt.ylabel('value')
plt.xlabel('')
plt.tight_layout()
sns.despine(offset=10, trim=True, bottom=True)
plt.tick_params(axis='x', which='both', bottom=False, top=False)
plt.show()
```
### Hiding Components

```python
# Only show violin and scatter
raincloudplot(
    data=df, 
    x='group', 
    y='value',
    show_box=False,
    show_violin=True,
    show_scatter=True
)
```

### Per-point scatter colours

`scatter_colors` colours each dot individually instead of one colour per group.
Pass a column name or an array with one entry per data row:

```python
# Colour each dot by a numeric column through a colormap
raincloudplot(
    data=df, x='group', y='value',
    scatter_colors='omega',     # numeric -> mapped through 'viridis'
    scatter_cmap='magma',       # optional, default 'viridis'
)

# Or a list of literal colours, one per row
raincloudplot(
    data=df, x='group', y='value',
    scatter_colors=['#ff0000' if g == 'A' else '#1f77b4' for g in df['group']],
)

# Or categorical values with an explicit palette
raincloudplot(
    data=df, x='group', y='value',
    scatter_colors='condition',
    scatter_palette={'control': '#888888', 'treatment': '#d62728'},
)
```

Dense rows are thinned by the density estimate; `scatter_colors` stays aligned
with the dots actually drawn, so each dot carries the colour of its source row.

## Features

- 🎨 **Customizable colors** - Use any seaborn color palette or custom colors
- 🌈 **Per-point scatter colors** - Colour each dot by a value, a colormap, or explicit colours
- 📏 **Flexible sizing** - Control box width, violin width, and dot sizes
- 🎯 **Density-aligned scatter** - Points are intelligently positioned based on data density
- 🔧 **Component control** - Show/hide individual components (box, violin, scatter)
- 📊 **Works with pandas** - Seamless integration with pandas DataFrames
- 🎭 **Matplotlib-based** - Fully compatible with matplotlib customization


## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | DataFrame | None | Input data (required) |
| `x` | str | None | Column name for categorical variable |
| `y` | str | None | Column name for continuous variable |
| `order` | list | None | Order to plot categorical levels |
| `palette` | str/list | None | Colors for different groups |
| `ax` | Axes | None | Matplotlib axes object |
| `box_width` | float | 0.15 | Width of boxplot boxes |
| `violin_width` | float | 0.3 | Maximum width of violin plot |
| `dot_size` | float | 7 | Size of scatter points |
| `dot_spacing` | float | 0.03 | Horizontal spacing between dots |
| `box_dots_spacing` | float | 0.05 | Gap between boxplot and scatter points |
| `y_threshold` | float/str/None | "5%" | Threshold for grouping y-values: None=stripplot (3% jitter), "5%"=percentage, number=absolute |
| `n_bins` | int | 40 | Number of bins for density estimation |
| `box_kwargs` | dict | None | Additional boxplot arguments |
| `violin_kwargs` | dict | None | Additional violin plot arguments |
| `scatter_kwargs` | dict | None | Additional scatter plot arguments |
| `scatter_colors` | str/array | None | Per-point scatter colours: a column name or an array of values/colours |
| `scatter_cmap` | str/Colormap | None | Colormap for numeric `scatter_colors` (default 'viridis') |
| `scatter_norm` | Normalize | None | Normalization for numeric `scatter_colors` |
| `scatter_palette` | str/list/dict | None | Palette for categorical `scatter_colors` |
| `show_box` | bool | True | Whether to show boxplot |
| `show_violin` | bool | True | Whether to show violin plot |
| `show_scatter` | bool | True | Whether to show scatter plot |
| `orient` | str | 'v' | Plot orientation ('v' or 'h') |

## Requirements

- Python >= 3.7
- numpy >= 1.19.0
- matplotlib >= 3.3.0
- scipy >= 1.5.0
- pandas >= 1.1.0
- seaborn >= 0.11.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{raincloudpy2025,
  author = {Basile Garcia},
  title = {raincloudpy: Beautiful raincloud plots for Python},
  year = {2025},
  url = {https://github.com/bsgarcia/raincloudpy}
}
```

## Acknowledgments

Inspired by the original raincloud plots concept and various implementations in R and Python.

## References

- Allen, M., Poggiali, D., Whitaker, K., Marshall, T. R., & Kievit, R. A. (2019). Raincloud plots: a multi-platform tool for robust data visualization. Wellcome Open Research, 4.
