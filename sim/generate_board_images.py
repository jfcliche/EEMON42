#!/usr/bin/env python3
"""Generate EEMON42 simulator board PNGs (run once after layout changes)."""

import os

import pygame

SIM_DIR = os.path.dirname(os.path.abspath(__file__))

PCB = (40, 44, 48)
PCB_EDGE = (60, 65, 70)
BEZEL = (18, 18, 20)
SCREEN_BG = (0, 0, 0)
BUTTON_FACE = (90, 92, 98)
BUTTON_EDGE = (130, 132, 140)
LABEL = (180, 185, 195)


def _draw_board(width, height, display_pos, display_size, button_rects, labels, path):
    surf = pygame.Surface((width, height))
    surf.fill(PCB)
    pygame.draw.rect(surf, PCB_EDGE, (8, 8, width - 16, height - 16), 2)

    dx, dy = display_pos
    dw, dh = display_size
    pygame.draw.rect(surf, BEZEL, (dx - 5, dy - 5, dw + 10, dh + 10))
    pygame.draw.rect(surf, SCREEN_BG, (dx, dy, dw, dh))

    font = pygame.font.SysFont("dejavusans", 11)
    title = font.render("EEMON42", True, LABEL)
    surf.blit(title, (16, 12))

    for name, rect in button_rects.items():
        pygame.draw.rect(surf, BUTTON_FACE, rect, border_radius=5)
        pygame.draw.rect(surf, BUTTON_EDGE, rect, 2, border_radius=5)
        if name in labels:
            txt = font.render(labels[name], True, LABEL)
            surf.blit(txt, (rect.x + 4, rect.y + rect.h // 2 - 6))

    dw_label = font.render(f"{dw}x{dh}", True, LABEL)
    surf.blit(dw_label, (dx, dy + dh + 6))

    out = os.path.join(SIM_DIR, path)
    pygame.image.save(surf, out)
    print(f"Wrote {out}")


def main():
    pygame.init()

    _draw_board(
        width=400,
        height=320,
        display_pos=(180, 66),
        display_size=(96, 64),
        button_rects={
            "rot": pygame.Rect(169, 165, 58, 47),
            "b": pygame.Rect(246, 161, 26, 28),
            "c": pygame.Rect(246, 203, 26, 28),
            "a": pygame.Rect(246, 245, 26, 28),
        },
        labels={"a": "A", "b": "B", "c": "C", "rot": "ENC"},
        path="eemon42_ssd1331.png",
    )

    _draw_board(
        width=420,
        height=520,
        display_pos=(120, 44),
        display_size=(128, 160),
        button_rects={
            "rot": pygame.Rect(300, 280, 58, 47),
            "b": pygame.Rect(360, 276, 26, 28),
            "c": pygame.Rect(360, 318, 26, 28),
            "a": pygame.Rect(360, 360, 26, 28),
        },
        labels={"a": "A", "b": "B", "c": "C", "rot": "ENC"},
        path="eemon42_st7735.png",
    )

    pygame.quit()


if __name__ == "__main__":
    main()
