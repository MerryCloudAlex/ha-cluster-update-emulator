# HA Cluster Update Emulator

A console-based simulator of a two-node high-availability cluster update process.
Written in pure Python 3, no external dependencies.

> **Disclaimer:** This is a personal educational project. It is an independent
> emulator that reproduces the *logic* of a cluster upgrade workflow for learning
> purposes. It is **not** affiliated with, sponsored by, or endorsed by any
> commercial vendor or product mentioned in the description. All product names
> and trademarks belong to their respective owners. No proprietary code,
> documentation, or internal materials were used in the creation of this project.

---

## What it is

This project simulates the update procedure for a two-node HA cluster with
Active/Passive failover. The goal was to understand and practice the sequence
of commands, cluster state transitions, and failover mechanics without access
to real hardware.

The emulator reproduces:

- Cluster state management (Active / Passive)
- Service lifecycle (`mftp`, `ipdr`, `failover`)
- Physical actions (marking cables, placing inventory stickers, USB/token insertion)
- Encrypted VBE key export
- Software upgrade procedure with a post-reboot setup wizard
- Full and configuration-only backups
- Role switching and failover restart

---

## Requirements

- Python 3.8+
- No third-party libraries

---

## Run

```bash
python3 hw1000_v4.py
