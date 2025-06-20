#!/usr/bin/env python3
import signal
from os.path import dirname

import gi
from ovos_bus_client.message import Message
from ovos_bus_client.util import get_mycroft_bus

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3

APP_ID = "openvoiceos.tray"
ICON = f"{dirname(__file__)}/logo.png"

# TODO icons
THINKING = "Thinking"
LISTENING = "Listening"
SPEAKING = "Speaking"
SLEEPING = "Sleeping"
WAKEWORD = "WakeWord"
STT_ERROR = "STT Error"
INTENT_ERROR = "Intent Error"
INTENT = "Intent Executing"
IDLE = "Idle"


class OVOSTrayApp:
    def __init__(self):
        self.status = IDLE
        self.bus = get_mycroft_bus()
        self.bus.on("recognizer_loop:wakeword", self.set_ww)
        self.bus.on("recognizer_loop:utterance", self.handle_utterance)
        self.bus.on("recognizer_loop:record_begin", self.set_listening)
        self.bus.on("recognizer_loop:record_end", self.end_listening)
        self.bus.on("recognizer_loop:audio_output_start", self.set_speaking)
        self.bus.on("recognizer_loop:audio_output_end", self.end_speaking)
        self.bus.on("recognizer_loop:sleep", self.set_sleeping)
        self.bus.on("recognizer_loop:wake_up", self.set_idle)
        self.bus.on("mycroft.awoken", self.set_idle)
        self.bus.on("recognizer_loop:recognition_unknown", self.set_stt_error)
        self.bus.on("complete_intent_failure", self.set_intent_error)
        self.bus.on("mycroft.skill.handler.start", self.set_intent)
        self.bus.on("mycroft.skill.handler.complete", self.set_idle)
        self.bus.on("ovos.utterance.handled", self.set_idle)

        self.bus.on("speak", self.handle_speak)

        self.indicator = AppIndicator3.Indicator.new(
            APP_ID,
            ICON,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("OpenVoiceOS")

        self.menu = Gtk.Menu()

        item_restart = Gtk.MenuItem(label="Stop")
        item_restart.connect("activate", self.stop)
        self.menu.append(item_restart)

        item_restart = Gtk.MenuItem(label="Mic Listen")
        item_restart.connect("activate", self.listen)
        self.menu.append(item_restart)

        item_chat = Gtk.MenuItem(label="Ask")
        item_chat.connect("activate", self.say_to_ovos)
        self.menu.append(item_chat)

        item_chat = Gtk.MenuItem(label="Speak")
        item_chat.connect("activate", self.tts)
        self.menu.append(item_chat)

        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", self.quit)
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    @property
    def ovos_running(self) -> bool:
        return self.bus.connected_event.is_set()

    def listen(self):
        self.bus.emit(Message("mycroft.mic.listen"))

    def stop(self):
        self.bus.emit(Message("mycroft.stop"))

    def tts(self, _):
        text = self.prompt_text("Text to Speech", "Enter text to speak:")
        if text:
            self.bus.emit(Message("speak", {"utterance": text}))

    def say_to_ovos(self, _):
        self.indicator.set_label("Listening...", "")

        text = self.prompt_text("Ask OpenVoiceOS", "Enter your utterance:")
        if text:
            self.bus.emit(Message("recognizer_loop:utterance", {"utterances": [text]}))

    def handle_utterance(self, message: Message):
        utterance = message.data["utterances"][0]
        self.status = THINKING
        self.indicator.set_title("OpenVoiceOS: thinking")

    def set_listening(self, message: Message):
        self.status = LISTENING
        self.indicator.set_title("OpenVoiceOS: listening")

    def end_listening(self, message: Message):
        self.status = IDLE
        self.indicator.set_title("OpenVoiceOS")

    def set_speaking(self, message: Message):
        self.status = SPEAKING
        self.indicator.set_title("OpenVoiceOS: speaking")

    def set_sleeping(self, message: Message):
        self.status = SLEEPING
        self.indicator.set_title("OpenVoiceOS: sleeping")

    def end_speaking(self, message: Message):
        self.status = IDLE
        self.indicator.set_title("OpenVoiceOS")

    def set_idle(self, message: Message):
        self.status = IDLE
        self.indicator.set_title("OpenVoiceOS")

    def set_stt_error(self, message: Message):
        self.status = STT_ERROR
        self.indicator.set_title("OpenVoiceOS: STT error")

    def set_intent(self, message: Message):
        self.status = INTENT
        self.indicator.set_title("OpenVoiceOS: intent executing")

    def set_intent_error(self, message: Message):
        self.status = INTENT_ERROR
        self.indicator.set_title("OpenVoiceOS: intent error")

    def set_ww(self, message: Message):
        self.status = WAKEWORD
        self.indicator.set_title("OpenVoiceOS: wake-word detected")

    def handle_speak(self, message: Message):
        utterance = message.data["utterance"]
        self.status = utterance

    def prompt_text(self, title: str, label: str) -> str:
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=title
        )
        dialog.format_secondary_text(label)

        entry = Gtk.Entry()
        entry.set_activates_default(True)
        dialog.vbox.pack_end(entry, True, True, 0)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.show_all()

        response = dialog.run()
        text = entry.get_text()
        dialog.destroy()

        if response == Gtk.ResponseType.OK and text:
            return text
        return None

    def quit(self, _):
        Gtk.main_quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Allow Ctrl+C to exit
    OVOSTrayApp()
    Gtk.main()


if __name__ == "__main__":
    main()
