"""
Tests for raincloud plot functionality.
"""

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from raincloudpy import raincloudplot


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        'group': ['A'] * 30 + ['B'] * 30 + ['C'] * 30,
        'value': np.concatenate([
            np.random.randn(30) + 2,
            np.random.randn(30) + 3,
            np.random.randn(30) + 2.5
        ])
    })


def test_basic_raincloud_plot(sample_data):
    """Test basic raincloud plot creation."""
    fig, ax = plt.subplots()
    result = raincloudplot(data=sample_data, x='group', y='value', ax=ax)
    assert result is not None
    assert isinstance(result, plt.Axes)
    plt.close(fig)


def test_missing_data_raises_error():
    """Test that missing data parameter raises ValueError."""
    with pytest.raises(ValueError, match="data parameter is required"):
        raincloudplot(data=None)


def test_missing_x_y_raises_error(sample_data):
    """Test that missing x or y raises ValueError."""
    with pytest.raises(ValueError, match="Must specify both x and y"):
        raincloudplot(data=sample_data, x='group')
    
    with pytest.raises(ValueError, match="Must specify both x and y"):
        raincloudplot(data=sample_data, y='value')


def test_custom_palette(sample_data):
    """Test custom color palette."""
    fig, ax = plt.subplots()
    colors = ['red', 'green', 'blue']
    result = raincloudplot(
        data=sample_data, 
        x='group', 
        y='value', 
        palette=colors,
        ax=ax
    )
    assert result is not None
    plt.close(fig)


def test_custom_order(sample_data):
    """Test custom ordering of groups."""
    fig, ax = plt.subplots()
    result = raincloudplot(
        data=sample_data, 
        x='group', 
        y='value', 
        order=['C', 'B', 'A'],
        ax=ax
    )
    assert result is not None
    plt.close(fig)


def test_hide_components(sample_data):
    """Test hiding individual components."""
    fig, ax = plt.subplots()
    
    # Hide box
    result = raincloudplot(
        data=sample_data, 
        x='group', 
        y='value',
        show_box=False,
        ax=ax
    )
    assert result is not None
    
    # Hide violin
    result = raincloudplot(
        data=sample_data, 
        x='group', 
        y='value',
        show_violin=False,
        ax=ax
    )
    assert result is not None
    
    # Hide scatter
    result = raincloudplot(
        data=sample_data, 
        x='group', 
        y='value',
        show_scatter=False,
        ax=ax
    )
    assert result is not None
    
    plt.close(fig)


def test_custom_widths(sample_data):
    """Test custom width parameters."""
    fig, ax = plt.subplots()
    result = raincloudplot(
        data=sample_data, 
        x='group', 
        y='value',
        box_width=0.25,
        violin_width=0.4,
        ax=ax
    )
    assert result is not None
    plt.close(fig)


def test_custom_kwargs(sample_data):
    """Test custom kwargs for components."""
    fig, ax = plt.subplots()
    result = raincloudplot(
        data=sample_data, 
        x='group', 
        y='value',
        box_kwargs={'linewidth': 3},
        violin_kwargs={'alpha': 0.5},
        scatter_kwargs={'s': 20, 'alpha': 0.8},
        ax=ax
    )
    assert result is not None
    plt.close(fig)


def test_no_axes_provided(sample_data):
    """Test that function works without providing axes."""
    plt.figure()
    result = raincloudplot(data=sample_data, x='group', y='value')
    assert result is not None
    assert isinstance(result, plt.Axes)
    plt.close()


def test_compute_scatter_coords():
    """Test scatter coordinate computation."""
    from raincloudpy.raincloud import _compute_scatter_coords
    
    y_values = np.array([1, 1.1, 1.2, 2, 2.1, 3])
    x_coords, y_coords, indices = _compute_scatter_coords(
        x_pos=0,
        y_values=y_values,
        dot_spacing=0.03,
        y_threshold=0.2,
        n_bins=40
    )
    
    assert len(x_coords) > 0
    assert len(y_coords) > 0
    assert len(x_coords) == len(y_coords) == len(indices)
    assert indices.max() < len(y_values)
    # default keeps every point
    assert sorted(indices.tolist()) == list(range(len(y_values)))


def _scatter_collections(ax):
    """Return the scatter PathCollections on an axis."""
    from matplotlib.collections import PathCollection

    return [c for c in ax.collections if isinstance(c, PathCollection)]


def _unique_facecolors(ax):
    colls = _scatter_collections(ax)
    assert colls, 'no scatter collections found'
    fcs = np.concatenate([np.asarray(c.get_facecolors()) for c in colls], axis=0)
    return np.unique(fcs, axis=0)


def _scatter_dot_count(ax):
    return sum(len(np.asarray(c.get_offsets())) for c in _scatter_collections(ax))


def test_scatter_colors_numeric_column_maps_to_multiple_colours(sample_data):
    """Numeric scatter_colors should map through a colormap."""
    fig, ax = plt.subplots()
    data = sample_data.copy()
    data['trait'] = np.linspace(0, 1, len(data))
    raincloudplot(data=data, x='group', y='value', scatter_colors='trait', ax=ax)
    assert len(_unique_facecolors(ax)) > 2
    plt.close(fig)


def test_scatter_colors_literal_color_array(sample_data):
    """A list of literal colours should be used per-point."""
    fig, ax = plt.subplots()
    colors = ['red' if g == 'A' else 'blue' for g in sample_data['group']]
    raincloudplot(data=sample_data, x='group', y='value', scatter_colors=colors, ax=ax)
    assert len(_unique_facecolors(ax)) == 2
    plt.close(fig)


def test_scatter_colors_categorical_with_palette_dict(sample_data):
    """Categorical values should map through a supplied palette dict."""
    fig, ax = plt.subplots()
    data = sample_data.copy()
    data['cond'] = np.where(data['value'] > data['value'].median(), 'hi', 'lo')
    raincloudplot(
        data=data, x='group', y='value', scatter_colors='cond',
        scatter_palette={'hi': '#ff0000', 'lo': '#0000ff'}, ax=ax
    )
    assert len(_unique_facecolors(ax)) == 2
    plt.close(fig)


def test_scatter_colors_wrong_length_raises(sample_data):
    """A scatter_colors array of the wrong length should raise ValueError."""
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match='one entry per data row'):
        raincloudplot(data=sample_data, x='group', y='value',
                      scatter_colors=[0.1, 0.2], ax=ax)
    plt.close(fig)


def test_scatter_colors_unknown_column_raises(sample_data):
    """An unknown scatter_colors column should raise ValueError."""
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match='not found in data'):
        raincloudplot(data=sample_data, x='group', y='value',
                      scatter_colors='does_not_exist', ax=ax)
    plt.close(fig)


def test_scatter_colors_ignored_when_scatter_hidden(sample_data):
    """scatter_colors should be ignored (no error) when show_scatter=False."""
    fig, ax = plt.subplots()
    raincloudplot(data=sample_data, x='group', y='value',
                  scatter_colors='value', show_scatter=False, ax=ax)
    plt.close(fig)


def test_show_all_dots_draws_every_point(sample_data):
    """By default every data point should be drawn (no density thinning)."""
    fig, ax = plt.subplots()
    raincloudplot(data=sample_data, x='group', y='value', ax=ax)
    assert _scatter_dot_count(ax) == len(sample_data)
    plt.close(fig)


def test_show_all_dots_false_thins(sample_data):
    """show_all_dots=False should never draw more dots than data points."""
    fig, ax = plt.subplots()
    raincloudplot(data=sample_data, x='group', y='value',
                  show_all_dots=False, ax=ax)
    assert _scatter_dot_count(ax) <= len(sample_data)
    plt.close(fig)

