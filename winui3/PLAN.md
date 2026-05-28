# WinUI 3 Backend Plan

This file is the persistent coordination state for the experimental `toga-winui3` backend. Future agents MUST read this file before planning or editing WinUI 3 backend work, MUST update it whenever new status, blockers, test results, or next tasks are discovered, and MUST update it again before giving a final response so context survives compaction and handoff.

## Current Status

- Last updated: 2026-05-28.
- Active Toga branch: `winui3-backend`.
- Active slice: app/window and coverage-gap triage is underway after the completed widget entry point sweep; native toolbar, menu probing, app icon updates, about dialogs, first-pass generic dialog entry points, document save-as routing, backend-managed status icon behavior, focused window lifecycle behavior, app exit/cursor/current-window cleanup, focused app presentation behavior, full desktop app suite stabilization, native command shortcut conversion/display, screen metadata/image capture, window image capture, Table/Tree select-all keyboard shortcuts, OptionContainer content-based rehinting, and the full window suite are complete, and remaining app/window work focuses on true native fullscreen/presentation parity, document launch/drag behavior, real keyboard accelerator injection coverage, and WinUI-specific DPI coverage.
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
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/canvas/test_canvas.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/widgets/test_mapview.py --tb=short
$env:TOGA_BACKEND='toga_winui3'; uvx --python cpython-3.13.13-windows-aarch64-none briefcase dev --app testbed-winui3 --test -- tests/app/test_screens.py tests/window/test_window.py::test_as_image --tb=short
```

Run this from `C:\Users\jezdez\Code\toga`:

```powershell
uvx ruff check winui3/src/toga_winui3/container.py winui3/src/toga_winui3/fonts.py winui3/src/toga_winui3/images.py winui3/src/toga_winui3/widgets/base.py winui3/src/toga_winui3/widgets/button.py winui3/src/toga_winui3/widgets/label.py winui3/src/toga_winui3/widgets/imageview.py winui3/src/toga_winui3/widgets/textinput.py winui3/src/toga_winui3/widgets/multilinetextinput.py winui3/src/toga_winui3/widgets/dateinput.py winui3/src/toga_winui3/widgets/timeinput.py winui3/src/toga_winui3/widgets/optioncontainer.py winui3/src/toga_winui3/widgets/slider.py winui3/src/toga_winui3/widgets/splitcontainer.py winui3/src/toga_winui3/widgets/switch.py winui3/src/toga_winui3/widgets/selection.py winui3/src/toga_winui3/widgets/divider.py winui3/src/toga_winui3/widgets/numberinput.py winui3/src/toga_winui3/widgets/passwordinput.py winui3/src/toga_winui3/widgets/progressbar.py winui3/src/toga_winui3/widgets/scrollcontainer.py winui3/src/toga_winui3/widgets/activityindicator.py winui3/src/toga_winui3/widgets/table.py winui3/src/toga_winui3/widgets/tree.py winui3/src/toga_winui3/widgets/detailedlist.py winui3/src/toga_winui3/widgets/canvas.py winui3/src/toga_winui3/widgets/mapview.py winui3/src/toga_winui3/widgets/webview.py winui3/src/toga_winui3/factory.py winui3/tests_backend/images.py winui3/tests_backend/fonts.py winui3/tests_backend/probe.py winui3/tests_backend/widgets/base.py winui3/tests_backend/widgets/button.py winui3/tests_backend/widgets/imageview.py winui3/tests_backend/widgets/textinput.py winui3/tests_backend/widgets/multilinetextinput.py winui3/tests_backend/widgets/dateinput.py winui3/tests_backend/widgets/timeinput.py winui3/tests_backend/widgets/optioncontainer.py winui3/tests_backend/widgets/slider.py winui3/tests_backend/widgets/splitcontainer.py winui3/tests_backend/widgets/switch.py winui3/tests_backend/widgets/selection.py winui3/tests_backend/widgets/divider.py winui3/tests_backend/widgets/numberinput.py winui3/tests_backend/widgets/passwordinput.py winui3/tests_backend/widgets/progressbar.py winui3/tests_backend/widgets/scrollcontainer.py winui3/tests_backend/widgets/activityindicator.py winui3/tests_backend/widgets/table.py winui3/tests_backend/widgets/tree.py winui3/tests_backend/widgets/detailedlist.py winui3/tests_backend/widgets/canvas.py winui3/tests_backend/widgets/mapview.py winui3/tests_backend/widgets/webview.py
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
- `tests/widgets/test_optioncontainer.py` previously passed with `8 passed, 1 skipped`; this has been superseded by the later `9 passed` result with content-based rehinting enabled.
- `tests/widgets/test_optioncontainer.py` now passes with `9 passed`; content-based rehinting is enabled after fixing off-screen tab minimum-size propagation and the WinUI probe wait loop.
- `tests/widgets/test_table.py` passed with `26 passed`.
- `tests/widgets/test_tree.py` passed with `25 passed`.
- `tests/widgets/test_table.py` and `tests/widgets/test_tree.py` passed together with `51 passed` after enabling WinUI Table and Tree keyboard shortcut probes for select-all behavior.
- `tests/widgets/test_detailedlist.py` passed with `15 passed`.
- `tests/widgets/canvas/test_canvas.py` passed with `14 passed, 31 skipped`; the skipped tests are the visual raster reference suite because WinUI Canvas drawing is not implemented yet.
- `tests/widgets/test_mapview.py` passed with `7 passed`.
- `tests/app/test_app.py::test_main_window_toolbar` and `tests/window/test_window.py::test_secondary_window_toolbar` passed together with `2 passed`.
- `tests/app/test_app.py` passed with `10 passed`.
- `tests/app/test_dialogs.py` passed with `28 passed`; this validates dialog construction/result plumbing through the WinUI backend and probes, not fully native user-driven picker UI yet.
- `tests/app/test_document_app.py` passed with `7 passed, 2 xfailed`; the xfails are initial document launch and document opening by drag. This suite currently needs a workspace-local `TMP`/`TEMP` override on this machine because pytest sometimes gets `WinError 5` under `AppData\Local\Temp\pytest-of-jezdez`.
- `tests/test_statusicons.py` passed with `4 passed`; this validates Toga status icon set state, menu grouping, add/remove, and action dispatch, not native Windows notification-area UI yet.
- A focused window lifecycle/current-window slice passed with `14 passed`: `tests/window/test_window.py::test_title`, `test_secondary_window`, `test_secondary_window_with_args`, `test_secondary_window_with_content`, `test_secondary_window_cleanup`, `test_secondary_window_toolbar`, `test_non_resizable`, `test_non_closable`, `test_non_minimizable`, `test_visibility`, `test_move_and_resize`, `test_window_state_change[MainWindow-second_window_kwargs0-WindowState.NORMAL-WindowState.MINIMIZED]`, `test_window_state_change[MainWindow-second_window_kwargs0-WindowState.NORMAL-WindowState.MAXIMIZED]`, and `tests/app/test_desktop.py::test_current_window`.
- `tests/app/test_dialogs.py` still passed with `28 passed` after adding dialog setup support to `WindowProbe`; this remains deterministic dialog result plumbing, not full native dialog focus probing.
- `tests/window/test_window.py` passed with `58 passed`; WinUI fullscreen and presentation state tests are now stable by using the native overlapped/maximized presenter plus Toga state flags, not the crashing native `FullScreen` presenter.
- `tests/app/test_desktop.py` was measured after the window-state slice and before the app cleanup/presentation slices with `4 passed, 22 failed, 8 xfailed`; rerun the full desktop app suite after the system-DPI path is handled, because the targeted app failures below have since been fixed.
- `tests/app/test_desktop.py::test_menu_exit`, `tests/app/test_desktop.py::test_show_hide_cursor`, and `tests/app/test_desktop.py::test_current_window` passed together with `3 passed`; menu Exit now exercises the real WinUI menu command path, cursor hide/show tracks the Win32 cursor display count locally, and current-window lookup ignores hidden windows.
- `tests/app/test_desktop.py::test_presentation_mode` and `tests/app/test_desktop.py::test_presentation_mode_exit_on_window_state_change` passed together with `4 passed`; app presentation now restores the pre-presentation screen, changing any other window state exits app presentation mode, and windows get an immediate first layout after `show()` so the Testbed's pre-redraw size snapshot is stable.
- A combined focused app desktop slice passed with `8 passed`: `test_menu_exit`, `test_show_hide_cursor`, `test_current_window`, `test_presentation_mode`, `test_window_presentation_exit_on_another_window_presentation`, and all three `test_presentation_mode_exit_on_window_state_change` cases.
- `tests/app/test_desktop.py` now passes for WinUI with `11 passed, 23 xfailed`; the xfails are the existing unsupported WinUI app-level hide/window-management menu/edit no-focus behaviors plus the explicitly WinForms-only system-DPI test cases.
- `tests/app/test_desktop.py::test_app_level_menu_hide` followed by `tests/app/test_desktop.py::test_presentation_mode` passed as `1 passed, 1 xfailed` after window cleanup stopped retaining a native probe reference through close and programmatic close switched to XAML `Window.Close()`.
- `tests/window/test_window.py` still passed with `58 passed` after the app presentation changes to window state and first-show layout.
- `tests/window/test_window.py` still passed with `58 passed` after switching programmatic WinUI window close from `AppWindow.Destroy()` to native XAML `Window.Close()`.
- `tests/test_keys.py`, `tests/app/test_app.py::test_menu_items`, and `tests/app/test_app.py::test_system_menus` passed together with `27 passed`; this validates WinUI key conversion round-trips, menu shortcut display text, and system menu shortcut setup.
- `tests/test_keys.py`, full `tests/app/test_app.py`, and `tests/app/test_desktop.py::test_menu_exit` passed together with `36 passed`; native menu command wiring still works after adding `KeyboardAccelerator` objects, and the previous `Command shortcuts` `NotImplementedWarning` no longer appears.
- `tests/window/test_window.py::test_as_image` passed with `1 passed`; WinUI `Window.as_image()` now captures a native window-client screenshot and the probe accounts for screen scale.
- `tests/window/test_window.py` still passed with `58 passed` after enabling WinUI window screenshot capture.
- `tests/app/test_screens.py` and `tests/window/test_window.py::test_as_image` passed together with `5 passed`; WinUI screen names, origins, sizes, screen screenshots, and the refactored window screenshot path are covered.
- `tests/widgets/test_optioncontainer.py` and `tests/window/test_window.py` passed together with `67 passed`; this covers OptionContainer content-based rehinting plus the shared window content-size growth path.
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
- `winui3/src/toga_winui3/widgets/canvas.py`: adds native WinUI `CanvasControl` support for layout, background styling, no-op focus/enabled behavior, resize callbacks, mouse/pointer handler dispatch through the probe, basic text measurement, drawing-action dispatch through a no-op context, and PNG export of the current canvas bounds/background; actual drawing/rasterization is not implemented.
- `winui3/src/toga_winui3/widgets/mapview.py`: adds a native WinUI host for MapView with deterministic location, zoom, pin add/update/remove, pin selection callbacks, focus tracking, and OSM-compatible zoom-span math; actual map tiles are not rendered.
- `winui3/src/toga_winui3/widgets/webview.py`: adds native XAML `WebView2` support for async initialization, URL loading/clearing, static and large content, user-agent overrides, JavaScript evaluation, cookie retrieval, webview-load events, and sync/async navigation-starting handlers.
- `winui3/src/toga_winui3/command.py`: updates WinUI command enablement to use native XAML `IsEnabled` with the core-computed enabled value, which applies to both menu flyout items and toolbar buttons.
- `winui3/src/toga_winui3/keys.py`: adds WinUI key and modifier conversion for letters, digits, function keys, common punctuation, special keys, numpad digits/operators, and shifted display values using WinUI `VirtualKey` and `VirtualKeyModifiers`.
- `winui3/src/toga_winui3/command.py`: adds native WinUI `KeyboardAccelerator` support for menu commands with shortcut display text, enabled-state propagation, and accelerator invocation through the command action.
- `winui3/src/toga_winui3/libs/screenshot.py`: provides shared Win32 GDI screenshot capture and PNG encoding for WinUI windows and screens.
- `winui3/src/toga_winui3/dialogs.py`: adds first-pass dialog backend classes for Info, Question, Confirm, Error, StackTrace, SaveFile, OpenFile, and SelectFolder dialogs so dialog objects construct and Testbed probes can drive deterministic results.
- `winui3/src/toga_winui3/app.py`: updates existing windows when the app icon changes so `app.icon = ...` takes effect after startup, and adds a native WinUI `ContentDialog` About dialog.
- `winui3/src/toga_winui3/app.py`: makes cursor hide/show idempotent using the backend cursor-visible flag, and returns only visible windows from `get_current_window()` so hidden windows cannot remain current through cached or activated WinUI state.
- `winui3/src/toga_winui3/container.py`: removes native children by WinUI vector identity instead of by the Python widget-list index, because the hidden staging panel also lives in the native `Children` collection and made content reattachment fail, and exposes an optional refresh callback so root window containers can respond to content minimum-size changes.
- `winui3/src/toga_winui3/container.py`: uses temporary explicit native dimensions as a fallback while a just-shown WinUI window has bounds but not yet a nonzero XAML `ActualSize`, allowing the first Toga layout pass to be measured synchronously.
- `winui3/src/toga_winui3/screens.py`: reports screen height from the native `OuterBounds.Height` instead of width, and implements `Screen.get_image_data()` using the shared screenshot helper.
- `winui3/src/toga_winui3/widgets/optioncontainer.py`: propagates explicit off-screen tab content width/height into the OptionContainer intrinsic size and refreshes the root window content when tab content minimums change, allowing content-based rehinting to resize the window.
- `winui3/src/toga_winui3/window.py`: adds native WinUI `CommandBar` toolbar support with `AppBarButton`, `AppBarSeparator`, labels, tooltips, icons, command enablement, automatic group separators, removal/clearing behavior, probe activation hooks, stores/applies the current app icon for each window, activates windows when shown, helps the app maintain a deterministic current-window value, routes user close attempts through cancellable `AppWindow.Closing`, honors explicit close through native XAML `Window.Close()`, clears current-window state on hide/close, reports outer `AppWindow` size instead of client bounds, grows windows when content minimum size exceeds the current client area, preserves logical size while minimized, suppresses resize callbacks for normal/minimized state changes, models fullscreen/presentation state transitions with the native overlapped/maximized presenter plus Toga state flags, hides WinUI menu/toolbar chrome during presentation mode, restores the pre-presentation screen on exit, exits app presentation when another window state changes, runs an immediate first layout after showing a window, and detaches native/content references on close so closed windows can be garbage-collected.
- `winui3/src/toga_winui3/window.py`: caps window chrome-size deltas at zero when content is already wider or taller than the current window, so oversized content minimums can grow the window instead of being cancelled by negative deltas.
- `winui3/src/toga_winui3/window.py`: adds `Window.get_image_data()` by capturing the WinUI window client area with Win32 GDI, converting BGRA pixels to PNG, and returning real screenshot bytes for `Window.as_image()`.
- `winui3/src/toga_winui3/statusicons.py`: adds backend-managed status icon state for menu and button status icons, including menu grouping, separators, primary menu fallback, command dispatch, add/remove state, and unknown-group validation.
- `winui3/pyproject.toml` and `winui3/src/toga_winui3/factory.py`: enable every current Toga widget entry point in the backend entry points and factory exports, including `Canvas`, `DetailedList`, `MapView`, and `Tree`.
- `winui3/tests_backend/images.py`: adds an Image probe and records that this slice supports PNG save/load only.
- `winui3/tests_backend/fonts.py`: adds a WinUI font probe mixin.
- `winui3/tests_backend/probe.py`: makes width and height probes prefer finite assigned layout dimensions before falling back to actual size.
- `winui3/tests_backend/probe.py`: compares screenshot sizes in physical pixels using the active WinUI screen scale and a one-pixel compositor rounding tolerance.
- `winui3/tests_backend/probe.py`: gives `redraw(wait_for=...)` a default one-second wait budget so WinUI async layout conditions are actually polled even when individual tests do not pass an explicit delay.
- `winui3/tests_backend/screens.py`: adds Screen probing for screen metadata and `Screen.as_image()` coverage.
- `winui3/tests_backend/widgets/base.py`: adds color/background probing for `SolidColorBrush`, including reporting fully transparent black as Toga `TRANSPARENT`, and falls back to backend `get_enabled()` for native elements without `IsEnabled`.
- `winui3/tests_backend/widgets/button.py`: probes Button `TextBlock` content, targets that content for font assertions, and verifies native icon image size.
- `winui3/tests_backend/widgets/imageview.py`: probes the `Border`/XAML `Image` split and aspect-preserving stretch mode.
- `winui3/tests_backend/widgets/label.py`: probes the `Border`/`TextBlock` split correctly for text, foreground color, font, and alignment.
- `winui3/tests_backend/widgets/textinput.py`: adds TextInput probing for value, placeholder, readonly, alignment, typing, confirm key, selection, and cursor placement.
- `winui3/tests_backend/widgets/multilinetextinput.py`: adds MultilineTextInput probing for normalized values, document extent, scroll position, typed input, selection, placeholder behavior, and marks mouse-wheel simulation unsupported.
- `winui3/tests_backend/widgets/dateinput.py`: probes native `DatePicker` values, native min/max dates, and day-by-day simulated changes.
- `winui3/tests_backend/widgets/timeinput.py`: probes native `TimePicker` minute-resolution values and simulated minute changes; native min/max limit probing is marked unsupported because WinUI `TimePicker` lacks limit properties.
- `winui3/tests_backend/widgets/optioncontainer.py`: probes native `TabView`, tab selection, disabled tab behavior, no-tab-limit behavior, content-based rehinting, and records unsupported tab icons.
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
- `winui3/tests_backend/widgets/table.py`: enables shared keyboard shortcut coverage for select-all behavior, including multi-select tables.
- `winui3/tests_backend/widgets/tree.py`: probes native `Grid`/`ListView` Tree structure, backend-managed path and expansion state, child counts, selection, activation, peripheral mouse/keyboard behavior, structural-change selection clearing, structural-change collapse behavior, disabled cell widget support, and column sizing.
- `winui3/tests_backend/widgets/tree.py`: enables shared keyboard shortcut coverage for select-all behavior, including multi-select trees.
- `winui3/tests_backend/widgets/detailedlist.py`: probes native `ListView` DetailedList rows, row title/subtitle/icon cache, selection/deselection, scrolling, backend action hooks, and backend refresh hooks.
- `winui3/tests_backend/widgets/canvas.py`: probes native `CanvasControl`, mouse/alternate mouse handler dispatch, and explicit visual-reference skips until Win2D drawing/raster export is implemented.
- `winui3/tests_backend/widgets/mapview.py`: probes the native WinUI MapView host, location/zoom math, pin count, pin selection callbacks, and asynchronous map-wait no-ops.
- `winui3/tests_backend/widgets/webview.py`: probes native XAML `WebView2`, marks Windows content URLs and JavaScript exceptions as unsupported, extracts cookies, and resolves large-content cache file URLs.
- `winui3/tests_backend/app.py`: adds native WinUI menu probing for system menus, nested menu order, enabled state, visit-homepage activation, separators, the backend-specific formal name, app icon update assertions, About dialog activation/closing, deterministic dialog focus tolerance, and backend-managed status icon probing.
- `winui3/tests_backend/app.py`: routes menu Exit through the native WinUI menu-command probe rather than directly calling unconditional `app.exit()`, preserving `App.on_exit` handling.
- `winui3/tests_backend/app.py`: enables WinUI key conversion coverage through the shared Testbed key suite and validates shortcut display text for special menu command cases.
- `winui3/tests_backend/dialogs.py`: adds deterministic dialog result setup for the Testbed dialog suite.
- `winui3/tests_backend/window.py`: drives user-close, minimize, and restore through Win32 messages against the WinUI HWND, adds deterministic dialog setup support for window-modal dialog tests, and probes the focused window lifecycle behavior covered by the latest window slice.
- `winui3/tests_backend/window.py`: releases the probe's native window reference before cleanup close so xfailed tests that leave extra windows behind do not trigger delayed win32more COM release warnings after the native window has been closed.
- `winui3/tests_backend/window.py`: enables `supports_as_image` now that WinUI window screenshots pass the shared Testbed assertion.
- `testbed/tests/app/test_desktop.py`: now explicitly xfails `test_system_dpi_change` unless the active backend is `toga_winforms`, because that test imports `toga_winforms.libs.shcore` and .NET `SystemEvents` and is not a generic Windows-backend DPI contract.

## Known Gaps

- TextInput custom fonts and registered font files are unsupported; arbitrary system font names are accepted optimistically.
- Image support is currently PNG-only for load/save/data roundtrips; JPEG, GIF, BMP, and TIFF support need either WinRT encoder/decoder coverage or a deliberately chosen dependency.
- TimeInput is minute-resolution because WinUI `TimePicker` does not expose seconds selection; min/max limits are tracked by the backend rather than enforced by native picker properties.
- OptionContainer tab icons are not exposed by the backend yet; content-based rehinting is now implemented and covered.
- Table cell icons and widgets are not supported; cell widget values emit a warning and render as missing values, and icon values render text only.
- Tree uses native WinUI `ListView` rows with backend-managed expansion rather than the native WinUI `TreeView`, because Toga's Tree requires multi-column cells; Tree cell icons and widgets are not supported, structural insert/delete collapses expansion state, and structural insert/delete clears selection.
- DetailedList actions and refresh are currently exposed through backend/probe hooks, not native swipe, pull-to-refresh, or context-menu UI.
- Canvas uses native WinUI `CanvasControl` for hosting but does not yet render Toga drawing actions with Win2D; the visual reference tests are skipped, and `get_image_data()` currently exports only the canvas background/bounds rather than drawn content.
- MapView uses a native WinUI host with backend-managed state, not a real map tile control; there is no map tile rendering, pan/gesture support, provider integration, geolocation, or platform map service bridge yet.
- The backend currently implements and has focused Testbed coverage for 25 widget entry points: ActivityIndicator, Box, Button, Canvas, DateInput, DetailedList, Divider, ImageView, Label, MapView, MultilineTextInput, NumberInput, OptionContainer, PasswordInput, ProgressBar, ScrollContainer, Selection, Slider, SplitContainer, Switch, Table, TextInput, TimeInput, Tree, and WebView.
- The backend has no disabled widget entry points left in `winui3/pyproject.toml`; the latest focused scan of `winui3/pyproject.toml` and `winui3/src/toga_winui3/factory.py` confirmed every current widget entry point is enabled.
- WinUI app resource lookup still logs missing `winui3app.xbf` and `winui3app.xaml` resource messages during Testbed startup, although the tests still run.
- Command shortcuts now have first-pass native WinUI menu `KeyboardAccelerator` objects, shortcut display text, and key-conversion coverage, but the Testbed currently round-trips conversion rather than injecting real OS keypresses to prove accelerator invocation end-to-end.
- WinUI app/window probes still xfail app-level hide/unhide, document opening by drag, initial document launch, and window-management menu behavior; the window-management menu xfails currently match the stable WinForms/GTK/Qt Windows/Linux menu-surface limitation rather than a proved WinUI-specific impossibility, and WinUI still needs its own DPI-change coverage because the current Testbed DPI test is WinForms-specific.
- WinUI fullscreen/presentation tests are stable, but this is not true native fullscreen parity yet: the backend intentionally avoids `AppWindowPresenterKind.FullScreen` because it caused a native access violation in Testbed, and it also avoids `OverlappedPresenter.SetBorderAndTitleBar(False, False)` because title-bar restoration changed the normal client size on plain windows.
- Widget behavior gaps intentionally recorded in probes: undo/redo are skipped globally by `winui3/tests_backend/widgets/base.py`; Selection, NumberInput, and PasswordInput text alignment xfail because the native controls do not expose a simple alignment surface; WebView content root URLs and JavaScript exceptions are marked unsupported to match Windows/WebView2 behavior.

## Coverage Gap Review

- Latest review date: 2026-05-28 after OptionContainer plus the full window suite passed with `67 passed`.
- Latest mechanical gap scan: 2026-05-28 after commit `0ad6911ba Add WinUI MapView support`; the WinUI widget entry point list is fully enabled and the remaining skips/xfails are app/window probe gaps, native platform limitations, or the two explicit major widget parity gaps.
- OptionContainer now has content-based rehint coverage; its remaining tab-icon gap is recorded above.
- Table is now green with native `ListView` rows and backend-managed table state; its remaining icon/widget cell gaps are recorded above.
- Tree is now green with native `ListView` rows and backend-managed expansion/selection state; its remaining icon/widget/native-TreeView gaps are recorded above.
- DetailedList is now green with native `ListView` rows and backend-managed action/refresh hooks; its remaining native gesture/menu gaps are recorded above.
- Canvas has first-pass host/event/export coverage but not visual drawing parity; implement Win2D drawing and image export before considering Canvas complete.
- MapView is green at the Toga state/probe level but is not a real map renderer; implement a native or WebView-backed map provider before considering MapView complete.
- All current widget entry points have first-pass WinUI implementations, backend probes, and focused Testbed results; the remaining work is quality/parity gaps, app/window skipped coverage, and full-backend regression coverage.
- App probe key conversion coverage now runs through `tests/test_keys.py`; app probe xfails remain for app-level unhide, app-level hide menu behavior, window-management menu actions, initial document support, and document opening by drag, and physical OS keypress injection for native accelerators is still not covered.
- Native toolbar support and toolbar probe activation are now implemented and covered by focused Testbed tests; non-closable behavior is implemented by cancelling user close requests, but `supports_closable` remains false because WinUI does not expose a simple title-bar close-button removal flag through the current backend; `supports_as_image` is now true.
- Native menu probing, command activation, shortcut display text, and key conversion are now implemented and covered by the app/key Testbed suites; physical accelerator invocation through synthetic OS input is still a coverage gap.
- Generic dialogs now have construction/result plumbing and full Testbed dialog coverage, but most dialog classes are not yet real native WinUI UI; replace the deterministic first-pass backend with native `ContentDialog`, `FileSavePicker`, `FileOpenPicker`, and folder picker implementations before claiming production dialog parity.
- Status icons now have backend-managed state and full Testbed status icon coverage, but they do not create real Windows notification-area icons; investigate Windows App SDK/AppNotification or Win32 `Shell_NotifyIcon` integration for production parity.
- Widget probe gaps from the latest scan are concentrated in custom fonts, undo/redo, Canvas visual rendering, MultilineTextInput mouse-wheel simulation, OptionContainer icons, Selection/NumberInput/PasswordInput text alignment, Table and Tree cell widgets/icons plus remaining boundary-shortcut limits, TimeInput seconds/native limits, and WebView content root URLs/JavaScript exception behavior.
- WebView now has broad Testbed coverage but not failure-mode coverage for missing WebView2 runtime/initialization failures; keep that as a defensive hardening task rather than blocking Salut use.

## Next Work

1. Investigate true fullscreen/presentation parity without reintroducing the native `FullScreen` presenter crash or the title-bar restoration bug from `SetBorderAndTitleBar(False, False)`.
2. Implement or explicitly justify the remaining app/window probe gaps: physical keyboard accelerator invocation, document launch/drag behavior, and window-management menu behavior.
3. Replace the first-pass deterministic dialog backend with real native WinUI dialogs and pickers while preserving the passing Testbed dialog contract.
4. Replace backend-managed status icon state with real Windows notification-area integration while preserving the passing Testbed status icon contract.
5. Replace Canvas no-op drawing with Win2D-backed rendering and real `get_image_data()` output so the visual reference tests can run instead of skipping.
6. Replace MapView's backend-managed placeholder with a real map provider/control, or document a deliberate WebView-backed provider plan if no native WinUI map control is viable.
7. Revisit widget limitation probes after the app/window pass and separate hard native limits from missing implementation work.

## Commit Boundary

Milestone commit message for the latest completed implementation slice: `Enable WinUI option content rehinting`.
