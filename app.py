from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from natal import Data, Chart
from datetime import datetime
import logging
import json
import re
import os

# Configuración de logging para debug
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder="static")

# Clase modificada para SVG transparente
class MonochromaticThemeChart(Chart):
    def __init__(self, data, width=600, **kwargs):
        self.chart_width = width
        super().__init__(data, width, **kwargs)
    
    @property
    def bg_colors(self):
        return ["transparent"] * 12  # Fondos transparentes
    
    @property
    def svg(self):
        original_svg = super().svg
        
        try:
            name = self.data.name.upper()
            birth_date = self.data.utc_dt.strftime('%d.%m.%Y %H:%M hs')
            location = f"{self.data.lat:.4f}, {self.data.lon:.4f}"
            
            # Extraer contenido del SVG original
            svg_content = re.search(r'<svg[^>]*>(.*?)</svg>', original_svg, re.DOTALL).group(1)
            
            # Nuevo SVG con elementos de texto y transparente
            new_svg = f'''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 740" width="{self.chart_width}" height="{self.chart_width * 740 / 600}">
                <text x="50%" y="60" font-family="Cinzel, serif" font-size="40" fill="#d4af37" 
                      text-anchor="middle" font-weight="bold">{name}</text>
                <g transform="translate(0, 100)">
                    {svg_content}
                </g>
                <text x="570" y="720" font-family="Cinzel, serif" font-size="12" 
                      fill="#d4af37" text-anchor="end">{birth_date}</text>
                <text x="570" y="735" font-family="Cinzel, serif" font-size="12" 
                      fill="#d4af37" text-anchor="end">{location}</text>
            </svg>'''
            
            return new_svg
        except Exception as e:
            app.logger.error(f"Error al personalizar el SVG: {str(e)}")
            return original_svg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/backgrounds')
def get_backgrounds():
    try:
        with open('static/config/backgrounds.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        app.logger.error(f"Error loading backgrounds: {str(e)}")
        return jsonify({"backgrounds": []})

@app.route('/generar_carta_natal', methods=['POST'])
def generar_carta_natal():
    try:
        datos = request.get_json()
        
        datos_natal = Data(
            name=datos['name'],
            utc_dt=datetime.strptime(datos['utc_dt'], "%Y-%m-%d %H:%M"),
            lat=datos['lat'],
            lon=datos['lon']
        )
        
        chart = MonochromaticThemeChart(
            datos_natal, 
            width=int(datos.get('width', 600))
        
        return chart.svg, 200, {'Content-Type': 'image/svg+xml'}
    
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)