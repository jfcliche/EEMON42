#!/usr/bin/env python 

import sys
sys.pycache_prefix = "__pycache__"  # NOQA
# add the EEMON42 application folder after this package so emulated modules will be loaded
sys.path.append("../software")  # NOQA

import pygame
import socket
import struct
import binascii
import asyncio

sys.modules['usocket'] = socket
sys.modules['ustruct'] = struct
sys.modules['ubinascii'] = binascii

# local imports
from eemon42 import EEMON42
from button import Button
from ssd1331 import SSD1331

# SCREEN_SCALE = 4


class EEMON42Sim(EEMON42):

    DISPLAY_POS = (180, 66)  # Upper left corner of the display area
    BUTTON_ROT_RECT = (169, 165, 58, 47)
    BUTTON_B_RECT = (246, 161, 26, 28)
    BUTTON_C_RECT = (246, 203, 26, 28)
    BUTTON_A_RECT = (246, 245, 26, 28)
    BUTTON_ZOOM_RECT = (DISPLAY_POS[0] - 6, DISPLAY_POS[1] - 6, SSD1331.WIDTH + 12, SSD1331.HEIGHT + 12) 

    def __init__(self):
        pygame.init()

        self.zoom_display = False
        self.board = pygame.image.load("eemon42.png")
        pygame.display.set_caption("EEMON42 Simulator")
        self.screen = pygame.display.set_mode(self.board.get_size())
        # SSD1331.surface = self.surface = pygame.surface.Surface((SSD1331.WIDTH, SSD1331.HEIGHT))


        # Initialize the original EEMON42
        super().__init__()

        # Pass the surface object to the emulated display instance. 
        # self.display.set_surface(self.surface)  


        # Pass graphical parameters to the emulated button instances
        self.button_rot.set_rect(pygame.Rect(*self.BUTTON_ROT_RECT))
        self.button_a.set_rect(pygame.Rect(*self.BUTTON_A_RECT))
        self.button_b.set_rect(pygame.Rect(*self.BUTTON_B_RECT))
        self.button_c.set_rect(pygame.Rect(*self.BUTTON_C_RECT))

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

    async def pygame_event_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    self.main_task.cancel()  # cancel the main task to exit the program
                    return

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
        print('pygame event processing loop has exited')

    async def main_loop(self):
        """ Runs the main program loop of the EEMON42, with an additional pygame display handling task.
        """
        self.pygame_task = asyncio.create_task(self.pygame_event_loop())
        # self.main_task = asyncio.create_task(super().main_loop())  # start main loop as an explicit task so we can cancel it.
        # await self.main_task # Run until the main loop exits for some reason (return or exception)
        await super().main_loop()  # start main loop as an explicit task so we can cancel it.

    def run(self):
        try:
            asyncio.run(self.main_loop())
        except asyncio.CancelledError:
            print('Cancelled by user. Bye!')
        except KeyboardInterrupt:
            print('Interrupted by user. Bye!')
        except Exception as e:
            print('Exception!')
            raise


if __name__=="__main__":
    sim = EEMON42Sim()
    sim.run()
