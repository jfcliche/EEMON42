

import sys
import os
sys.pycache_prefix = "__pycache__"  # NOQA

os.environ['SDL_AUDIODRIVER'] = 'dsp'  # Remove ALSA warnings when pygame starts
import pygame
import asyncio

# import socket
# import struct
# import binascii
# sys.modules['usocket'] = socket
# sys.modules['ustruct'] = struct
# sys.modules['ubinascii'] = binascii

# local imports
import eemon42
from button_sim import Button
from ssd1331_sim import SSD1331


class EEMON42(eemon42.EEMON42):

    DISPLAY_POS = (180, 66)  # Upper left corner of the display area
    BUTTON_ROT_RECT = (169, 165, 58, 47)
    BUTTON_B_RECT = (246, 161, 26, 28)
    BUTTON_C_RECT = (246, 203, 26, 28)
    BUTTON_A_RECT = (246, 245, 26, 28)
    BUTTON_ZOOM_RECT = (DISPLAY_POS[0] - 6, DISPLAY_POS[1] - 6, SSD1331.WIDTH + 12, SSD1331.HEIGHT + 12) 

    def __init__(self):

        # Initialize the original EEMON42
        super().__init__()

        # set default pin values
        self.pin_cs0_rota.value(1)
        self.pin_cs1_rotb.value(1)
        self.pin_cs2_button_rot.value(1)
        self.pin_cs3_button_a.value(1)
        self.pin_cs4_button_b.value(1)
        self.pin_cs5_button_c.value(1)
        self.pin_cs6_irq.value(1)

        self.zoom_display = True # show zoomed display by default

        # Pass graphical parameters to the emulated button instances
        self.button_rot.set_rect(pygame.Rect(*self.BUTTON_ROT_RECT))
        self.button_a.set_rect(pygame.Rect(*self.BUTTON_A_RECT)) # ENTER
        self.button_a.set_key(pygame.K_RETURN)

        self.button_b.set_rect(pygame.Rect(*self.BUTTON_B_RECT)) # ESCAPE
        self.button_b.set_key(pygame.K_ESCAPE)

        self.button_c.set_rect(pygame.Rect(*self.BUTTON_C_RECT))
        self.button_c.set_key(pygame.K_LSHIFT)

        # add a display zoom button
        self.zoom_button = Button(rect=pygame.Rect(*self.BUTTON_ZOOM_RECT))

        # create a list of graphical widgets to process 
        self.widgets = (self.rot_enc,
                        self.button_rot,
                        self.button_a,
                        self.button_b,
                        self.button_c,
                        self.zoom_button
                        )

        print('Controls:')
        print('  Use the wheel anywhere to rotate the knob')
        print('  Click on the buttons or knob to press them')
        print('  Clock on the screen to show/hide a magnified display')

    def init(self):
        pygame.init()
        self.board = pygame.image.load("../sim/eemon42.png")
        pygame.display.set_caption("EEMON42 Simulator")
        self.screen = pygame.display.set_mode(self.board.get_size())
        super().init()

    async def pygame_event_loop(self):
        print('Starting pygame event loop task')
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL):
                        # self.main_task.cancel()  # cancel the main task to exit the program
                        raise asyncio.CancelledError('Pygame loop terminated by closing the panel or by CTRL-C')
                        # break

                    # call the event handler of each widget
                    for widget in self.widgets:
                        widget.handle_event(event)

                # Check if zoom button was pressed
                if self.zoom_button.value():
                    self.zoom_display = not self.zoom_display

                # Display screen
                self.screen.blit(self.board, self.screen.get_rect())
                self.screen.blit(self.display.surface, self.DISPLAY_POS)

                # Display screen zoom insert, if activated
                if self.zoom_display:
                    self.screen.blit(pygame.transform.scale(
                        self.display.surface, (SSD1331.WIDTH * 2, SSD1331.HEIGHT * 2)), (0, self.screen.get_rect().bottom-SSD1331.HEIGHT * 2))

                # Display widget bounding boxes
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
        """ Runs the main program loop of the EEMON42, with an additional pygame display handling task.
        """
        self.pygame_task = asyncio.create_task(self.pygame_event_loop())
        await super().main_loop(extra_tasks = (self.pygame_task,))  # start main loop as an explicit task so we can cancel it.
