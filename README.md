# SnapMsg API

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Proceso de Pensamiento](#proceso-de-pensamiento)
3. [Desafíos del Proyecto](#desafíos-del-proyecto)
4. [Pre-requisitos](#pre-requisitos)
5. [Comandos para Construir y Ejecutar](#comandos-para-construir-y-ejecutar)
   - [Correr la Base de Datos](#construir-la-imagen-de-docker)
   - [Correr el Servicio](#correr-la-base-de-datos)
   - [Correr los tests](#correr-el-servicio)
6. [Guía del Usuario para Testing](#guía-del-usuario-para-testing)
7. [Mejoras a la solución](#mejoras-a-la-solución)

## Introducción

SnapMsg es una API REST desarrollada con FastAPI que permite crear, consultar y eliminar mensajes cortos, conocidos como "Snaps". Este proyecto está diseñado para ser escalable y fácil de mantener. La solución planteada se basa en una estructura bajo Package by Layer Design con:
   router: Encargado del enrutamiento entre los endpoints y controller.
   controller: Recibe el contexto de la solicitud y lo envía al servicio correspondiente para su procesamiento.
   service: Actúa como el intermediario entre el controller y la capa de base de datos.
   repository: Gestiona la escritura y lectura de los datos en la base de datos.
   models: Contiene los modelos de datos utilizados, en este caso los Snaps.
   config: Se configura el logger y la sesión con la base de datos.

## Proceso de Pensamiento

### Estructura del Proyecto: Package by Layer Design

La elección de una estructura basada en capas se debe a la necesidad de mantener el código modular y fácil de mantener. Separar las responsabilidades en capas permite que cada una de ellas tenga una función bien definida y facilita la escalabilidad del proyecto.

### Manejo de Errores con Middleware

Un manejo centralizado de errores mejora la mantenibilidad y consistencia en la API. Al capturar y manejar excepciones en un único lugar, se asegura que todas las respuestas de error sean coherentes y fáciles de gestionar, respetando un formato estándar según RFC 7807.

### Logging

La decisión de implementar un sistema de logging se debe a la necesidad de monitorear y depurar la aplicación. Registrar las actividades importantes, como la creación o eliminación de snaps, ayuda a mantener un rastro de eventos, facilitando la solución de problemas.

### Clase Snap y Modelado de la Base de Datos

La clase Snap representa la entidad principal en el sistema, que es un mensaje corto creado por los usuarios. El modelado de esta clase en SQLAlchemy permite mapearla directamente a la tabla snaps en la base de datos.

Atributos:
id: Se decidió utilizar un UUID como identificador único para cada Snap. Esto asegura que cada Snap tenga un identificador que no se repita, ofreciendo seguridad y evitando colisiones.

message: El contenido del Snap se almacena en un campo de tipo String, con una longitud máxima definida por la constante MAX_MESSAGE_LENGTH. Se asegura que este campo sea obligatorio (nullable=False), ya que un Snap no tendría sentido sin un mensaje.

created_at: Se incluye un campo de fecha y hora que se establece automáticamente al momento de crear el Snap, para poder ordenar los snaps en orden cronológico a la hora de obtenerlos a partir del endpoint de get snaps.

Los esquemas de Pydantic se utilizan para validar y serializar los datos que entran y salen de la API. Esto asegura que los datos sean consistentes y estén en el formato correcto.

SnapCreate: Este esquema se utiliza para validar los datos que el cliente envía al crear un nuevo Snap. Solo se requiere el campo message.

SnapData: Representa los datos de un Snap individual. Este modelo incluye tanto el id como el message, asegurando que la respuesta siempre tenga estos dos campos clave.

SnapResponse: Este esquema envuelve el SnapData en un campo data.

SnapListResponse: Similar a SnapResponse, pero diseñado para manejar una lista de Snaps. Utiliza una lista de objetos SnapData para representar múltiples Snaps.

ErrorResponse: Este modelo se utiliza para estructurar las respuestas de error, asegurando que todos los errores en la API sigan un formato consistente. Incluye campos como type, title, status, detail, y instance, alineándose con las mejores prácticas y con el estándar RFC 7807 para mensajes de error HTTP.

## Desafíos del Proyecto

El aspecto más desafiante del proyecto fue generar una base de datos de prueba y utilizar ésta para llevar a cabo los tests. La solución planteada fue generar dos docker-compose diferentes: development y testing. Para correr el servicio, utilizamos el de development. Si queremos correr los tests, utilizamos el de testing para correr la app y los tests con la base de datos de testing.

Otro desafío significativo fue la implementación de un middleware personalizado para el manejo centralizado de errores. Este middleware se encargó de capturar excepciones a lo largo del ciclo de vida de las solicitudes, asegurando que los errores se gestionen de manera consistente y se devuelvan en un formato estándar según RFC 7807. Lo desafiante consistió en el hecho de garantizar que el middleware capturara correctamente todas las excepciones, incluyendo las generadas por errores HTTP (HTTPException), y que no fueran manejadas prematuramente por otros mecanismos internos de FastAPI.

## Pre-requisitos

Para levantar el entorno de desarrollo, asegúrate de tener instalados los siguientes componentes:

- **Python 3.9**: Lenguaje de programación utilizado para desarrollar la API.
- **Pip 21.x**: Manejador de paquetes para instalar las dependencias de Python.
- **Docker 20.x**: Plataforma para automatizar el despliegue de aplicaciones en contenedores.
- **Docker Compose 1.29.x**: Herramienta para definir y correr aplicaciones Docker de múltiples contenedores.

## Comandos para Construir y Ejecutar

Nota: Se debe situar en la carpeta SnapMsg para correr los comandos correctamente

### Correr la Base de Datos

Para correr la base de datos en un contenedor Docker, utiliza Docker Compose con el siguiente comando:

```bash
docker-compose -f docker-compose.development.yml up snapmsg_db
```

Si se desea correr la base de datos de testing, utilizar el comando:

```bash
docker-compose -f docker-compose.testing.yml up snapmsg_test_db
```

### Correr el Servicio

Para levantar el servicio FastAPI junto con la base de datos, ejecuta:

```bash
docker-compose -f docker-compose.development.yml build

docker-compose -f docker-compose.development.yml up
```

### Correr los tests

Para correr los tests, utilizar el comando:

```bash
docker-compose -f docker-compose.testing.yml build

docker-compose -f docker-compose.testing.yml up --abort-on-container-exit
```


## Guía del Usuario para Testing

Para realizar pruebas de la API, se utilizó la librería pytest, que permite estructurar y ejecutar las pruebas de manera eficiente. Puedes consultar la guía oficial de pytest en el siguiente enlace:

https://docs.pytest.org/en/stable/

## Mejoras a la solución

1. Mejora en la Gestión de Conexiones a la Base de Datos

 Sería útil implementar un gestor de contexto para manejar la sesión de la base de datos en lugar de depender de un generador. Esto puede asegurar una limpieza más robusta de las sesiones.


2. Optimización de Consultas a la Base de Datos

Para este proyecto, no debería haber problemas de tiempo para las consultas a las bases de datos. Sin embargo, para garantizar escalabilidad
podríamos asegurarnos de que las consultas a las bases de datos estén optimizadas. Por ejemplo, se podría usar paginación en la recuperación de snaps para evitar cargar demasiados datos en la memoria.


3. Tests de Integración

Después de realizar una operación, como crear o eliminar un snap, una posible mejora sería verificar el estado de la base de datos para confirmar que la operación tuvo el efecto deseado.



