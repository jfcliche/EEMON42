import sys
import pygame
from gui import GUI
from sim_display import SimDisplay
from sim_rotary import SimRotary
from sim_button import SimButton

SCREEN_SCALE = 4

zoom_display = False


def event_loop():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.Rect.collidepoint(pygame.Rect(180, 66, 96, 64), event.pos) and event.button == 1:
            global zoom_display
            zoom_display = not zoom_display
        else:
            rot.handle_event(event)
            button_rot.handle_event(event)
            button_a.handle_event(event)
            button_b.handle_event(event)
            button_c.handle_event(event)

        screen.blit(board, screen.get_rect())
        screen.blit(surface, (180, 66))
        if zoom_display:
            screen.blit(pygame.transform.scale(
                surface, (96*2, 64*2)), (0, screen.get_rect().bottom-64*2))
        pygame.draw.rect(screen, (255, 0, 0), button_rot.rect(), 5)
        pygame.draw.rect(screen, (255, 0, 0), button_a.rect(), 5)
        pygame.draw.rect(screen, (255, 0, 0), button_b.rect(), 5)
        pygame.draw.rect(screen, (255, 0, 0), button_c.rect(), 5)
        pygame.display.flip()


def main():
    global screen, surface, rot, button_rot, button_a, button_b, button_c, board

    pygame.init()
    board = pygame.image.load("software/eemon42.png")
    pygame.display.set_caption("EEMON42 Simulator")
    screen = pygame.display.set_mode(board.get_size())
    surface = pygame.surface.Surface((96, 64))

    display = SimDisplay(surface)
    rot = SimRotary()
    button_rot = SimButton(pygame.Rect(
        169, 165, 58, 47))
    button_a = SimButton(pygame.Rect(
        246, 161, 26, 28))
    button_b = SimButton(pygame.Rect(
        246, 203, 26, 28))
    button_c = SimButton(pygame.Rect(
        246, 245, 26, 28))

    gui = GUI(display, rot, button_rot, button_a,
              button_b, button_c, event_loop=event_loop)
    print(gui.show_text_input(0, 0, 8))


main()
