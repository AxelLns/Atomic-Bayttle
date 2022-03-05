import pygame
import json

pygame.init()

class Axis:
    value = 0
    increment = 0.1
    deadzone = (0,1)
   
    @staticmethod
    def bound(x:int,bounds:tuple):
        if bounds[0]> bounds[1]:
            bounds = bounds[::-1]
        return min(max(x,bounds[0]),bounds[1])

    @staticmethod
    def sign(x):
        if x>=0:
            return 1
        else:
            return -1

    @staticmethod
    def same_sign(x,y):
        if Axis.sign(x) == Axis.sign(y):
            return True
        else:
            return False

    def update(self,x_press:bool=False,y_press:bool=False):
        if not x_press and not y_press:
            self.value = self.bound(self.value - (self.increment)*self.sign(self.value)*1.25,(0,self.sign(self.value))) 
        elif x_press and y_press:
            return
        else:
            direction = 1 if x_press else -1
            if not self.same_sign(self.value,direction):
                self.value = 0
            self.value += self.increment * direction
        self.value = self.bound(self.value,(0,self.sign(self.value)))

    def __mul__(self, other):
        return self.get()*other

    def get(self):
        if self.value==0 or abs(self.value)<self.deadzone[0]:
            return 0
        return self.value if abs(self.value)<self.deadzone[1] else self.deadzone[1]*self.sign(self.value)

    def set(self,value:int):
        self.value = value

    def __call__(self):
        return self.get()

    def __abs__(self):
        return abs(self.get())

class sprite_sheet(pygame.Surface):

    def __init__(self,path,size:tuple[int]):
        _img = pygame.image.load(path)
        super().__init__(_img.get_size(),pygame.SRCALPHA)
        self.blit(_img,(0,0))

        self.tile_size = size
        self.render_size = size
        self.x_nb = (self.get_width()//self.tile_size[0])
        self.y_nb = (self.get_height()//self.tile_size[1])

    def __getitem__(self, key):
        x = (key%self.x_nb)*self.tile_size[0]
        y = ((key//self.x_nb)%self.y_nb)*self.tile_size[1]

        _surf = pygame.Surface(self.tile_size,pygame.SRCALPHA)

        _surf.blit(self,(0,0),pygame.Rect(x,y,*self.tile_size))

        _surf = pygame.transform.scale(_surf,self.render_size)

        return _surf

    def config(self,size):
        self.render_size = size

class animation_Manager(object):
    
    def __init__(self):
        self.frame = 0
        self.incrementor = 1
        self.annim_speed_factor = 1
        self.spritesheets:dict[list[sprite_sheet]] = {}
        self.links:dict[list] = {}
        self.__loaded:sprite_sheet = None
        self.__loaded_name:str = None

    @property
    def surface(self):
        self.frame += self.incrementor*self.annim_speed_factor
        return self.__loaded[int(self.frame)]
    
    @property
    def actual_surface(self):
        return self.__loaded[int(self.frame)]
    
    def add_annimation(self,name,spritesheet:sprite_sheet,_frame:int):
        _increment = 1/_frame
        self.spritesheets[name or f"animation-{pygame.time.get_ticks()}"] = [spritesheet,_increment]

    def load(self,name):
        if name in self.spritesheets.keys():
            if name!=self.__loaded_name:
                self.__loaded = self.spritesheets[name][0]
                self.__loaded_name = name
                self.frame = 0
                self.incrementor = self.spritesheets[name][1]
        else:
            raise AttributeError

class Vector2:
    """
    class Vecteur 2 dimension pour un stockage des position et range plus facile qu'avec un array tuple
    """
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'({self.x},{self.y})'

    def __call__(self) -> tuple:
        """return a tuple of the vector"""
        return (self.x,self.y)

class Key:
    def __init__(self,key:int,alias:int=None):
        self.key = key
        self.alias = alias
        self.name = pygame.key.name(key)
        self.name_alias = pygame.key.name(alias) if alias else None

    @property
    def is_pressed(self):
        state = pygame.key.get_pressed()
        return state[self.key] or (state[self.alias] if self.alias else False)

class Keyboard:
    right = Key(pygame.K_d,pygame.K_RIGHT)
    left = Key(pygame.K_q,pygame.K_LEFT)
    up = Key(pygame.K_z,pygame.K_UP)
    down = Key(pygame.K_s,pygame.K_DOWN)
    jump = Key(pygame.K_SPACE)
    interact = Key(pygame.K_e)
    pause = Key(pygame.K_ESCAPE)
    end_turn = Key(pygame.K_RETURN)
    inventory = Key(pygame.K_i)

    Manette = False

    @staticmethod
    def load(path):
        settings = json.load(open(path / "data" / "settings.json"))
        for key,val in settings["keys"].items():
            if type(val)!=list:
                open(path / "data" / "log.txt","a").write("Error while loading key from the settings")
                continue
            setattr(Keyboard,key,Key(val[0], val[1] if val[1]!=-1 else None))
   
    @staticmethod
    def save(path):
        settings = json.load(open(path / "data" / "settings.json"))
        settings["keys"] = dict()
        for key,val in Keyboard.__dict__.items():
            if type(val)==Key:
                settings["keys"][key] = [getattr(Keyboard,key).key,getattr(Keyboard,key).alias or -1]
        json.dump(settings,open(path / "data" / "settings.json","w"))

class MixeurAudio:
    pygame.mixer.set_num_channels(6)

    __musicMixer = pygame.mixer.Channel(1)
    __effectMixerCallback = pygame.mixer.Channel(2)
    __listEffectChannel = []
    volume_musique = 1
    volume_effect = 1
    music_factor = None
    gn = None

    @staticmethod
    def set_musique(path,loops=True):
        MixeurAudio.__musicMixer.set_volume(MixeurAudio.volume_musique)
        MixeurAudio.__musicMixer.play(pygame.mixer.Sound(path),-1 if loops else 0)

    @staticmethod
    def update_musique():
        if MixeurAudio.__musicMixer.get_queue() == None:
            _buffer = MixeurAudio.gn.Sounds_buffer.get()
            MixeurAudio.__musicMixer.queue(pygame.mixer.Sound(_buffer))
        elif not MixeurAudio.__musicMixer.get_busy() and not MixeurAudio.__musicMixer.get_queue():
            _buffer = MixeurAudio.gn.Sounds_buffer.get()
            MixeurAudio.__musicMixer.play(pygame.mixer.Sound(_buffer))

    @staticmethod
    def play_effect(path,volume=None):
        mixer = pygame.mixer.find_channel() or MixeurAudio.__effectMixerCallback
        mixer.set_volume(volume or MixeurAudio.volume_effect)
        mixer.play(pygame.mixer.Sound(path))

    @staticmethod
    def play_until_Stop(path,volume=None):
        mixer = pygame.mixer.find_channel() or MixeurAudio.__effectMixerCallback
        mixer.set_volume(volume or MixeurAudio.volume_effect)
        mixer.play(pygame.mixer.Sound(path),loops=-1)
        MixeurAudio.__listEffectChannel.append(mixer)
        def func():
            mixer.stop()
            MixeurAudio.__listEffectChannel.remove(mixer)
        return func

    @staticmethod
    def stop(channel:str="all"):
        """ all / music"""
        if channel=="all": pygame.mixer.fadeout(2000)
        if channel=="music": MixeurAudio.__musicMixer.fadeout(2000)

    @staticmethod
    def update_volume():
        MixeurAudio.__musicMixer.set_volume(MixeurAudio.volume_musique)
        for mixer in MixeurAudio.__listEffectChannel:
            mixer.set_volume(MixeurAudio.volume_effect)