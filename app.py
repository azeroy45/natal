from flask import Flask, request, jsonify, send_file, render_template
from natal import Data, Chart
from datetime import datetime
import logging
import json
import re
import base64
from pathlib import Path

# Configuración de logging para debug
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder="static")

# Clase para el tema monocromático con fondo de imagen
class MonochromaticThemeChart(Chart):
    def __init__(self, data, width=600, **kwargs):
        self.chart_width = width
        super().__init__(data, width, **kwargs)
    
    @property
    def bg_colors(self):
        # Color monocromático para todas las casas
        return ["#FFFFFF"] * 12
    
    # Sobrescribimos la propiedad svg para personalizar el SVG
    @property
    def svg(self):
        # Primero obtenemos el SVG original de la clase padre
        original_svg = super().svg
        
        # Verificamos que original_svg sea un string
        if not isinstance(original_svg, str):
            app.logger.error(f"El SVG original no es un string: {type(original_svg)}")
            return original_svg
        
        try:
            # Obtener los datos para la personalización
            name = self.data.name.upper()
            birth_date = self.data.utc_dt.strftime('%d.%m.%Y %H:%M hs')
            location = f"{self.data.lat:.4f}, {self.data.lon:.4f}"
            
            # Extraer el viewBox del SVG original para determinar las dimensiones
            viewbox_match = re.search(r'viewBox="([^"]+)"', original_svg)
            viewbox = viewbox_match.group(1) if viewbox_match else "0 0 600 600"
            viewbox_parts = [float(part) for part in viewbox.split()]
            
            # Configurar nuevas dimensiones
            orig_width = viewbox_parts[2]
            orig_height = viewbox_parts[3]
            
            # Nuevo viewBox con espacio adicional arriba y abajo
            new_width = orig_width
            new_height = orig_height + 140  # 100px arriba para el nombre, 40px abajo para la información
            
            # Calcular el offset para centrar el gráfico original
            y_offset = 100  # El espacio que añadimos arriba para el nombre
            
            # Crear el nuevo SVG con el diseño elegante
            new_svg = f'''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {new_width} {new_height}" width="{self.chart_width}" height="{self.chart_width * new_height / new_width}">
                <defs>
                    <pattern id="background-pattern" patternUnits="userSpaceOnUse" width="{new_width}" height="{new_height}">
                        <image href="/static/images/template-1.png" x="0" y="0" width="{new_width}" height="{new_height}" />
                    </pattern>
                </defs>
                
                <!-- Fondo con imagen -->
                <rect width="100%" height="100%" fill="url(#background-pattern)" />
                
                <!-- Nombre en la parte superior -->
                <text x="{new_width/2}" y="60" font-family="Cinzel, serif" font-size="40" fill="#d4af37" 
                      text-anchor="middle" font-weight="bold">{name}</text>
            '''
            
            # Extraer el contenido del SVG original
            svg_content_match = re.search(r'<svg[^>]*>(.*?)</svg>', original_svg, re.DOTALL)
            if svg_content_match:
                svg_content = svg_content_match.group(1)
                
                # Envolver el contenido en un grupo y moverlo
                new_svg += f'''
                    <!-- Contenido original de la carta natal -->
                    <g transform="translate(0, {y_offset})">
                        {svg_content}
                    </g>
                    
                    <!-- Información de nacimiento -->
                    <text x="{new_width - 30}" y="{new_height - 30}" font-family="Cinzel, serif" font-size="12" 
                          fill="#d4af37" text-anchor="end">{birth_date}</text>
                    <text x="{new_width - 30}" y="{new_height - 15}" font-family="Cinzel, serif" font-size="12" 
                          fill="#d4af37" text-anchor="end">{location}</text>
                </svg>
                '''
            else:
                # Si no podemos extraer el contenido, devolvemos el SVG original con un mensaje de error
                new_svg = original_svg
                app.logger.error("No se pudo extraer el contenido del SVG original")
            
            return new_svg
        except Exception as e:
            app.logger.error(f"Error al personalizar el SVG: {str(e)}")
            # Si hay algún error, devolvemos el SVG original sin modificar
            return original_svg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar_carta_natal', methods=['POST'])
def generar_carta_natal():
    try:
        app.logger.debug('Inicio de la ruta /generar_carta_natal')
        datos = request.get_json()

        if not datos:
            app.logger.error("No se recibieron datos")
            return jsonify({"error": "No se recibieron datos"}), 400

        name = datos.get('name')
        utc_dt = datos.get('utc_dt')  # Se espera el formato "YYYY-MM-DD HH:MM"
        lat = datos.get('lat')
        lon = datos.get('lon')
        width = int(datos.get('width', 600))

        if not all([name, utc_dt, lat, lon]):
            app.logger.error("Faltan datos obligatorios")
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        # Convertir el string a objeto datetime
        try:
            fecha_hora = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M")
        except ValueError as e:
            app.logger.error(f"Formato de fecha inválido: {str(e)}")
            return jsonify({"error": "Formato de fecha inválido", "message": str(e)}), 400

        # Crear los datos de la carta natal
        datos_natal = Data(name=name, utc_dt=fecha_hora, lat=lat, lon=lon)
        
        # Utilizar la clase MonochromaticThemeChart
        try:
            chart = MonochromaticThemeChart(datos_natal, width=width)
            svg_output = chart.svg
            
            app.logger.debug('Carta natal generada exitosamente')
            return svg_output, 200, {'Content-Type': 'image/svg+xml'}
        except Exception as e:
            app.logger.error(f"Error al generar la carta: {str(e)}")
            return jsonify({"error": f"No se pudo generar la carta natal: {str(e)}"}), 500

    except Exception as e:
        app.logger.error(f"Error al generar la carta natal: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

