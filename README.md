Seedbox Autoinstall
====================

User-focused, reproducible Ubuntu seedbox provisioning with cloud-init NoCloud seeds.

What this is
-------------

- Static bundles of `meta-data` and `user-data` for Ubuntu autoinstall.
- Ready-to-use sample host profiles under `cloud-init/v1/hosts/` you can copy and customize.
- A validator script to catch common mistakes before you boot.

Requirements
------------

- A VM, server, or bare-metal install that supports cloud-init NoCloud.
- Ubuntu Server autoinstall (20.04+)
- One delivery method for the seed:
  - ISO/USB labeled `cidata` containing `user-data` and `meta-data`, or
  - HTTP(S) serving of these files (NoCloud-Net).

Quick start (ISO / USB NoCloud)
-------------------------------

1. Pick a starting profile from `cloud-init/v1/hosts/` (e.g. `sample`, `minimal`, or `ansible`).
2. Copy it to a new directory name:
   - `cloud-init/v1/hosts/<your-host>/`
3. Edit `meta-data` and `user-data` to suit your environment.
4. Create a small ISO (or USB) labeled `cidata` containing exactly these two files from your new host directory:
   - `user-data`
   - `meta-data`
5. Attach the media and boot the target. Cloud-init will apply the configuration on first boot.

Quick start (serve over HTTP)
-----------------------------

- Serve the version folder `cloud-init/v1/` with any static web server.
- Use the included landing page and hosts browser to verify paths.
  - Landing page: `.../cloud-init/v1/index.html`
  - Hosts list: `.../cloud-init/v1/hosts/_list.html`
- The installer will fetch these files for your chosen host:
  - `.../hosts/<your-host>/user-data`
  - `.../hosts/<your-host>/meta-data`

Example from the repository root:

```bash
python -m http.server 8000 --directory cloud-init/
# Open the helper page in a browser to copy the computed URL:
# http://<server>:8000/index.html
# Or browse host seeds directly:
# http://<server>:8000/hosts/_list.html
```

Note: the address needs to be accessible from the target server being installed.

Ubuntu installer kernel line (NoCloud-Net)
-----------------------------------------

When booting the Ubuntu installer (GRUB/syslinux), add the following to the kernel command line to enable unattended install via HTTP. The helper page shows this with your exact base URL and offers a one-click copy.

```text
autoinstall ds="nocloud;s=http://ashley/cloud-init/v1/hosts/<hostname>/" ip=dhcp
```

Notes:

- Replace `<hostname>` with your host directory name under `cloud-init/v1/hosts/`.
- Keep the trailing `/` after the host directory.
- The URL must be reachable from the target machine.
- If the ds parameter isn't quoted, you must backslash/escape the semicolon (;) like this: `\;`

Customize a new host profile
----------------------------

- Create `cloud-init/v1/hosts/<your-host>/` with copies of `meta-data` and `user-data` from a sample profile.
- Edit `meta-data`:
  - Set a unique `instance-id` (often starting with your `local-hostname`).
  - Set `local-hostname`.
- Edit `user-data`:
  - Keep the first line `#cloud-config`.
  - Adjust `autoinstall` sections (e.g., storage, identity, packages, late-commands).
  - Re-run the validator until it passes.

Directory layout
----------------

- `cloud-init/v1/`
  - `hosts/`
    - `minimal/`, `sample/`, `ansible/` → example profiles
      - `meta-data`
      - `user-data`
  - `index.html` → optional landing page if serving over HTTP
  - `hosts/_list.html` → optional host browser page when serving over HTTP
- `scripts/`
  - `validate_autoinstall.py` → checks your host profiles
  - `ubuntu_autoinstall_schema.json` → validation schema
  - `requirements.txt` → Python deps for the validator
- `LICENSE`

Versioning
----------

- Breaking changes will land in new version folders like `cloud-init/v2/`.

License
-------

- See `LICENSE`.

Validate your files (recommended)
---------------------------------

1. Install requirements once:

```bash
pip install -r scripts/requirements.txt
```

1. Run the validator:

```bash
python scripts/validate_autoinstall.py
# or specify a different hosts dir
python scripts/validate_autoinstall.py --hosts-dir cloud-init/v1/hosts
```

The validator checks:

- Presence and basic correctness of `meta-data` (`instance-id`, `local-hostname`).
- `user-data` YAML, top-level `#cloud-config`, and `autoinstall` structure against the official JSON schema.

Schema reference:

- The JSON schema used by the validator is vendored at `scripts/ubuntu_autoinstall_schema.json`. See Canonical Subiquity Autoinstall documentation for upstream details.

Todo list
---------

The `one of these days, I'll have the time` list:

- Full user-data with comments
- Scaffold profiles for desktop and k8s-node
- Overlays (comon, proxmox, aws)
- J2 templates and snippets
- Clean and release push scripts
