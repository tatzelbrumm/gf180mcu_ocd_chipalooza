# handoff: for the harness maintainer and the slot designers

- [`CHANGES_FOR_TIM.md`](CHANGES_FOR_TIM.md): every change on branch `custom_padframe` against `main` (`2f18cd4`),
  the custom pad class, the checks run, what is open, and pre-existing harness issues found on the way.
- [`SLOT10_FIXES.md`](SLOT10_FIXES.md): three harness problems around slot 10, with fixes, and what the slot 10
  designer should know.
- `logs/`: the extraction, LVS and comparison logs those two files cite (scratch paths written `<scratch>`, this
  repository `<fork>`).
- `tools/`: `net_compare.py` (connectivity of two xschem netlists, pins by name), `spice_inst.py`, `sym_pins.py`
  (symbol pin positions against a git revision).

Written 2026-11-28 by a Claude Code session working for the slot 16 designer. Nothing here has been sent to anyone.
