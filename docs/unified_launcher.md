# Unified Launcher

The Unified Launcher is a central hub for accessing all versions of the Deep Blue Pool Chemistry application.

## Features

- Access to all versions of the application (Standard UI, Responsive UI, Enhanced Data Visualization)
- Settings management
- Recent files tracking
- Documentation access
- Theme customization

## Usage

To start the Unified Launcher, run:

```bash
python run_all.py
```

Or directly:

```bash
python unified_launcher.py
```

## Configuration

The Unified Launcher can be configured by editing the `config/launcher_config.json` file.

Available settings:
- `theme`: UI theme ("light" or "dark")
- `last_used_version`: Last used application version
- `show_welcome`: Whether to show the welcome screen at startup
- `check_updates`: Whether to check for updates at startup
- `recent_files`: List of recently opened files
