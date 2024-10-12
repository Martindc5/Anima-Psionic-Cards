import kivy
kivy.require('2.3.0')
from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from sqlite3 import connect
from kivy.lang import Builder
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.popup import Popup


class MainWindow(Screen):

    def on_enter(self, *args):
        Clock.schedule_once(self.add_psiquicos, 0.1)
        Clock.schedule_once(self.add_button_newPsiquicos, 0.1)
        Clock.schedule_once(self.build_buttons, 0.1)
        
    def add_button_newPsiquicos(self, dt):
        # Obtener el BoxLayout
        tarjetas = self.ids.tarjetas

        btn = Button(
            background_normal=("DisciplineCards/AddPsiquico.png"), 
            size_hint= (None, 1),
            width= self.width * 0.8,
            background_color= (1, 1, 1, 1)
        )

        btn.bind(on_press=lambda instance:  self.change_screen("create_psiquico"))

        tarjetas.add_widget(btn)

    def add_psiquicos(self, dt): #Modificar para agregar un botón para borra psíquicos
        # Conexión a la DB
        conn = connect('PsionicData.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM MisPsiquicos")
        N = cursor.fetchall()[0][0]

        # Obtener el BoxLayout
        tarjetas = self.ids.tarjetas

        # Borra los botones anteriores para asegurarse de que no hay repetidos o actualizar los cambios
        tarjetas.clear_widgets()

        # Crear botones
        for i in range(N):
            cursor.execute("SELECT Nombre FROM MisPsiquicos LIMIT 1 OFFSET ?;", (i,))
            nombre = cursor.fetchall()[0][0]
            
            # Crear el botón
            btn = Button(
                text=nombre,
                size_hint=(None, 1),
                height=50,
                width=self.width * 0.8,
                background_color=(1, 1, 1, 1)
            )
            
            btn.bind(on_press=lambda instance, nombre=nombre: self.change_to_screen_show_psiquico(nombre))            
            tarjetas.add_widget(btn)

        conn.close()
        

    def build_buttons(self, dt):
        # Conexión a la DB
        conn = connect('PsionicData.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Disciplinas")
        N = cursor.fetchall()[0][0]

        # Obtener el BoxLayout
        box_layout = self.ids.tarjetas


        # Crear los botones
        for i in range(N):
            cursor.execute("SELECT Imagen FROM Disciplinas LIMIT 1 OFFSET ?;", (i,))
            imagen_source = cursor.fetchall()[0][0]
            cursor.execute("SELECT Nombre FROM Disciplinas LIMIT 1 OFFSET ?;", (i,))
            disciplina = cursor.fetchall()[0][0]
            
            # Crear el botón
            btn = Button(
                background_normal=(imagen_source), #Agrega la imagen dentro del botón
                size_hint=(None, 1),
                width=self.width * 0.8,
                background_color=(1, 1, 1, 1)
            )

            # Asignar el cambio de pantalla al botón
            btn.bind(on_press=lambda instance, disciplina=disciplina: self.on_button_press(disciplina))
            btn.bind(on_touch_move=lambda instance, touch, disciplina=disciplina: self.on_button_touch_move(disciplina, instance, touch))
                        
            # Añadir el botón al BoxLayout
            box_layout.add_widget(btn)

        conn.commit()
        conn.close()

    def on_button_touch_move(self, disciplina, instance, touch):
        # Cambiar de pantalla y añadir dinámicamente botones
        self.manager.current = "powers"
        self.manager.transition.direction = "up"
        app = App.get_running_app()
        app.root.get_screen("powers").add_dynamic_buttons(disciplina)

    
    # Cuando se pulsa una tarjeta
    def on_button_press(self, disciplina):
        
        #Se conecta a la Base de datos y la respuesta la asigna a un label
        conn = connect('PsionicData.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Descripcion FROM Disciplinas WHERE Nombre = ?;", (disciplina, ) )
        description = cursor.fetchall()[0][0]
        self.ids.output_label.text = description
        self.ids.output_label_up.text = disciplina
        conn.commit()
        conn.close()

    def change_to_screen_show_psiquico(self, psiquico):
        self.manager.current = "show_psiquico"
        self.manager.get_screen("show_psiquico").show_powers(psiquico)
            
    def change_screen(self, instance):
        self.manager.current = "create_psiquico"



class showPsiquico(Screen):

    def show_powers(self, psiquico):
        # Controlador de botones --> Solventa el problema de la recursividad de las funciones
        self.is_button_clicked = False

        # Modifica el botón del header para regresar a la ventana anterior
        self.ids.header.ids.button.unbind()
        self.ids.header.ids.button.bind(on_press=lambda instance: self.change_to_main_screen(instance))

        # Añade al botón de borrar su funcionalidad --> Fue necesario para pasar psiquico por parametro
        self.ids.boton_borrar.unbind()
        self.ids.boton_borrar.bind(on_press=lambda instance, psiquico=psiquico: self.show_confirm_popup(psiquico))
        
        # Añade al botón de modificar su funcionalidad --> Fue necesario para pasar psiquico por parametro
        self.ids.boton_modificar.unbind()
        self.ids.boton_modificar.bind(on_press=lambda instance, psiquico=psiquico: self.button_edit_psiquico(psiquico))
        
        # Obtener el GridLayout
        scroll_layout = self.ids.scroll_layout

        # Conexión a la BD
        conn = connect('PsionicData.db')
        cursor = conn.cursor()

        # Obtener el número de botones (poderes) asociados al psíquico
        cursor.execute("SELECT COUNT(*) FROM PsiquicosPoderes WHERE Psiquicos= ?;", (psiquico,))
        N = cursor.fetchone()[0]

        # Limpiar el layout antes de agregar nuevos botones
        scroll_layout.clear_widgets()

        # Crear botones dinámicamente
        for i in range(N):
            #Seleccionar el poder
            cursor.execute("SELECT Poderes FROM PsiquicosPoderes WHERE Psiquicos=? LIMIT 1 OFFSET ?", (psiquico, i))
            poder_nombre = cursor.fetchone()[0]

            # Crear el botón y añadirlo al GridLayout
            btn = Button(
                text=poder_nombre,
                size_hint_y=None,
                height=50
            )
            btn.bind(on_press=lambda instance, poder=poder_nombre: self.change_to_card_screen(instance, poder))
            scroll_layout.add_widget(btn)

        # Ajustar la altura del GridLayout al número de botones
        scroll_layout.height = len(scroll_layout.children) * 50
        conn.close()

    def change_to_main_screen(self, instance):
        # Cambiar a la pantalla "main" al presionar el botón
        app = App.get_running_app()
        app.root.current = "main"
    
    def change_to_card_screen(self, instance, poder):
        # Cambiar a la pantalla "card" al presionar el botón
        app = App.get_running_app()
        app.root.current = "card"
        app.root.get_screen("card").rellena_carta(poder, "show_psiquico")

    def show_confirm_popup(self, psiquico):
        if not self.is_button_clicked:
            self.is_button_clicked = True  # Actualizamos el flag para indicar que ya se ha pulsado
            
            # Crear el contenido del popup
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

            # Mensaje de confirmación
            message = Label(text=f"¿Estás seguro de que deseas borrar a {psiquico}?")
            layout.add_widget(message)

            # Botón de Confirmar
            btn_confirm = Button(text="Confirmar", size_hint=(1, 0.5))
            btn_confirm.bind(on_press=lambda x: self.delete_item(psiquico))  # Llama a la función de borrar
            layout.add_widget(btn_confirm)

            # Botón de Cancelar
            btn_cancel = Button(text="Cancelar", size_hint=(1, 0.5))
            btn_cancel.bind(on_press=lambda x: self.popup.dismiss())  # Cierra el popup sin hacer nada
            layout.add_widget(btn_cancel)

            # Crear el Popup
            self.popup = Popup(title="Confirmar Acción",
                        content=layout,
                        size_hint=(0.6, 0.4),  # Tamaño del popup
                        auto_dismiss=False)    # Evita que el popup se cierre automáticamente

            # Mostrar el Popup
            self.popup.open()

    def delete_item(self, psiquico):
        # Conexión a la BD
        conn = connect('PsionicData.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM MisPsiquicos WHERE Nombre = ?;", (psiquico,))
        cursor.execute("DELETE FROM PsiquicosPoderes WHERE Psiquicos = ?;", (psiquico,))

        conn.commit()
        conn.close()

        # Cierra el popup
        self.popup.dismiss()

        # Reiniciar volviendo al main
        app = App.get_running_app()
        app.root.current = "main"

    def button_edit_psiquico(self, psiquico):
        # Hacer las acciones
        self.manager.current = "create_psiquico"
        self.manager.get_screen("create_psiquico").edit_psiquico(psiquico)
            




class CreatePsiquico(Screen):

    poderes_seleccionados = []
    check_ref = {} #Crea una referencia entre los checkbox para preseleccionarlos

    def on_enter(self, *args):
        # Llamar a la función que crea los botones cuando se entra a la pantalla
        self.create_psiquico()
        
    def create_psiquico(self):
        # Obtener el GridLayout
        scroll_layout = self.ids.scroll_layout
        
        # Conexión a la BD
        conn = connect('PsionicData.db')
        cursor = conn.cursor()

        # Crear los desplegables de Disciplinas
        disciplinas = []
        cursor.execute("SELECT COUNT(*) FROM Disciplinas;")
        N = cursor.fetchall()[0][0]

        for i in range(N):
            cursor.execute("SELECT Nombre FROM Disciplinas LIMIT 1 OFFSET ?;", (i,))
            disciplinas.append(cursor.fetchall()[0][0])
        # Limpiar el layout antes de añadir nuevos botones
        scroll_layout.clear_widgets()
        
        for disciplina in disciplinas:
            # Crear el botón y añadirlo al BoxLayout
            btn = Button(
                text=disciplina,
                size_hint_y=None,
                height=50
            )
            # Vincular el botón con el método drop_down
            btn.bind(on_press=lambda instance, disciplina=disciplina: self.drop_down(instance, disciplina))
            scroll_layout.add_widget(btn)

        # Ajustar la altura del GridLayout al número de botones
        scroll_layout.height = len(scroll_layout.children) * 50
        conn.commit()
        conn.close()

        # Modifica el botón del header para regresar a la ventana anterior
        self.ids.header.ids.button.bind(on_press=lambda instance: self.change_to_main_screen(instance))


    def edit_psiquico(self, psiquico):
        # Conexión a la BD
        conn = connect('PsionicData.db')
        cursor = conn.cursor()

        # Obtención de los poderes del psiquico
        cursor.execute("SELECT Poderes FROM PsiquicosPoderes WHERE Psiquicos=?;", (psiquico,))
        poderes = cursor.fetchall() # --> Array

        for poder in poderes:
            self.poderes_seleccionados.append(poder[0])
        
        # Inicializar menú
        self.create_psiquico()

        # Predefinir el nombre del psiquico
        self.ids.nombre_psiquico.text = psiquico
        

    def drop_down(self, button, disciplina):
        # Crear dropdown
        dropdown = DropDown()

        # Conexión a la BD
        conn = connect('PsionicData.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Poderes FROM DisciplinasPoderes WHERE Disciplinas=?;", (disciplina,))
        poderes = cursor.fetchall()  # Obtener todos los poderes --> Array

        # Crear un hbox para contener todos los elementos
        hbox = BoxLayout(orientation='vertical', size_hint_y=None)
        hbox.bind(minimum_height=hbox.setter('height'))

        # Añadir un rectángulo negro debajo de todos los checkboxes
        with hbox.canvas.before:
            Color(0, 0, 0, 1)  # Color negro
            self.rect = Rectangle(pos=(0, 0), size=(button.width, 44 * len(poderes)))

        # Añadir opciones al dropdown con CheckBox y Label
        for poder in poderes:

            # Crear una caja horizontal para poner el checkbox y el label juntos
            item_hbox = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)

            # Define el Checkbox
            checkbox = CheckBox(size_hint_x=None, width=50)
            
            # Introduce la referencia en el diccionario
            self.check_ref[poder[0]] = checkbox

            # Capturar el nombre del poder usando un closure
            def on_checkbox_active(checkbox, estado, poder_nombre=poder[0]):
                self.on_checkbox_select(checkbox, poder_nombre)

            checkbox.bind(active=on_checkbox_active)

            label = Label(text=poder[0], size_hint_y=None, height=44)

            item_hbox.add_widget(checkbox)
            item_hbox.add_widget(label)
            hbox.add_widget(item_hbox)

        dropdown.add_widget(hbox)
        
        # Actualizar dorpdown por si hay poderes preseleccionados (al editar un psiquico)
        self.check_poderes()

        # Asignar el dropdown al botón y abrirlo
        button.bind(on_release=dropdown.open)
        conn.commit()
        conn.close()

    def check_poderes(self):
        for poder in self.poderes_seleccionados:
            if poder in self.check_ref:
                self.check_ref[poder].active = True

    def on_checkbox_select(self, checkbox, poder_nombre):
        if checkbox.active:
            self.poderes_seleccionados.append(poder_nombre)
        else:
            self.poderes_seleccionados.remove(poder_nombre)

    def submit_psiquico(self):

        if self.ids.nombre_psiquico.text == "":
            pass
        else:
            # Conexión a la BD
            conn = connect('PsionicData.db')
            cursor = conn.cursor()

            name = self.ids.nombre_psiquico.text
            
            # Añade al psíquico
            cursor.execute("INSERT INTO MisPsiquicos (Nombre) VALUES (?);", (name, ))

            # Añade los poderes a la tabla de relación entre psíquicos y poderes
            for poder in self.poderes_seleccionados:
                cursor.execute("INSERT INTO PsiquicosPoderes (Psiquicos, Poderes) VALUES (?,?)", (name, poder))
            conn.commit()
            conn.close()
            app = App.get_running_app()
            app.root.current = "main"

    def change_to_main_screen(self, instance):
        # Cambiar a la pantalla "main" al presionar el botón
        app = App.get_running_app()
        app.root.current = "main"


class PowersWindow(Screen):
    def add_dynamic_buttons(self, disciplina):

        # Obtener el GridLayout usando el id del archivo kv
        powers_grid = self.ids.powers_grid

        # Limpiar los widgets previos si ya existen
        powers_grid.clear_widgets()

        # Conexión a la BD
        conn = connect('PsionicData.db')
        cursor = conn.cursor()

        # Obtener el número de botones (poderes) asociados a la disciplina
        cursor.execute("SELECT COUNT(*) FROM DisciplinasPoderes WHERE Disciplinas=?", (disciplina,))
        N = cursor.fetchone()[0]

        # Crear botones dinámicamente
        for i in range(N):
            #Seleccionar el poder
            cursor.execute("SELECT Poderes FROM DisciplinasPoderes WHERE Disciplinas=? LIMIT 1 OFFSET ?", (disciplina, i))
            poder_nombre = cursor.fetchone()[0]

            # Crear el botón y añadirlo al GridLayout
            btn = Button(
                text=poder_nombre,
                size_hint_y=None,
                height=50
            )
            btn.bind(on_press=lambda instance, poder=poder_nombre: self.change_to_card_screen(instance, poder))
            powers_grid.add_widget(btn)

        # Ajustar la altura del GridLayout al número de botones
        powers_grid.height = len(powers_grid.children) * 50
        conn.close()

        # Modifica el botón del header para regresar a la ventana anterior
        self.ids.header.ids.button.bind(on_press=lambda instance: self.change_to_main_screen(instance))

        
    def change_to_card_screen(self, instance, poder):
        # Cambiar a la pantalla "card" al presionar el botón
        app = App.get_running_app()
        app.root.current = "card"
        app.root.get_screen("card").rellena_carta(poder, "powers")

    def change_to_main_screen(self, instance):
        # Cambiar a la pantalla "main" al presionar el botón
        app = App.get_running_app()
        app.root.current = "main"



class CardWindow(Screen):
    def rellena_carta(self, poder, screen_anterior):
        # Conexión a la BD
        conn = connect('PsionicData.db')
        cursor = conn.cursor()

        #Obtener el nivel del poder
        cursor.execute("SELECT Nivel FROM Poderes WHERE Nombre = ?;", (poder,))
        nivel_poder = cursor.fetchone()[0]
        cursor.execute("SELECT Mantenimiento FROM Poderes WHERE Nombre = ?;", (poder,))
        Mantenimiento = cursor.fetchone()[0]
        cursor.execute("SELECT Descripcion FROM Poderes WHERE Nombre = ?;", (poder,))
        Descripcion = cursor.fetchone()[0]
        cursor.execute("SELECT Maestria FROM Poderes WHERE Nombre = ?;", (poder,))
        Maestria = cursor.fetchone()[0]
        cursor.execute("SELECT Accion FROM Poderes WHERE Nombre = ?;", (poder,))
        Accion = cursor.fetchone()[0]
        cursor.execute("SELECT Cogito FROM Poderes WHERE Nombre = ?;", (poder,))
        Cogito = cursor.fetchone()[0]

        self.ids.nombre_poder.text = poder
        self.ids.nivel_poder.text = nivel_poder
        self.ids.Mantenimiento.markup = True
        self.ids.Mantenimiento.text = "[b]Mantenimiento[/b]: " + Mantenimiento
        self.ids.Descripcion.markup = True
        self.ids.Descripcion.text = "[b]Efecto[/b]: " + Descripcion
        self.ids.Maestria.markup = True
        self.ids.Maestria.text = "[b]Maestía[/b]: " + Maestria
        self.ids.Accion.markup = True
        self.ids.Accion.text = "[b]Accion[/b]: " + Accion
        self.ids.Cogito.markup = True
        self.ids.Cogito.text = "[b]Cogito[/b]: " + Cogito

        # Desvincular cualquier acción previa antes de asignar la nueva
        self.ids.header.ids.button.unbind(on_press=self.change_screen)

        # Modifica la acción del botón para regresar a la pantalla anterior
        self.ids.header.ids.button.bind(on_press=lambda instance: self.change_screen(screen_anterior))
        conn.close()

    def change_screen(self, screen_anterior):
        app = App.get_running_app()

        # Prevenir cambios múltiples de pantalla
        if hasattr(self, 'transition_done') and self.transition_done:
            return  # Si ya ha hecho una transición, no hacer nada más
        else:
            self.transition_done = True  # Marcar que la transición ha sido realizada

        current_screen = app.root.current

        # Cambiar a la pantalla anterior
        app.root.current = screen_anterior

        # Restablecer la bandera tras un corto tiempo (permitir nuevos cambios después)
        Clock.schedule_once(lambda dt: self.reset_transition_flag(), 0.5)

    def reset_transition_flag(self):
        # Permitir nuevos cambios de pantalla
        self.transition_done = False

class WindowManager(ScreenManager):
    pass


kv = Builder.load_file('animapsioniccards.kv')

class AnimaPsionicCards(App): # <- Main Class
    
    def build(self):
        return kv

if __name__ == '__main__':
    AnimaPsionicCards().run()