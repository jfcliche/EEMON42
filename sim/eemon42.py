import sys
import os

sys.pycache_prefix = "__pycache__"  # NOQA

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))

os.environ['SDL_AUDIODRIVER'] = 'dsp'  # Remove ALSA warnings when pygame starts
import pygame
import asyncio

from software.eemon42 import EEMON42 as EEMON42_HW # shadowed module; use package import for hardware
from button import Button  # Needed to add an additional sim-only display zoom button

# Board layout keyed by (display width, height)
BOARD_LAYOUTS = {
    (96, 64): {
        "image": "eemon42_ssd1331.png",
        "display_pos": (180, 66),
        "button_rot_rect": (169, 165, 58, 47),
        "button_b_rect": (246, 161, 26, 28),
        "button_c_rect": (246, 203, 26, 28),
        "button_a_rect": (246, 245, 26, 28),
    },
    (128, 160): {
        "image": "eemon42_st7735.png",
        "display_pos": (120, 44),
        "button_rot_rect": (300, 280, 58, 47),
        "button_b_rect": (360, 276, 26, 28),
        "button_c_rect": (360, 318, 26, 28),
        "button_a_rect": (360, 360, 26, 28),
    },
}


def _layout_for_display(display):
    key = (display.WIDTH, display.HEIGHT)
    if key not in BOARD_LAYOUTS:
        raise ValueError(f"No simulator board layout for display size {key}")
    return BOARD_LAYOUTS[key]


class EEMON42(EEMON42_HW):

    CONFIG_FOLDER = '../software/'

    def __init__(self):

        super().__init__()

        layout = _layout_for_display(self.display)
        self._board_image = os.path.join(_SIM_DIR, layout["image"])
        self.DISPLAY_POS = layout["display_pos"]
        zoom = (
            self.DISPLAY_POS[0] - 6,
            self.DISPLAY_POS[1] - 6,
            self.display.WIDTH + 12,
            self.display.HEIGHT + 12,
        )
        self.BUTTON_ZOOM_RECT = zoom

        self.pin_cs0_rota.value(1)
        self.pin_cs1_rotb.value(1)
        self.pin_cs2_button_rot.value(1)
        self.pin_cs3_button_a.value(1)
        self.pin_cs4_button_b.value(1)
        self.pin_cs5_button_c.value(1)
        self.pin_cs6_irq.value(1)

        self.zoom_display = True

        self.button_rot.set_rect(pygame.Rect(*layout["button_rot_rect"]))
        self.button_a.set_rect(pygame.Rect(*layout["button_a_rect"]))
        self.button_a.set_key(pygame.K_RETURN)

        self.button_b.set_rect(pygame.Rect(*layout["button_b_rect"]))
        self.button_b.set_key(pygame.K_ESCAPE)

        self.button_c.set_rect(pygame.Rect(*layout["button_c_rect"]))
        self.button_c.set_key(pygame.K_LSHIFT)

        self.zoom_button = Button(rect=pygame.Rect(*self.BUTTON_ZOOM_RECT))

        self.widgets = (
            self.rot_enc,
            self.button_rot,
            self.button_a,
            self.button_b,
            self.button_c,
            self.zoom_button,
        )

        print('Controls:')
        print('  Use the wheel anywhere to rotate the knob')
        print('  Click on the buttons or knob to press them')
        print('  Click on the screen to show/hide a magnified display')

    def init(self):
        pygame.init()
        self.board = pygame.image.load(self._board_image)
        pygame.display.set_caption("EEMON42 Simulator")
        self.screen = pygame.display.set_mode(self.board.get_size())
        super().init()

    async def pygame_event_loop(self):
        print('Starting pygame event loop task')
        dw, dh = self.display.WIDTH, self.display.HEIGHT
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_c
                        and pygame.key.get_mods() & pygame.KMOD_CTRL
                    ):
                        raise asyncio.CancelledError(
                            'Pygame loop terminated by closing the panel or by CTRL-C'
                        )

                    for widget in self.widgets:
                        widget.handle_event(event)

                if self.zoom_button.value():
                    self.zoom_display = not self.zoom_display

                self.screen.blit(self.board, self.screen.get_rect())
                self.screen.blit(self.display.surface, self.DISPLAY_POS)

                if self.zoom_display:
                    self.screen.blit(
                        pygame.transform.scale(
                            self.display.surface, (dw * 2, dh * 2)
                        ),
                        (0, self.screen.get_rect().bottom - dh * 2),
                    )

                for widget in self.widgets:
                    if hasattr(widget, 'rect'):
                        pygame.draw.rect(self.screen, (255, 0, 0), widget.rect(), 5)
                pygame.display.flip()
                await asyncio.sleep(0.03)
        except BaseException as e:
            print(f'Exception in Pygame event loop task: {e!r}')
            raise
        finally:
            print('pygame event processing loop task has terminated')

    def dispose(self):
        super().dispose()
        pygame.display.quit()

    async def main_loop(self):
        self.pygame_task = asyncio.create_task(self.pygame_event_loop())
        await super().main_loop(extra_tasks=(self.pygame_task,))
