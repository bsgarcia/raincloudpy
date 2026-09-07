# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-09-07

### Added
- `scatter_colors` parameter to colour scatter dots individually
  - accepts a column name in `data` or an array-like with one entry per row
  - numeric values are mapped through a colormap (`scatter_cmap`, default 'viridis')
  - valid matplotlib colours are used literally
  - categorical values are mapped through `scatter_palette`
- `scatter_cmap`, `scatter_norm`, and `scatter_palette` parameters to control the
  per-point colour mapping
- `show_all_dots` parameter (default True): draw every data point instead of
  thinning dense rows by the KDE density estimate, which silently dropped dots
- Density-aligned scatter coordinates now also return the source row index of each
  drawn dot, so per-point colours stay aligned even though dense rows are thinned

## [0.4.0] - 2025-10-09

### Added
- Initial release of raincloudpy
- Core `raincloudplot()` function
- Support for boxplot, half-violin, and density-aligned scatter components
- Customizable colors via seaborn palettes
- Flexible component visibility controls
- Comprehensive documentation and examples
- Test suite with pytest
- CI/CD configuration
- MIT License

### Features
- Density-aligned scatter plots
- Half-violin plots on the left side
- Boxplot in the center
- Support for pandas DataFrames
- Customizable component widths and sizes
- Optional component kwargs for fine-tuned control
- Group ordering support
- Works with matplotlib axes

[0.4.0]: https://github.com/bsgarcia/raincloudpy/releases/tag/v0.4.0
