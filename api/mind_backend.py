#!/usr/bin/env python3
"""
THE MIND - Backend MEJORADO v4.3 ULTRA-COMPATIBLE + SISTEMA DE BALANCE
Versión: Analizador Astuto + Sugerencias Jerárquicas + Nuevos Campos Semánticos + Control de Partida
- ✅ Analizador con REGEX para variaciones lingüísticas
- ✅ Sistema de sugerencias jerárquico: formato → universo → específicas
- ✅ Modo perfilado activable por nivel de información
- ✅ Diferenciación estricta Real vs Ficticio
- ✅ Pistas secuenciales (no aleatorias) con desbloqueo por turnos
- ✅ Género aplicado correctamente en sugerencias (masculino/femenino)
- ✅ 100% COMPATIBLE con frontend existente
- ✅ Dashboard completo
- ✅ Límite de usos de sugerencias y control de refrescos
- ✅ Adivinanza permitida desde la primera pregunta
"""

from flask import Flask, request, jsonify, render_template_string, make_response
from flask_cors import CORS
from io import StringIO
from collections import Counter
import random
import unicodedata
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Set

app = Flask(__name__)
CORS(app)

# ===================================================================
# RUTA RAÍZ - PARA QUE FUNCIONE EL LINK DE RENDER
# ===================================================================
@app.route('/')
def home():
    return f"""
    <html>
    <head>
        <title>Mind Duel</title>
        <style>
            body {{
                font-family: 'Courier New', monospace;
                background: #000;
                color: #0f0;
                margin: 40px;
                text-align: center;
            }}
            h1 {{
                color: #ff00ff;
                font-size: 3em;
                text-shadow: 0 0 10px #ff00ff;
            }}
            .stats {{
                background: #111;
                border: 2px solid #0f0;
                border-radius: 15px;
                padding: 30px;
                margin: 30px auto;
                max-width: 600px;
            }}
            .stat-item {{
                font-size: 1.2em;
                margin: 15px;
                padding: 10px;
                border-bottom: 1px solid #0f0;
            }}
            a {{
                color: #0f0;
                font-size: 1.3em;
                text-decoration: none;
                padding: 10px 20px;
                border: 2px solid #0f0;
                border-radius: 10px;
                margin: 10px;
                display: inline-block;
            }}
            a:hover {{
                background: #0f0;
                color: #000;
            }}
        </style>
    </head>
    <body>
        <h1>🧠 THE MIND</h1>
        <div class="stats">
            <div class="stat-item">🎭 Personajes cargados: {len(PERSONAJES)}</div>
            <div class="stat-item">✅ Servidor activo en Render</div>
            <div class="stat-item">📊 Endpoints: /api/oracle, /health, /dashboard, /api/dashboard/stats</div>
            <div class="stat-item">⚡ Sistema de métricas activado</div>
            <div class="stat-item">🎯 Analizador con 80+ patrones</div>
        </div>
        <a href="/dashboard">📊 IR AL DASHBOARD</a>
        <a href="/health">🔍 HEALTH CHECK</a>
        <a href="/api/dashboard/stats">📈 STATS JSON</a>
    </body>
    </html>
    """

# ===================================================================
# CONFIGURACIÓN
# ===================================================================

REGISTRO_HUECOS_FILE = "huecos_diccionario.json"
METRICAS_FILE = "metricas_oracle.json"
PERSONAJES_FILE = "personajes.json"
MAX_PREGUNTAS = 20

# Variable global para mantener el estado de la partida actual
# Se han añadido campos para el sistema de balance
current_game = {
    'character': None,
    'questions': [],
    'answers': [],
    'questions_count': 0,
    # Nuevas variables para balance de sugerencias y pistas
    'suggestions_used': 0,               # Contador de usos reales de sugerencias (ciclos)
    'max_suggestions': 5,                 # Límite máximo de usos de sugerencias por partida
    'suggestion_refresh_count': 0,        # Contador de refrescos en el ciclo actual
    'max_refresh_per_cycle': 3,            # Máximo de refrescos permitidos sin nueva pregunta
    'cached_suggestions': []               # Últimas sugerencias generadas para el ciclo actual
}


# ===================================================================
# CARGADOR DE PERSONAJES
# ===================================================================

def cargar_personajes(archivo: str = PERSONAJES_FILE) -> List[Dict]:
    """Carga personajes desde archivo JSON externo."""
    try:
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_completa = os.path.join(directorio_actual, archivo)

        if os.path.exists(ruta_completa):
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                data = json.load(f)
                personajes = data.get('personajes', [])
                print(f"✅ {len(personajes)} personajes cargados desde {ruta_completa}")
                return personajes
        else:
            print(f"⚠️  Archivo {ruta_completa} no encontrado")
            return []
    except Exception as e:
        print(f"❌ Error cargando personajes: {e}")
        return []

PERSONAJES = cargar_personajes()

if not PERSONAJES:
    print("=" * 60)
    print("⚠️  ADVERTENCIA: No se cargaron personajes")
    print("=" * 60)


# ===================================================================
# SISTEMA DE MÉTRICAS
# ===================================================================

class MetricasManager:
    def __init__(self):
        self.metricas = self.cargar_metricas()

    def cargar_metricas(self) -> Dict:
        if os.path.exists(METRICAS_FILE):
            try:
                with open(METRICAS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "partidas_totales": 0,
            "partidas_ganadas": 0,
            "partidas_perdidas": 0,
            "preguntas_totales": 0,
            "personajes_usados": {},
            "preguntas_frecuentes": {},
            "tasa_exito_por_personaje": {},
            "errores": []
        }

    def guardar_metricas(self):
        try:
            with open(METRICAS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.metricas, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando métricas: {e}")

    def registrar_pregunta(self, pregunta: str):
        self.metricas["preguntas_totales"] += 1
        if pregunta not in self.metricas["preguntas_frecuentes"]:
            self.metricas["preguntas_frecuentes"][pregunta] = 0
        self.metricas["preguntas_frecuentes"][pregunta] += 1
        self.guardar_metricas()

    def registrar_resultado(self, personaje: str, ganado: bool):
        self.metricas["partidas_totales"] += 1
        if ganado:
            self.metricas["partidas_ganadas"] += 1
        else:
            self.metricas["partidas_perdidas"] += 1
        
        if personaje not in self.metricas["personajes_usados"]:
            self.metricas["personajes_usados"][personaje] = 0
        self.metricas["personajes_usados"][personaje] += 1
        
        if personaje not in self.metricas["tasa_exito_por_personaje"]:
            self.metricas["tasa_exito_por_personaje"][personaje] = {"ganadas": 0, "perdidas": 0}
        
        if ganado:
            self.metricas["tasa_exito_por_personaje"][personaje]["ganadas"] += 1
        else:
            self.metricas["tasa_exito_por_personaje"][personaje]["perdidas"] += 1
        
        self.guardar_metricas()

metricas_manager = MetricasManager()


# ===================================================================
# REGISTRO DE HUECOS
# ===================================================================

def registrar_hueco(pregunta: str, personaje: Dict, pregunta_normalizada: str):
    try:
        huecos = []
        if os.path.exists(REGISTRO_HUECOS_FILE):
            with open(REGISTRO_HUECOS_FILE, 'r', encoding='utf-8') as f:
                huecos = json.load(f)
        
        huecos.append({
            "timestamp": datetime.now().isoformat(),
            "pregunta": pregunta,
            "pregunta_normalizada": pregunta_normalizada,
            "personaje": personaje.get('nombre', 'Desconocido')
        })
        
        with open(REGISTRO_HUECOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(huecos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error registrando hueco: {e}")


# ===================================================================
# NORMALIZADOR
# ===================================================================

class Normalizador:
    SINONIMOS = {
        'hombre': 'masculino',
        'mujer': 'femenino',
        'varon': 'masculino',
        'chica': 'femenino',
        'chico': 'masculino',
        'lentes': 'gafas',
        'anteojos': 'gafas',
        'existio': 'real',
        'inventado': 'ficticio',
        'comic': 'comic',
        'historieta': 'comic',
        'pelicula': 'pelicula',
        'film': 'pelicula',
        'cine': 'pelicula',
        'magia': 'magia',
        'mago': 'mago',
        'brujo': 'mago',
        'superheroe': 'superheroe',
        'superhéroe': 'superheroe',
        'villano': 'villano',
        'antagonista': 'villano',
        'dios': 'deidad',
        'diosa': 'deidad',
        'mitologico': 'mitologico',
        'leyenda': 'mitologico',
    }
    
    @staticmethod
    def normalizar(texto: str) -> str:
        if not texto:
            return ""
        
        texto = texto.lower()
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        
        signos = '¿?¡!.,;:()[]{}"\'-'
        for signo in signos:
            texto = texto.replace(signo, ' ')
        
        texto = ' '.join(texto.split())
        
        palabras = texto.split()
        palabras_procesadas = [Normalizador.SINONIMOS.get(p, p) for p in palabras]
        
        return ' '.join(palabras_procesadas)


# ===================================================================
# ANALIZADOR DE PREGUNTAS MEJORADO CON REGEX
# ===================================================================

class AnalizadorPreguntas:
    """Analizador astuto con expresiones regulares"""
    
    @staticmethod
    def analizar(pregunta: str, personaje: Dict) -> Dict:
        pregunta_norm = Normalizador.normalizar(pregunta)
        
        # ========== TIPO ==========
        if re.search(r'\b(real|existio|historico|carne y hueso|de verdad)\b', pregunta_norm):
            es_real = personaje.get('tipo') == 'real'
            return {'answer': 'Sí' if es_real else 'No', 'clarification': ''}
        
        if re.search(r'\b(ficticio|inventado|imaginario|ficcion|fantasia|ser imaginario)\b', pregunta_norm):
            es_ficticio = personaje.get('tipo') == 'ficticio'
            return {'answer': 'Sí' if es_ficticio else 'No', 'clarification': ''}
        
        # ========== GÉNERO ==========
        if re.search(r'\b(masculino|es (un )?hombre|sexo masculino|del sexo masculino|es (un )?tipo)\b', pregunta_norm):
            es_hombre = personaje.get('genero') == 'masculino'
            return {'answer': 'Sí' if es_hombre else 'No', 'clarification': ''}
        
        if re.search(r'\b(femenino|femenina|es (una )?(mujer|dama|senora|chica)|sexo femenino|del sexo femenino)\b', pregunta_norm):
            es_mujer = personaje.get('genero') == 'femenino'
            return {'answer': 'Sí' if es_mujer else 'No', 'clarification': ''}
        
        # ========== ESTADO VITAL ==========
        if re.search(r'\b(vivo|vive|esta vivo|sigue vivo|aun vive|vive actualmente)\b', pregunta_norm):
            vivo = personaje.get('vivo', False)
            return {'answer': 'Sí' if vivo else 'No', 'clarification': ''}
        
        if re.search(r'\b(muerto|murio|fallecio|fallecida|ya murio|esta muerto|ha fallecido|persona fallecida)\b', pregunta_norm):
            muerto = not personaje.get('vivo', True)
            return {'answer': 'Sí' if muerto else 'No', 'clarification': ''}
        
        # ========== FAMA ==========
        if re.search(r'\b(famoso|famosa|conocido|conocida|celebre|reconocido|popular)\b', pregunta_norm):
            famoso = personaje.get('famoso', False)
            return {'answer': 'Sí' if famoso else 'No', 'clarification': ''}
        
        if re.search(r'\b(todo (el )?mundo|mundialmente conocido|conocido en todo el mundo)\b', pregunta_norm):
            conocido = personaje.get('famoso', False)
            return {'answer': 'Sí' if conocido else 'No', 'clarification': ''}
        
        # ========== RIQUEZA ==========
        if re.search(r'\b(rico|rica|millonario|millonaria|adinerado|tiene (mucho )?dinero|fortuna|multimillonario|multimillonaria|billones|fortuna colosal)\b', pregunta_norm):
            rico = personaje.get('rico', False) or personaje.get('fortuna', '') == 'colosal'
            return {'answer': 'Sí' if rico else 'No', 'clarification': ''}
        
        if re.search(r'\b(pobre|sin dinero|pobreza|humilde)\b', pregunta_norm):
            pobre = personaje.get('pobre', False)
            return {'answer': 'Sí' if pobre else 'No', 'clarification': ''}
        
        # ========== PROFESIONES ==========
        if re.search(r'\b(cientifico|cientifica|investigador|investigadora|persona de ciencia)\b', pregunta_norm):
            es_cientifico = personaje.get('profesion') in ['cientifico', 'cientifica'] or personaje.get('area') in ['fisica', 'quimica', 'electricidad']
            return {'answer': 'Sí' if es_cientifico else 'No', 'clarification': ''}
        
        if re.search(r'\b(artista|pintor|pintora|escultor|escultora|creador|hace arte|crea arte)\b', pregunta_norm):
            es_artista = personaje.get('profesion') == 'artista' or personaje.get('area') == 'arte'
            return {'answer': 'Sí' if es_artista else 'No', 'clarification': ''}
        
        if re.search(r'\b(escritor|escritora|autor|autora|novelista|poeta|poetisa|dramaturgo|dramaturga)\b', pregunta_norm):
            es_escritor = personaje.get('profesion') == 'escritor' or personaje.get('area') == 'literatura'
            return {'answer': 'Sí' if es_escritor else 'No', 'clarification': ''}
        
        if re.search(r'\b(militar|soldado|soldada|guerrero|guerrera|combatiente|luchador)\b', pregunta_norm):
            es_militar = personaje.get('profesion') in ['militar', 'guerrera', 'guerrero'] or personaje.get('area') == 'guerra'
            return {'answer': 'Sí' if es_militar else 'No', 'clarification': ''}
        
        if re.search(r'\b(mago|maga|bruja|brujo|hechicero|hechicera|usa magia|hace magia)\b', pregunta_norm):
            es_mago = personaje.get('profesion') in ['mago', 'bruja', 'maga'] or personaje.get('area') == 'magia'
            return {'answer': 'Sí' if es_mago else 'No', 'clarification': ''}
        
        if re.search(r'\b(superheroe|heroe|heroina|salvador|salvadora|protector)\b', pregunta_norm):
            es_heroe = personaje.get('profesion') == 'superheroe' or personaje.get('rol', {}).get('heroe', False)
            return {'answer': 'Sí' if es_heroe else 'No', 'clarification': ''}
        
        if re.search(r'\b(villano|villana|malo|mala|antagonista|enemigo|malvado)\b', pregunta_norm):
            es_villano = personaje.get('profesion') == 'villano' or personaje.get('rol', {}).get('antagonista', False)
            return {'answer': 'Sí' if es_villano else 'No', 'clarification': ''}
        
        if re.search(r'\b(detective|investigador privado|investigadora privada)\b', pregunta_norm):
            es_detective = personaje.get('profesion') == 'detective'
            return {'answer': 'Sí' if es_detective else 'No', 'clarification': ''}
        
        # ========== FORMATO / ORIGEN ==========
        if re.search(r'\b(comic|historieta|viñetas|comics)\b', pregunta_norm):
            es_comic = personaje.get('formato') == 'comic' or personaje.get('origen') == 'comic'
            return {'answer': 'Sí' if es_comic else 'No', 'clarification': ''}
        
        if re.search(r'\b(pelicula|film|cine|películas)\b', pregunta_norm):
            es_pelicula = personaje.get('formato') == 'pelicula' or personaje.get('origen') == 'pelicula'
            return {'answer': 'Sí' if es_pelicula else 'No', 'clarification': ''}
        
        if re.search(r'\b(libro|novela|literatura|obra literaria)\b', pregunta_norm):
            es_libro = personaje.get('formato') == 'libro' or personaje.get('origen') == 'libro'
            return {'answer': 'Sí' if es_libro else 'No', 'clarification': ''}
        
        if re.search(r'\b(serie de tv|television|serie televisiva)\b', pregunta_norm):
            es_serie = personaje.get('formato') == 'serie' or personaje.get('origen') == 'television'
            return {'answer': 'Sí' if es_serie else 'No', 'clarification': ''}
        
        if re.search(r'\b(videojuego|juego|consola)\b', pregunta_norm):
            es_videojuego = personaje.get('formato') == 'videojuego' or personaje.get('origen') == 'videojuego'
            return {'answer': 'Sí' if es_videojuego else 'No', 'clarification': ''}
        
        if re.search(r'\b(anime|animacion japonesa|japonés animado)\b', pregunta_norm):
            es_anime = personaje.get('formato') == 'anime' or personaje.get('origen') == 'anime'
            return {'answer': 'Sí' if es_anime else 'No', 'clarification': ''}
        
        if re.search(r'\b(dibujos animados|caricatura|animacion occidental)\b', pregunta_norm):
            es_dibujos = personaje.get('formato') == 'dibujos' or personaje.get('origen') == 'animacion'
            return {'answer': 'Sí' if es_dibujos else 'No', 'clarification': ''}
        
        if re.search(r'\b(internet|web|youtube|tiktok|streamer|influencer)\b', pregunta_norm):
            es_internet = personaje.get('formato') == 'internet' or personaje.get('origen') == 'web'
            return {'answer': 'Sí' if es_internet else 'No', 'clarification': ''}
        
        if re.search(r'\b(mitologico|mito|leyenda|ser mitologico|criatura mitologica)\b', pregunta_norm):
            es_mitologico = personaje.get('tipo_ser') == 'mitologico' or personaje.get('especie') in ['dios', 'semidios', 'elfo', 'enano', 'trol']
            return {'answer': 'Sí' if es_mitologico else 'No', 'clarification': ''}
        
        if re.search(r'\b(deidad|dios|diosa|divinidad|ser divino)\b', pregunta_norm):
            es_deidad = personaje.get('tipo_ser') == 'deidad' or personaje.get('especie') == 'dios'
            return {'answer': 'Sí' if es_deidad else 'No', 'clarification': ''}
        
        # ========== DISNEY ==========
        if re.search(r'\b(disney|de disney|personaje disney|película de disney)\b', pregunta_norm):
            es_disney = personaje.get('origen') == 'disney' or 'disney' in personaje.get('universo', '').lower()
            return {'answer': 'Sí' if es_disney else 'No', 'clarification': ''}
        
        # ========== NACIONALIDAD ==========
        if re.search(r'\b(europa|europeo|europea)\b', pregunta_norm):
            europa = personaje.get('nacionalidad') in ['aleman', 'frances', 'ingles', 'italiano', 'espanol', 'polaca', 'francesa', 'inglesa', 'polaco', 'britanico', 'griego', 'romano', 'serbio']
            return {'answer': 'Sí' if europa else 'No', 'clarification': ''}
        
        if re.search(r'\b(america|americano|americana)\b', pregunta_norm):
            america = personaje.get('nacionalidad') in ['americano', 'estadounidense', 'mexicana', 'mexicano', 'venezolano']
            return {'answer': 'Sí' if america else 'No', 'clarification': ''}
        
        if re.search(r'\b(asia|asiatico|asiatica)\b', pregunta_nor
