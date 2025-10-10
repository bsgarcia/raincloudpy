"""
Core raincloud plot implementation.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from typing import Optional, Union, Tuple, Dict, Any
import pandas as pd


def raincloudplot(
    data: Optional[pd.DataFrame] = None,
    x: Optional[str] = None,
    y: Optional[str] = None,
    order: Optional[list] = None,
    palette: Optional[Union[str, list]] = None,
    ax: Optional[plt.Axes] = None,
    box_width: float = 0.15,
    violin_width: float = 0.3,
    dot_size: float = 7,
    dot_spacing: float = 0.03,
    y_threshold: Optional[float] = None,
    n_bins: int = 40,
    box_kwargs: Optional[Dict[str, Any]] = None,
    violin_kwargs: Optional[Dict[str, Any]] = None,
    scatter_kwargs: Optional[Dict[str, Any]] = None,
    show_box: bool = True,
    show_violin: bool = True,
    show_scatter: bool = True,
    orient: str = 'v'
) -> plt.Axes:
    """
    Create a raincloud plot combining boxplot, half-violin, and density-aligned scatter.
    
    Parameters
    ----------
    data : DataFrame, optional
        Input data structure. If specified, x and y should be column names.
    x : str, optional
        Column name for categorical variable (groups).
    y : str, optional
        Column name for continuous variable (values).
    order : list, optional
        Order to plot the categorical levels in.
    palette : str or list, optional
        Colors to use for different levels of the hue variable.
    ax : matplotlib Axes, optional
        Axes object to draw the plot onto, otherwise uses current Axes.
    box_width : float, default=0.15
        Width of the boxplot boxes.
    violin_width : float, default=0.3
        Maximum width of the violin (KDE) plot.
    dot_size : float, default=7
        Size of scatter points.
    dot_spacing : float, default=0.03
        Horizontal spacing between scattered dots.
    y_threshold : float, optional
        Threshold for grouping y-values together. If None, computed as 5% of data range.
    n_bins : int, default=40
        Number of bins for density estimation.
    box_kwargs : dict, optional
        Additional keyword arguments for boxplot.
    violin_kwargs : dict, optional
        Additional keyword arguments for violin plot.
    scatter_kwargs : dict, optional
        Additional keyword arguments for scatter plot.
    show_box : bool, default=True
        Whether to show the boxplot component.
    show_violin : bool, default=True
        Whether to show the violin (KDE) component.
    show_scatter : bool, default=True
        Whether to show the scatter component.
    orient : str, default='v'
        Orientation of the plot ('v' for vertical, 'h' for horizontal).
        
    Returns
    -------
    ax : matplotlib Axes
        The Axes object with the plot.
        
    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> from raincloudpy import raincloudplot
    >>> df = pd.DataFrame({'group': ['A']*50 + ['B']*50, 
    ...                    'value': np.random.randn(100)})
    >>> raincloudplot(data=df, x='group', y='value', palette='Set2')
    
    >>> # Customized plot
    >>> raincloudplot(
    ...     data=df, 
    ...     x='group', 
    ...     y='value',
    ...     box_width=0.2,
    ...     violin_width=0.35,
    ...     dot_size=10,
    ...     dot_spacing=0.03,
    ...     box_kwargs={'linewidth': 3},
    ...     scatter_kwargs={'alpha': 0.9}
    ... )
    """
    import seaborn as sns
    
    # Get current axes if not provided
    if ax is None:
        ax = plt.gca()
    
    # Parse data
    if data is not None:
        if x is None or y is None:
            raise ValueError("Must specify both x and y when data is provided")
        groups = data[x].unique()
        if order is not None:
            groups = [g for g in order if g in groups]
    else:
        raise ValueError("data parameter is required")
    
    # Set default kwargs
    box_kwargs = box_kwargs or {}
    violin_kwargs = violin_kwargs or {}
    scatter_kwargs = scatter_kwargs or {}
    
    # Get colors
    if palette is None:
        palette = sns.color_palette()
    elif isinstance(palette, str):
        palette = sns.color_palette(palette, n_colors=len(groups))
    
    # Set defaults for box, violin, and scatter
    box_defaults = {
        # 'linecolor': 'black',
        'fliersize': 0,
        'width': box_width,
        'linewidth': 2,
        'capprops': dict(visible=False),
        'zorder': 1
    }
    violin_defaults = {'alpha': 0.2, 'zorder': 0}
    scatter_defaults = {
        's': dot_size,
        'edgecolor': 'black',
        'linewidth': 1,
        'alpha': 0.7,
        'zorder': 3
    }
    
    box_defaults.update(box_kwargs)
    violin_defaults.update(violin_kwargs)
    scatter_defaults.update(scatter_kwargs)
    
    # Create boxplot
    if show_box:
        sns.boxplot(
            data=data,
            x=x,
            y=y,
            order=groups,
            palette=palette,
            ax=ax,
            **box_defaults
        )
    
    # Add violin and scatter for each group
    for i, (group_val, color) in enumerate(zip(groups, palette)):
        y_vals = data[data[x] == group_val][y].values
        
        if show_violin:
            _add_half_violin(
                ax, i, y_vals, color, violin_width, **violin_defaults
            )
        
        if show_scatter:
            _add_density_scatter(
                ax, i, y_vals, color, box_width, 
                dot_spacing, y_threshold, n_bins, **scatter_defaults
            )
    
    return ax


def _add_half_violin(ax, position, y_vals, color, violin_width, **kwargs):
    """Add a left-side half violin plot."""
    kde = gaussian_kde(y_vals, bw_method='scott')
    y_density = np.linspace(y_vals.min(), y_vals.max(), 100)
    density = kde(y_density)
    
    # Normalize density to violin_width
    density_normalized = density / density.max() * violin_width
    
    # Plot left half violin only (negative x direction from center)
    ax.fill_betweenx(
        y_density,
        position - density_normalized,
        position,
        color=color,
        **kwargs
    )


def _add_density_scatter(
    ax, position, y_vals, color, box_width,
    dot_spacing, y_threshold, n_bins, **kwargs
):
    """Add density-aligned scatter points."""
    x_coords, y_coords = _compute_scatter_coords(
        position + box_width/2 + 0.05,
        y_vals,
        dot_spacing,
        y_threshold,
        n_bins
    )
    
    ax.scatter(x_coords, y_coords, color=color, **kwargs)


def _compute_scatter_coords(
    x_pos: float,
    y_values: np.ndarray,
    dot_spacing: float = 0.03,
    y_threshold: Optional[float] = None,
    n_bins: int = 40
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute coordinates for density-aligned scatter points.
    
    Points with similar y-values are aligned horizontally, with density
    determining how many points are shown at each level.
    """
    y_values = np.array(y_values)
    
    # Compute threshold if not provided
    if y_threshold is None:
        y_range_data = y_values.max() - y_values.min()
        y_threshold = y_range_data * 0.05
    
    # Sort and group similar y-values
    sorted_indices = np.argsort(y_values)
    sorted_y = y_values[sorted_indices]
    
    y_groups = []
    current_group = [sorted_y[0]]
    
    for i in range(1, len(sorted_y)):
        # Compare to the first value in the current group to ensure total range doesn't exceed threshold
        if (sorted_y[i] - current_group[0]) <= y_threshold:
            current_group.append(sorted_y[i])
        else:
            y_groups.append(current_group)
            current_group = [sorted_y[i]]
    y_groups.append(current_group)
    
    # Estimate density
    kde = gaussian_kde(y_values, bw_method='scott')
    y_range = np.linspace(y_values.min(), y_values.max(), n_bins)
    max_density = kde(y_range).max()
    
    x_coords = []
    y_coords = []
    
    for group in y_groups:
        group_y = np.mean(group)
        n_points = len(group)
        
        density = kde(group_y)[0]
        n_dots_to_show = int(np.ceil(n_points * density / max_density))
        n_dots_to_show = min(n_dots_to_show, n_points)
        
        x_offsets = [i * dot_spacing for i in range(n_dots_to_show)]
        
        x_coords.extend([x_pos + offset for offset in x_offsets])
        y_coords.extend([group_y] * n_dots_to_show)
    
    return np.array(x_coords), np.array(y_coords)
