import pygame
from pygame.locals import *
from src.tools.constant import PATH

pygame.init()
INFO = pygame.display.Info()
INFO = pygame.display.Info()

pygame.display.set_mode((int(INFO.current_w*0.7),int(INFO.current_h*0.7)), OPENGL|DOUBLEBUF,depth=16)
pygame.display.init()
pygame.display.set_icon(pygame.image.load(PATH / "assets" / "ico.png"))

import src.tools.opengl_pygame as gl
from src.tools.tools import MixeurAudio
from src.tools.constant import EndPartie
import src.menu_main as menu_main
#import test
import src.game_manager as game_manager
import src.map.Background as bg

# there is only one game so we do not need a instance, modifying dinamically the class allow us to access it without an instance
class Game:
    running = True
    clock = pygame.time.Clock()
    serialized = 0
    partie = None

    def run():
        MixeurAudio.set_musique(path=PATH / "assets" / "music" / "main-loop.wav")
        MixeurAudio.play_until_Stop(PATH / "assets" / "sound" / "water_effect_loop.wav",volume=0.35)
        gl.config(INFO)
        
        menu_main.setup_manager()
        Camera.maximise = False

        while Game.running:
            if Game.partie:
                try:
                    Game.partie.Update()
                except EndPartie:
                    Game.partie = None
                    menu_main.setup_manager()
            else:
                menu_main.game.Update()

            gl.cleangl()
            if Game.partie or True:
                Camera.render_bg()
            Camera.render()
            
            #print(Game.clock.get_fps())
            pygame.display.flip()

            Game.serialized = Game.clock.tick(60)/16.7
        else:
            raise SystemExit

    def start_partie(j1,j2):
        Game.partie = game_manager.Partie()
        Game.partie.add_player("j1.1",j1, weapon=True)
        Game.partie.add_player("j2.1",j2,True, weapon=True)
        #Game.partie.add_player("j1.2",j1,True) # ajouter avec respawn pour éviter le bordel
        #Game.partie.add_player("j2.3",j2,True)
        MixeurAudio.gn.reset()
        Game.partie.add_object("test",(400,200), PATH / "assets" / "weapons" / "mortier1.png")
        Camera.HUD = True
        Camera.maximise = True
        MixeurAudio.stop("music")

class Camera:
    x = 0
    y = 0
    zoom = 1
    zoom_offset = (1,1)
    maximise = True
    HUD = True
    _off_screen:pygame.Surface = pygame.Surface((1536,864),flags=SRCALPHA)
    _screen_UI:pygame.Surface = pygame.Surface((1280,720),flags=SRCALPHA)
    cache = False
    _bg = bg.background()

    def render() -> None:
        Camera.zoom = max(1,Camera.zoom)
        Camera.x,Camera.y,Camera.zoom_offset = gl.surfaceToScreen(Camera._off_screen,(Camera.x,Camera.y),Camera.zoom,maximize=Camera.maximise)
        # add when we will need UI, for now render is not fully optimised so we wont render useless surface
        if Camera.HUD:
            gl.uiToScreen(Camera._screen_UI if not Camera.cache else None) # try to blit only if not null take more time to check than blit it anyway
            Camera.cache = True

    def to_virtual(x,y) -> tuple[int,int]:

        x_zoom = Camera.zoom*Camera.zoom_offset[0]
        local = x/INFO.current_w - 0.5
        _x = local/x_zoom + Camera.x + 0.5

        y_zoom = Camera.zoom*Camera.zoom_offset[1]
        local = y/INFO.current_h - 0.5
        _y = local/y_zoom + Camera.y + 0.5

        return (int(_x*Camera._off_screen.get_width()), int(_y*Camera._off_screen.get_height()))

    def to_absolute(x,y) -> tuple[int,int]:

        x_zoom = Camera.zoom*Camera.zoom_offset[0]
        _x = (x/Camera._off_screen.get_width() -0.5 - Camera.x) * x_zoom + 0.5

        y_zoom = Camera.zoom*Camera.zoom_offset[1]
        _y = (y/Camera._off_screen.get_height() -0.5 - Camera.y) * y_zoom + 0.5

        return (int(_x * INFO.current_w),int(_y * INFO.current_h))

    def render_bg():
        Camera.zoom = max(1,Camera.zoom)
        _bg, _bgsize, _bcloud,_bx,_bsize, _ccloud,_cx,_csize = next(Camera._bg) # background dynamique
        Camera.x,Camera.y,Camera.zoom_offset = gl.simpleRender(_bg,(Camera.x,Camera.y),_bgsize,Camera.zoom,maximize=Camera.maximise)
        gl.simpleRender(_bcloud,(_bx,Camera.y),_bsize,Camera.zoom,maximize=Camera.maximise,offset=(-Camera.x*Camera.zoom*2,0))
        gl.simpleRender(_ccloud,(_cx,Camera.y),_csize,Camera.zoom,maximize=Camera.maximise,offset=(-Camera.x*Camera.zoom*2,0))

# class parent now accessible to childs too
game_manager.GAME = menu_main.GAME= Game
game_manager.CAMERA = menu_main.CAMERA = Camera
