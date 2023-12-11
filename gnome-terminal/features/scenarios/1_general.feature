@general_feature
Feature: General Tests


  @start_via_command
  Scenario: Start application via command.
    * Start application "terminal" via "command"


  @start_via_menu
  Scenario: Start application via menu.
    * Start application "terminal" via "menu"


  @quit_via_shortcut
  Scenario: Ctrl-Q to quit application.
    * Start application "terminal" via "command"
    * Make sure window is focused for wayland testing
    * Close application "terminal" via "shortcut"


  @close_via_gnome_panel
  Scenario: Close application via menu.
    * Start application "terminal" via "command"
    * Make sure window is focused for wayland testing
    * Close application "terminal" via "gnome panel with workaround"


  @open_new_window_via_shortcut
  Scenario: Open new window via shortcut.
    * Start application "terminal" via "command"
    * Make sure window is focused for wayland testing
    * Key combo: "<Shift><Ctrl><N>"
    * Terminal has "2" windows


  @close_window_via_shortcut
  Scenario: Close terminal window via shortcut.
    * Start application "terminal" via "command"
    * Make sure window is focused for wayland testing
    * Key combo: "<Shift><Ctrl><N>"
    * Key combo: "<Shift><Ctrl><W>"
    * Terminal has "1" windows


  @add_tab
  Scenario: Add terminal tab.
    * Start application "terminal" via "command"
    * Make sure window is focused for wayland testing
    * Key combo: "<Shift><Ctrl><T>"
    * Terminal has "2" tabs


  @close_tab
  Scenario: Close terminal tab.
    * Start application "terminal" via "command"
    * Make sure window is focused for wayland testing
    * Key combo: "<Shift><Ctrl><T>"
    * Terminal has "2" tabs
    * Key combo: "<Shift><Ctrl><W>"
    * Terminal has "1" tabs


  @switch_tab
  Scenario: Switch terminal tab.
    * Start application "terminal" via "command"
    * Make sure window is focused for wayland testing
    * Key combo: "<Shift><Ctrl><T>"
    * Key combo: "<Alt><1>"
    * Execute in terminal: "echo test string"
    * Terminal contains string "test string"


  @detach_tab
  Scenario: Detach terminal tab.
    * Start application "terminal" via "command"
    * Make sure window is focused for wayland testing
    * Key combo: "<Shift><Ctrl><T>"
    * Right click "test@" "page tab" in "terminal"
    * Left click "Detach Terminal" "menu item" in "terminal"
    * Terminal has "2" windows
