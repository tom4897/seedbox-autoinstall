# Ubuntu Autoinstall Scope Execution Order

## Overview

This document outlines the execution order of scopes in Ubuntu autoinstall configurations based on analysis of the seedbox-autoinstall project.

## Execution Order

### 1. Early Configuration Scopes

These scopes are executed first during the installation process:

- **`identity`** - Sets hostname, username, and password
- **`ssh`** - Configures SSH server settings  
- **`network`** - Network configuration (optional)
- **`storage`** - Disk layout configuration

### 2. Package Management Scopes

Executed after early configuration:

- **`apt`** - APT repository configuration
- **`packages`** - Package installation

### 3. User Configuration Scope

Executed after package installation:

- **`user-data`** - Nested cloud-config containing:
  - `users` - User creation and SSH key setup
  - `write_files` - File creation (configs, scripts)
  - `runcmd` - Commands to run during installation
  - `timezone`, `locale`, `keyboard` - System locale settings

### 4. Final Commands Scope

Executed last, after system installation:

- **`late-commands`** - Commands executed after installation but before reboot

## Key Points

1. **Sequential Execution**: Scopes execute in the order they appear in the file
2. **Nested user-data**: The `user-data` scope contains cloud-config directives that execute during installation
3. **Command Context**:
   - `runcmd` (within nested user-data) runs during installation
   - `late-commands` runs after installation using `curtin in-target`
4. **Execution Frequency**: All scopes run once during the installation process

## Example Structure

```yaml
#cloud-config
autoinstall:
  version: 1
  identity:
    hostname: example
    username: user
  ssh:
    install-server: true
  storage:
    layout:
      name: direct
  apt:
    geoip: true
  packages:
    - package1
    - package2
  user-data:
    users:
      - name: user
    write_files:
      - path: /etc/config
    runcmd:
      - command1
  late-commands:
    - curtin in-target -- command2
```

## References

- Ubuntu Server Guide: Autoinstall Reference
- Ubuntu autoinstall schema documentation
- Cloud-init documentation (for nested user-data behavior)

## Notes

- This execution order is based on analysis of the seedbox-autoinstall project
- For authoritative documentation, refer to official Ubuntu autoinstall documentation
- The nested `user-data` scope follows cloud-init execution patterns
