# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 15:31:27 2020

@author: German
"""



import arcade 


ANCHO= 1600
ALTO= 640
SCALING= 1.5
PLAYER_MOVEMENT_SPEED = 10
PLAYER_JUMP_SPEED = 14
MARGEN_IZQUIERDO = 200
MARGEN_DERECHO = 200
scaling= 1

puntaje = 0

class Mapa(arcade.Window):
    
    def __init__(self):
        super().__init__(ANCHO, ALTO, "Mapa", False, True)
        
        arcade.set_background_color(arcade.color.AERO_BLUE)


 
class GameOver(arcade.View):
    
    def __init__(self):        
        super().__init__()
       #self.texture = arcade.load_texture("imagenes/wasted.png")
        #arcade.set_viewport(0,640,1600,640) """   
    def on_draw(self):
        arcade.start_render() 
        
        """self.texture.draw_sized(800/2,600/2,800,600)"""
        
        arcade.draw_text("han matado a Covid-19!",ANCHO//2 , ALTO//2 + 100, arcade.color.BLACK,48)
        arcade.draw_text(f"Contagiaste a {puntaje} humanos",ANCHO//2 , ALTO//2 - 50 , arcade.color.BLACK,24)
        arcade.draw_text("Presiona Enter para reiniciar",ANCHO//2 ,  100, arcade.color.BLACK,18)
     
    
                         
    
    def on_key_release(self, key, modifiers):
        if key == arcade.key.ENTER:
            global puntaje
            puntaje = 0                     
            mostrar_juego()
    
class Juego(arcade.View):
    
    def __init__(self):        
        super().__init__()
        
       
    def setup(self):
        self.musica = arcade.Sound("sonidos/fondo.mp3", True)
        self.musica.play(volume=0.05)
        self.sonido_personas= arcade.Sound("sonidos/oof.wav", False)
        self.perdiste= arcade.Sound("sonidos/game_over.mp3", False)
        #lista de personahes en la pantalla
        self.view_bottom =0
        self.view_left=0
        
        
        self.personajes = arcade.SpriteList()
        self.personaje = arcade.Sprite("imagenes/Green_Virus.png", SCALING)
        self.personaje.center_x= ALTO
        self.personaje.center_y= 1000
        self.personajes.append(self.personaje)
        # leer el mapa
       
        self.map = arcade.tilemap.read_tmx("Mapas/mapa_scrolling.tmx")
        #cargar los layers dentro del sprite list
        self.piso = arcade.SpriteList(use_spatial_hash = True)
        self.piso.extend(arcade.tilemap.process_layer(self.map, "piso"))
        
        borde_izquierdo = arcade.SpriteSolidColor(1 , ALTO*2, arcade.color.BLACK)
        borde_izquierdo.left = -1
        borde_izquierdo.bottom = -ALTO//2  
        self.piso.append(borde_izquierdo)
        borde_derecho = arcade.SpriteSolidColor(1 , ALTO*2, arcade.color.BLACK)
        borde_derecho.left = self.map.tile_size.width*self.map.map_size.width
        borde_derecho.bottom = -ALTO//2 
        self.piso.append(borde_derecho)
        
        self.vegetacion = arcade.SpriteList(use_spatial_hash = True)
        self.vegetacion.extend(arcade.tilemap.process_layer(self.map, "vegetacion"))
        self.edificios = arcade.SpriteList(use_spatial_hash = True)
        self.edificios.extend(arcade.tilemap.process_layer(self.map, "edificios")) 
        self.cielo = arcade.SpriteList(use_spatial_hash = True)
        self.cielo.extend(arcade.tilemap.process_layer(self.map, "cielo")) 
        self.personas = arcade.SpriteList(use_spatial_hash = True)
        self.personas.extend(arcade.tilemap.process_layer(self.map, "personas"))
        self.enemigos = arcade.tilemap.process_layer(self.map, "enemigos", scaling)
        
        for enemigo in self.enemigos:
            enemigo.change_x=2
        
        self.motor_fisica = arcade.PhysicsEnginePlatformer(self.personaje, self.piso)
        
        
        
    def on_draw(self):
        

        #comenzar dibujo
        arcade.start_render()
        
        
        
        self.personajes.draw()
        self.piso.draw()  
        self.vegetacion.draw()
        self.edificios.draw()
        self.cielo.draw()
        self.personas.draw()
        self.enemigos.draw()        
        
        arcade.draw_text(f"contagiados:{puntaje}" ,50 + self.view_left, ALTO- self.view_bottom,
                         arcade.csscolor.BLACK, 18)
        
    def on_update(self, delta_time):
        global puntaje
        #actualiza motor fisica
        self.motor_fisica.update()
        
        for enemigo in self.enemigos:
            tope = arcade.check_for_collision_with_list(enemigo, self.piso)            
            if enemigo.left <= 0 or enemigo.right >= ANCHO + self.view_left or len(tope) != 0:
                enemigo.change_x *= -1
        
        self.enemigos.update()
        
        muerte = arcade.check_for_collision_with_list(self.personaje, self.enemigos)
        if len(muerte) != 0:
            self.musica.stop()
            mostrar_game_over()
            self.perdiste.play(volume=0.05)
        for personaje in self.personajes:
            tope = arcade.check_for_collision_with_list(personaje, self.piso)
            if personaje.left <= 0 or personaje.right >= ANCHO+self.view_left or len(tope) != 0:
                self.musica.stop()
                mostrar_game_over()
                self.perdiste.play(volume=0.05)
        personas_contagiadas = arcade.check_for_collision_with_list(
            self.personaje, 
            self.personas
        )
        
        if len(personas_contagiadas) != 0:
            for persona in personas_contagiadas:
                
                puntaje += 1
               
        self.personas.update() 
        
        changed = False
        
        left_boundary = self.view_left + MARGEN_IZQUIERDO
        if self.personaje.left < left_boundary:
            self.view_left -= left_boundary - self.personaje.left
            if self.view_left< 0:
                self.view_left = 0
            changed = True
            
        right_boundary = self.view_left + ANCHO - MARGEN_DERECHO
        if self.personaje.right > right_boundary:
            self.view_left += self.personaje.right - right_boundary
            if self.view_left > self.map.map_size.width*self.map.tile_size.width - ANCHO:
                self.view_left = self.map.map_size.width*self.map.tile_size.width - ANCHO
            changed = True
        
        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            arcade.set_viewport(self.view_left,
                                ANCHO + self.view_left,
                                self.view_bottom,
                                ALTO + self.view_bottom)

        
    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.UP and self.motor_fisica.can_jump():
            self.personaje.change_y = PLAYER_JUMP_SPEED            
        elif key == arcade.key.LEFT:
            self.personaje.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT: 
            self.personaje.change_x = PLAYER_MOVEMENT_SPEED
    
        
    
    def on_key_release(self, key, modifiers): 
              
        if key == arcade.key.LEFT:
            self.personaje.change_x = 0
        elif key == arcade.key.RIGHT: 
            self.personaje.change_x = 0
    
    
def mostrar_juego():
    
    juego = Juego()
    juego.setup()
    arcade.get_window().show_view(juego)
    
def mostrar_game_over():
    
    game_over = GameOver()
    arcade.get_window().show_view(game_over)     

    
def main():
    
    Mapa()
    mostrar_juego()
    arcade.run()
    
main()    