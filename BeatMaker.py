from config import *
import pygame
from pygame import mixer
from typing import Literal


class BeatMaker:
    pygame.init()
    pygame.mixer.set_num_channels(INSTRUMENT_COUNT * 3)

    save_file = open('saved_beats.txt', 'w+')
    saved_beats = [line for line in save_file.readlines()]

    label_font = pygame.font.Font('freesansbold.ttf', 28)
    medium_font = pygame.font.Font('freesansbold.ttf', 18)

    BPM = 240
    BEAT_COUNT = 8
    sounds = (
        mixer.Sound(r'sounds\hi hat.WAV'), mixer.Sound(r'sounds\snare.WAV'),
        mixer.Sound(r'sounds\kick.WAV'), mixer.Sound(r'sounds\crash.wav'),
        mixer.Sound(r'sounds\clap.wav'), mixer.Sound(r'sounds\tom.WAV'),
    )

    def __init__(self):
        self._screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )
        pygame.display.set_caption('Beat Maker')

        self._timer = pygame.time.Clock()

        self._clicked_boxes = [[-1 for _ in range(self.BEAT_COUNT)]
                               for _ in range(INSTRUMENT_COUNT)]
        self._active_instruments = [1 for _ in range(INSTRUMENT_COUNT)]

        self.is_playing = True
        self._was_beat_changed = True

        self.active_beat = 0
        self.active_length = 0

        self.sound_dict: [int, pygame.mixer.Sound] = {
            idx: self.sounds[idx] for idx in range(INSTRUMENT_COUNT)
        }

        self._save_menu = False
        self._load_menu = False

        self._run(non_stop=True)

    def _handle_events(self, boxes: list[...],
                       bpm_add_rect, bpm_sub_rect,
                       beat_add_rect, beat_sub_rect,
                       clear_button_rect,
                       save_button_rect, load_button_rect,
                       # exit_button_rect,
                       instrument_rects: list[...]) -> bool:
        app_exit = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_exit = True

            if event.type == pygame.MOUSEBUTTONDOWN \
                    and not self._save_menu and not self._load_menu:
                for box in boxes:
                    if box[0].collidepoint(event.pos):
                        box_cords = box[1]
                        self._clicked_boxes[box_cords[1]][box_cords[0]] *= -1

            if event.type == pygame.MOUSEBUTTONUP \
                    and not self._save_menu and not self._load_menu:
                if self.play_pause.collidepoint(event.pos):
                    self.is_playing = not self.is_playing

                elif bpm_add_rect.collidepoint(event.pos):
                    self.BPM += 5
                elif bpm_sub_rect.collidepoint(event.pos) and self.BPM > 5:
                    self.BPM -= 5

                elif beat_add_rect.collidepoint(event.pos):
                    self.BEAT_COUNT += 1
                    for idx, _ in enumerate(self._clicked_boxes):
                        self._clicked_boxes[idx].append(-1)
                elif beat_sub_rect.collidepoint(event.pos) and self.BEAT_COUNT > 1:
                    self.BEAT_COUNT -= 1
                    for idx, _ in enumerate(self._clicked_boxes):
                        self._clicked_boxes[idx].pop()

                elif clear_button_rect.collidepoint(event.pos):
                    self._clicked_boxes = [[-1 for _ in range(self.BEAT_COUNT)]
                                           for _ in range(INSTRUMENT_COUNT)]

                '''
                elif save_button_rect.collidepoint(event.pos):
                    self._save_menu = True
                elif load_button_rect.collidepoint(event.pos):
                    self._load_menu = True
                '''

                for idx, rect in enumerate(instrument_rects):
                    if rect.collidepoint(event.pos):
                        self._active_instruments[idx] *= -1

            '''
            elif event.type == pygame.MOUSEBUTTONUP:
                if exit_button_rect.collidepoint(event.pos):
                    self._save_menu = False
                    self._load_menu = False
                    self.is_playing = True
            '''

        return app_exit

    def _run(self, *, non_stop: bool = False) -> None:
        app_exit = False
        while not app_exit:
            self._timer.tick(FPS)
            self._screen.fill(RGB_BLACK)

            '''
            exit_button_rect = None
            if self._save_menu:
                exit_button_rect = self.render_save_menu()
            elif self._load_menu:
                exit_button_rect = self.render_load_menu()
            '''

            boxes = self.render_grid()
            self.render_pause_button()

            app_exit = self._handle_events(
                boxes,
                *self.render_bpm_buttons(),
                *self.render_beat_buttons(),
                self.render_reset_button(),
                *self.render_save_load_buttons(),
                # exit_button_rect,
                [pygame.rect.Rect((0, i * 100), (200, 100))
                 for i in range(INSTRUMENT_COUNT)]
            )

            if self._was_beat_changed:
                self.play_notes()
                self._was_beat_changed = False

            self._set_selected_actives()

            if not non_stop:
                break

            pygame.display.flip()

    def play_notes(self) -> None:
        for idx, box in enumerate(self._clicked_boxes):
            if box[self.active_beat] == 1:
                if self._active_instruments[idx] == 1:
                    self.sound_dict[idx].play()

    def render_grid(self) -> list[tuple[pygame.Rect, tuple[int, int]]]:
        pygame.draw.rect(
            self._screen, RGB_GRAY,
            [0, 0, 200, HEIGHT - 200],
            width=5
        )
        pygame.draw.rect(
            self._screen, RGB_GRAY,
            [0, HEIGHT - 200, WIDTH, 200],
            width=5
        )

        boxes = []
        colors = (RGB_DARK_GRAY, RGB_WHITE, RGB_DARK_GRAY)
        instrument_names = (
            'Hi Hat', 'Hit Snare', 'Bass Drum',
            'Crash', 'Clap', 'Floor Tom',
        )
        for idx, name in enumerate(instrument_names):
            self._blit_label(name, (30, 40 + 100 * idx),
                             color=colors[self._active_instruments[idx]])
            pygame.draw.line(
                self._screen,
                RGB_GRAY,
                (0, (idx + 1) * 100),
                (195, (idx + 1) * 100),
                width=5
            )

        for i in range(self.BEAT_COUNT):
            for j in range(INSTRUMENT_COUNT):
                if self._clicked_boxes[j][i] == -1:
                    color = RGB_GRAY
                else:
                    color = RGB_GREEN \
                        if self._active_instruments[j] == 1 \
                        else RGB_DARK_GRAY

                rect = pygame.draw.rect(
                    self._screen, color,
                    [i * ((WIDTH - 200) // self.BEAT_COUNT) + 205,
                     (j * 100) + 5,
                     (WIDTH - 200) // self.BEAT_COUNT - 10,
                     (HEIGHT - 200) // INSTRUMENT_COUNT - 10
                     ],
                    width=0, border_radius=3
                )
                pygame.draw.rect(
                    self._screen, RGB_GOLD,
                    [i * ((WIDTH - 200) // self.BEAT_COUNT) + 200,
                     (j * 100),
                     (WIDTH - 200) // self.BEAT_COUNT,
                     (HEIGHT - 200) // INSTRUMENT_COUNT
                     ],
                    width=5, border_radius=5
                )
                pygame.draw.rect(
                    self._screen, RGB_BLACK,
                    [i * ((WIDTH - 200) // self.BEAT_COUNT) + 200,
                     (j * 100),
                     (WIDTH - 200) // self.BEAT_COUNT,
                     (HEIGHT - 200) // INSTRUMENT_COUNT
                     ],
                    width=2, border_radius=5
                )

                boxes.append((rect, rect_cords := (i, j)))

        pygame.draw.rect(
                self._screen, RGB_BLUE,
                [self.active_beat * ((WIDTH - 200) // self.BEAT_COUNT) + 200,
                 0, ((WIDTH - 200) // self.BEAT_COUNT), INSTRUMENT_COUNT * 100],
                width=5, border_radius=3
            )
        return boxes

    def render_pause_button(self) -> None:
        # lower menu buttons
        self.play_pause = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [50, HEIGHT - 150, 200, 100],
            width=0, border_radius=5
        )
        self._blit_label('Play/Pause', (70, HEIGHT - 115))

        self._blit_label(
            'Playing' if self.is_playing else 'Paused',
            (115, HEIGHT - 80),
            on_font='medium', color=RGB_DARK_GRAY
        )

    def render_bpm_buttons(self) -> tuple[pygame.Rect, pygame.Rect]:
        pygame.draw.rect(
            self._screen, RGB_GRAY,
            [300, HEIGHT - 150, 200, 100],
            width=5, border_radius=5
        )
        bpm_enhancer_rect = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [510, HEIGHT - 150, 48, 48],
            width=0, border_radius=5
        )
        bpm_reducer_rect = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [510, HEIGHT - 100, 48, 48],
            width=0, border_radius=5
        )

        self._blit_label('Beats Per Minute', (325, HEIGHT - 115),
                         on_font='medium')
        self._blit_label(f'{self.BPM}', (385, HEIGHT - 95),
                         on_font='medium')
        self._blit_label('+5', (525, HEIGHT - 135),
                         on_font='medium')
        self._blit_label('-5', (525, HEIGHT - 85),
                         on_font='medium')

        return bpm_enhancer_rect, bpm_reducer_rect

    def render_beat_buttons(self) -> tuple[pygame.Rect, pygame.Rect]:
        pygame.draw.rect(
            self._screen, RGB_GRAY,
            [600, HEIGHT - 150, 200, 100],
            width=5, border_radius=5
        )
        beat_enhancer_rect = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [810, HEIGHT - 150, 48, 48],
            width=0, border_radius=5
        )
        beat_reducer_rect = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [810, HEIGHT - 100, 48, 48],
            width=0, border_radius=5
        )

        self._blit_label('Beats In Loop', (638, HEIGHT - 115),
                         on_font='medium')
        self._blit_label(f'{self.BEAT_COUNT}', (695, HEIGHT - 95),
                         on_font='medium')
        self._blit_label('+1', (825, HEIGHT - 135),
                         on_font='medium')
        self._blit_label('-1', (825, HEIGHT - 85),
                         on_font='medium')

        return beat_enhancer_rect, beat_reducer_rect

    def render_save_load_buttons(self) -> tuple[pygame.Rect, pygame.Rect]:
        save_button = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [900, HEIGHT - 150, 200, 48],
            width=0, border_radius=5
        )
        load_button = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [900, HEIGHT - 100, 200, 48],
            width=0, border_radius=5
        )

        self._blit_label('Save Beat', (930, HEIGHT - 140))
        self._blit_label('Load Beat', (930, HEIGHT - 90))

        return save_button, load_button

    def render_reset_button(self) -> pygame.Rect:
        reset_button = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [1150, HEIGHT - 150, 200, 100],
            width=0, border_radius=5
        )
        self._blit_label('Clear Board', (1165, HEIGHT - 115))

        return reset_button

    '''
    def render_save_menu(self) -> pygame.Rect:
        pygame.draw.rect(self._screen, RGB_BLACK, [0, 0, WIDTH, HEIGHT])
        exit_button = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [WIDTH - 200, HEIGHT - 100, 180, 90],
            width=0, border_radius=5
        )
        self._blit_label('Close', (WIDTH - 160, HEIGHT - 70))

        return exit_button

    def render_load_menu(self) -> pygame.Rect:
        pygame.draw.rect(self._screen, RGB_BLACK, [0, 0, WIDTH, HEIGHT])
        exit_button = pygame.draw.rect(
            self._screen, RGB_GRAY,
            [WIDTH - 200, HEIGHT - 100, 180, 90],
            width=0, border_radius=5
        )
        self._blit_label('Load', (WIDTH - 160, HEIGHT - 70))

        return exit_button
    '''

    def _set_selected_actives(self) -> None:
        beat_length = 3600 // self.BPM
        if self.is_playing:
            if self.active_length < beat_length:
                self.active_length += 1
            else:
                self.active_length = 0
                if self.active_beat < self.BEAT_COUNT - 1:
                    self.active_beat += 1
                else:
                    self.active_beat = 0
                self._was_beat_changed = True

    def _blit_label(self, name: str, cords: tuple[int, int],
                    *,
                    on_font: Literal['label', 'medium'] = 'label',
                    color: tuple[int, int, int] = RGB_WHITE) -> None:
        label_text = self.label_font.render(name, True, color) \
            if on_font == 'label' else \
            self.medium_font.render(name, True, color)

        self._screen.blit(label_text, cords)
