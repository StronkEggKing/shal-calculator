import os
import asyncio
from pathlib import Path

import flet as ft

try:
    import flet_video as ftv
    HAS_VIDEO = True
except ImportError:
    HAS_VIDEO = False

import CalFuncs

# ── Constants ──────────────────────────────────────────────────────────────────

EASTER_EGG_TRIGGERS = {"shalshafahath", "Šal"}

BG_DARK     = "#121212"
FG_LIGHT    = "#eeeeee"
GREY        = "#333333"
RED         = "#cf6679"
FONT_FAMILY = "Arial"


def get_assets_dir() -> Path:
    """Resolves assets dir for both dev (flet run) and production (APK) builds."""
    default = Path(__file__).parent / "assets"
    return Path(os.environ.get("FLET_ASSETS_DIR", str(default))).resolve()


# ── Easter-egg view ────────────────────────────────────────────────────────────

class EasterEggView(ft.Column):
    """Plays test.mp4 then calls on_finish()."""

    def __init__(self, on_finish, assets_dir: Path, **kwargs):
        super().__init__(**kwargs)
        self._on_finish = on_finish
        self.expand = True
        self.spacing = 0

        self._video_path = str(assets_dir / "test.mp4")

        self._started = False

        if HAS_VIDEO:
            self.video = ftv.Video(
                playlist=[ftv.VideoMedia(self._video_path)],
                autoplay=True,
                fill_color=BG_DARK,
                fit=ft.BoxFit.COVER,
                on_complete=lambda e: self._on_complete(e),
            )
            main_content = self.video
        else:
            self.video = None
            main_content = ft.Container()

        self.controls = [
            ft.Stack(
                expand=True,
                controls=[main_content],
            )
        ]

    def did_mount(self):
        if self.video is not None:
            self.video.width = self.page.width
            self.video.height = self.page.height
            self.video.update()
            self.page.run_task(self._watch_playback)
        else:
            self.page.run_task(self._finish_after_delay)

    async def _watch_playback(self):
        # Poll until is_playing becomes True, then arm the completion gate
        for _ in range(30):  # wait up to 30s for playback to start
            await asyncio.sleep(1)
            if self.video.is_playing:
                self._started = True
                break

    def _on_complete(self, e):
        if self._started:
            self._finish()

    async def _finish_after_delay(self):
        await asyncio.sleep(2)
        self._finish()

    def _finish(self):
        self._on_finish()


# ── Calculator view ────────────────────────────────────────────────────────────

class CalculatorView(ft.Column):

    def __init__(self, show_easter_egg, **kwargs):
        super().__init__(**kwargs)
        self._show_easter_egg = show_easter_egg
        self.spacing = 16
        self.expand = False

        self.entry = ft.TextField(
            hint_text="Enter expression…",
            bgcolor=FG_LIGHT,
            color=BG_DARK,
            cursor_color=BG_DARK,
            border_color=FG_LIGHT,
            focused_border_color=FG_LIGHT,
            text_style=ft.TextStyle(color=BG_DARK, font_family=FONT_FAMILY, size=22),
            on_submit=self._submit,
            expand=True,
            height=50,
        )

        self.calc_btn = ft.Button(
            content=ft.Text("Calculate", color=ft.Colors.WHITE, font_family=FONT_FAMILY),
            style=ft.ButtonStyle(
                bgcolor=GREY,
                shape=ft.RoundedRectangleBorder(radius=6),
            ),
            on_click=self._submit,
            height=50,
            width=130,
        )

        self.output = ft.TextField(
            read_only=True,
            bgcolor=BG_DARK,
            color=FG_LIGHT,
            border_color=GREY,
            text_style=ft.TextStyle(color=FG_LIGHT, font_family=FONT_FAMILY, size=20),
            hint_text="Result will appear here",
            hint_style=ft.TextStyle(color="#555555"),
            multiline=False,
            height=50,
        )

        self.controls = [
            ft.Text("Input",  color=FG_LIGHT, font_family=FONT_FAMILY, size=24, weight=ft.FontWeight.W_500),
            ft.Row(
                controls=[self.entry, self.calc_btn],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Text("Output", color=FG_LIGHT, font_family=FONT_FAMILY, size=20, weight=ft.FontWeight.W_500),
            self.output,
        ]

    def _submit(self, e=None):
        user_input = (self.entry.value or "").strip()
        if not user_input:
            return

        if user_input in EASTER_EGG_TRIGGERS:
            self._show_easter_egg()
            return

        try:
            answer = CalFuncs.calculate(user_input)
            self.output.value = str(answer)
            self.output.color = FG_LIGHT
        except ZeroDivisionError:
            self.output.value = "Error: Division by zero"
            self.output.color = RED
        except (ValueError, SyntaxError) as ex:
            self.output.value = f"Error: {ex}"
            self.output.color = RED
        except Exception as ex:
            self.output.value = f"Error: {ex}"
            self.output.color = RED

        self.output.update()


# ── App entry point ────────────────────────────────────────────────────────────

def main(page: ft.Page):
    assets_dir = get_assets_dir()

    page.title    = "Šal Calculator"
    page.bgcolor  = BG_DARK
    page.padding  = 20
    page.scroll   = ft.ScrollMode.AUTO
    page.fonts    = {FONT_FAMILY: str(assets_dir / "Fonts" / "ARIAL.ttf")}

    # Desktop only — ignored on Android
    page.window.width     = 400
    page.window.height    = 700
    page.window.resizable = True

    def _show_calculator():
        page.controls.clear()
        page.controls.append(calc_view)
        page.update()

    def _show_easter_egg():
        page.controls.clear()
        egg = EasterEggView(on_finish=_show_calculator, assets_dir=assets_dir)
        page.controls.append(egg)
        page.update()

    calc_view = CalculatorView(show_easter_egg=_show_easter_egg)

    _show_calculator()


ft.run(main, assets_dir="assets")
