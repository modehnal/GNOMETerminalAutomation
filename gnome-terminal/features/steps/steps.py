#!/usr/bin/env python3
"""
Main file where the python code is located for execution via behave.
"""

from time import sleep
from behave import step  # pylint: disable=no-name-in-module
from dogtail.rawinput import (  # pylint: disable=import-error
    keyCombo,
    typeText,
    click,
    pressKey,
)
from qecore.utility import run, Tuple

# Find a better solution how to get the precoded steps here instead of linter disable.
from qecore.common_steps import *  # pylint: disable=unused-wildcard-import,wildcard-import

from qecore.logger import Logging

LOGGING = Logging()


@step("Make sure window is focused for wayland testing")
def wait_some_ammount_of_time(context) -> None:
    """
    Making sure window is focused for wayland testing.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    # Attempt to prevent race conditions.
    sleep(2)

    if context.sandbox.session_type == "wayland":
        context.terminal.instance.children[0].click()


@step("Make sure Menubar is showing")
def make_sure_menubar_is_showing(context) -> None:
    """
    Make sure Menubar is showing.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    menubar = context.terminal.instance.child(roleName="menu bar")
    for _ in range(10):
        if not (menubar.showing and menubar.visible):
            terminal_frame = context.terminal.instance.child(roleName="frame")
            sleep(1)
            terminal_frame.click(3)
            try:
                context.execute_steps(
                    '* Left click "Show Menubar" "check menu item" in "terminal"'
                )
            except Exception:  # pylint: disable=broad-except
                pressKey("Esc")


@step("Expand Change profile menu")
def expand_menu_workaround(context) -> None:
    """
    Expand Change profile menu.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    if context.sandbox.session_type == "x11":
        context.execute_steps('* Mouse over "Change Profile" "menu" in "terminal"')
    else:  # context.sandbox.session_type == "wayland"
        context.execute_steps('* Left click "Change Profile" "menu" in "terminal"')


@step('Open toggle menu of profile: "{profile_name}"')
def open_new_profile_toggle_menu(context, profile_name) -> None:
    """
    Open toggle menu of given profile.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile_name: Profile name.
    :type profile_name: str
    """

    context.preferences.instance.child(profile_name).parent.child(
        "Menu", "toggle button"
    ).click()


@step('Execute in terminal: "{command}"')
def execute_command(context, command) -> None:  # pylint: disable=unused-argument
    """
    Execute command in terminal.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param command: Command to execute.
    :type command: str
    """

    typeText(command)
    pressKey("Enter")


@step('Select option in row: "{color_row}" and column: "{color_column}"')
def select_option_in_row_and_column(context, color_row, color_column) -> None:
    """
    Select option in a given row and column.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param color_row: Color row.
    :type color_row: str

    :param color_column: Color column.
    :type color_column: str
    """

    color_setting = {
        ("Default color:", "Text"): 6,
        ("Default color:", "Background"): 5,
        ("Bold color:", "Text"): 4,
        ("Cursor color:", "Text"): 3,
        ("Cursor color:", "Background"): 2,
        ("Highlight color:", "Text"): 1,
        ("Highlight color:", "Background"): 0,
    }

    menu_target = context.preferences.instance.child("Text and Background Color").parent
    color_target = menu_target.findChildren(
        lambda x: x.roleName == "push button" and x.showing
    )
    index = color_setting[color_row, color_column]
    color_target[index].click()

    choose_terminal_dialog = context.preferences.instance.findChild(
        lambda x: "Choose Terminal" in x.name and x.roleName == "dialog"
    )

    for _ in range(5):
        if not choose_terminal_dialog.sensitive:
            LOGGING.info(
                f"Dialog '{choose_terminal_dialog.name}' is not sensitive yet."
            )
            sleep(1)
        else:
            break


@step('Change color to: "{color_hex_value}"')
def change_color_to(context, color_hex_value) -> None:
    """
    Change color to given color.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param color_hex_value: Color hex value.
    :type color_hex_value: str
    """

    context.terminal.instance.child("Color Name", "text").click()
    keyCombo("<Ctrl><A>")
    typeText(color_hex_value)


@step('Set spin button to: "{set_value}"')
def set_spin_button_to(context, set_value) -> None:
    """
    Set value to spin button.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param set_value: Set value to spin button.
    :type set_value: str
    """

    target = context.preferences.instance.findChildren(
        lambda x: x.name == ""
        and x.roleName == "spin button"
        and x.sensitive
        and x.showing
    )[0]

    click(
        target.position[0] + target.size[0] / 2 - 10,
        target.position[1] + target.size[1] / 2,
    )

    target.click()
    keyCombo("<Ctrl><A>")
    typeText(set_value)


@step('The profile option: "{color_opt}" is set to "{exp_value}" in dconf')
@step('The profile option: "{color_opt}" is {negation} set to "{exp_value}" in dconf')
def profile_option_is_set_to(  # pylint: disable=unused-argument
    context,
    color_opt,
    exp_value,
    negation=None,
) -> None:
    """
    Verify that the profile option given is set in dconf.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param color_opt: Given color option.
    :type color_opt: str

    :param exp_value: Expected value in dconf.
    :type exp_value: str

    :param negation: Negating the verification result, defaults to None
    :type negation: str, optional
    """

    # Prevent race on slower machines.
    sleep(3)

    dconf = "/org/gnome/terminal/legacy/profiles:/"

    profile_id = run(f"dconf list {dconf}")
    profile_id = profile_id.strip("\n")

    stored_value = run(f"dconf read {dconf}{profile_id}{color_opt}")
    stored_value = stored_value.strip("\n")

    if negation:
        assert exp_value not in stored_value, " ".join(
            (
                "Expected value does not differ from actually stored value!",
                f"'{exp_value}' == '{stored_value}'",
            )
        )

    else:
        assert exp_value in stored_value, " ".join(
            (
                "Expected value differs from actually stored value! ",
                f"'{exp_value}' != '{stored_value}'",
            )
        )


@step('Set "{option}" to "{value}" under: "{under_given_menu}"')
def set_values_to_combo_box(context, option, value, under_given_menu) -> None:
    """
    Set values to combo box.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param option: Option to set.
    :type option: str

    :param value: Value to set the combo box to.
    :type value: str

    :param under_given_menu: Find the specific menu in a11y.
    :type under_given_menu: str
    """

    menu_target = context.preferences.instance.child(under_given_menu).parent
    item_target = menu_target.child(option, "label").parent

    for _ in range(3):
        pressKey("Esc")
        try:
            combo_box_target = item_target.child(roleName="combo box")
            combo_box_target.click()
            sleep(1)
            context.execute_steps(
                f'* Left click "{value}" "menu item" in "preferences"'
            )
            break
        except Exception:  # pylint: disable=broad-except
            LOGGING.info("Combo box presumably failed to open, retrying.")
            sleep(1)


@step("Reset settings")
def reset_settings(context) -> None:
    """
    Reset settings.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    reset_buttons = context.terminal.instance.findChildren(
        lambda x: x.name == "Reset" and x.roleName == "push button" and x.showing
    )

    for reset in reset_buttons:
        reset.click()

    context.execute_steps("* Close preferences")


@step('Set cursor to "{set_cursor}"')
def set_cursor_to(context, set_cursor) -> None:
    """
    Set cursor to chosen one.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param set_cursor: Cursor selected.
    :type set_cursor: str
    """

    cursor = context.preferences.instance.findChild(
        lambda x: x.name == "I-Beam" and x.roleName == "menu item"
    ).parent.parent
    cursor.click()

    context.execute_steps(f'* Left click "{set_cursor}" "menu item" in "preferences"')
    context.execute_steps("* Close preferences")


@step('Profile named "{profile}" is selected as default')
def profile_named_is_selected_as_default(context, profile) -> None:
    """
    Verify that the given profile is selected as default.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile: Given profile.
    :type profile: str
    """

    context.execute_steps('* Left click "Terminal" "menu" in "terminal"')
    context.execute_steps('* Left click "Change Profile" "menu" in "terminal"')
    context.execute_steps(
        f'* Item "{profile}" "radio menu item" is "checked" in "terminal"'
    )
    pressKey("Esc")


@step('Profile named "{profile}" is not selected as default')
def profile_named_is_not_selected_as_default(context, profile) -> None:
    """
    Verify that the given profile is not selected as default.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile: Given profile.
    :type profile: str
    """

    context.execute_steps('* Left click "Terminal" "menu" in "terminal"')
    context.execute_steps('* Left click "Change Profile" "menu" in "terminal"')
    context.execute_steps(
        f'* Item "{profile}" "radio menu item" is not "showing" in "terminal"'
    )
    pressKey("Esc")


@step('Profile named "{profile}" is showing')
def profile_named_is_showing(context, profile) -> None:
    """
    Verify that the profile is showing.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile: Given profile.
    :type profile: str
    """

    context.execute_steps('* Left click "Terminal" "menu" in "terminal"')
    context.execute_steps('* Left click "Change Profile" "menu" in "terminal"')
    context.execute_steps(
        f'* Item "{profile}" "radio menu item" is "showing" in "terminal"'
    )
    pressKey("Esc")


@step('Profile named "{profile}" is not showing')
def profile_named_is_not_showing(context, profile) -> None:
    """
    Verify that the profile is not showing.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile: Given profile.
    :type profile: str
    """

    context.execute_steps('* Left click "Terminal" "menu" in "terminal"')
    context.execute_steps('* Left click "Change Profile" "menu" in "terminal"')
    context.execute_steps(
        f'* Item "{profile}" "radio menu item" is not "showing" in "terminal"'
    )
    pressKey("Esc")


@step('Terminal size is set as columns: "{columns_size}" and rows: "{rows_size}"')
def terminal_size_is_set_as_columns_and_rows(context, columns_size, rows_size) -> None:
    """
    Terminal size is set as columns and rows.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param columns_size: Given column size.
    :type columns_size: str

    :param rows_size: Given row size.
    :type rows_size: str
    """

    target_columns = context.preferences.instance.findChild(
        lambda x: x.name == "columns" and x.roleName == "label"
    ).parent.children[0]

    target_rows = context.preferences.instance.findChild(
        lambda x: x.name == "rows" and x.roleName == "label"
    ).parent.children[0]

    assert str(columns_size) == str(target_columns.text), "".join(
        (
            f"\nColumn expected: {columns_size}",
            f"\nActual column: {target_columns.text}",
        )
    )

    assert str(rows_size) == str(target_rows.text), "".join(
        (f"\nColumn expected: {rows_size}", f"\nActual column: {target_rows.text}")
    )

    context.execute_steps("* Close preferences")


@step('Create profile named "{profile}"')
def create_profile_names(context, profile) -> None:
    """
    Create profile with specific name.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile: Name of the new profile.
    :type profile: str
    """

    context.execute_steps("* Open preferences")

    # If profile is already created, skip the rest
    existing_profile = context.preferences.instance.findChildren(
        lambda x: x.name == profile and x.roleName == "label"
    )
    if existing_profile != []:
        context.execute_steps("* Close preferences")
        return

    anchor_point = (
        context.preferences.instance.child("Unnamed")
        .parent.child("Menu", "toggle button")
        .position
    )
    add_new_profile = (anchor_point[0] + 17, anchor_point[1] - 50 + 17)
    click(*(add_new_profile))

    new_profile_dialog = context.preferences.instance.child("New Profile").parent
    text_field = new_profile_dialog.child(roleName="text")
    text_field.text = profile

    context.execute_steps('* Left click "Create" "push button" in "preferences"')
    context.execute_steps("* Close preferences")


@step('Delete profile named "{profile}"')
def delete_profile_named(context, profile) -> None:
    """
    Delete profile.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile: Profile to be deleted.
    :type profile: str
    """

    if context.sandbox.session_type == "wayland":
        sleep(5)

    context.execute_steps("* Open preferences")
    context.execute_steps(f'* Left click "{profile}" "label" in "preferences"')
    context.execute_steps(f'* Open toggle menu of profile: "{profile}"')
    pressKey("Down")
    pressKey("Down")
    pressKey("Enter")
    context.execute_steps('* Left click "Delete" "push button" in "preferences"')
    context.execute_steps("* Close preferences")


@step('Profile named "{profile}" exists')
def profile_named_exists(context, profile) -> None:
    """
    Verify that the given profile exists.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile: Given profile.
    :type profile: str
    """

    context.execute_steps("* Open preferences")
    context.execute_steps(f'* Item "{profile}" "label" is "showing" in "preferences"')
    context.execute_steps("* Close preferences")


@step('Profile named "{profile}" does not exist')
def profile_named_does_not_exist(context, profile) -> None:
    """
    Verify that the given profile does not exists.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param profile: Given profile.
    :type profile: str
    """

    context.execute_steps("* Open preferences")
    context.execute_steps(
        f'* Item "{profile}" "label" is not "showing" in "preferences"'
    )
    context.execute_steps("* Close preferences")


@step('Terminal contains string "{tested_string}"')
def terminal_contains_string(context, tested_string) -> None:
    """
    Verify that the terminal contains given string.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param tested_string: String to be compared against.
    :type tested_string: str
    """

    text_in_terminal = context.terminal.instance.findChild(
        lambda x: x.name == "Terminal" and x.roleName == "terminal" and x.focused
    ).text

    assert tested_string in text_in_terminal, "".join(
        (
            f"\nExpected string:\n '{tested_string}'",
            f"\nFound string   :\n '{text_in_terminal}'",
        )
    )


@step('Terminal does not contain string "{tested_string}"')
def terminal_does_not_contain_string(context, tested_string) -> None:
    """
    Verify that the terminal does not contain given string.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param tested_string: String to be compared against.
    :type tested_string: str
    """

    terminal = context.terminal.instance.findChild(
        lambda x: x.name == "Terminal" and x.roleName == "terminal" and x.focused
    ).text

    assert (
        tested_string not in terminal
    ), "String was found. Indication of test failure."


@step("Terminal output is empty")
def terminal_output_is_empty(context) -> None:
    """
    Verify that the terminal output is empty.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    terminal = context.terminal.instance.findChild(
        lambda x: x.name == "Terminal" and x.roleName == "terminal" and x.focused
    ).text

    assert terminal.strip("\n") == "", "\n".join(
        (
            "\nTerminal is not empty. Indication of test failure.",
            f"Terminal lenght : '{len(terminal)}'",
            f"Terminal content: '{terminal}'",
        )
    )


@step("Open preferences")
def open_preferences(context) -> None:
    """
    Open preferences

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    context.execute_steps('* Left click "Edit" "menu" in "terminal"')
    context.execute_steps('* Left click "Preferences" "menu item" in "terminal"')
    context.execute_steps('* Application "preferences" is running')
    sleep(2)


@step('Terminal has "{expected_number:d}" windows')
def terminal_has_windows(context, expected_number) -> None:
    """
    Verify that the terminal has expected number of windows.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param expected_number: Expected number.
    :type expected_number: str
    """

    terminal_windows_count = 0

    for _ in range(5):
        terminal_windows_count = len(
            context.terminal.instance.findChildren(
                lambda x: ("Terminal" in x.name or "test@" in x.name)
                and x.roleName == "frame"
            )
        )

        if terminal_windows_count == expected_number:
            return

        sleep(1)

    assert False, "".join(
        (
            f"\nNumber of expected open windows: '{expected_number}'",
            f"\nNumber of found open windows:    '{terminal_windows_count}'",
        )
    )


@step("Enable GTK inspector")
def enable_gtk_inspector(context) -> None:  # pylint: disable=unused-argument
    """
    Enable GTK inspector.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    run("dconf write /org/gtk/settings/debug/enable-inspector-keybinding true")


@step('Terminal has "{expected_number:d}" tabs')
def terminal_has_tabs(context, expected_number) -> None:
    """
    Verify that terminal has expected number of tabs.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param expected_number: Given expected number of tabs.
    :type expected_number: str
    """

    terminal_tabs_count = 0

    for _ in range(5):
        terminal_tabs_count = len(
            context.terminal.instance.findChildren(
                lambda x: x.name == "Terminal" and x.roleName == "terminal"
            )
        )

        if terminal_tabs_count == int(expected_number):
            return

        sleep(1)

    assert False, "".join(
        (
            f"\nNumber of expected open tabs: '{expected_number}'",
            f"\nNumber of found open tabs:    '{terminal_tabs_count}'",
        )
    )


@step("Window is fullscreen")
@step("Window is {negation} fullscreen")
def window_is_fullscreen(context, negation=None) -> None:
    """
    Verify that the terminal window is fullscreen.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param negation: Negation of result when comparing, defaults to None.
    :type negation: str, optional.
    """

    sleep(3)
    frame = context.terminal.instance.child(roleName="frame")
    size_x = frame.size[0]
    size_y = frame.size[1]

    screen_size_x = context.sandbox.resolution[0]
    screen_size_y = context.sandbox.resolution[1]

    if negation:
        assert (
            screen_size_x != size_x or screen_size_y != size_y
        ), "Window is still in fullscreen mode."
    else:
        assert screen_size_x == size_x and screen_size_y == size_y, "\n".join(
            (
                "\nWindow is not in fullscreen mode.",
                f"Existing resolution='{context.sandbox.resolution}'",
                f"X: Screen Size='{screen_size_x}' != Terminal Size='{size_x}'.",
                f"Y: Screen Size='{screen_size_y}' != Terminal Size='{size_y}'.",
            )
        )

        assert frame.position[1] == 0, "Fullscreen frame is not top aligned."


@step('Terminal window is now "{expected_resize}"')
def terminal_window_is_now_of_size(context, expected_resize) -> None:
    """
    Verify the size of the terminal window.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param expected_resize: Expected resize.
    :type expected_resize: str
    """

    terminal_size = Tuple(context.terminal.instance.child(roleName="frame").size)

    if expected_resize == "smaller":
        assert context.stored_size > terminal_size + Tuple((0, -27)), "".join(
            (
                "Assertion failed. Sizes do not corespond - smaller.",
                f"\nExpected: '{context.stored_size}'",
                f"\nCurrent:  '{terminal_size}'",
            )
        )

    if expected_resize == "smaller or not changed":
        assert context.stored_size >= terminal_size + Tuple((0, -27)), "".join(
            (
                "Assertion failed. Sizes do not corespond - smaller or not changed.",
                f"\nExpected: '{context.stored_size}'",
                f"\nCurrent:  '{terminal_size}'",
            )
        )

    if expected_resize == "bigger":
        assert context.stored_size < terminal_size + Tuple((0, -27)), "".join(
            (
                "Assertion failed. Sizes do not corespond - bigger.",
                f"\nExpected: '{context.stored_size}'",
                f"\nCurrent:  '{terminal_size}'",
            )
        )

    if expected_resize == "back to original":
        assert (
            context.stored_size >= terminal_size
            or context.stored_size == terminal_size + Tuple((0, 27))
            or context.stored_size == terminal_size + Tuple((0, -27))
        ), "".join(
            (
                "Assertion failed. Sizes do not corespond - back to original.",
                f"\nExpected: '{context.stored_size}'",
                f"\nCurrent:  '{terminal_size}'",
            )
        )


@step("Store terminal size")
def store_terminal_size(context) -> None:
    """
    Store terminal size.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    # Attempt to prevent race conditions.
    sleep(1)

    context.stored_size = Tuple(context.terminal.instance.child(roleName="frame").size)


@step('Set terminal size to columns: "{columns_size}" and rows: "{rows_size}"')
def set_terminal_size_to_columns_and_rows(context, columns_size, rows_size) -> None:
    """
    Set terminal size to given sizes.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param columns_size: Column size.
    :type columns_size: str

    :param rows_size: Row size.
    :type rows_size: str
    """

    target_columns = context.preferences.instance.findChild(
        lambda x: x.name == "columns" and x.roleName == "label"
    ).parent.child(roleName="spin button")

    target_rows = context.preferences.instance.findChild(
        lambda x: x.name == "rows" and x.roleName == "label"
    ).parent.child(roleName="spin button")

    target_columns.click()
    target_columns.text = columns_size
    pressKey("Enter")
    # keyCombo("<Ctrl><A>")
    # typeText(columns_size)

    target_rows.click()
    target_rows.text = rows_size
    pressKey("Enter")
    # keyCombo("<Ctrl><A>")
    # typeText(rows_size)

    context.execute_steps("* Close preferences")
    sleep(1)


@step("Enable shortcuts")
def enable_shorcuts(context) -> None:
    """
    Enable shortcuts.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    context.execute_steps("* Open preferences")
    context.execute_steps('* Left click "Shortcuts" "label" in "preferences"')
    context.execute_steps(
        '* Item "Enable shortcuts" "check box" is "checked" in "preferences"'
    )
    context.execute_steps("* Close preferences")


@step("Close preferences")
def close_preferences(context) -> None:
    """
    Close preferences.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    target_frame = context.preferences.instance.findChild(
        lambda x: "Preferences" in x.name and x.roleName == "frame"
    )

    target_frame.findChildren(
        lambda x: x.name == "Close" and x.roleName == "push button" and x.showing
    )[-1].click()


@step('Find "{find_string}"')
def find_string_in_find_frame_dialog(context, find_string) -> None:
    """
    Find the given string in find frame dialog.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param find_string: Find given string.
    :type find_string: str
    """

    find_text_field = context.terminal.instance.child("Search", "text")
    find_text_field.text = find_string
    sleep(1)
    pressKey("Enter")
    sleep(1)


@step("Prepare two Tabs for testing")
def prepare_two_tabs_for_testing(context) -> None:
    """
    Prepare two Tabs for testing.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    context.execute_steps('* Left click "Terminal" "menu" in "terminal"')
    context.execute_steps('* Left click "Set Title" "menu item" in "terminal"')
    context.execute_steps('* Item "Set Title" "alert" is "showing" in "terminal"')
    context.execute_steps('* Type text: "tab-1"')
    context.execute_steps('* Left click "OK" "push button" in "terminal"')
    context.execute_steps('* Type text: "tab-1"')
    context.execute_steps('* Press key: "Enter"')
    keyCombo("<Ctrl><Shift><T>")
    context.execute_steps('* Left click "Terminal" "menu" in "terminal"')
    context.execute_steps('* Left click "Set Title" "menu item" in "terminal"')
    context.execute_steps('* Item "Set Title" "alert" is "showing" in "terminal"')
    context.execute_steps('* Type text: "tab-2"')
    context.execute_steps('* Left click "OK" "push button" in "terminal"')
    context.execute_steps('* Type text: "tab-2"')
    context.execute_steps('* Press key: "Enter"')


@step('Tab "{tab_name}" was targeted and contains string "{given_string}"')
def tab_was_targeted_and_contains_string(context, tab_name, given_string) -> None:
    """
    Given tab has expected string.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param tab_name: Tab name to search in.
    :type tab_name: str

    :param given_string: Givne string to compare against.
    :type given_string: str
    """

    # Attempt to prevent race conditions.
    sleep(1)

    target_tab = context.terminal.instance.child(tab_name, "page tab")
    tab_string_content = target_tab.child("Terminal", "terminal").text

    assert given_string in tab_string_content, "".join(
        (
            f"\nExpected string to be found: '{given_string}'",
            f"\nString that was found in tab: '{tab_string_content}'",
        )
    )


@step('Left click on "{page_tab_name}" page tab and make sure the tab was selected')
def make_sure_page_tab_selection_is_immune_to_slow_machines(
    context, page_tab_name
) -> None:
    """
    Left click on specific page tab and make sure it was selected.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param page_tab_name: Page tab name.
    :type page_tab_name: str
    """

    page_tab = context.preferences.instance.child(page_tab_name, "page tab")
    page_tab.click()

    for _ in range(5):
        if not page_tab.selected:
            page_tab.click()
            sleep(1)
        else:
            return

    assert False, "".join((f"Page tab '{page_tab_name}' failed to be selected."))


@step('Set color name to: "{color_name}"')
def set_color_name_to(context, color_name) -> None:
    """
    Set color to given color name.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param color_name: Color to change.
    :type color_name: str
    """

    choose_terminal_dialog = context.preferences.instance.findChild(
        lambda x: "Choose Terminal" in x.name and x.roleName == "dialog"
    )

    color_name_field = choose_terminal_dialog.child("Color Name", "text")

    # Testing if click will make sure the attribute propagates.
    color_name_field.click()

    color_name_field.text = color_name
    sleep(1)
