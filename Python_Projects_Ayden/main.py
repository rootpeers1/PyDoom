import pygame as pg
import sys
import threading
import warnings
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *

class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.rect = pg.Rect(x, y, width, height)
        self.action = action  # Function to call when button is clicked

    def draw(self, screen):
        font = pg.font.SysFont("Arial", 36)
        pg.draw.rect(screen, (0, 0, 0), self.rect)  # Button color
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def on_click(self):
        if self.action:
            self.action()  # Call the action function if defined

class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(True)  # Allow mouse visibility in menu
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(False)  # Allow mouse to move freely in menu
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.loading_bar_width = RES[0] // 2  # Width of the loading bar
        self.loading_bar_height = 30  # Height of the loading bar
        self.loading_percentage = 0  # Initial loading percentage

        self.game_initialized = False  # Flag to track if game has been initialized
        self.new_game()

    def new_game(self):
        if not self.game_initialized:
            # Show the loading screen only if it's the first time initializing the game
            self.show_loading_screen()

        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

        # Mark the game as initialized
        self.game_initialized = True

        # After loading, clear loading screen and show main menu
        self.loading_percentage = 100
        pg.time.wait(500)  # Wait for half a second to show the completion
        self.loading_percentage = 0  # Reset the loading bar for future use
        self.show_main_menu()  # Show the main menu after loading is done

    def show_loading_screen(self):
        """Displays a loading bar while the game is initializing."""
        while self.loading_percentage < 100:
            self.screen.fill((0, 0, 0))  # Fill the screen with black
            # Draw the loading bar background (empty)
            pg.draw.rect(self.screen, (200, 200, 200), (RES[0] // 4, RES[1] // 2, self.loading_bar_width, self.loading_bar_height))
            # Draw the loading progress (filled part)
            pg.draw.rect(self.screen, (204, 0, 0), (RES[0] // 4, RES[1] // 2, self.loading_bar_width * (self.loading_percentage / 100), self.loading_bar_height))
            
            # Draw loading text
            font = pg.font.SysFont("Arial", 24)
            text = font.render(f"Loading the experience.. {int(self.loading_percentage)}%", True, (255, 255, 255))
            text_rect = text.get_rect(center=(RES[0] // 2, RES[1] // 2 - 40))
            self.screen.blit(text, text_rect)

            # Update the display
            pg.display.flip()
            
            # Simulate loading by incrementing the percentage (you could change this logic to track actual loading events)
            pg.time.delay(50)  # Delay to simulate load time
            self.loading_percentage += 1
            
            # Handle events like quitting during loading
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()

    def show_main_menu(self):
        """Displays the main menu after loading."""
        pg.mouse.set_visible(True)  # Make sure the mouse cursor is visible in the menu
        pg.event.set_grab(False)  # Release the mouse capture (allow the mouse to leave the window)
        menu_font = pg.font.SysFont("Arial", 36)
        menu_running = True
        
        # Load the Doom logo image
        doom_image = pg.image.load("doom.png")  # Replace with the actual path to your image
        
        # Resize the image (scale down)
        doom_width = 400  # New width
        doom_height = 200  # New height
        doom_image = pg.transform.scale(doom_image, (doom_width, doom_height))  # Resize the image
        
        # Get the new rect after resizing
        doom_rect = doom_image.get_rect(center=(RES[0] // 2, RES[1] // 3))  # Center the image on the screen
        
        # Create buttons
        start_button = Button("Start Game", RES[0] // 2 - 100, RES[1] // 2 - 50, 200, 50, self.start_game)
        quit_button = Button("Quit", RES[0] // 2 - 100, RES[1] // 2 + 50, 200, 50, self.quit_game)
        
        rotation_angle = 0  # Initialize rotation angle

        while menu_running:
            self.screen.fill((0, 0, 0))  # Fill the screen with black for the menu
            
            # Rotate the Doom image
            rotated_doom = pg.transform.rotate(doom_image, rotation_angle)
            rotated_rect = rotated_doom.get_rect(center=doom_rect.center)  # Keep the image centered
            
            # Draw the rotated Doom image
            self.screen.blit(rotated_doom, rotated_rect)
            
            # Draw buttons
            start_button.draw(self.screen)
            quit_button.draw(self.screen)
            
            # Handle mouse hover and clicks
            mouse_pos = pg.mouse.get_pos()
            if start_button.is_hovered(mouse_pos):
                if pg.mouse.get_pressed()[0]:  # Left mouse button clicked
                    start_button.on_click()
            if quit_button.is_hovered(mouse_pos):
                if pg.mouse.get_pressed()[0]:  # Left mouse button clicked
                    quit_button.on_click()

            # Update the display
            pg.display.flip()

            # Handle events (key presses for menu options)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:  # Enter key to start game
                        self.start_game()
                        menu_running = False
                    elif event.key == pg.K_ESCAPE:  # Escape key to quit
                        pg.quit()
                        sys.exit()

            # Increment the rotation angle to create a slower spinning effect
            rotation_angle += 0.2  # Slower rotation speed
            if rotation_angle >= 360:
                rotation_angle = 0  # Reset the angle to prevent overflow

    def start_game(self):
        """Starts the game after the menu."""
        print("Starting the game!")
        pg.mouse.set_visible(False)  # Hide the cursor
        pg.event.set_grab(True)  # Capture the mouse, preventing it from leaving the window
        self.run()

    def quit_game(self):
        """Handles quitting the game."""
        pg.quit()
        sys.exit()

    def reset_game(self):
        """Resets the game state without showing the loading screen."""
        self.player.reset()
        self.object_handler.reset()
        self.weapon.reset()
        self.sound.reset()
        self.map.reset()
        self.pathfinding.reset()

    def handle_death(self):
        """Handles the player's death."""
        self.reset_game()  # Reset the game state
        self.show_main_menu()  # Show the main menu (or game over screen)

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        self.object_renderer.draw()
        self.weapon.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
