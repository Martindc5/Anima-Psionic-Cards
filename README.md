# Anima Psionic Cards
Este es un proyecto simple realizado con Python y Kivy, para ayudar a los jugadores del juego de rol Anima Beyond Fantasy a crear a sus psiquicos sin tener que consultar los múltiples manuales y complementos en los que están repartidas las diferentes disciplinas y poderes.

>[!NOTE] 
>La app no ha sido completamente desarrollada y de momento no es funcional en Android

## Características

- **Gestión de psíquicos**: Ver, agregar, modificar y eliminar personajes psíquicos.
- **Gestión de poderes**: Asignar y gestionar poderes psiónicos a cada psíquico basado en su disciplina.
- **Interfaz interactiva**: Los poderes y psíquicos se gestionan mediante botones dinámicos que generan interfaces personalizadas basadas en la base de datos.
- **Soporte para base de datos**: Conexión a una base de datos SQLite para almacenar y recuperar datos.

## Instalación

Sigue estos pasos para clonar e instalar el proyecto en tu entorno local.

1. Clona este repositorio:
    ```bash 
    git clone https://github.com/Martindc5/Anima-Psionic-Cards.git
    ```

2. Navega al directorio del proyecto:
    ```bash
    cd Anima-Psionic-Cards
    ```

3. Crea un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

4. Instala las dependencias requeridas:
    ```bash
    pip install -r requirements.txt
    ```

5. Ejecuta la aplicación:
    ```bash
    python main.py
    ```

## Uso

### Pantalla Principal
Al iniciar la aplicación, serás dirigido a la pantalla principal donde puedes ver una lista de disciplinas psiquicas y los personajes que quieras añadir dentro el menú de creación de personajes. Además, simplemente con pulsar sobre cualquier botón de disciplina, aparecerá el nombre de la misma y su descripción. En caso de querer entrar en la ventana de disciplina bastará con pinchar y arrastrar.

### Ventana de disciplinas
Dentro de esta ventana, que se puede visualizar todos los diferentes poderes psiquicos pertenecientes a dicha disciplina, con la posibilidad de abrir cualquier tarjeta y visualizar el poder en detalle.

## Ventana de psiquico
Al hacer click sobre un psiquico, se abre esta ventana que contendrá una lista con todos los poderes de dicho personaje. De igual forma que con la ventana de disciplinas se podrá consultar cada poder. Adicionalmente cuenta con dos botones, uno para modificar y otro para borrar dicho psiquico.

## Ventana de crear psiquicos
Dentro de esta ventana se pueden añadir psiquicos a la base de datos SQLite para luego visualizarlos en la pantalla principal.
