"""
Core raincloud plot implementation.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Colormap, Normalize, to_rgba, to_rgba_array
from scipy.stats import gaussian_kde
from typing import Optional, Union, Tuple, Dict, Any, Sequence
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
    box_dots_spacing: float = 0.05,
    y_threshold: Optional[Union[float, str]] = "5%",
    n_bins: int = 40,
    box_kwargs: Optional[Dict[str, Any]] = None,
    violin_kwargs: Optional[Dict[str, Any]] = None,
    scatter_kwargs: Optional[Dict[str, Any]] = None,
    scatter_colors: Optional[Union[str, Sequence, np.ndarray]] = None,
    scatter_cmap: Optional[Union[str, Colormap]] = None,
    scatter_norm: Optional[Normalize] = None,
    scatter_palette: Optional[Union[str, list, dict]] = None,
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
    box_dots_spacing : float, default=0.05
        Gap between the boxplot and the scatter points.
    y_threshold : float, str, or None, default="5%"
        Threshold for grouping y-values together. 
        - None: stripplot with 3% jitter (random scatter)
        - str (e.g., "5%"): percentage of data range for grouping
        - float/int: absolute threshold value for grouping
    n_bins : int, default=40
        Number of bins for density estimation.
    box_kwargs : dict, optional
        Additional keyword arguments for boxplot.
    violin_kwargs : dict, optional
        Additional keyword arguments for violin plot.
    scatter_kwargs : dict, optional
        Additional keyword arguments for scatter plot.
    scatter_colors : str, array-like, optional
        Per-point colours for the scatter dots. Either a column name in `data`
        or an array-like with one entry per data row (matched positionally).
        Numeric values are mapped through `scatter_cmap`; non-numeric values that
        are valid matplotlib colours are used literally; anything else is treated
        as categorical and mapped through `scatter_palette`.
    scatter_cmap : str or Colormap, optional
        Colormap used when `scatter_colors` values are numeric. Default 'viridis'.
    scatter_norm : Normalize, optional
        Normalization for numeric `scatter_colors`. Defaults to the data range.
    scatter_palette : str, list, or dict, optional
        Palette used when `scatter_colors` values are categorical. A dict maps
        category -> colour; a list or seaborn palette name assigns colours in
        order of appearance. Defaults to seaborn's default palette.
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

    # Resolve per-point scatter colours once, aligned to the data rows.
    point_rgba = None
    if show_scatter and scatter_colors is not None:
        point_rgba = _resolve_scatter_colors(
            data, scatter_colors, scatter_cmap, scatter_norm, scatter_palette
        )
    
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
    n_groups = len(groups)
    for i, (group_val, color) in enumerate(zip(groups, palette)):
        mask = (data[x] == group_val).to_numpy()
        y_vals = data.loc[mask, y].to_numpy()
        
        if show_violin:
            _add_half_violin(
                ax, i, y_vals, color, violin_width, n_groups, **violin_defaults
            )
        
        if show_scatter:
            point_colors = None if point_rgba is None else point_rgba[mask]
            _add_density_scatter(
                ax, i, y_vals, color, box_width, 
                dot_spacing, box_dots_spacing, y_threshold, n_bins, n_groups,
                point_colors=point_colors, **scatter_defaults
            )
    
    return ax


def _add_half_violin(ax, position, y_vals, color, violin_width, n_groups, **kwargs):
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
    dot_spacing, box_dots_spacing, y_threshold, n_bins, n_groups,
    point_colors=None, **kwargs
):
    """Add density-aligned scatter points to the right of the box.

    If ``point_colors`` is given (an ``(n, 4)`` RGBA array aligned with
    ``y_vals``), each drawn dot is coloured by its own value instead of the
    single group ``color``.
    """
    # Position scatter points to the right of the box
    x_start = position + box_width/2 + box_dots_spacing
    
    x_coords, y_coords, indices = _compute_scatter_coords(
        x_start,
        y_vals,
        dot_spacing,
        y_threshold,
        n_bins
    )
    
    if point_colors is None:
        ax.scatter(x_coords, y_coords, color=color, **kwargs)
    else:
        ax.scatter(x_coords, y_coords, c=np.asarray(point_colors)[indices], **kwargs)


def _compute_scatter_coords(
    x_pos: float,
    y_values: np.ndarray,
    dot_spacing: float = 0.03,
    y_threshold: Optional[Union[float, str]] = "5%",
    n_bins: int = 40
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute coordinates for density-aligned scatter points.

    Returns ``(x_coords, y_coords, indices)`` where ``indices`` maps each drawn
    dot back to its row in ``y_values``, so per-point colours stay aligned even
    though dense rows are thinned and reordered by the density estimate.
    """
    y_values = np.asarray(y_values, dtype=float)
    n = y_values.size
    if n == 0:
        return np.array([]), np.array([]), np.array([], dtype=int)
    
    # Parse threshold
    if y_threshold is None:
        # Stripplot with 3% jitter - each point gets random x offset
        jitter_amount = 0.03
        x_coords = x_pos + np.random.uniform(-jitter_amount, jitter_amount, size=len(y_values))
        return x_coords, y_values, np.arange(n)
    elif isinstance(y_threshold, str):
        # Percentage string (e.g., "5%")
        if y_threshold.endswith('%'):
            percentage = float(y_threshold.rstrip('%')) / 100
            y_range_data = y_values.max() - y_values.min()
            y_threshold_value = y_range_data * percentage
        else:
            raise ValueError("String threshold must end with '%' (e.g., '5%')")
    else:
        # Absolute numeric value
        y_threshold_value = float(y_threshold)
    
    # Sort and group similar y-values, tracking original indices
    order = np.argsort(y_values, kind='stable')
    sorted_y = y_values[order]
    
    groups = []
    current_group = [0]
    for j in range(1, n):
        # Compare to the first value in the current group to ensure total range doesn't exceed threshold
        if (sorted_y[j] - sorted_y[current_group[0]]) <= y_threshold_value:
            current_group.append(j)
        else:
            groups.append(current_group)
            current_group = [j]
    groups.append(current_group)
    
    # Estimate density
    kde = gaussian_kde(y_values, bw_method='scott')
    y_range = np.linspace(y_values.min(), y_values.max(), n_bins)
    max_density = kde(y_range).max()
    if max_density <= 0:
        max_density = 1.0
    
    x_coords = []
    y_coords = []
    indices = []
    
    for group in groups:
        group_y = np.mean(sorted_y[group])
        n_points = len(group)
        
        density = kde(group_y)[0]
        n_dots_to_show = int(np.ceil(n_points * density / max_density))
        n_dots_to_show = min(n_dots_to_show, n_points)
        
        # Keep the first n_dots_to_show points (in sorted order) of the group.
        for k, sorted_idx in enumerate(group[:n_dots_to_show]):
            x_coords.append(x_pos + k * dot_spacing)
            y_coords.append(group_y)
            indices.append(order[sorted_idx])
    
    return (
        np.array(x_coords),
        np.array(y_coords),
        np.array(indices, dtype=int)
    )


def _resolve_scatter_colors(data, scatter_colors, scatter_cmap, scatter_norm,
                            scatter_palette):
    """Resolve ``scatter_colors`` into an ``(n, 4)`` RGBA array aligned with
    the rows of ``data``."""
    if isinstance(scatter_colors, str):
        if scatter_colors not in data.columns:
            raise ValueError(
                f"scatter_colors column '{scatter_colors}' not found in data "
                f"columns {list(data.columns)}"
            )
        values = data[scatter_colors].to_numpy()
    else:
        values = np.asarray(scatter_colors)
        if values.ndim == 2 and values.shape[1] in (3, 4):
            # An array of literal RGB(A) colours, one per row.
            if len(values) != len(data):
                raise ValueError(
                    f"scatter_colors has {len(values)} rows but data has "
                    f"{len(data)} rows"
                )
            return to_rgba_array(values)
        if values.ndim != 1 or len(values) != len(data):
            raise ValueError(
                f"scatter_colors must have one entry per data row: got "
                f"{len(values)} values for {len(data)} rows"
            )

    return _values_to_rgba(values, scatter_cmap, scatter_norm, scatter_palette)


def _values_to_rgba(values, scatter_cmap=None, scatter_norm=None,
                    scatter_palette=None):
    """Turn an array of per-point values into an RGBA array.

    Numeric values are mapped through a colormap; valid matplotlib colours are
    used literally; anything else is treated as categorical and mapped through
    a palette.
    """
    values = np.asarray(values)
    n = values.size
    if n == 0:
        return np.empty((0, 4))

    # An explicit palette forces the categorical path.
    if scatter_palette is not None:
        return _categorical_to_rgba(values, scatter_palette)

    is_numeric = np.issubdtype(values.dtype, np.number) or scatter_cmap is not None
    if is_numeric:
        colormap = _get_colormap(scatter_cmap or 'viridis')
        vals = values.astype(float)
        finite = np.isfinite(vals)
        if scatter_norm is None:
            if finite.any():
                vmin = float(vals[finite].min())
                vmax = float(vals[finite].max())
            else:
                vmin, vmax = 0.0, 1.0
            if vmax <= vmin:
                vmax = vmin + 1.0
            norm = Normalize(vmin=vmin, vmax=vmax)
        else:
            norm = scatter_norm
        return np.asarray(colormap(norm(vals)))

    # Non-numeric: use valid matplotlib colours literally if possible.
    finite_mask = ~pd.isna(values)
    try:
        rgba = np.zeros((n, 4))
        rgba[finite_mask] = to_rgba_array(values[finite_mask].tolist())
        return rgba
    except (ValueError, TypeError):
        pass

    return _categorical_to_rgba(values, scatter_palette)


def _categorical_to_rgba(values, palette=None):
    """Map categorical values to colours and return an RGBA array."""
    values = np.asarray(values)
    n = values.size
    finite_mask = ~pd.isna(values)

    categories = []
    for v in values[finite_mask]:
        if v not in categories:
            categories.append(v)

    colors = _build_categorical_palette(categories, palette)

    rgba = np.zeros((n, 4))
    for i in range(n):
        if finite_mask[i]:
            rgba[i] = to_rgba(colors[values[i]])
    return rgba


def _build_categorical_palette(categories, palette=None):
    """Return a ``{category: colour}`` dict for the given categories."""
    import seaborn as sns

    n = len(categories)
    if palette is None:
        palette = sns.color_palette(n_colors=max(n, 1))
    elif isinstance(palette, str):
        palette = sns.color_palette(palette, n_colors=max(n, 1))
    elif isinstance(palette, dict):
        return palette
    else:
        palette = list(palette)
        if len(palette) < n:
            raise ValueError(
                f"scatter_palette has {len(palette)} colours but {n} categories "
                f"are present"
            )
    return {cat: palette[i] for i, cat in enumerate(categories)}


def _get_colormap(cmap):
    """Return a Colormap from a name or Colormap instance."""
    if isinstance(cmap, Colormap):
        return cmap
    try:
        return plt.colormaps[cmap]
    except (AttributeError, KeyError):
        return cm.get_cmap(cmap)
