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
    x_coords, y_coords = _compute_scatter_coords(
        x_pos=0,
        y_values=y_values,
        dot_spacing=0.03,
        y_threshold=0.2,
        n_bins=40
    )
    
    assert len(x_coords) > 0
    assert len(y_coords) > 0
    assert len(x_coords) == len(y_coords)
