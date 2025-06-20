# OpenVoiceOS Tray Indicator

A simple system tray application for **OpenVoiceOS** that visually reflects the assistant’s current status and allows quick interaction through a menu. Built with Python, GTK3, and AppIndicator3.

---

## Features

* Displays OpenVoiceOS status in the system tray (Listening, Speaking, Thinking, Sleeping, WakeWord, Errors, Idle)
* Menu options for:

  * Starting microphone listening
  * Stopping current OpenVoiceOS actions
  * Typing a query to send to OpenVoiceOS as if spoken
  * Typing text for text-to-speech output
  * Quitting the tray app
* Updates tray icon title to reflect assistant status in real-time based on OpenVoiceOS message bus events

---

## Requirements

* Python 3
* GTK 3 (with Python GObject introspection bindings)
* AppIndicator3 (Ubuntu or other Linux systems with libappindicator support)
* `ovos_bus_client` package from OpenVoiceOS

---

## Usage

* The tray icon updates automatically based on OpenVoiceOS events.
* Use the tray menu to control OpenVoiceOS or send text commands.
* Press **Quit** in the menu or `Ctrl+C` in the terminal to exit.

