import sys
import os
from sim import gc as gc
sys.modules["gc"] = gc

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
_BOARD_IMAGE = os.path.join(_SIM_DIR, "eemon42.png")

os.environ['SDL_AUDIODRIVER'] = 'dsp'  # Remove ALSA warnings when pygame starts
import pygame
import asyncio

from embedded.eemon42 import EEMON42 as EEMON42_HW  # hardware; flat import uses this sim module
from button import Button  # Needed to add an additional sim-only display zoom button

# Visible LCD area on eemon42.png (photo), used to center the sim framebuffer.
_LCD_BBOX = (127, 56, 335, 179)

# Click targets on the photo (x, y, w, h) — wider than visible switches for easier clicking.
_BUTTON_ROT_RECT = (0, 230, 42, 52)
_BUTTON_B_RECT = (405, 248, 45, 40)
_BUTTON_C_RECT = (405, 178, 45, 40)
_BUTTON_A_RECT = (405, 318, 45, 40)

_ZOOM_MARGIN = 12
_ZOOM_SCALE = 3


def _display_pos(display):
    x0, y0, x1, y1 = _LCD_BBOX
    cx = (x0 + x1 + 1) // 2
    cy = (y0 + y1 + 1) // 2
    return (cx - display.WIDTH // 2, cy - display.HEIGHT // 2)


class EEMON42(EEMON42_HW):

    CONFIG_FOLDER = _SIM_DIR  # Config is modified by the sim, so let's keep it local to the sim directory

    def __init__(self):

        super().__init__()

        self._board_image = _BOARD_IMAGE
        self.DISPLAY_POS = _display_pos(self.display)
        dw, dh = self.display.WIDTH, self.display.HEIGHT
        self.BUTTON_ZOOM_RECT = (
            self.DISPLAY_POS[0] - 4,
            self.DISPLAY_POS[1] - 4,
            dw + 8,
            dh + 8,
        )

        self.pin_cs0_rota.value(1)
        self.pin_cs1_rotb.value(1)
        self.pin_cs2_button_rot.value(1)
        self.pin_cs3_button_a.value(1)
        self.pin_cs4_button_b.value(1)
        self.pin_cs5_button_c.value(1)
        self.pin_cs6_irq.value(1)

        self.zoom_display = True
        self._board_x = 0

        self.button_rot.set_rect(pygame.Rect(*_BUTTON_ROT_RECT))
        self.button_a.set_rect(pygame.Rect(*_BUTTON_A_RECT))
        self.button_a.set_key(pygame.K_RETURN)

        self.button_b.set_rect(pygame.Rect(*_BUTTON_B_RECT))
        self.button_b.set_key(pygame.K_ESCAPE)

        self.button_c.set_rect(pygame.Rect(*_BUTTON_C_RECT))
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

    def _offset_widget_rects(self):
        """Map board-local hit rects to screen coordinates when the board is centered."""
        for widget in self.widgets:
            if hasattr(widget, 'rect'):
                r = widget.rect()
                if r is not None:
                    widget.set_rect(r.move(self._board_x, 0))

    def init(self):
        pygame.init()
        self.board = pygame.image.load(self._board_image)
        self._board_w, self._board_h = self.board.get_size()
        dw, dh = self.display.WIDTH, self.display.HEIGHT
        zoom_w, zoom_h = dw * _ZOOM_SCALE, dh * _ZOOM_SCALE
        self._window_w = max(self._board_w, zoom_w)
        self._window_h = self._board_h + _ZOOM_MARGIN + zoom_h
        self._board_x = (self._window_w - self._board_w) // 2
        self._zoom_pos = (
            (self._window_w - zoom_w) // 2,
            self._board_h + _ZOOM_MARGIN,
        )
        self._zoom_size = (zoom_w, zoom_h)
        self._below_board_rect = pygame.Rect(
            0, self._board_h, self._window_w, self._window_h - self._board_h
        )
        self._offset_widget_rects()
        pygame.display.set_caption("EEMON42 Simulator")
        self.screen = pygame.display.set_mode((self._window_w, self._window_h))
        self.screen.fill((0, 0, 0))
        super().init()

    async def pygame_event_loop(self):
        print('Starting pygame event loop task')
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

                self.screen.blit(self.board, (self._board_x, 0))
                self.screen.blit(
                    self.display.surface,
                    (self._board_x + self.DISPLAY_POS[0], self.DISPLAY_POS[1]),
                )

                if self.zoom_display:
                    self.screen.blit(
                        pygame.transform.scale(
                            self.display.surface, self._zoom_size
                        ),
                        self._zoom_pos,
                    )
                else:
                    self.screen.fill((0, 0, 0), self._below_board_rect)

                for widget in self.widgets:
                    if hasattr(widget, 'rect'):
                        rect = widget.rect()
                        if rect is not None:
                            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)
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
