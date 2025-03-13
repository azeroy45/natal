# Proyecto de Cartas Natales

## Estructura de Directorios

\`\`\`
/
├── app.py                  # Archivo principal de Flask
├── templates/
│   └── index.html          # Plantilla HTML para la interfaz de usuario
└── static/
    ├── css/
    │   └── styles.css      # Estilos CSS para la interfaz
    ├── js/
    │   └── app.js          # JavaScript para la interactividad del cliente
    ├── config/
    │   └── backgrounds.json # Configuración de fondos disponibles
    └── images/
        └── backgrounds/     # Imágenes de fondo para las cartas natales
            ├── template-1.png
            ├── template-2.png
            ├── template-3.png
            ├── template-4.png
            └── thumbnails/   # Miniaturas para la selección en la interfaz
                ├── thumb-template-1.png
                ├── thumb-template-2.png
                ├── thumb-template-3.png
                └── thumb-template-4.png
\`\`\`

## Configuración de Fondos

Los fondos disponibles se configuran en el archivo `static/config/backgrounds.json`. Cada fondo tiene:

- `id`: Identificador único
- `name`: Nombre mostrado en la interfaz
- `file`: Nombre del archivo en la carpeta `static/images/backgrounds/`
- `thumbnail`: Nombre del archivo de miniatura en la carpeta `static/images/backgrounds/thumbnails/`
- `description`: Descripción del fondo

