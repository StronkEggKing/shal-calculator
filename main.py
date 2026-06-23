import assets.Modules.CalFuncs as CalFuncs

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.video import Video
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.clock import Clock

import PIL.Image

PIL.Image.preinit()
PIL.Image.init()

# Constants

EASTER_EGG_TRIGGERS = {"shalshafahath", "Šal"}

BG_DARK  = (18  / 255, 18  / 255, 18  / 255, 1)   # #121212
FG_LIGHT = (238 / 255, 238 / 255, 238 / 255, 1)   # #eeeeee
GREY     = (0.2, 0.2, 0.2, 1)

FONT     = "assets/Fonts/ARIAL.ttf"
MOBILE_BREAKPOINT = dp(600)
NARROW_BREAKPOINT = dp(400)

Window.clearcolor = BG_DARK

# Helpers

def is_mobile():
    return Window.width < MOBILE_BREAKPOINT

def is_narrow():
    return Window.width < NARROW_BREAKPOINT


# Easter-egg screen

class EasterEggScreen(Screen):

    def __init__(self, on_finish, **kwargs):
        super().__init__(name="easter_egg", **kwargs)
        self._on_finish = on_finish
        self.video = Video()
        self.video.bind(eos=self._video_ended)
        self.add_widget(self.video)

    def on_enter(self):
        Clock.schedule_once(self._start_video, 0.5)

    def _start_video(self, dt):
        self.video.source = "assets/test.mp4"
        self.video.state = "play"

    def _video_ended(self, instance, value):
        if value:
            self.video.state = "stop"
            self._on_finish()


# Calculator screen

class CalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="calculator", **kwargs)
        self.layout = CalculatorLayout()
        self.add_widget(self.layout)


# Calculator layout

class CalculatorLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self._build_ui()
        Window.bind(on_resize=self._on_resize)

    # Metrics

    def _metrics(self):
        mobile = is_mobile()
        return {
            "padding":   [dp(12)] * 4 if mobile else [dp(20)] * 4,
            "spacing":   dp(12)  if mobile else dp(16),
            "fs_label":  "22sp"  if mobile else "24sp",
            "fs_input":  "22sp"  if mobile else "24sp",
            "fs_output": "20sp",
            "fs_btn":    "20sp"  if mobile else "22sp",
            "h_label":   dp(44)  if mobile else dp(40),
            "h_row":     dp(56)  if mobile else dp(50),
            "h_output":  dp(56)  if mobile else dp(50),
        }

    def _apply_metrics(self):
        m = self._metrics()
        self.padding = m["padding"]
        self.spacing = m["spacing"]
        return m

    # Resize handler

    def _on_resize(self, window, width, height):
        now_mobile = is_mobile()
        now_narrow = is_narrow()
        if now_mobile != self._was_mobile or now_narrow != self._was_narrow:
            self._was_mobile = now_mobile
            self._was_narrow = now_narrow
            self.clear_widgets()
            self._build_ui()
        else:
            self._apply_metrics()

    # UI construction

    def _build_ui(self):
        self._was_mobile = is_mobile()
        self._was_narrow = is_narrow()
        m = self._apply_metrics()

        # Input label
        input_label = Label(
            text="Input",
            color=FG_LIGHT,
            font_name=FONT,
            font_size=m["fs_label"],
            size_hint=(1, None),
            height=m["h_label"],
            halign="left",
            valign="middle",
        )
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)

        if is_narrow():
            input_row = BoxLayout(
                orientation="vertical",
                size_hint=(1, None),
                height=m["h_row"] * 2 + dp(8),
                spacing=dp(8),
            )
            entry_size_hint = (1, None)
            entry_height    = m["h_row"]
            btn_size_hint   = (1, None)
            btn_height      = m["h_row"]
        else:
            input_row = GridLayout(
                cols=2,
                size_hint=(1, None),
                height=m["h_row"],
                spacing=dp(10),
            )
            entry_size_hint = (1, 1)
            entry_height    = None
            btn_size_hint   = (0.38, 1)
            btn_height      = None

        self.entry = TextInput(
            font_name=FONT,
            font_size=m["fs_input"],
            background_color=FG_LIGHT,
            foreground_color=BG_DARK,
            cursor_color=BG_DARK,
            multiline=False,
            size_hint=entry_size_hint,
            height=entry_height if entry_height is not None else 0,
        )
        self.entry.bind(on_text_validate=self.submit)
        input_row.add_widget(self.entry)

        btn = Button(
            text="Calculate",
            font_name=FONT,
            font_size=m["fs_btn"],
            size_hint=btn_size_hint,
            height=btn_height if btn_height is not None else 0,
            background_color=GREY,
            background_normal="",
            color=(1, 1, 1, 1),
        )
        btn.bind(on_release=self.submit)
        input_row.add_widget(btn)

        self.add_widget(input_row)

        # Output label
        output_label = Label(
            text="Output",
            color=FG_LIGHT,
            font_name=FONT,
            font_size=m["fs_output"],
            size_hint=(1, None),
            height=m["h_label"],
            halign="left",
            valign="middle",
        )
        output_label.bind(size=output_label.setter("text_size"))
        self.add_widget(output_label)

        # Output field
        self.output = TextInput(
            text="",
            font_name=FONT,
            font_size=m["fs_output"],
            background_color=BG_DARK,
            foreground_color=FG_LIGHT,
            background_normal="",
            readonly=True,
            size_hint=(1, None),
            height=m["h_output"],
            multiline=False,
        )
        self.add_widget(self.output)

        # Spacer
        self.add_widget(Label(size_hint=(1, 1)))

    # Logic

    def submit(self, *args):
        user_input = self.entry.text.strip()

        if not user_input:
            return

        if user_input in EASTER_EGG_TRIGGERS:
            app = App.get_running_app()
            app.show_easter_egg()
            return

        try:
            answer = CalFuncs.calculate(user_input)
            self.output.text = str(answer)
        except ZeroDivisionError:
            self.output.text = "Error: Division by zero"
        except (ValueError, SyntaxError) as e:
            self.output.text = f"Error: {e}"
        except Exception as e:
            self.output.text = f"Error: {e}"


# App

class ShalCalculatorApp(App):

    def build(self):
        self.title = "Šal Calculator"
        self._set_desktop_size()

        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))

        self.calc_screen = CalculatorScreen()
        self.sm.add_widget(self.calc_screen)

        return self.sm

    def _set_desktop_size(self):
        try:
            from kivy.utils import platform
            if platform not in ("android", "ios"):
                Window.size = (400, 700)
        except Exception:
            pass

    def show_easter_egg(self):
        if self.sm.has_screen("easter_egg"):
            return
        egg = EasterEggScreen(on_finish=self.hide_easter_egg)
        self.sm.add_widget(egg)
        self.sm.current = "easter_egg"
        #Window.fullscreen = "auto"

    def hide_easter_egg(self):
        #Window.fullscreen = False
        self.sm.current = "calculator"
        self.sm.remove_widget(self.sm.get_screen("easter_egg"))


if __name__ == "__main__":
    ShalCalculatorApp().run()