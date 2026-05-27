# WinUI 3 Backend Plan

This file is the persistent coordination state for the experimental `toga-winui3` backend. Future agents MUST read this file before planning or editing WinUI 3 backend work, MUST update it whenever new status, blockers, test results, or next tasks are discovered, and MUST update it again before giving a final response so context survives compaction and handoff.

## Current Status

- Last updated: 2026-05-28.
- Active Toga branch: `winui3-backend`.
- Branch lineage: this branch builds on Oliver's WinUI 3 proof-of-concept seed commit `595679a2a` and the local scaffolding commit `02d039f25 Add experimental WinUI 3 backend scaffolding`.
- Related Salut state: stable Windows support lives on Salut branch `fix/windows-support-revival`; Salut WinUI experimentation lives on `experiment/winui3-backend`.
- The latest completed WinUI slice builds out Button, Label, TextInput, Switch, font handling, staging measurement, color probes, and backend probes.
- Active continuation target after Switch: Selection, chosen because Salut's Windows settings panes use multiple `toga.Selection` controls for log level, transport, model, and preload choices.

## Operating Rules

- Before any WinUI 3 backend work, read this file, `.specify/memory/constitution.md`, and root `AGENTS.md`.
- Keep this file current while working: update status when a test result changes, a blocker is found, a scope boundary changes, or a new next task becomes clearer.
- Do not let this file become aspirational only; record what has actually passed, what is known failing, and what is merely proposed.
- Use targeted Testbed slices for backend behavior and record exact pass/fail summaries here.
- After changing backend entry points in `winui3/pyproject.toml`, run the WinUI Testbed with `--update-requirements` so Briefcase refreshes the dev environment.

## Verification Commands

Run these from `C:\Users\jezdez\Code\toga\testbed` unless noted:

```powershell
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_button.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_textinput.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_label.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_switch.py --tb=short
```

Run this from `C:\Users\jezdez\Code\toga`:

```powershell
uvx ruff check winui3/src/toga_winui3/fonts.py winui3/src/toga_winui3/widgets/base.py winui3/src/toga_winui3/widgets/button.py winui3/src/toga_winui3/widgets/label.py winui3/src/toga_winui3/widgets/textinput.py winui3/src/toga_winui3/widgets/switch.py winui3/src/toga_winui3/factory.py winui3/tests_backend/fonts.py winui3/tests_backend/probe.py winui3/tests_backend/widgets/base.py winui3/tests_backend/widgets/button.py winui3/tests_backend/widgets/textinput.py winui3/tests_backend/widgets/switch.py
```

If `--update-requirements` hits a locked `coverage\tracer.cp313-win_arm64.pyd`, look for stale `uvx`, `uv`, `briefcase`, or `python` processes whose command lines mention `testbed-winui3` or `Code\toga\testbed`, then kill only those stale testbed-related processes and retry.

## Verified So Far

- Ruff passed across the touched WinUI backend files listed in the verification command.
- `tests/widgets/test_button.py` passed with `15 passed`.
- `tests/widgets/test_label.py` passed with `18 passed`.
- `tests/widgets/test_textinput.py` passed with `38 passed, 1 skipped, 4 xfailed`; undo is skipped and edit-menu readonly cases xfail because the current backend does not expose platform edit menu behavior.
- `tests/widgets/test_switch.py` passed with `15 passed`; implementation uses native WinUI `CheckBox`, not `ToggleSwitch`, because `ToggleSwitch` did not satisfy Toga desktop Switch measurement expectations around header text and font-driven width.
- Earlier tiny app/Testbed startup checks passed after the backend registration and `testbed-winui3` app setup.

## Latest Completed Slice

- `winui3/src/toga_winui3/fonts.py`: maps Toga font families, size, weight, and style to WinUI `FontFamily`, `FontSize`, `FontWeight`, and `FontStyle`; custom registered fonts are still unsupported.
- `winui3/src/toga_winui3/widgets/base.py`: stages content synchronously with `Measure(Size(10000, 10000))`, applies fonts to native controls and staged content, and keeps layout refreshing when font changes affect intrinsic size.
- `winui3/src/toga_winui3/widgets/button.py`: uses `WeakrefCallable` for `Click`, uses `TextBlock` content so text measures correctly, renders icons as 32x32 native XAML `Image` content, treats empty text as zero-width space for height, and keeps Button-specific transparent background behavior as a native reset.
- `winui3/src/toga_winui3/widgets/label.py`: uses a native `Border` wrapper with an inner `TextBlock`, supports native background colors, foreground color reset, font application, enabled state, horizontal text alignment, zero-width-space height preservation for empty text, and content-based measurement.
- `winui3/src/toga_winui3/widgets/textinput.py`: adds minimal but tested WinUI `TextBox` support for value, placeholder, readonly, text alignment, focus/change/confirm events, validation state, font-sensitive rehinting, and single-line behavior.
- `winui3/src/toga_winui3/widgets/switch.py`: adds native `CheckBox` support for text, value, enabled, color/background, font-sensitive measurement, focus, press/change events, and WinRT boxed Boolean unboxing with `win32more.unbox_value`.
- `winui3/pyproject.toml` and `winui3/src/toga_winui3/factory.py`: enable `TextInput` and `Switch` in the backend entry points and factory exports.
- `winui3/tests_backend/fonts.py`: adds a WinUI font probe mixin.
- `winui3/tests_backend/probe.py`: makes width and height probes prefer finite assigned layout dimensions before falling back to actual size.
- `winui3/tests_backend/widgets/base.py`: adds color/background probing for `SolidColorBrush`, including reporting fully transparent black as Toga `TRANSPARENT`, and falls back to backend `get_enabled()` for native elements without `IsEnabled`.
- `winui3/tests_backend/widgets/button.py`: probes Button `TextBlock` content, targets that content for font assertions, and verifies native icon image size.
- `winui3/tests_backend/widgets/label.py`: probes the `Border`/`TextBlock` split correctly for text, foreground color, font, and alignment.
- `winui3/tests_backend/widgets/textinput.py`: adds TextInput probing for value, placeholder, readonly, alignment, typing, confirm key, selection, and cursor placement.
- `winui3/tests_backend/widgets/switch.py`: probes `CheckBox` content text and font target, normalizes zero-width-space empty text, and simulates press via the backend value path because a native WinUI click is not currently injectable in the probe.

## Known Gaps

- TextInput custom fonts and registered font files are unsupported; arbitrary system font names are accepted optimistically.
- The backend still lacks most widgets beyond Box, Button, Label, and TextInput, and needs a parity roadmap for each widget before it becomes more than experimental.
- WinUI app resource lookup still logs missing `winui3app.xbf` and `winui3app.xaml` resource messages during Testbed startup, although the tests still run.
- Command shortcuts are still not implemented and emit `NotImplementedWarning`.

## Next Work

1. Implement and test Selection using WinUI `ComboBox`; cover item list, selected item/value, enabled state, font-sensitive sizing, and change events.
2. After Selection, prioritize Salut's remaining Windows settings blockers: Divider, NumberInput, PasswordInput, ProgressBar, and ScrollContainer, then WebView for chat.
3. Continue expanding backend parity one widget at a time, recording each Testbed file status here before moving to the next widget.

## Commit Boundary

Milestone commit message for the latest completed slice: `Add WinUI Switch support`.
