# WinUI 3 Backend Plan

This file is the persistent coordination state for the experimental `toga-winui3` backend. Future agents MUST read this file before planning or editing WinUI 3 backend work, MUST update it whenever new status, blockers, test results, or next tasks are discovered, and MUST update it again before giving a final response so context survives compaction and handoff.

## Current Status

- Last updated: 2026-05-28.
- Active Toga branch: `winui3-backend`.
- Active slice: `DetailedList` focused verification is green; next slice is `Canvas`.
- Branch lineage: this branch builds on Oliver's WinUI 3 proof-of-concept seed commit `595679a2a` and the local scaffolding commit `02d039f25 Add experimental WinUI 3 backend scaffolding`.
- Related Salut state: stable Windows support lives on Salut branch `fix/windows-support-revival`; Salut WinUI experimentation lives on `experiment/winui3-backend`.
- The latest completed WinUI slice builds out Image, ImageView, Button, Label, TextInput, MultilineTextInput, DateInput, TimeInput, OptionContainer, Slider, SplitContainer, Switch, Selection, Divider, NumberInput, PasswordInput, ProgressBar, ScrollContainer, ActivityIndicator, Table, WebView, font handling, staging measurement, color probes, and backend probes.
- WebView was initially believed to require a Core WebView2 HWND controller bridge, but after the Briefcase dev environment was refreshed the installed `win32more.Microsoft.UI.Xaml.Controls` package exposed the XAML `WebView2` control. The backend now uses that native control directly.
- MultilineTextInput cannot inherit TextInput focus tracking directly because the core `MultilineTextInput` interface does not expose `on_gain_focus`/`on_lose_focus`; its backend must use native focus without dispatching TextInput-only focus handlers.
- Image support currently uses a PNG-backed `NativeImage` wrapper around WinUI `BitmapImage`; broader JPEG/GIF/BMP/TIFF decode and encode support remains a follow-up.
- Slider uses native WinUI `Slider` with value/min/max/tick support, pointer press/release events, and focused Testbed coverage.
- DateInput uses native WinUI `DatePicker` with native min/max dates; TimeInput uses native WinUI `TimePicker` with minute-resolution values and backend-tracked min/max limits because the native control does not expose limit properties or seconds selection.

## Operating Rules

- Before any WinUI 3 backend work, read this file, `.specify/memory/constitution.md`, and root `AGENTS.md`.
- This plan is NOT done until every Toga widget entry point has a WinUI implementation, backend probe, focused Testbed result recorded here, and no disabled widget entry remains in `winui3/pyproject.toml`; agents must keep building rather than stopping at partial Salut usefulness.
- Keep this file current while working: update status when a test result changes, a blocker is found, a scope boundary changes, or a new next task becomes clearer.
- Do not let this file become aspirational only; record what has actually passed, what is known failing, and what is merely proposed.
- Use targeted Testbed slices for backend behavior and record exact pass/fail summaries here.
- After changing backend entry points in `winui3/pyproject.toml`, run the WinUI Testbed with `--update-requirements` so Briefcase refreshes the dev environment.

## Completion Criteria

- Do not call this plan finished while any widget entry point is still commented out or missing from `winui3/pyproject.toml`.
- Do not call this plan finished while any implemented widget lacks a WinUI probe under `winui3/tests_backend/widgets/` and a focused Testbed pass/fail summary in this file.
- After all widgets are implemented and verified, the remaining app/window probe skips and xfails must be reviewed and either implemented, explicitly justified as native-platform limits, or moved into a follow-up plan with clear scope.

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
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_multilinetextinput.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/test_images.py tests/widgets/test_imageview.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_slider.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_dateinput.py tests/widgets/test_timeinput.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_splitcontainer.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_optioncontainer.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_table.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_tree.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_detailedlist.py --tb=short
```

Run this from `C:\Users\jezdez\Code\toga`:

```powershell
uvx ruff check winui3/src/toga_winui3/container.py winui3/src/toga_winui3/fonts.py winui3/src/toga_winui3/images.py winui3/src/toga_winui3/widgets/base.py winui3/src/toga_winui3/widgets/button.py winui3/src/toga_winui3/widgets/label.py winui3/src/toga_winui3/widgets/imageview.py winui3/src/toga_winui3/widgets/textinput.py winui3/src/toga_winui3/widgets/multilinetextinput.py winui3/src/toga_winui3/widgets/dateinput.py winui3/src/toga_winui3/widgets/timeinput.py winui3/src/toga_winui3/widgets/optioncontainer.py winui3/src/toga_winui3/widgets/slider.py winui3/src/toga_winui3/widgets/splitcontainer.py winui3/src/toga_winui3/widgets/switch.py winui3/src/toga_winui3/widgets/selection.py winui3/src/toga_winui3/widgets/divider.py winui3/src/toga_winui3/widgets/numberinput.py winui3/src/toga_winui3/widgets/passwordinput.py winui3/src/toga_winui3/widgets/progressbar.py winui3/src/toga_winui3/widgets/scrollcontainer.py winui3/src/toga_winui3/widgets/activityindicator.py winui3/src/toga_winui3/widgets/table.py winui3/src/toga_winui3/widgets/tree.py winui3/src/toga_winui3/widgets/detailedlist.py winui3/src/toga_winui3/widgets/webview.py winui3/src/toga_winui3/factory.py winui3/tests_backend/images.py winui3/tests_backend/fonts.py winui3/tests_backend/probe.py winui3/tests_backend/widgets/base.py winui3/tests_backend/widgets/button.py winui3/tests_backend/widgets/imageview.py winui3/tests_backend/widgets/textinput.py winui3/tests_backend/widgets/multilinetextinput.py winui3/tests_backend/widgets/dateinput.py winui3/tests_backend/widgets/timeinput.py winui3/tests_backend/widgets/optioncontainer.py winui3/tests_backend/widgets/slider.py winui3/tests_backend/widgets/splitcontainer.py winui3/tests_backend/widgets/switch.py winui3/tests_backend/widgets/selection.py winui3/tests_backend/widgets/divider.py winui3/tests_backend/widgets/numberinput.py winui3/tests_backend/widgets/passwordinput.py winui3/tests_backend/widgets/progressbar.py winui3/tests_backend/widgets/scrollcontainer.py winui3/tests_backend/widgets/activityindicator.py winui3/tests_backend/widgets/table.py winui3/tests_backend/widgets/tree.py winui3/tests_backend/widgets/detailedlist.py winui3/tests_backend/widgets/webview.py
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
- `tests/widgets/test_multilinetextinput.py` passed with `38 passed, 2 skipped`; undo/redo and mouse-wheel simulation are skipped by current WinUI probe policy.
- `tests/test_images.py` and `tests/widgets/test_imageview.py` passed together with `18 passed`.
- `tests/widgets/test_slider.py` passed with `15 passed`.
- `tests/widgets/test_dateinput.py` and `tests/widgets/test_timeinput.py` passed together with `26 passed`.
- `tests/widgets/test_splitcontainer.py` passed with `8 passed`.
- `tests/widgets/test_optioncontainer.py` passed with `8 passed, 1 skipped`; content-based rehinting is skipped because WinUI window/content minimum-size propagation is not yet supported.
- `tests/widgets/test_table.py` passed with `26 passed`.
- `tests/widgets/test_tree.py` passed with `25 passed`.
- `tests/widgets/test_detailedlist.py` passed with `15 passed`.
- Earlier tiny app/Testbed startup checks passed after the backend registration and `testbed-winui3` app setup.

## Latest Completed Slice

- `winui3/src/toga_winui3/fonts.py`: maps Toga font families, size, weight, and style to WinUI `FontFamily`, `FontSize`, `FontWeight`, and `FontStyle`; custom registered fonts are still unsupported.
- `winui3/src/toga_winui3/images.py`: adds PNG-backed Toga Image support using a `NativeImage` wrapper around WinUI `BitmapImage`, cached file URIs for XAML loading, PNG dimension parsing, raw native-image roundtrips, and PNG save support.
- `winui3/src/toga_winui3/widgets/base.py`: stages content synchronously with `Measure(Size(10000, 10000))`, applies fonts to native controls and staged content, keeps layout refreshing when font changes affect intrinsic size, and tracks the focused WinUI widget requested through Toga so composite controls can report focus consistently.
- `winui3/src/toga_winui3/widgets/button.py`: uses `WeakrefCallable` for `Click`, uses `TextBlock` content so text measures correctly, renders icons as 32x32 native XAML `Image` content, treats empty text as zero-width space for height, and keeps Button-specific transparent background behavior as a native reset.
- `winui3/src/toga_winui3/widgets/label.py`: uses a native `Border` wrapper with an inner `TextBlock`, supports native background colors, foreground color reset, font application, enabled state, horizontal text alignment, zero-width-space height preservation for empty text, and content-based measurement.
- `winui3/src/toga_winui3/widgets/imageview.py`: adds native WinUI XAML `Image` support inside a `Border` wrapper for background styling, image clearing/restoring, aspect-preserving stretch modes, no-op focus/enabled behavior, and image-driven size hints through core `rehint_imageview`.
- `winui3/src/toga_winui3/widgets/textinput.py`: adds minimal but tested WinUI `TextBox` support for value, placeholder, readonly, text alignment, focus/change/confirm events, validation state, font-sensitive rehinting, and single-line behavior.
- `winui3/src/toga_winui3/widgets/multilinetextinput.py`: adds native WinUI multiline `TextBox` support for value, placeholder, readonly, text alignment, focus, change events, newline normalization, multiline wrapping, and programmatic scrolling through the TextBox template's internal `ScrollViewer`.
- `winui3/src/toga_winui3/widgets/dateinput.py`: adds native WinUI `DatePicker` support for value, native min/max dates, change events, color/background, enabled state, and size hints.
- `winui3/src/toga_winui3/widgets/timeinput.py`: adds native WinUI `TimePicker` support for minute-resolution value changes, backend-tracked min/max times, change events, color/background, enabled state, and size hints.
- `winui3/src/toga_winui3/widgets/optioncontainer.py`: adds native WinUI `TabView`/`TabViewItem` support for tab insertion/removal, selection, enabled state, text changes, content sizing, selection notifications, cleanup-safe event/container references, and disabled-tab probing; tab icons are currently unsupported.
- `winui3/src/toga_winui3/widgets/slider.py`: adds native WinUI `Slider` support for value, min/max, discrete tick counts, focus, enabled state, programmatic and user/probe changes, and pointer press/release events.
- `winui3/src/toga_winui3/widgets/splitcontainer.py`: adds native WinUI `Grid` and `Thumb` support for two-pane SplitContainer layout, vertical and horizontal directions, flex-based proportions, explicit splitter moves, zero-size recovery, and synchronous pane size reporting for Toga child layout.
- `winui3/src/toga_winui3/widgets/switch.py`: adds native `CheckBox` support for text, value, enabled, color/background, font-sensitive measurement, focus, press/change events, and WinRT boxed Boolean unboxing with `win32more.unbox_value`.
- `winui3/src/toga_winui3/widgets/selection.py`: adds native `ComboBox` support for list data source updates, duplicate display titles, programmatic and user selection changes, selected-item preservation across source inserts/removals, font-sensitive text measurement, and explicit Python-side title tracking because WinUI/win32more does not reliably expose `ComboBoxItem.Content` after insertion.
- `winui3/src/toga_winui3/widgets/divider.py`: adds a native WinUI `Border` separator with horizontal/vertical intrinsic sizing and inert background styling.
- `winui3/src/toga_winui3/widgets/numberinput.py`: adds native WinUI `NumberBox` support for decimal parsing, raw editing text, empty values, min/max, step, readonly state, focus, increment/decrement, and change events; the backend keeps a Python-side raw text cache because `NumberBox.Text` normalizes partial input such as trailing decimal points.
- `winui3/src/toga_winui3/widgets/passwordinput.py`: adds native WinUI `PasswordBox` support for hidden values, placeholder text, backend-guarded readonly state, focus/change/confirm events, validation, color/background, and font-sensitive measurement inherited from TextInput; text alignment is unsupported by native `PasswordBox`.
- `winui3/src/toga_winui3/widgets/progressbar.py`: adds native WinUI `ProgressBar` support for determinate values, maximum changes, backend-tracked running state, and indeterminate animation through native `IsIndeterminate`.
- `winui3/src/toga_winui3/widgets/scrollcontainer.py`: adds native WinUI `ScrollViewer` support with an owned inner `Canvas` container for Toga layout content, horizontal/vertical enablement, programmatic and simulated manual scrolling, scroll event notifications, content clearing/restoring, background styling, and no-op focus/enabled semantics.
- `winui3/src/toga_winui3/widgets/activityindicator.py`: adds native WinUI `ProgressRing` support with backend-tracked running state, stop-as-hidden behavior that preserves layout, explicit no-op focus/enabled behavior, and fixed 32x32 intrinsic sizing.
- `winui3/src/toga_winui3/widgets/table.py`: adds native WinUI `ListView`-based Table support with headers, row rendering, source updates, selection and activation callbacks, multiple selection, keyboard-probe navigation, programmatic scrolling, column insert/remove/resize behavior, and deprecated ListListener method shims; cell icons and widgets are currently unsupported.
- `winui3/src/toga_winui3/widgets/tree.py`: adds native WinUI `Grid`/`ListView`-based Tree support with headers, backend-managed tree state, expand/collapse, source updates, single and multiple selection, activation callbacks, keyboard/probe navigation, column insert/remove/resize behavior, and deprecated TreeListener/ListListener method shims.
- `winui3/src/toga_winui3/widgets/detailedlist.py`: adds native WinUI `ListView`-based DetailedList support with title/subtitle/icon rows, source updates, selection/deselection, programmatic scrolling, backend action/refresh hooks, and deprecated ListListener method shims.
- `winui3/src/toga_winui3/widgets/webview.py`: adds native XAML `WebView2` support for async initialization, URL loading/clearing, static and large content, user-agent overrides, JavaScript evaluation, cookie retrieval, webview-load events, and sync/async navigation-starting handlers.
- `winui3/src/toga_winui3/container.py`: removes native children by WinUI vector identity instead of by the Python widget-list index, because the hidden staging panel also lives in the native `Children` collection and made content reattachment fail.
- `winui3/pyproject.toml` and `winui3/src/toga_winui3/factory.py`: enable `Image`, `ImageView`, `TextInput`, `MultilineTextInput`, `DateInput`, `TimeInput`, `OptionContainer`, `Slider`, `SplitContainer`, `Switch`, `Selection`, `Divider`, `NumberInput`, `PasswordInput`, `ProgressBar`, `ScrollContainer`, `ActivityIndicator`, `Table`, `Tree`, `DetailedList`, and `WebView` in the backend entry points and factory exports.
- `winui3/tests_backend/images.py`: adds an Image probe and records that this slice supports PNG save/load only.
- `winui3/tests_backend/fonts.py`: adds a WinUI font probe mixin.
- `winui3/tests_backend/probe.py`: makes width and height probes prefer finite assigned layout dimensions before falling back to actual size.
- `winui3/tests_backend/widgets/base.py`: adds color/background probing for `SolidColorBrush`, including reporting fully transparent black as Toga `TRANSPARENT`, and falls back to backend `get_enabled()` for native elements without `IsEnabled`.
- `winui3/tests_backend/widgets/button.py`: probes Button `TextBlock` content, targets that content for font assertions, and verifies native icon image size.
- `winui3/tests_backend/widgets/imageview.py`: probes the `Border`/XAML `Image` split and aspect-preserving stretch mode.
- `winui3/tests_backend/widgets/label.py`: probes the `Border`/`TextBlock` split correctly for text, foreground color, font, and alignment.
- `winui3/tests_backend/widgets/textinput.py`: adds TextInput probing for value, placeholder, readonly, alignment, typing, confirm key, selection, and cursor placement.
- `winui3/tests_backend/widgets/multilinetextinput.py`: adds MultilineTextInput probing for normalized values, document extent, scroll position, typed input, selection, placeholder behavior, and marks mouse-wheel simulation unsupported.
- `winui3/tests_backend/widgets/dateinput.py`: probes native `DatePicker` values, native min/max dates, and day-by-day simulated changes.
- `winui3/tests_backend/widgets/timeinput.py`: probes native `TimePicker` minute-resolution values and simulated minute changes; native min/max limit probing is marked unsupported because WinUI `TimePicker` lacks limit properties.
- `winui3/tests_backend/widgets/optioncontainer.py`: probes native `TabView`, tab selection, disabled tab behavior, no-tab-limit behavior, and records unsupported content-based rehinting and tab icons.
- `winui3/tests_backend/widgets/slider.py`: probes native `Slider` position, tick count, user/probe changes, and press/release events.
- `winui3/tests_backend/widgets/splitcontainer.py`: probes the native `Grid` container, programmatic splitter moves, and records that direction changes intentionally reset rather than preserve the prior split position.
- `winui3/tests_backend/widgets/switch.py`: probes `CheckBox` content text and font target, normalizes zero-width-space empty text, and simulates press via the backend value path because a native WinUI click is not currently injectable in the probe.
- `winui3/tests_backend/widgets/selection.py`: probes `ComboBox` item titles through the backend title cache, selected title, GUI selection changes, content-resize behavior, and xfails text alignment.
- `winui3/tests_backend/widgets/divider.py`: probes the native `Border` separator used by Divider.
- `winui3/tests_backend/widgets/numberinput.py`: probes `NumberBox` value text through the backend raw text cache, readonly state, focus, font-sensitive height, increment/decrement, typed numeric input, and above-maximum redraw clipping; text alignment is xfailed.
- `winui3/tests_backend/widgets/passwordinput.py`: probes `PasswordBox` hidden value behavior, placeholder visibility, backend readonly state, typed password input, and confirm-key handling; text alignment is xfailed.
- `winui3/tests_backend/widgets/progressbar.py`: probes native `ProgressBar` determinate/indeterminate state, native animation flag, and value position.
- `winui3/tests_backend/widgets/scrollcontainer.py`: probes native `ScrollViewer` content extents, scroll positions, content presence, and manual scroll simulation.
- `winui3/tests_backend/widgets/activityindicator.py`: probes native `ProgressRing` animation and hidden state.
- `winui3/tests_backend/widgets/table.py`: probes native `Grid`/`ListView` Table structure, backend-managed row and column state, selection, activation, scroll position, keyboard navigation, disabled icon support, disabled cell widget support, and column resizing.
- `winui3/tests_backend/widgets/tree.py`: probes native `Grid`/`ListView` Tree structure, backend-managed path and expansion state, child counts, selection, activation, peripheral mouse/keyboard behavior, structural-change selection clearing, structural-change collapse behavior, disabled cell widget support, and column sizing.
- `winui3/tests_backend/widgets/detailedlist.py`: probes native `ListView` DetailedList rows, row title/subtitle/icon cache, selection/deselection, scrolling, backend action hooks, and backend refresh hooks.
- `winui3/tests_backend/widgets/webview.py`: probes native XAML `WebView2`, marks Windows content URLs and JavaScript exceptions as unsupported, extracts cookies, and resolves large-content cache file URLs.

## Known Gaps

- TextInput custom fonts and registered font files are unsupported; arbitrary system font names are accepted optimistically.
- Image support is currently PNG-only for load/save/data roundtrips; JPEG, GIF, BMP, and TIFF support need either WinRT encoder/decoder coverage or a deliberately chosen dependency.
- TimeInput is minute-resolution because WinUI `TimePicker` does not expose seconds selection; min/max limits are tracked by the backend rather than enforced by native picker properties.
- OptionContainer tab icons are not exposed by the backend yet, and content-based rehinting is skipped because WinUI window/content minimum-size propagation is not implemented.
- Table cell icons and widgets are not supported; cell widget values emit a warning and render as missing values, and icon values render text only.
- Tree uses native WinUI `ListView` rows with backend-managed expansion rather than the native WinUI `TreeView`, because Toga's Tree requires multi-column cells; Tree cell icons and widgets are not supported, structural insert/delete collapses expansion state, and structural insert/delete clears selection.
- DetailedList actions and refresh are currently exposed through backend/probe hooks, not native swipe, pull-to-refresh, or context-menu UI.
- The backend currently implements and has focused Testbed coverage for 23 widget entry points: ActivityIndicator, Box, Button, DateInput, DetailedList, Divider, ImageView, Label, MultilineTextInput, NumberInput, OptionContainer, PasswordInput, ProgressBar, ScrollContainer, Selection, Slider, SplitContainer, Switch, Table, TextInput, TimeInput, Tree, and WebView.
- The backend still has 2 disabled widget entry points in `winui3/pyproject.toml`: Canvas and MapView.
- WinUI app resource lookup still logs missing `winui3app.xbf` and `winui3app.xaml` resource messages during Testbed startup, although the tests still run.
- Command shortcuts are still not implemented and emit `NotImplementedWarning`.
- WinUI app/window probes still skip or xfail app icon probing, about dialogs, dialogs, menus, keyboard shortcuts/probing, status icons, app-level hide/unhide, document opening by drag, window-management menu behavior, and toolbar probing.
- Widget behavior gaps intentionally recorded in probes: undo/redo are skipped globally by `winui3/tests_backend/widgets/base.py`; Selection, NumberInput, and PasswordInput text alignment xfail because the native controls do not expose a simple alignment surface; WebView content root URLs and JavaScript exceptions are marked unsupported to match Windows/WebView2 behavior.

## Coverage Gap Review

- Latest review date: 2026-05-28 after `tests/widgets/test_detailedlist.py` passed with `15 passed`.
- OptionContainer is now green enough for backend parity tracking; its remaining content-based rehint and tab-icon gaps are recorded above.
- Table is now green with native `ListView` rows and backend-managed table state; its remaining icon/widget cell gaps are recorded above.
- Tree is now green with native `ListView` rows and backend-managed expansion/selection state; its remaining icon/widget/native-TreeView gaps are recorded above.
- DetailedList is now green with native `ListView` rows and backend-managed action/refresh hooks; its remaining native gesture/menu gaps are recorded above.
- Container/navigation/data widgets still need first-pass implementation and probes: Canvas and MapView.
- App/window coverage needs a separate pass after core Salut widgets: command shortcuts, menus, dialogs, app/window icon behavior, status icons, toolbar probing, and document-opening behavior remain mostly skipped/xfail in the WinUI probes.
- WebView now has broad Testbed coverage but not failure-mode coverage for missing WebView2 runtime/initialization failures; keep that as a defensive hardening task rather than blocking Salut use.

## Next Work

1. Implement and verify `Canvas`, or document any unavoidable platform/probe limits.
2. Continue expanding backend parity one widget at a time, recording each Testbed file status here before moving to the next widget.
3. After the Salut-critical widgets are green, start app/window coverage work for menus, dialogs, shortcuts, toolbar probing, status icons, and document-opening behavior.

## Commit Boundary

Milestone commit message for the latest completed slice: `Add WinUI DetailedList support`.
