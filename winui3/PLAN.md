# WinUI 3 Backend Plan

This file is the persistent coordination state for the experimental `toga-winui3` backend. Future agents MUST read this file before planning or editing WinUI 3 backend work, MUST update it whenever new status, blockers, test results, or next tasks are discovered, and MUST update it again before giving a final response so context survives compaction and handoff.

## Current Status

- Last updated: 2026-05-28.
- Active Toga branch: `winui3-backend`.
- Branch lineage: this branch builds on Oliver's WinUI 3 proof-of-concept seed commit `595679a2a` and the local scaffolding commit `02d039f25 Add experimental WinUI 3 backend scaffolding`.
- Related Salut state: stable Windows support lives on Salut branch `fix/windows-support-revival`; Salut WinUI experimentation lives on `experiment/winui3-backend`.
- The latest completed WinUI slice builds out Button, Label, TextInput, Switch, Selection, Divider, NumberInput, PasswordInput, ProgressBar, ScrollContainer, ActivityIndicator, WebView, font handling, staging measurement, color probes, and backend probes.
- WebView was initially believed to require a Core WebView2 HWND controller bridge, but after the Briefcase dev environment was refreshed the installed `win32more.Microsoft.UI.Xaml.Controls` package exposed the XAML `WebView2` control. The backend now uses that native control directly.

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
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_selection.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_divider.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_numberinput.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_passwordinput.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_progressbar.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_scrollcontainer.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_activityindicator.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_webview.py --tb=short
```

Run this from `C:\Users\jezdez\Code\toga`:

```powershell
uvx ruff check winui3/src/toga_winui3/container.py winui3/src/toga_winui3/fonts.py winui3/src/toga_winui3/widgets/base.py winui3/src/toga_winui3/widgets/button.py winui3/src/toga_winui3/widgets/label.py winui3/src/toga_winui3/widgets/textinput.py winui3/src/toga_winui3/widgets/switch.py winui3/src/toga_winui3/widgets/selection.py winui3/src/toga_winui3/widgets/divider.py winui3/src/toga_winui3/widgets/numberinput.py winui3/src/toga_winui3/widgets/passwordinput.py winui3/src/toga_winui3/widgets/progressbar.py winui3/src/toga_winui3/widgets/scrollcontainer.py winui3/src/toga_winui3/widgets/activityindicator.py winui3/src/toga_winui3/widgets/webview.py winui3/src/toga_winui3/factory.py winui3/tests_backend/fonts.py winui3/tests_backend/probe.py winui3/tests_backend/widgets/base.py winui3/tests_backend/widgets/button.py winui3/tests_backend/widgets/textinput.py winui3/tests_backend/widgets/switch.py winui3/tests_backend/widgets/selection.py winui3/tests_backend/widgets/divider.py winui3/tests_backend/widgets/numberinput.py winui3/tests_backend/widgets/passwordinput.py winui3/tests_backend/widgets/progressbar.py winui3/tests_backend/widgets/scrollcontainer.py winui3/tests_backend/widgets/activityindicator.py winui3/tests_backend/widgets/webview.py
```

If `--update-requirements` hits a locked `coverage\tracer.cp313-win_arm64.pyd`, look for stale `uvx`, `uv`, `briefcase`, or `python` processes whose command lines mention `testbed-winui3` or `Code\toga\testbed`, then kill only those stale testbed-related processes and retry.

## Verified So Far

- Ruff passed across the touched WinUI backend files listed in the verification command.
- `tests/widgets/test_button.py` passed with `15 passed`.
- `tests/widgets/test_label.py` passed with `18 passed`.
- `tests/widgets/test_textinput.py` passed with `38 passed, 1 skipped, 4 xfailed`; undo is skipped and edit-menu readonly cases xfail because the current backend does not expose platform edit menu behavior.
- `tests/widgets/test_switch.py` passed with `15 passed`; implementation uses native WinUI `CheckBox`, not `ToggleSwitch`, because `ToggleSwitch` did not satisfy Toga desktop Switch measurement expectations around header text and font-driven width.
- `tests/widgets/test_selection.py` passed with `21 passed, 1 xfailed`; text alignment is xfailed because native WinUI `ComboBox` text alignment is not exposed through the current backend/probe, matching similar limitations on other desktop backends.
- `tests/widgets/test_divider.py` passed with `4 passed`.
- `tests/widgets/test_numberinput.py` passed with `16 passed, 1 skipped, 1 xfailed`; undo/redo is skipped by the shared Windows test policy, and text alignment is xfailed because WinUI `NumberBox` does not expose a simple text alignment surface through the current backend/probe.
- `tests/widgets/test_passwordinput.py` passed with `28 passed, 1 skipped, 1 xfailed`; undo/redo is skipped by the shared Windows test policy, and text alignment is xfailed because WinUI `PasswordBox` does not expose a simple text alignment surface through the current backend/probe.
- `tests/widgets/test_progressbar.py` passed with `8 passed`.
- `tests/widgets/test_scrollcontainer.py` passed with `18 passed`.
- `tests/widgets/test_activityindicator.py` passed with `7 passed`.
- `tests/widgets/test_webview.py` passed with `20 passed`.
- Earlier tiny app/Testbed startup checks passed after the backend registration and `testbed-winui3` app setup.

## Latest Completed Slice

- `winui3/src/toga_winui3/fonts.py`: maps Toga font families, size, weight, and style to WinUI `FontFamily`, `FontSize`, `FontWeight`, and `FontStyle`; custom registered fonts are still unsupported.
- `winui3/src/toga_winui3/widgets/base.py`: stages content synchronously with `Measure(Size(10000, 10000))`, applies fonts to native controls and staged content, and keeps layout refreshing when font changes affect intrinsic size.
- `winui3/src/toga_winui3/widgets/button.py`: uses `WeakrefCallable` for `Click`, uses `TextBlock` content so text measures correctly, renders icons as 32x32 native XAML `Image` content, treats empty text as zero-width space for height, and keeps Button-specific transparent background behavior as a native reset.
- `winui3/src/toga_winui3/widgets/label.py`: uses a native `Border` wrapper with an inner `TextBlock`, supports native background colors, foreground color reset, font application, enabled state, horizontal text alignment, zero-width-space height preservation for empty text, and content-based measurement.
- `winui3/src/toga_winui3/widgets/textinput.py`: adds minimal but tested WinUI `TextBox` support for value, placeholder, readonly, text alignment, focus/change/confirm events, validation state, font-sensitive rehinting, and single-line behavior.
- `winui3/src/toga_winui3/widgets/switch.py`: adds native `CheckBox` support for text, value, enabled, color/background, font-sensitive measurement, focus, press/change events, and WinRT boxed Boolean unboxing with `win32more.unbox_value`.
- `winui3/src/toga_winui3/widgets/selection.py`: adds native `ComboBox` support for list data source updates, duplicate display titles, programmatic and user selection changes, selected-item preservation across source inserts/removals, font-sensitive text measurement, and explicit Python-side title tracking because WinUI/win32more does not reliably expose `ComboBoxItem.Content` after insertion.
- `winui3/src/toga_winui3/widgets/divider.py`: adds a native WinUI `Border` separator with horizontal/vertical intrinsic sizing and inert background styling.
- `winui3/src/toga_winui3/widgets/numberinput.py`: adds native WinUI `NumberBox` support for decimal parsing, raw editing text, empty values, min/max, step, readonly state, focus, increment/decrement, and change events; the backend keeps a Python-side raw text cache because `NumberBox.Text` normalizes partial input such as trailing decimal points.
- `winui3/src/toga_winui3/widgets/passwordinput.py`: adds native WinUI `PasswordBox` support for hidden values, placeholder text, backend-guarded readonly state, focus/change/confirm events, validation, color/background, and font-sensitive measurement inherited from TextInput; text alignment is unsupported by native `PasswordBox`.
- `winui3/src/toga_winui3/widgets/progressbar.py`: adds native WinUI `ProgressBar` support for determinate values, maximum changes, backend-tracked running state, and indeterminate animation through native `IsIndeterminate`.
- `winui3/src/toga_winui3/widgets/scrollcontainer.py`: adds native WinUI `ScrollViewer` support with an owned inner `Canvas` container for Toga layout content, horizontal/vertical enablement, programmatic and simulated manual scrolling, scroll event notifications, content clearing/restoring, background styling, and no-op focus/enabled semantics.
- `winui3/src/toga_winui3/widgets/activityindicator.py`: adds native WinUI `ProgressRing` support with backend-tracked running state, stop-as-hidden behavior that preserves layout, explicit no-op focus/enabled behavior, and fixed 32x32 intrinsic sizing.
- `winui3/src/toga_winui3/widgets/webview.py`: adds native XAML `WebView2` support for async initialization, URL loading/clearing, static and large content, user-agent overrides, JavaScript evaluation, cookie retrieval, webview-load events, and sync/async navigation-starting handlers.
- `winui3/src/toga_winui3/container.py`: removes native children by WinUI vector identity instead of by the Python widget-list index, because the hidden staging panel also lives in the native `Children` collection and made content reattachment fail.
- `winui3/pyproject.toml` and `winui3/src/toga_winui3/factory.py`: enable `TextInput`, `Switch`, `Selection`, `Divider`, `NumberInput`, `PasswordInput`, `ProgressBar`, `ScrollContainer`, `ActivityIndicator`, and `WebView` in the backend entry points and factory exports.
- `winui3/tests_backend/fonts.py`: adds a WinUI font probe mixin.
- `winui3/tests_backend/probe.py`: makes width and height probes prefer finite assigned layout dimensions before falling back to actual size.
- `winui3/tests_backend/widgets/base.py`: adds color/background probing for `SolidColorBrush`, including reporting fully transparent black as Toga `TRANSPARENT`, and falls back to backend `get_enabled()` for native elements without `IsEnabled`.
- `winui3/tests_backend/widgets/button.py`: probes Button `TextBlock` content, targets that content for font assertions, and verifies native icon image size.
- `winui3/tests_backend/widgets/label.py`: probes the `Border`/`TextBlock` split correctly for text, foreground color, font, and alignment.
- `winui3/tests_backend/widgets/textinput.py`: adds TextInput probing for value, placeholder, readonly, alignment, typing, confirm key, selection, and cursor placement.
- `winui3/tests_backend/widgets/switch.py`: probes `CheckBox` content text and font target, normalizes zero-width-space empty text, and simulates press via the backend value path because a native WinUI click is not currently injectable in the probe.
- `winui3/tests_backend/widgets/selection.py`: probes `ComboBox` item titles through the backend title cache, selected title, GUI selection changes, content-resize behavior, and xfails text alignment.
- `winui3/tests_backend/widgets/divider.py`: probes the native `Border` separator used by Divider.
- `winui3/tests_backend/widgets/numberinput.py`: probes `NumberBox` value text through the backend raw text cache, readonly state, focus, font-sensitive height, increment/decrement, typed numeric input, and above-maximum redraw clipping; text alignment is xfailed.
- `winui3/tests_backend/widgets/passwordinput.py`: probes `PasswordBox` hidden value behavior, placeholder visibility, backend readonly state, typed password input, and confirm-key handling; text alignment is xfailed.
- `winui3/tests_backend/widgets/progressbar.py`: probes native `ProgressBar` determinate/indeterminate state, native animation flag, and value position.
- `winui3/tests_backend/widgets/scrollcontainer.py`: probes native `ScrollViewer` content extents, scroll positions, content presence, and manual scroll simulation.
- `winui3/tests_backend/widgets/activityindicator.py`: probes native `ProgressRing` animation and hidden state.
- `winui3/tests_backend/widgets/webview.py`: probes native XAML `WebView2`, marks Windows content URLs and JavaScript exceptions as unsupported, extracts cookies, and resolves large-content cache file URLs.

## Known Gaps

- TextInput custom fonts and registered font files are unsupported; arbitrary system font names are accepted optimistically.
- The backend still lacks many widgets beyond the currently completed set and needs a parity roadmap for each widget before it becomes more than experimental.
- WinUI app resource lookup still logs missing `winui3app.xbf` and `winui3app.xaml` resource messages during Testbed startup, although the tests still run.
- Command shortcuts are still not implemented and emit `NotImplementedWarning`.

## Next Work

1. Continue with Salut-driven widgets; likely candidates include MultilineTextInput and ImageView.
2. Review current Testbed coverage gaps now that WebView is green, especially missing probes/xfails/skips and unimplemented widget entry points.
3. Continue expanding backend parity one widget at a time, recording each Testbed file status here before moving to the next widget.

## Commit Boundary

Milestone commit message for the latest completed slice: `Add WinUI WebView support`.
