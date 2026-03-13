#!/usr/bin/env python3
"""
THE MIND - Backend MEJORADO v4.4 ULTRA-COMPATIBLE + SISTEMA DE BALANCE + SUGERENCIAS SINCRONIZADAS
Versión: Analizador completo + Sugerencias 100% cubiertas + Mensaje sincero
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
            <div class="stat-item">🎯 Analizador con 100+ patrones</div>
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
current_game = {
    'character': None,
    'questions': [],
    'answers': [],
    'questions_count': 0,
    'suggestions_used': 0,
    'max_suggestions': 5,
    'suggestion_refresh_count': 0,
    'max_refresh_per_cycle': 3,
    'cached_suggestions': []
}


# ===================================================================
# CARGADOR DE PERSONAJES
# ===================================================================

def cargar_personajes(archivo: str = PERSONAJES_FILE) -> List[Dict]:
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
# REGISTRO DE HUECOS (MEJORADO)
# ===================================================================

def registrar_hueco(pregunta: str, personaje: Dict, pregunta_normalizada: str):
    try:
        if not pregunta or not isinstance(pregunta, str):
            print(f"⚠️ registrar_hueco: pregunta inválida {repr(pregunta)}")
            return
        pregunta = pregunta.strip()
        if not pregunta:
            return

        huecos = []
        if os.path.exists(REGISTRO_HUECOS_FILE):
            try:
                with open(REGISTRO_HUECOS_FILE, 'r', encoding='utf-8') as f:
                    huecos = json.load(f)
                    if not isinstance(huecos, list):
                        huecos = []
            except json.JSONDecodeError:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = f"{REGISTRO_HUECOS_FILE}.corrupto_{timestamp}"
                os.rename(REGISTRO_HUECOS_FILE, backup)
                print(f"⚠️ Archivo de huecos corrupto. Respaldado como: {backup}")
                huecos = []
            except Exception as e:
                print(f"❌ Error leyendo huecos: {e}")
                huecos = []

        huecos.append({
            "timestamp": datetime.now().isoformat(),
            "pregunta": pregunta,
            "pregunta_normalizada": pregunta_normalizada,
            "personaje": personaje.get('nombre', 'Desconocido')
        })

        if len(huecos) > 1000:
            huecos = huecos[-1000:]

        temp_file = REGISTRO_HUECOS_FILE + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(huecos, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, REGISTRO_HUECOS_FILE)
    except Exception as e:
        print(f"❌ Error crítico en registrar_hueco: {e}")
        import traceback
        traceback.print_exc()


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
# ANALIZADOR DE PREGUNTAS (CON REGLAS Y NUEVAS NACIONALIDADES)
# ===================================================================

class AnalizadorPreguntas:
    CATEGORIAS_SEMANTICAS = {
        'genero': ['hombre', 'mujer', 'masculino', 'femenino', 'varon', 'dama', 'sexo', 'genero'],
        'vital': ['vivo', 'vive', 'viven', 'muerto', 'murio', 'fallecio', 'fallecida', 'fallecido'],
        'tipo': ['real', 'ficticio', 'existio', 'inventado', 'historico', 'imaginario', 'fantasia'],
        'riqueza': ['rico', 'pobre', 'millonario', 'adinerado', 'multimillonario', 'fortuna', 'dinero'],
        'fama': ['famoso', 'conocido', 'celebre', 'popular', 'reconocido', 'mundialmente'],
        'nacionalidad_europa': ['alemán', 'alemana', 'alemania', 'francés', 'francesa', 'francia', 'inglés', 'inglesa', 'inglaterra', 'británico', 'italiano', 'italiana', 'italia', 'español', 'española', 'españa', 'polaco', 'polaca', 'polonia', 'griego', 'grecia', 'romano'],
        'nacionalidad_america': ['americano', 'americana', 'américa', 'estadounidense', 'usa', 'estados unidos', 'mexicano', 'mexicana', 'méxico'],
        'nacionalidad_asia': ['asiático', 'asiática', 'asia', 'chino', 'china', 'japonés', 'japonesa', 'japón', 'indio', 'india'],
        'nacionalidad_africa': ['africano', 'africana', 'áfrica', 'egipcio', 'egipcia', 'egipto'],
        'nacionalidad_latina': ['uruguayo', 'uruguaya', 'uruguay', 'argentino', 'argentina', 'chileno', 'chilena', 'colombiano', 'colombiana', 'venezolano', 'venezolana', 'peruano', 'peruana'],
        'epoca': ['antigua', 'antigüedad', 'medieval', 'edad media', 'renacimiento', 'moderna', 'contemporáneo', 'siglo', 'antes de cristo'],
        'profesion_ciencia': ['científico', 'científica', 'investigador', 'físico', 'químico', 'biólogo', 'matemático', 'astrónomo'],
        'profesion_arte': ['artista', 'pintor', 'pintora', 'escultor', 'escultora', 'músico', 'compositor'],
        'profesion_literatura': ['escritor', 'escritora', 'autor', 'autora', 'novelista', 'poeta', 'poetisa', 'dramaturgo'],
        'profesion_politica': ['político', 'política', 'presidente', 'presidenta', 'gobernante', 'líder', 'emperador', 'emperatriz', 'rey', 'reina', 'monarca'],
        'profesion_militar': ['militar', 'soldado', 'guerrero', 'guerrera', 'general', 'conquistador'],
        'profesion_otros': ['inventor', 'inventora', 'detective', 'explorador', 'exploradora', 'mago', 'maga', 'sacerdote'],
        'musico': ['músico', 'musico', 'cantante', 'cantar'],
        'matematico': ['matemático', 'matematico', 'matemática', 'matematica'],
        'inteligente': ['inteligente', 'genio', 'brillante', 'sabio'],
        'objeto': ['objeto', 'cosa', 'artefacto'],
        'poderes': ['poderes', 'superpoderes', 'volar', 'vuela', 'inmortal', 'inmortalidad', 'fuerza sobrehumana', 'magia', 'habilidades especiales'],
        'armas': ['arma', 'armas', 'espada', 'arco', 'lanza', 'escudo', 'martillo', 'gadgets', 'tecnología avanzada'],
        'fisico': ['gafas', 'lentes', 'anteojos', 'barba', 'bigote', 'calvo', 'alto', 'bajo', 'estatura', 'pelo'],
        'universo': ['dc', 'dc comics', 'marvel', 'star wars', 'harry potter', 'señor de los anillos', 'tolkien', 'disney'],
        'formato': ['libro', 'película', 'comic', 'serie', 'televisión', 'videojuego', 'anime', 'dibujos animados', 'internet'],
        'logros': ['descubrimientos', 'premios', 'nobel', 'revolucionó', 'cambió la historia', 'legado'],
        'moral': ['pacifista', 'violento', 'conquistador', 'libertad', 'religioso'],
        'relaciones': ['enemigos', 'aliados', 'familia', 'huérfano', 'equipo'],
        'ideologia': ['liberal', 'conservador', 'progresista'],
        'invencible': ['invencible', 'indestructible'],
        'siglo': ['siglo', 'siglos'],
    }

    REGLAS = [
        # TIPO
        {'patron': r'\b(real|existio|historico|carne y hueso|de verdad|existió|existía)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('tipo') == 'real' else 'No', 'clarification': ''}},
        {'patron': r'\b(ficticio|inventado|imaginario|ficcion|fantasia|ser imaginario|es un personaje|es personaje)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('tipo') == 'ficticio' else 'No', 'clarification': ''}},

        # OBJETO
        {'patron': r'\b(es un objeto|es objeto|es una cosa|es cosa)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('tipo') == 'objeto' else 'No', 'clarification': ''}},

        # GÉNERO
        {'patron': r'\b(masculino|es (un )?hombre|sexo masculino|del sexo masculino|es (un )?tipo|varon)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('genero') == 'masculino' else 'No', 'clarification': ''}},
        {'patron': r'\b(femenino|femenina|es (una )?(mujer|dama|senora|chica)|sexo femenino|del sexo femenino)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('genero') == 'femenino' else 'No', 'clarification': ''}},

        # VITAL
        {'patron': r'\b(vivo|vive|esta vivo|sigue vivo|aun vive|vive actualmente)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('vivo', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(muerto|murio|fallecio|fallecida|ya murio|esta muerto|ha fallecido|persona fallecida)\b',
         'respuesta': lambda p: {'answer': 'Sí' if not p.get('vivo', True) else 'No', 'clarification': ''}},

        # FAMA
        {'patron': r'\b(famoso|famosa|conocido|conocida|celebre|reconocido|popular)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('famoso', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(todo (el )?mundo|mundialmente conocido|conocido en todo el mundo)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('famoso', False) else 'No', 'clarification': ''}},

        # RIQUEZA
        {'patron': r'\b(rico|rica|millonario|millonaria|adinerado|tiene (mucho )?dinero|fortuna|multimillonario|multimillonaria|billones|fortuna colosal)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rico', False) or p.get('fortuna') == 'colosal' else 'No', 'clarification': ''}},
        {'patron': r'\b(pobre|sin dinero|pobreza|humilde)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('pobre', False) else 'No', 'clarification': ''}},

        # PROFESIONES
        {'patron': r'\b(cientifico|cientifica|investigador|investigadora|persona de ciencia)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') in ['cientifico', 'cientifica'] or p.get('area') in ['fisica', 'quimica', 'electricidad'] else 'No', 'clarification': ''}},
        {'patron': r'\b(artista|pintor|pintora|escultor|escultora|creador|hace arte|crea arte)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') == 'artista' or p.get('area') == 'arte' else 'No', 'clarification': ''}},
        {'patron': r'\b(escritor|escritora|autor|autora|novelista|poeta|poetisa|dramaturgo|dramaturga)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') == 'escritor' or p.get('area') == 'literatura' else 'No', 'clarification': ''}},
        {'patron': r'\b(militar|soldado|soldada|guerrero|guerrera|combatiente|luchador)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') in ['militar', 'guerrera', 'guerrero'] or p.get('area') == 'guerra' else 'No', 'clarification': ''}},
        {'patron': r'\b(mago|maga|bruja|brujo|hechicero|hechicera|usa magia|hace magia)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') in ['mago', 'bruja', 'maga'] or p.get('area') == 'magia' else 'No', 'clarification': ''}},
        {'patron': r'\b(superheroe|heroe|heroina|salvador|salvadora|protector)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') == 'superheroe' or p.get('rol', {}).get('heroe', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(villano|villana|malo|mala|antagonista|enemigo|malvado)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') == 'villano' or p.get('rol', {}).get('antagonista', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(detective|investigador privado|investigadora privada)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') == 'detective' else 'No', 'clarification': ''}},

        # MÚSICO / CANTANTE
        {'patron': r'\b(es músico|musico|es cantante|cantante|compositor|interpreta música)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') in ['músico', 'musico', 'cantante', 'compositor'] else 'No', 'clarification': ''}},

        # MATEMÁTICO
        {'patron': r'\b(es matemático|matematico|es matemática|matematica|estudió matemáticas)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') in ['matemático', 'matematico', 'matemática', 'matematica'] else 'No', 'clarification': ''}},

        # INTELIGENTE
        {'patron': r'\b(es inteligente|inteligente|se destaca por su inteligencia|es genio|es brillante|es sabio)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rasgos', {}).get('inteligente', False) or p.get('profesion') in ['cientifico', 'matematico', 'fisico', 'filósofo'] else 'No', 'clarification': ''}},

        # FORMATO / ORIGEN
        {'patron': r'\b(comic|historieta|viñetas|comics)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('formato') == 'comic' or p.get('origen') == 'comic' else 'No', 'clarification': ''}},
        {'patron': r'\b(pelicula|film|cine|películas)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('formato') == 'pelicula' or p.get('origen') == 'pelicula' else 'No', 'clarification': ''}},
        {'patron': r'\b(libro|novela|literatura|obra literaria)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('formato') == 'libro' or p.get('origen') == 'libro' else 'No', 'clarification': ''}},
        {'patron': r'\b(serie de tv|television|serie televisiva)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('formato') == 'serie' or p.get('origen') == 'television' else 'No', 'clarification': ''}},
        {'patron': r'\b(videojuego|juego|consola)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('formato') == 'videojuego' or p.get('origen') == 'videojuego' else 'No', 'clarification': ''}},
        {'patron': r'\b(anime|animacion japonesa|japonés animado)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('formato') == 'anime' or p.get('origen') == 'anime' else 'No', 'clarification': ''}},
        {'patron': r'\b(dibujos animados|caricatura|animacion occidental)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('formato') == 'dibujos' or p.get('origen') == 'animacion' else 'No', 'clarification': ''}},
        {'patron': r'\b(internet|web|youtube|tiktok|streamer|influencer)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('formato') == 'internet' or p.get('origen') == 'web' else 'No', 'clarification': ''}},
        {'patron': r'\b(mitologico|mito|leyenda|ser mitologico|criatura mitologica)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('tipo_ser') == 'mitologico' or p.get('especie') in ['dios', 'semidios', 'elfo', 'enano', 'trol'] else 'No', 'clarification': ''}},
        {'patron': r'\b(deidad|dios|diosa|divinidad|ser divino)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('tipo_ser') == 'deidad' or p.get('especie') == 'dios' else 'No', 'clarification': ''}},

        # DISNEY
        {'patron': r'\b(disney|de disney|personaje disney|película de disney)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('origen') == 'disney' or 'disney' in p.get('universo', '').lower() else 'No', 'clarification': ''}},

        # NACIONALIDAD (continentes y específicas)
        {'patron': r'\b(europa|europeo|europea)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['aleman', 'frances', 'ingles', 'italiano', 'espanol', 'polaca', 'francesa', 'inglesa', 'polaco', 'britanico', 'griego', 'romano', 'serbio'] else 'No', 'clarification': ''}},
        {'patron': r'\b(america|americano|americana)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['americano', 'estadounidense', 'mexicana', 'mexicano', 'venezolano'] else 'No', 'clarification': ''}},
        {'patron': r'\b(asia|asiatico|asiatica)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['chino', 'china', 'japones', 'japonesa', 'indio', 'india'] else 'No', 'clarification': ''}},
        {'patron': r'\b(africa|africano|africana)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['egipcio', 'egipcia', 'etíope', 'nigeriano', 'sudafricano', 'keniata', 'marroquí'] else 'No', 'clarification': ''}},

        # NACIONALIDADES LATINAS (NUEVAS)
        {'patron': r'\b(uruguayo|uruguaya|de uruguay|nació en uruguay|uruguay)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['uruguayo', 'uruguaya'] else 'No', 'clarification': ''}},
        {'patron': r'\b(argentino|argentina|de argentina|nació en argentina)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['argentino', 'argentina'] else 'No', 'clarification': ''}},
        {'patron': r'\b(chileno|chilena|de chile|nació en chile)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['chileno', 'chilena'] else 'No', 'clarification': ''}},
        {'patron': r'\b(colombiano|colombiana|de colombia|nació en colombia)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['colombiano', 'colombiana'] else 'No', 'clarification': ''}},
        {'patron': r'\b(venezolano|venezolana|de venezuela|nació en venezuela)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['venezolano', 'venezolana'] else 'No', 'clarification': ''}},
        {'patron': r'\b(peruano|peruana|de perú|nació en perú)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['peruano', 'peruana'] else 'No', 'clarification': ''}},

        # Otras nacionalidades específicas
        {'patron': r'\b(aleman|alemana|de alemania)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'aleman' in p.get('nacionalidad', '').lower() else 'No', 'clarification': ''}},
        {'patron': r'\b(frances|francesa|de francia)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'frances' in p.get('nacionalidad', '').lower() else 'No', 'clarification': ''}},
        {'patron': r'\b(ingles|inglesa|britanico|britanica|de inglaterra|del reino unido)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'ingles' in p.get('nacionalidad', '').lower() or 'britanico' in p.get('nacionalidad', '').lower() else 'No', 'clarification': ''}},
        {'patron': r'\b(espanol|espanola|de espana)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'espanol' in p.get('nacionalidad', '').lower() else 'No', 'clarification': ''}},
        {'patron': r'\b(estadounidense|de (los )?estados unidos|de usa|norteamericano)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'estadounidense' in p.get('nacionalidad', '').lower() or 'americano' in p.get('nacionalidad', '').lower() else 'No', 'clarification': ''}},
        {'patron': r'\b(indio|india|de la india|hindú)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['indio', 'india', 'hindú'] else 'No', 'clarification': ''}},
        {'patron': r'\b(egipcio|egipcia|de egipto)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['egipcio', 'egipcia'] else 'No', 'clarification': ''}},
        {'patron': r'\b(japonés|japonesa|de japón|nipón|anime japonés)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') in ['japonés', 'japonesa'] or p.get('origen') == 'anime' else 'No', 'clarification': ''}},
        {'patron': r'\b(mexicano|mexicana|de méxico)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('nacionalidad') == 'mexicano' else 'No', 'clarification': ''}},

        # ÉPOCA
        {'patron': r'\b(antigua|antiguo|de la antiguedad|epoca antigua|antes de cristo)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('epoca') == 'antigua' or p.get('periodo', {}).get('vivio_antiguedad', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(medieval|edad media|medievo)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('epoca') == 'medieval' or p.get('periodo', {}).get('es_medieval', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(renacimiento|renacentista)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'renacimiento' in p.get('epoca', '').lower() or p.get('periodo', {}).get('es_renacimiento', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(moderna|moderno|contemporaneo|contemporanea|epoca moderna)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('epoca') in ['moderna', 'victoriana', 'contemporanea'] else 'No', 'clarification': ''}},

        # SIGLOS (caso especial)
        {'patron': r'\b(siglo|siglos)\b',
         'respuesta': lambda p: AnalizadorPreguntas._procesar_siglo(p, p)},

        # UNIVERSOS
        {'patron': r'\b(dc|de dc comics|dc comics)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('universo', '').lower() == 'dc' else 'No', 'clarification': ''}},
        {'patron': r'\b(marvel|de marvel)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('universo', '').lower() == 'marvel' else 'No', 'clarification': ''}},
        {'patron': r'\b(harry potter|de harry potter|del mundo de harry potter)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'harry potter' in p.get('universo', '').lower() else 'No', 'clarification': ''}},
        {'patron': r'\b(star wars|de star wars|guerra de las galaxias)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'star wars' in p.get('universo', '').lower() else 'No', 'clarification': ''}},
        {'patron': r'\b(senor de los anillos|tolkien|middle earth|tierra media)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'tolkien' in p.get('universo', '').lower() else 'No', 'clarification': ''}},

        # FÍSICO
        {'patron': r'\b(gafas|lentes|anteojos|usa gafas|lleva gafas)\b',
         'respuesta': lambda p: {'answer': 'Sí' if 'gafas' in ' '.join(p.get('caracteristicas', [])).lower() else 'No', 'clarification': ''}},
        {'patron': r'\b(barba|barbudo|barbuda|tiene barba|bigote|pelo facial)\b',
         'respuesta': lambda p: {'answer': 'Sí' if any(bb in ' '.join(p.get('caracteristicas', [])).lower() for bb in ['barba', 'bigote']) else 'No', 'clarification': ''}},
        {'patron': r'\b(alto|alta|de estatura alta|es alto|es alta)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('fisico', {}).get('alto', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(bajo|baja|de estatura baja|es bajo|es baja|chaparro|petizo)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('fisico', {}).get('bajo', False) else 'No', 'clarification': ''}},

        # PODERES
        {'patron': r'\b(poderes|superpoderes|habilidades sobrenaturales|habilidades magicas)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('tiene_poderes', False) or p.get('habilidades', {}).get('tiene_poderes', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(vuela|puede volar|volar|tiene alas|volador)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('habilidades', {}).get('vuela', False) or p.get('puede_volar', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(inmortal|vive para siempre|no muere|eterno|eterna|vida eterna|puede vivir para siempre|no envejece)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('habilidades', {}).get('es_inmortal', False) or p.get('especie') in ['dios', 'semidiós', 'elfo'] else 'No', 'clarification': ''}},

        # ARMAS
        {'patron': r'\b(porta|usa|empuña|lleva) (alguna|un|una)?\s*(arma|armas|espada|lanza|hacha|arco|escopeta|pistola)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('armas_objetos', {}).get('porta_armas', False) or p.get('armas_objetos', {}).get('usa_espada', False) or p.get('armas_objetos', {}).get('tiene_arco', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(arco|tiene arco|usa arco|arquero|arquera)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('armas_objetos', {}).get('tiene_arco', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(espada|usa espada|espadachin|maneja espada)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('armas_objetos', {}).get('usa_espada', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(tecnologia avanzada|alta tecnologia|tech)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('armas_objetos', {}).get('usa_tecnologia_avanzada', False) else 'No', 'clarification': ''}},

        # LOGROS
        {'patron': r'\b(premios? importantes|galardones?|distinciones?|reconocimientos?)\b',
         'respuesta': lambda p: {'answer': 'Sí' if len(p.get('impacto', {}).get('premios', [])) > 0 else 'No', 'clarification': ''}},
        {'patron': r'\b(premio nobel|nobel|gano el nobel)\b',
         'respuesta': lambda p: {'answer': 'Sí' if any('nobel' in str(pre).lower() for pre in p.get('impacto', {}).get('premios', [])) else 'No', 'clarification': ''}},
        {'patron': r'\b(cambio (el curso de )?la historia)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('impacto', {}).get('cambio_historia', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(revolucion|revoluciono|revolucionario|revolucionaria)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('impacto', {}).get('revoluciono_campo', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(figura iconica|icono|iconico|iconica)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('impacto', {}).get('iconico', False) or p.get('impacto', {}).get('figura_iconica', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(hizo descubrimientos?|descubrimientos? importantes|aportes a la ciencia|inventos científicos)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('impacto', {}).get('hizo_descubrimientos', False) else 'No', 'clarification': ''}},

        # PERFIL MORAL
        {'patron': r'\b(violento|violenta|violencia|agresivo|agresiva)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('perfil_moral', {}).get('violento', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(pacifista|de paz|promotor de la paz|no violento)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('perfil_moral', {}).get('pacifista', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(conquistador|conquistadora|conquisto)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('perfil_moral', {}).get('conquistador', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(imperialista|imperio)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('perfil_moral', {}).get('imperialista', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(lucho por la libertad|luchador de la libertad|defensor de la libertad)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('perfil_moral', {}).get('lucho_libertad', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(religioso|religiosa|sacerdote|monje|monja|clérigo|espiritual|creyente)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('perfil_moral', {}).get('religioso', False) or 'sacerdote' in p.get('profesion', '').lower() else 'No', 'clarification': ''}},

        # ROL
        {'patron': r'\b(lider|líder)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('lider', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(gobernante|goberno)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('gobernante', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(general|general del ejercito|comandante)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('general', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(politico|política|político)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('ocupo_cargo_politico', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(inventor|inventora|invento)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('es_inventor', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(heroe|héroe|heroina|heroína)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('heroe', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(antagonista|enemigo)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('antagonista', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(resuelve crímenes|detective|investiga crímenes)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('detective', False) or p.get('profesion') == 'detective' else 'No', 'clarification': ''}},
        {'patron': r'\b(emperador|emperatriz|imperial|imperio)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('titulo') == 'emperador' or p.get('rol', {}).get('emperador', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(presidente|presidenta|jefe de estado|mandatario)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('rol', {}).get('presidente', False) or p.get('cargo') == 'presidente' else 'No', 'clarification': ''}},
        {'patron': r'\b(explorador|exploradora|aventurero|descubridor)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('profesion') in ['explorador', 'aventurero'] or p.get('rol', {}).get('explorador', False) else 'No', 'clarification': ''}},

        # ESPECIE
        {'patron': r'\b(humano|humana|ser humano)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') == 'humano' or p.get('tipo_ser') == 'humano' else 'No', 'clarification': ''}},
        {'patron': r'\b(elfo|elfica|elfo)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') == 'elfo' else 'No', 'clarification': ''}},
        {'patron': r'\b(enano|enana)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') == 'enano' else 'No', 'clarification': ''}},
        {'patron': r'\b(alien|alienígena|extraterrestre)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') in ['alien', 'extraterrestre'] else 'No', 'clarification': ''}},
        {'patron': r'\b(robot|androide|autómata)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') in ['robot', 'androide'] else 'No', 'clarification': ''}},
        {'patron': r'\b(animal|criatura|bestia)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') == 'animal' else 'No', 'clarification': ''}},
        {'patron': r'\b(fantasma|espíritu|aparición)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') == 'fantasma' else 'No', 'clarification': ''}},
        {'patron': r'\b(dios|diosa|deidad|divinidad)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') == 'dios' or p.get('tipo_ser') == 'deidad' else 'No', 'clarification': ''}},
        {'patron': r'\b(semidiós|semidiosa)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('especie') == 'semidiós' else 'No', 'clarification': ''}},

        # INVENCIBLE (NUEVO)
        {'patron': r'\b(invencible|indestructible|no puede ser derrotado)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('habilidades', {}).get('es_invencible', False) or p.get('especie') in ['dios', 'semidiós'] else 'No', 'clarification': ''}},

        # ESTUDIÓ FÍSICA (NUEVO)
        {'patron': r'\b(estudió física|físico|científico de la física)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('area') == 'física' or p.get('profesion') in ['físico', 'científico'] else 'No', 'clarification': ''}},

        # IDEOLOGÍA (NUEVO)
        {'patron': r'\b(liberal|progresista)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('ideologia', {}).get('liberal', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(conservador|conservadora)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('ideologia', {}).get('conservador', False) else 'No', 'clarification': ''}},

        # RELACIONES (NUEVO)
        {'patron': r'\b(tiene enemigos|enemigos famosos|archienemigos)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('relaciones', {}).get('enemigos', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(tiene aliados|trabaja en equipo)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('relaciones', {}).get('aliados', False) else 'No', 'clarification': ''}},
        {'patron': r'\b(tiene familia|es huérfano)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('relaciones', {}).get('familia', False) else 'No', 'clarification': ''}},

        # HABILIDADES ESPECIALES
        {'patron': r'\b(habilidades especiales|habilidades especiales)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('habilidades', {}).get('tiene_habilidades_especiales', False) else 'No', 'clarification': ''}},

        # FUERZA SOBREHUMANA
        {'patron': r'\b(fuerza sobrehumana|superfuerza)\b',
         'respuesta': lambda p: {'answer': 'Sí' if p.get('habilidades', {}).get('fuerza_sobrehumana', False) else 'No', 'clarification': ''}},
    ]

    @staticmethod
    def obtener_categoria_pregunta(pregunta_norm: str) -> Optional[str]:
        for categoria, palabras in AnalizadorPreguntas.CATEGORIAS_SEMANTICAS.items():
            for palabra in palabras:
                if re.search(r'\b' + re.escape(palabra) + r'\b', pregunta_norm):
                    return categoria
        return None

    @staticmethod
    def verificar_pregunta_repetida(pregunta_norm: str, preguntas_hechas: List[str]) -> Optional[str]:
        cat_actual = AnalizadorPreguntas.obtener_categoria_pregunta(pregunta_norm)
        if not cat_actual:
            return None
        for p_anterior in preguntas_hechas:
            p_norm = Normalizador.normalizar(p_anterior)
            if AnalizadorPreguntas.obtener_categoria_pregunta(p_norm) == cat_actual:
                mensajes = {
                    'genero': "Ya me preguntaste sobre el género de otra forma.",
                    'vital': "Ya preguntaste si está vivo o muerto con otras palabras.",
                    'tipo': "Ya consultaste si es real o ficticio anteriormente.",
                    'riqueza': "Ya indagaste sobre su situación económica.",
                    'fama': "Ya preguntaste si es famoso o conocido.",
                    'nacionalidad_europa': "Ya preguntaste sobre nacionalidades europeas.",
                    'nacionalidad_america': "Ya preguntaste sobre nacionalidades americanas.",
                    'nacionalidad_asia': "Ya preguntaste sobre nacionalidades asiáticas.",
                    'nacionalidad_africa': "Ya preguntaste sobre nacionalidades africanas.",
                    'nacionalidad_latina': "Ya preguntaste sobre nacionalidades latinas.",
                    'epoca': "Ya preguntaste sobre la época en que vive/vivió.",
                    'profesion_ciencia': "Ya preguntaste sobre profesiones científicas.",
                    'profesion_arte': "Ya preguntaste sobre profesiones artísticas.",
                    'profesion_literatura': "Ya preguntaste sobre profesiones literarias.",
                    'profesion_politica': "Ya preguntaste sobre cargos políticos.",
                    'profesion_militar': "Ya preguntaste sobre su faceta militar.",
                    'profesion_otros': "Ya preguntaste sobre otras profesiones.",
                    'musico': "Ya preguntaste sobre música o canto.",
                    'matematico': "Ya preguntaste sobre matemáticas.",
                    'inteligente': "Ya preguntaste sobre inteligencia.",
                    'objeto': "Ya preguntaste si es un objeto.",
                    'poderes': "Ya preguntaste si tiene poderes o habilidades.",
                    'armas': "Ya preguntaste si usa armas o artefactos.",
                    'fisico': "Ya preguntaste sobre características físicas.",
                    'universo': "Ya preguntaste sobre el universo al que pertenece.",
                    'formato': "Ya preguntaste sobre el formato o medio de origen.",
                    'logros': "Ya preguntaste sobre sus logros o descubrimientos.",
                    'moral': "Ya preguntaste sobre su perfil moral.",
                    'relaciones': "Ya preguntaste sobre sus relaciones.",
                    'ideologia': "Ya preguntaste sobre su ideología.",
                    'invencible': "Ya preguntaste si es invencible.",
                    'siglo': "Ya preguntaste sobre el siglo.",
                }
                return mensajes.get(cat_actual, "Ya me preguntaste sobre eso de otra forma.")
        return None

    @staticmethod
    def verificar_contradiccion(pregunta_norm: str, respuestas_previas: List[str], preguntas_previas: List[str]) -> Optional[str]:
        if 'ficticio' in pregunta_norm or 'inventado' in pregunta_norm or 'imaginario' in pregunta_norm:
            for i, p in enumerate(preguntas_previas):
                p_norm = Normalizador.normalizar(p)
                if ('real' in p_norm or 'existio' in p_norm) and i < len(respuestas_previas):
                    if respuestas_previas[i] == 'Sí':
                        return "Eso contradice lo que ya sabés. Antes me preguntaste si era real y dije que sí."
        if 'real' in pregunta_norm or 'existio' in pregunta_norm:
            for i, p in enumerate(preguntas_previas):
                p_norm = Normalizador.normalizar(p)
                if ('ficticio' in p_norm or 'inventado' in p_norm) and i < len(respuestas_previas):
                    if respuestas_previas[i] == 'Sí':
                        return "Eso contradice lo que ya sabés. Antes me preguntaste si era ficticio y dije que sí."
        return None

    @staticmethod
    def _procesar_siglo(pregunta_norm: str, personaje: Dict) -> Dict:
        siglo_match = re.search(r'siglo\s+(\d+|[xxi?v]+)', pregunta_norm)
        if siglo_match:
            siglo_str = siglo_match.group(1)
            romanos = {'i':1, 'ii':2, 'iii':3, 'iv':4, 'v':5, 'vi':6, 'vii':7, 'viii':8, 'ix':9, 'x':10, 'xi':11, 'xii':12, 'xiii':13, 'xiv':14, 'xv':15, 'xvi':16, 'xvii':17, 'xviii':18, 'xix':19, 'xx':20, 'xxi':21}
            if siglo_str.isdigit():
                siglo_num = int(siglo_str)
            else:
                siglo_num = romanos.get(siglo_str.lower(), 0)
            periodo = personaje.get('periodo', {})
            siglo_inicio = periodo.get('siglo_inicio', 0)
            siglo_fin = periodo.get('siglo_fin', 0)
            if siglo_inicio <= siglo_num <= siglo_fin:
                return {'answer': 'Sí', 'clarification': ''}
            else:
                if siglo_num <= 5:
                    epoca_esperada = 'antigua'
                elif siglo_num <= 15:
                    epoca_esperada = 'medieval'
                elif siglo_num <= 18:
                    epoca_esperada = 'renacimiento'
                else:
                    epoca_esperada = 'moderna'
                if personaje.get('epoca') == epoca_esperada:
                    return {'answer': 'Sí', 'clarification': f'(vive en época {epoca_esperada})'}
                else:
                    return {'answer': 'No', 'clarification': ''}
        else:
            return {'answer': 'No lo sé', 'clarification': '¿Podrías especificar qué siglo?'}

    @staticmethod
    def analizar(pregunta: str, personaje: Dict, preguntas_previas: List[str] = None, respuestas_previas: List[str] = None) -> Dict:
        if not pregunta or not isinstance(pregunta, str):
            return {'answer': 'No lo sé', 'clarification': 'No entendí la pregunta.'}
        pregunta = pregunta.strip()
        if not pregunta:
            return {'answer': 'No lo sé', 'clarification': 'No entendí la pregunta.'}

        pregunta_norm = Normalizador.normalizar(pregunta)

        if preguntas_previas and respuestas_previas:
            repetida = AnalizadorPreguntas.verificar_pregunta_repetida(pregunta_norm, preguntas_previas)
            if repetida:
                return {'answer': 'Ya preguntaste eso', 'clarification': repetida}
            contradiccion = AnalizadorPreguntas.verificar_contradiccion(pregunta_norm, respuestas_previas, preguntas_previas)
            if contradiccion:
                return {'answer': 'Cuidado', 'clarification': contradiccion}

        for regla in AnalizadorPreguntas.REGLAS:
            if re.search(regla['patron'], pregunta_norm):
                return regla['respuesta'](personaje)

        # NO CLASIFICABLE - MENSAJE MÁS SINCERO
        if pregunta and isinstance(pregunta, str) and pregunta.strip():
            registrar_hueco(pregunta, personaje, pregunta_norm)
        else:
            print(f"⚠️ analizar: pregunta inválida, no se registra hueco: {repr(pregunta)}")

        return {'answer': 'No lo sé', 'clarification': 'No dispongo de esa información.'}


# ===================================================================
# GENERADOR DE SUGERENCIAS (CON NUEVAS CATEGORÍAS Y MÉTODOS COMPLETOS)
# ===================================================================

class GeneradorSugerencias:
    PREGUNTAS = {
        # BÁSICAS
        'tipo': [
            "¿Es una persona real?",
            "¿Es un personaje ficticio?",
            "¿Existió de verdad?",
            "¿Es un ser imaginario?",
        ],
        'genero_neutro': [
            "¿Es hombre o mujer?",
        ],
        'genero_masculino': [
            "¿Es un hombre?",
            "¿Es del sexo masculino?",
        ],
        'genero_femenino': [
            "¿Es una mujer?",
            "¿Es una dama?",
            "¿Es del sexo femenino?",
        ],

        # REALES
        'real_vital': [
            "¿Está vivo actualmente?",
            "¿Falleció?",
            "¿Ya murió?",
        ],
        'real_fama': [
            "¿Es famoso?",
            "¿Es conocido mundialmente?",
            "¿Todo el mundo lo conoce?",
        ],
        'real_profesion_masculino': [
            "¿Es científico?",
            "¿Es artista?",
            "¿Es escritor?",
            "¿Es pintor?",
            "¿Es militar?",
            "¿Es político?",
            "¿Es inventor?",
            "¿Es músico?",
            "¿Es filósofo?",
            "¿Es matemático?",
        ],
        'real_profesion_femenino': [
            "¿Es científica?",
            "¿Es artista?",
            "¿Es escritora?",
            "¿Es pintora?",
            "¿Es política?",
            "¿Es inventora?",
            "¿Es músico?",
            "¿Es filósofa?",
        ],
        'real_continente': [
            "¿Es de Europa?",
            "¿Es de América?",
            "¿Es de Asia?",
            "¿Es de África?",
        ],
        'real_epoca': [
            "¿Vivió en la antigüedad?",
            "¿Es de la Edad Media?",
            "¿Es del Renacimiento?",
            "¿Es de época moderna?",
            "¿Vivió antes de Cristo?",
            "¿Es del siglo XX?",
            "¿Es contemporáneo?",
        ],
        'real_nacionalidad_europa': [
            "¿Es alemán?",
            "¿Es francés?",
            "¿Es inglés?",
            "¿Es italiano?",
            "¿Es español?",
            "¿Es griego?",
        ],
        'real_nacionalidad_america': [
            "¿Es estadounidense?",
            "¿Es mexicano?",
            "¿Es de América del Sur?",
        ],
        'real_nacionalidad_asia': [
            "¿Es chino?",
            "¿Es japonés?",
            "¿Es indio?",
        ],
        'real_nacionalidad_latina': [
            "¿Es uruguayo?",
            "¿Es argentino?",
            "¿Es chileno?",
            "¿Es colombiano?",
            "¿Es venezolano?",
            "¿Es peruano?",
        ],
        'real_logros': [
            "¿Ganó el Premio Nobel?",
            "¿Revolucionó su campo?",
            "¿Cambió la historia?",
            "¿Hizo descubrimientos importantes?",
            "¿Tiene premios importantes?",
            "¿Dejó un legado importante?",
        ],
        'real_rol': [
            "¿Fue líder político?",
            "¿Fue gobernante?",
            "¿Fue un general?",
            "¿Fue presidente?",
            "¿Fue rey o reina?",
            "¿Fue un conquistador?",
        ],
        'real_moral': [
            "¿Fue pacifista?",
            "¿Fue un conquistador?",
            "¿Luchó por la libertad?",
            "¿Fue violento?",
        ],
        'real_ideologia': [
            "¿Era liberal?",
            "¿Era conservador?",
        ],

        # FICTICIOS
        'ficticio_formato': [
            "¿Es de un libro?",
            "¿Es de una película?",
            "¿Es de un cómic?",
            "¿Es de una serie de TV?",
            "¿Es de un videojuego?",
            "¿Es un anime?",
            "¿Es de dibujos animados?",
            "¿Es un personaje de internet?",
            "¿Es un ser mitológico?",
            "¿Es una deidad?",
        ],
        'ficticio_universo': [
            "¿Es de DC Comics?",
            "¿Es de Marvel?",
            "¿Es de Star Wars?",
            "¿Es de Harry Potter?",
            "¿Es del Señor de los Anillos?",
            "¿Es de Disney?",
        ],
        'ficticio_tipo_masculino': [
            "¿Es un superhéroe?",
            "¿Es un villano?",
            "¿Es un mago?",
            "¿Es un detective?",
            "¿Es un guerrero?",
            "¿Es el protagonista?",
            "¿Es un antagonista?",
        ],
        'ficticio_tipo_femenino': [
            "¿Es una superheroína?",
            "¿Es una villana?",
            "¿Es una maga?",
            "¿Es una detective?",
            "¿Es una guerrera?",
            "¿Es la protagonista?",
            "¿Es una antagonista?",
        ],
        'ficticio_poderes_masculino': [
            "¿Tiene superpoderes?",
            "¿Puede volar?",
            "¿Es inmortal?",
            "¿Tiene fuerza sobrehumana?",
            "¿Tiene habilidades especiales?",
            "¿Usa magia?",
            "¿Tiene poderes mentales?",
        ],
        'ficticio_poderes_femenino': [
            "¿Tiene superpoderes?",
            "¿Puede volar?",
            "¿Es inmortal?",
            "¿Tiene fuerza sobrehumana?",
            "¿Tiene habilidades especiales?",
            "¿Usa magia?",
            "¿Tiene poderes mentales?",
        ],
        'ficticio_armas': [
            "¿Tiene un arco?",
            "¿Usa una espada?",
            "¿Porta armas?",
            "¿Usa tecnología avanzada?",
            "¿Tiene gadgets?",
            "¿Tiene una varita?",
        ],
        'ficticio_especie': [
            "¿Es humano?",
            "¿Es un elfo?",
            "¿Es un enano?",
            "¿Es un alien?",
            "¿Es un robot?",
            "¿Es un semidiós?",
            "¿Es un dios?",
            "¿Es un animal?",
            "¿Es un fantasma?",
            "¿Es de otra especie?",
        ],
        'ficticio_rol': [
            "¿Es un héroe?",
            "¿Es un villano?",
            "¿Es el malo de la historia?",
            "¿Salva al mundo?",
        ],

        # CARACTERÍSTICAS FÍSICAS (AMBOS)
        'fisico': [
            "¿Usa gafas?",
            "¿Tiene barba?",
            "¿Es calvo?",
            "¿Es alto?",
            "¿Es bajo?",
            "¿Tiene el pelo largo?",
        ],

        # ECONÓMICO
        'economia': [
            "¿Es rico?",
            "¿Tiene mucho dinero?",
            "¿Es pobre?",
            "¿Es multimillonario?",
        ],

        # NUEVAS CATEGORÍAS
        'siglos': [
            "¿Es del siglo XV?",
            "¿Es del siglo XX?",
            "¿Vivió en el siglo XIX?",
        ],
        'invencible': [
            "¿Es invencible?",
            "¿Es indestructible?",
        ],
        'estudio_fisica': [
            "¿Estudió física?",
            "¿Es físico?",
        ],
        'relaciones': [
            "¿Tiene enemigos famosos?",
            "¿Tiene aliados?",
            "¿Trabaja en equipo?",
            "¿Tiene familia?",
        ],
        'ideologia': [
            "¿Es liberal?",
            "¿Es conservador?",
        ],
    }

    @staticmethod
    def extraer_conocimiento(preguntas: List[str], respuestas: List[str]) -> Dict:
        """
        Analiza las preguntas y respuestas previas para determinar qué se sabe.
        (Método original, completo)
        """
        conocimiento = {
            'tipo_conocido': False,
            'tipo': None,
            'genero_conocido': False,
            'genero': None,
            'vital_conocido': False,
            'vivo': None,
            'fama_conocida': False,
            'profesion_conocida': False,
            'profesion': None,
            'continente_conocido': False,
            'continente': None,
            'nacionalidad_conocida': False,
            'epoca_conocida': False,
            'epoca': None,
            'universo_conocido': False,
            'universo': None,
            'poderes_conocidos': False,
            'armas_conocidas': False,
            'especie_conocida': False,
            'tipo_ficticio_conocido': False,
            'tipo_ficticio': None,
            'formato_conocido': False,
            'formato': None,
            'fisico_conocido': set(),
            'economia_conocida': False,
            'logros_conocidos': False,
            'rol_conocido': False,
            'moral_conocido': False,
            'ideologia_conocida': False,
            'relaciones_conocidas': False,
            'invencible_conocido': False,
            'siglo_conocido': False,
            'tipo_descartado': None,
            'genero_descartado': None,
        }

        for i, pregunta in enumerate(preguntas):
            if i >= len(respuestas):
                break
            pregunta_norm = Normalizador.normalizar(pregunta)
            respuesta = respuestas[i]
            respuesta_norm = Normalizador.normalizar(respuesta)
            es_afirmativa = 'si' in respuesta_norm
            es_negativa = 'no' in respuesta_norm
            if not (es_afirmativa or es_negativa):
                continue

            # TIPO
            if re.search(r'\b(real|existio|historico)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['tipo_conocido'] = True
                    conocimiento['tipo'] = 'real'
                elif es_negativa:
                    conocimiento['tipo_conocido'] = True
                    conocimiento['tipo'] = 'ficticio'
                    conocimiento['tipo_descartado'] = 'real'
            elif re.search(r'\b(ficticio|inventado|imaginario|ficcion|ser imaginario)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['tipo_conocido'] = True
                    conocimiento['tipo'] = 'ficticio'
                elif es_negativa:
                    conocimiento['tipo_conocido'] = True
                    conocimiento['tipo'] = 'real'
                    conocimiento['tipo_descartado'] = 'ficticio'

            # GÉNERO
            if re.search(r'\b(masculino|hombre|varon)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['genero_conocido'] = True
                    conocimiento['genero'] = 'masculino'
                elif es_negativa:
                    conocimiento['genero_conocido'] = True
                    conocimiento['genero'] = 'femenino'
                    conocimiento['genero_descartado'] = 'masculino'
            elif re.search(r'\b(femenino|mujer|dama)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['genero_conocido'] = True
                    conocimiento['genero'] = 'femenino'
                elif es_negativa:
                    conocimiento['genero_conocido'] = True
                    conocimiento['genero'] = 'masculino'
                    conocimiento['genero_descartado'] = 'femenino'

            # FORMATO
            if re.search(r'\b(comic|historieta|pelicula|film|cine|libro|serie|tv|television|videojuego|anime|dibujos|internet|web)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['formato_conocido'] = True

            # TIPO FICTICIO
            if re.search(r'\b(superheroe|superhéroe)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['tipo_ficticio_conocido'] = True
                    conocimiento['tipo_ficticio'] = 'superheroe'
                elif es_negativa:
                    conocimiento['tipo_ficticio_descartado'] = 'superheroe'
            elif re.search(r'\b(mago|maga|bruja|brujo|hechicero|hechicera)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['tipo_ficticio_conocido'] = True
                    conocimiento['tipo_ficticio'] = 'mago'
                elif es_negativa:
                    conocimiento['tipo_ficticio_descartado'] = 'mago'
            elif re.search(r'\b(villano|villana|antagonista)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['tipo_ficticio_conocido'] = True
                    conocimiento['tipo_ficticio'] = 'villano'
                elif es_negativa:
                    conocimiento['tipo_ficticio_descartado'] = 'villano'

            # VITAL
            if es_afirmativa:
                if re.search(r'\b(vivo|vive)\b', pregunta_norm):
                    conocimiento['vital_conocido'] = True
                    conocimiento['vivo'] = True
                elif re.search(r'\b(muerto|murio|fallecio)\b', pregunta_norm):
                    conocimiento['vital_conocido'] = True
                    conocimiento['vivo'] = False

                # FAMA
                if re.search(r'\b(famoso|conocido|celebre|mundialmente|reconocido|popular)\b', pregunta_norm):
                    conocimiento['fama_conocida'] = True

                # PROFESIÓN
                if re.search(r'\b(cientifico|artista|escritor|pintor|militar|politico|inventor|musico|filosofo|matematico)\b', pregunta_norm):
                    conocimiento['profesion_conocida'] = True

                # CONTINENTE
                if re.search(r'\beuropa\b', pregunta_norm):
                    conocimiento['continente_conocido'] = True
                    conocimiento['continente'] = 'europa'
                elif re.search(r'\bamerica\b', pregunta_norm):
                    conocimiento['continente_conocido'] = True
                    conocimiento['continente'] = 'america'
                elif re.search(r'\basia\b', pregunta_norm):
                    conocimiento['continente_conocido'] = True
                    conocimiento['continente'] = 'asia'
                elif re.search(r'\bafrica\b', pregunta_norm):
                    conocimiento['continente_conocido'] = True
                    conocimiento['continente'] = 'africa'

                # ÉPOCA
                if re.search(r'\b(antigua|antiguedad|medieval|renacimiento|moderna|contemporaneo|antes de cristo)\b', pregunta_norm):
                    conocimiento['epoca_conocida'] = True

                # NACIONALIDAD ESPECÍFICA
                if re.search(r'\b(aleman|frances|ingles|italiano|espanol|estadounidense|mexicano|chino|japones|indio|egipcio|uruguayo|argentino|chileno|colombiano|venezolano|peruano)\b', pregunta_norm):
                    conocimiento['nacionalidad_conocida'] = True

                # UNIVERSO
                if re.search(r'\b(dc|marvel)\b', pregunta_norm):
                    conocimiento['universo_conocido'] = True
                elif re.search(r'\bstar wars\b', pregunta_norm):
                    conocimiento['universo_conocido'] = True
                elif re.search(r'\bharry potter\b', pregunta_norm):
                    conocimiento['universo_conocido'] = True
                elif re.search(r'\b(senor de los anillos|tolkien)\b', pregunta_norm):
                    conocimiento['universo_conocido'] = True

                # PODERES
                if re.search(r'\b(poderes|superpoderes|volar|inmortal|fuerza sobrehumana|magia)\b', pregunta_norm):
                    conocimiento['poderes_conocidos'] = True

                # ARMAS
                if re.search(r'\b(arco|espada|arma|gadgets|tecnologia avanzada)\b', pregunta_norm):
                    conocimiento['armas_conocidas'] = True

                # ESPECIE
                if re.search(r'\b(humano|elfo|enano|alien|robot|semidios|dios|animal|fantasma)\b', pregunta_norm):
                    conocimiento['especie_conocida'] = True

                # FÍSICO
                if re.search(r'\bgafas\b', pregunta_norm):
                    conocimiento['fisico_conocido'].add('gafas')
                if re.search(r'\bbarba\b', pregunta_norm):
                    conocimiento['fisico_conocido'].add('barba')
                if re.search(r'\bcalvo\b', pregunta_norm):
                    conocimiento['fisico_conocido'].add('calvo')
                if re.search(r'\balto\b', pregunta_norm):
                    conocimiento['fisico_conocido'].add('alto')
                if re.search(r'\bbajo\b', pregunta_norm):
                    conocimiento['fisico_conocido'].add('bajo')

                # ECONOMÍA
                if re.search(r'\b(rico|pobre|dinero|multimillonario)\b', pregunta_norm):
                    conocimiento['economia_conocida'] = True

                # LOGROS
                if re.search(r'\b(premio|nobel|revoluciono|cambio historia|descubrimientos)\b', pregunta_norm):
                    conocimiento['logros_conocidos'] = True

                # ROL
                if re.search(r'\b(lider|gobernante|general|presidente|rey|reina|emperador|explorador)\b', pregunta_norm):
                    conocimiento['rol_conocido'] = True

                # MORAL
                if re.search(r'\b(pacifista|conquistador|libertad|violento|religioso)\b', pregunta_norm):
                    conocimiento['moral_conocido'] = True

                # IDEOLOGÍA
                if re.search(r'\b(liberal|conservador|progresista)\b', pregunta_norm):
                    conocimiento['ideologia_conocida'] = True

                # RELACIONES
                if re.search(r'\b(enemigos|aliados|familia|huérfano|equipo)\b', pregunta_norm):
                    conocimiento['relaciones_conocidas'] = True

                # INVENCIBLE
                if re.search(r'\b(invencible|indestructible)\b', pregunta_norm):
                    conocimiento['invencible_conocido'] = True

                # SIGLO
                if re.search(r'\b(siglo|siglos)\b', pregunta_norm):
                    conocimiento['siglo_conocido'] = True

        return conocimiento

    @staticmethod
    def generate_profiled_suggestions(conocimiento: Dict, preguntas_norm: List[str]) -> List[str]:
        """
        Genera sugerencias específicas para perfilar al personaje.
        (Método original, completo)
        """
        perfiladas = []
        if not conocimiento['tipo_conocido']:
            return perfiladas

        tipo = conocimiento['tipo']

        if tipo == 'real':
            if not conocimiento['profesion_conocida']:
                if conocimiento['genero'] == 'femenino':
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_femenino'])
                elif conocimiento['genero'] == 'masculino':
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'])
                else:
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'][:5])
            if not conocimiento['logros_conocidos']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_logros'])
            if not conocimiento['rol_conocido']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_rol'])
            if not conocimiento['moral_conocido']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_moral'])
            if not conocimiento['ideologia_conocida']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_ideologia'])

        elif tipo == 'ficticio':
            if not conocimiento['formato_conocido']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_formato'])
            if not conocimiento['universo_conocido']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_universo'])
            if not conocimiento['tipo_ficticio_conocido']:
                if conocimiento['genero'] == 'femenino':
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_tipo_femenino'])
                else:
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_tipo_masculino'])
            if not conocimiento['poderes_conocidos']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_poderes_masculino'])
            if not conocimiento['armas_conocidas']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_armas'])
            if not conocimiento['especie_conocida']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_especie'])
            if not conocimiento['rol_conocido']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_rol'])

        # Filtrar preguntas ya hechas
        resultado = []
        for p in perfiladas:
            p_norm = Normalizador.normalizar(p)
            ya_preguntada = False
            for q_norm in preguntas_norm:
                if len(set(p_norm.split()) & set(q_norm.split())) >= 2:
                    ya_preguntada = True
                    break
            if not ya_preguntada and p not in resultado:
                resultado.append(p)

        return resultado[:5]

    @staticmethod
    def generar(preguntas_hechas: List[str], respuestas: List[str], max_sugerencias: int = 5) -> List[str]:
        """
        Genera sugerencias dinámicas y contextuales basadas en el estado actual.
        (Método original, completo)
        """
        conocimiento = GeneradorSugerencias.extraer_conocimiento(preguntas_hechas, respuestas)
        preguntas_norm = [Normalizador.normalizar(p) for p in preguntas_hechas]
        candidatas = []

        # PRIORIDAD 1: TIPO
        if not conocimiento['tipo_conocido']:
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['tipo'])

        # PRIORIDAD 2: GÉNERO
        if not conocimiento['genero_conocido']:
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['genero_masculino'])
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['genero_femenino'])

        # RAMA PARA REALES
        if conocimiento['tipo'] == 'real':
            if not conocimiento['vital_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_vital'])
            if not conocimiento['fama_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_fama'])
            if not conocimiento['profesion_conocida']:
                if conocimiento['genero'] == 'femenino':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_femenino'])
                elif conocimiento['genero'] == 'masculino':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'])
                else:
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'][:5])
            if not conocimiento['continente_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_continente'])
            if conocimiento['continente_conocido'] and not conocimiento['nacionalidad_conocida']:
                if conocimiento['continente'] == 'europa':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_nacionalidad_europa'])
                elif conocimiento['continente'] == 'america':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_nacionalidad_america'])
                elif conocimiento['continente'] == 'asia':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_nacionalidad_asia'])
            if not conocimiento['epoca_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_epoca'])
            if not conocimiento['logros_conocidos']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_logros'])
            if not conocimiento['rol_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_rol'])
            if not conocimiento['moral_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_moral'])
            if not conocimiento['ideologia_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_ideologia'])

        # RAMA PARA FICTICIOS
        elif conocimiento['tipo'] == 'ficticio':
            if not conocimiento['formato_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_formato'])
            if not conocimiento['universo_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_universo'])
            if not conocimiento['tipo_ficticio_conocido']:
                if conocimiento['genero'] == 'femenino':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_tipo_femenino'])
                else:
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_tipo_masculino'])
            if not conocimiento['poderes_conocidos']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_poderes_masculino'])
            if not conocimiento['armas_conocidas']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_armas'])
            if not conocimiento['especie_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_especie'])
            if not conocimiento['rol_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_rol'])

        # TIPO DESCONOCIDO
        else:
            if not conocimiento['fama_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_fama'])
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_continente'][:2])
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_universo'][:2])
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_formato'][:2])
            if conocimiento['genero'] == 'masculino':
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'][:3])
            elif conocimiento['genero'] == 'femenino':
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_femenino'][:3])

        # CARACTERÍSTICAS FÍSICAS
        for caracteristica in ['gafas', 'barba', 'calvo', 'alto', 'bajo']:
            if caracteristica not in conocimiento['fisico_conocido']:
                preguntas_fisicas = [p for p in GeneradorSugerencias.PREGUNTAS['fisico'] if caracteristica in p.lower()]
                candidatas.extend(preguntas_fisicas)

        # ECONOMÍA
        if not conocimiento['economia_conocida']:
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['economia'])

        # NUEVAS CATEGORÍAS (si no se han preguntado)
        if not conocimiento.get('invencible_conocido', False):
            candidatas.extend(GeneradorSugerencias.PREGUNTAS.get('invencible', []))
        if not conocimiento.get('siglo_conocido', False):
            candidatas.extend(GeneradorSugerencias.PREGUNTAS.get('siglos', []))
        if not conocimiento.get('relaciones_conocidas', False):
            candidatas.extend(GeneradorSugerencias.PREGUNTAS.get('relaciones', []))

        # FILTRAR PREGUNTAS YA HECHAS
        sugerencias_finales = []
        for candidata in candidatas:
            candidata_norm = Normalizador.normalizar(candidata)
            ya_preguntada = False
            for p_norm in preguntas_norm:
                palabras_candidata = set(candidata_norm.split())
                palabras_pregunta = set(p_norm.split())
                if len(palabras_candidata & palabras_pregunta) >= 2:
                    ya_preguntada = True
                    break
            if ya_preguntada:
                continue

            # FILTROS DE CONOCIMIENTO
            if conocimiento['genero'] == 'masculino' and any(p in candidata_norm for p in ['mujer', 'femenino', 'dama']):
                continue
            if conocimiento['genero'] == 'femenino' and any(p in candidata_norm for p in ['hombre', 'masculino']):
                continue
            if conocimiento['tipo'] == 'real' and any(p in candidata_norm for p in ['ficticio', 'imaginario', 'inventado', 'comic', 'pelicula', 'dc', 'marvel', 'disney', 'anime']):
                continue
            if conocimiento['tipo'] == 'ficticio' and any(p in candidata_norm for p in ['real', 'existio', 'historico']):
                continue

            sugerencias_finales.append(candidata)
            if len(sugerencias_finales) >= max_sugerencias * 4:
                break

        # MODO PERFILADO
        if len(preguntas_hechas) >= 12:
            perfiladas = GeneradorSugerencias.generate_profiled_suggestions(conocimiento, preguntas_norm)
            for p in perfiladas:
                if p not in sugerencias_finales:
                    sugerencias_finales.append(p)

        random.shuffle(sugerencias_finales)
        return sugerencias_finales[:max_sugerencias]


# ===================================================================
# ENDPOINTS
# ===================================================================
@app.route('/api/oracle', methods=['POST'])
def oracle_endpoint():
    global current_game
    try:
        data = request.json
        action = data.get('action')
        if action == 'start':
            current_game = {
                'character': None,
                'questions': [],
                'answers': [],
                'questions_count': 0,
                'suggestions_used': 0,
                'max_suggestions': 5,
                'suggestion_refresh_count': 0,
                'max_refresh_per_cycle': 3,
                'cached_suggestions': []
            }
            personaje = random.choice(PERSONAJES)
            current_game['character'] = personaje
            current_game['questions'] = []
            current_game['answers'] = []
            current_game['questions_count'] = 0
            return jsonify({'character': personaje, 'max_questions': MAX_PREGUNTAS})
        elif action == 'ask':
            if not current_game.get('character'):
                return jsonify({'error': 'No hay partida activa'}), 404
            pregunta = data.get('question', '')
            if not pregunta or not isinstance(pregunta, str):
                pregunta = ""
            personaje = current_game['character']
            resultado = AnalizadorPreguntas.analizar(pregunta, personaje, current_game['questions'], current_game['answers'])
            current_game['questions'].append(pregunta)
            current_game['answers'].append(resultado['answer'])
            current_game['questions_count'] += 1
            metricas_manager.registrar_pregunta(pregunta)
            current_game['suggestion_refresh_count'] = 0
            current_game['cached_suggestions'] = []
            return jsonify(resultado)
        elif action == 'suggestions':
            if not current_game.get('character'):
                return jsonify({'suggestions': []})
            if current_game['suggestions_used'] >= current_game['max_suggestions']:
                return jsonify({'suggestions': [], 'disabled': True, 'reason': 'limit_reached'})
            if current_game['suggestion_refresh_count'] < current_game['max_refresh_per_cycle']:
                if current_game['suggestion_refresh_count'] == 0:
                    current_game['suggestions_used'] += 1
                sugerencias = GeneradorSugerencias.generar(current_game['questions'], current_game['answers'], max_sugerencias=5)
                current_game['cached_suggestions'] = sugerencias
                current_game['suggestion_refresh_count'] += 1
            else:
                sugerencias = current_game['cached_suggestions']
            return jsonify({'suggestions': sugerencias})
        elif action == 'hint':
            if not current_game.get('character'):
                return jsonify({'hint': 'No hay partida activa'})
            pistas = current_game['character'].get('pistas', [])
            hint_level = data.get('hint_level', 1)
            questions_count = current_game['questions_count']
            if questions_count < 5:
                return jsonify({'hint': None, 'locked': True, 'required_turn': 5})
            elif questions_count < 10:
                if hint_level != 1:
                    return jsonify({'hint': None, 'locked': True, 'required_turn': 5})
            if hint_level == 1 and len(pistas) > 0:
                hint = pistas[0]
            elif hint_level == 2 and len(pistas) > 1:
                hint = pistas[1]
            else:
                hint = "No hay más pistas disponibles."
            return jsonify({'hint': hint})
        elif action == 'guess':
            if not current_game.get('character'):
                return jsonify({'error': 'No hay partida activa'}), 404
            if current_game['questions_count'] < 1:
                return jsonify({'error': 'must_ask_before_guess'}), 400
            guess = data.get('guess', '').strip().lower()
            nombre_real = current_game['character']['nombre'].lower()
            correcto = guess == nombre_real
            metricas_manager.registrar_resultado(current_game['character']['nombre'], correcto)
            return jsonify({'correct': correcto, 'character': current_game['character']['nombre'], 'hints': current_game['character'].get('pistas', [])})
        return jsonify({'error': 'Acción no válida'}), 400
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'personajes': len(PERSONAJES), 'mensaje': 'The MIND está funcionando correctamente'})


# ===================================================================
# ENDPOINTS DEL DASHBOARD
# ===================================================================
@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    try:
        metricas = metricas_manager.metricas
        total = metricas.get('partidas_totales', 0)
        ganadas = metricas.get('partidas_ganadas', 0)
        tasa_victoria = round((ganadas / total * 100), 2) if total > 0 else 0
        personajes_usados = metricas.get('personajes_usados', {})
        mas_usados = sorted(personajes_usados.items(), key=lambda x: x[1], reverse=True)[:10]
        menos_usados = sorted(personajes_usados.items(), key=lambda x: x[1])[:10]
        return jsonify({
            'partidas_totales': total,
            'partidas_ganadas': ganadas,
            'partidas_perdidas': metricas.get('partidas_perdidas', 0),
            'tasa_victoria': tasa_victoria,
            'preguntas_totales': metricas.get('preguntas_totales', 0),
            'personajes_mas_usados': mas_usados,
            'personajes_menos_usados': menos_usados,
            'preguntas_frecuentes': metricas.get('preguntas_frecuentes', {}),
            'tasa_exito_por_personaje': metricas.get('tasa_exito_por_personaje', {})
        })
    except Exception as e:
        print(f"Error en dashboard_stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/huecos', methods=['GET'])
def dashboard_huecos():
    try:
        limit = request.args.get('limit', 50, type=int)
        huecos = []
        if os.path.exists(REGISTRO_HUECOS_FILE):
            try:
                with open(REGISTRO_HUECOS_FILE, 'r', encoding='utf-8') as f:
                    huecos = json.load(f)
            except json.JSONDecodeError:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = f"{REGISTRO_HUECOS_FILE}.corrupto_{timestamp}"
                os.rename(REGISTRO_HUECOS_FILE, backup)
                print(f"⚠️ dashboard_huecos: archivo corrupto respaldado como {backup}")
                huecos = []
            except Exception as e:
                print(f"❌ Error leyendo huecos: {e}")
                return jsonify({'error': str(e)}), 500
        if not isinstance(huecos, list):
            huecos = []
        preguntas_counter = Counter()
        personajes_counter = Counter()
        for hueco in huecos:
            if not isinstance(hueco, dict):
                continue
            pregunta = hueco.get('pregunta_normalizada') or hueco.get('pregunta', '')
            personaje = hueco.get('personaje', 'Desconocido')
            if pregunta and isinstance(pregunta, str):
                preguntas_counter[pregunta] += 1
            if personaje:
                personajes_counter[personaje] += 1
        preguntas_frecuentes = preguntas_counter.most_common(20)
        personajes_problematicos = personajes_counter.most_common(10)
        huecos_ordenados = sorted(huecos, key=lambda x: x.get('timestamp', ''), reverse=True)
        ultimos = huecos_ordenados[:limit] if huecos_ordenados else []
        return jsonify({
            'total': len(huecos),
            'huecos': huecos,
            'preguntas_frecuentes': preguntas_frecuentes,
            'personajes_problematicos': personajes_problematicos,
            'ultimos': ultimos
        })
    except Exception as e:
        print(f"Error en dashboard_huecos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/exportar-txt', methods=['GET'])
def exportar_txt():
    output = StringIO()
    output.write("=" * 80 + "\n")
    output.write("THE MIND - REPORTE\n")
    output.write("=" * 80 + "\n")
    output.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    metricas = metricas_manager.metricas
    output.write(f"Partidas: {metricas.get('partidas_totales', 0)}\n")
    output.write(f"Ganadas: {metricas.get('partidas_ganadas', 0)}\n")
    output.write(f"Preguntas: {metricas.get('preguntas_totales', 0)}\n")
    txt_content = output.getvalue()
    response = make_response(txt_content)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=oracle_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    return response


@app.route('/api/dashboard/personajes', methods=['GET'])
def dashboard_personajes():
    try:
        personajes_stats = []
        personajes_usados = metricas_manager.metricas.get('personajes_usados', {})
        tasa_exito = metricas_manager.metricas.get('tasa_exito_por_personaje', {})
        for personaje in PERSONAJES:
            nombre = personaje.get('nombre', 'Desconocido')
            veces_usado = personajes_usados.get(nombre, 0)
            exito = tasa_exito.get(nombre, {'ganadas': 0, 'perdidas': 0})
            ganadas = exito.get('ganadas', 0)
            perdidas = exito.get('perdidas', 0)
            total_partidas = ganadas + perdidas
            porcentaje = round((ganadas / total_partidas * 100), 2) if total_partidas > 0 else 0
            personajes_stats.append({
                'nombre': nombre,
                'tipo': personaje.get('tipo', 'desconocido'),
                'genero': personaje.get('genero', 'desconocido'),
                'veces_usado': veces_usado,
                'partidas_ganadas': ganadas,
                'partidas_perdidas': perdidas,
                'porcentaje_victoria': porcentaje
            })
        personajes_stats.sort(key=lambda x: x['veces_usado'], reverse=True)
        return jsonify({'personajes': personajes_stats, 'total': len(personajes_stats)})
    except Exception as e:
        print(f"Error en dashboard_personajes: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/errores', methods=['GET'])
def dashboard_errores():
    try:
        errores = metricas_manager.metricas.get('errores', [])
        return jsonify({'total': len(errores), 'errores': errores, 'ultimos': errores[-50:] if len(errores) > 50 else errores})
    except Exception as e:
        print(f"Error en dashboard_errores: {e}")
        return jsonify({'error': str(e)}), 500


# ===================================================================
# DASHBOARD HTML (completo, se omite por brevedad pero debe estar)
# ===================================================================
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 MIND Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            border: 2px solid #ff00ff;
        }
        h1 {
            color: #ff00ff;
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px #ff00ff;
        }
        .subtitle {
            color: #00ff00;
            font-size: 1.2em;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .tab-button {
            padding: 15px 30px;
            background: rgba(255, 0, 255, 0.2);
            border: 2px solid #ff00ff;
            color: #ff00ff;
            cursor: pointer;
            border-radius: 10px;
            font-size: 1em;
            transition: all 0.3s;
        }
        .tab-button:hover {
            background: rgba(255, 0, 255, 0.4);
            transform: translateY(-2px);
        }
        .tab-button.active {
            background: #ff00ff;
            color: #1a1a2e;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(0, 0, 0, 0.4);
            padding: 25px;
            border-radius: 15px;
            border: 2px solid #00ff00;
            text-align: center;
        }
        .stat-value {
            font-size: 3em;
            color: #00ff00;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-label {
            color: #e0e0e0;
            font-size: 1em;
        }
        .section {
            background: rgba(0, 0, 0, 0.4);
            padding: 25px;
            border-radius: 15px;
            border: 2px solid #00ff00;
            margin-bottom: 30px;
        }
        .section h2 {
            color: #00ff00;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: rgba(0, 255, 0, 0.2);
            padding: 15px;
            text-align: left;
            color: #00ff00;
            border-bottom: 2px solid #00ff00;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid rgba(0, 255, 0, 0.2);
        }
        tr:hover {
            background: rgba(0, 255, 0, 0.1);
        }
        .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-right: 10px;
        }
        .badge-success {
            background: rgba(0, 255, 0, 0.3);
            color: #00ff00;
        }
        .badge-error {
            background: rgba(255, 0, 0, 0.3);
            color: #ff0000;
        }
        .badge-warning {
            background: rgba(255, 165, 0, 0.3);
            color: #ffA500;
        }
        .refresh-button {
            padding: 12px 25px;
            background: #00ff00;
            color: #000;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
        }
        .refresh-button:hover {
            background: #ff00ff;
            transform: scale(1.05);
        }
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.5em;
            color: #00ff00;
        }
        .empty-state {
            text-align: center;
            padding: 50px;
            color: #666;
            font-size: 1.2em;
        }
        @media (max-width: 768px) {
            h1 { font-size: 2em; }
            .stats-grid { grid-template-columns: 1fr; }
            .tabs { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 THE MIND</h1>
            <p class="subtitle">Panel de Control y Métricas</p>
            <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                <button class="refresh-button" onclick="loadAllData()">🔄 Actualizar Datos</button>
                <button class="refresh-button" onclick="exportarTXT()" style="background: #00ff00;">📄 Descargar TXT</button>
            </div>
        </header>

        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('general')">📊 General</button>
            <button class="tab-button" onclick="switchTab('personajes')">🎭 Personajes</button>
            <button class="tab-button" onclick="switchTab('huecos')">🕳️ Huecos</button>
            <button class="tab-button" onclick="switchTab('errores')">⚠️ Errores</button>
        </div>

        <div id="tab-general" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Partidas Totales</div>
                    <div class="stat-value" id="stat-partidas">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Partidas Ganadas</div>
                    <div class="stat-value" id="stat-ganadas">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Tasa de Victoria</div>
                    <div class="stat-value" id="stat-tasa">-%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Preguntas Totales</div>
                    <div class="stat-value" id="stat-preguntas">-</div>
                </div>
            </div>
            <div class="section">
                <h2>🎯 Personajes Más Jugados</h2>
                <table id="table-mas-usados">
                    <thead><tr><th>#</th><th>Personaje</th><th>Veces Usado</th></tr></thead>
                    <tbody><tr><td colspan="3" class="loading">Cargando...</td></tr></tbody>
                </table>
            </div>
            <div class="section">
                <h2>🎲 Personajes Menos Jugados</h2>
                <table id="table-menos-usados">
                    <thead><tr><th>#</th><th>Personaje</th><th>Veces Usado</th></tr></thead>
                    <tbody><tr><td colspan="3" class="loading">Cargando...</td></tr></tbody>
                </table>
            </div>
        </div>

        <div id="tab-personajes" class="tab-content">
            <div class="section">
                <h2>🎭 Estadísticas por Personaje</h2>
                <table id="table-personajes">
                    <thead><tr><th>Personaje</th><th>Tipo</th><th>Veces Usado</th><th>Ganadas</th><th>Perdidas</th><th>% Victoria</th><th>Dificultad</th></tr></thead>
                    <tbody><tr><td colspan="7" class="loading">Cargando...</td></tr></tbody>
                </table>
            </div>
        </div>

        <div id="tab-huecos" class="tab-content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total de Huecos</div>
                    <div class="stat-value" id="stat-huecos-total">-</div>
                </div>
            </div>
            <div class="section">
                <h2>❓ Preguntas Más Frecuentes (No Respondidas)</h2>
                <table id="table-huecos-frecuentes">
                    <thead><tr><th>#</th><th>Pregunta</th><th>Ocurrencias</th></tr></thead>
                    <tbody><tr><td colspan="3" class="loading">Cargando...</td></tr></tbody>
                </table>
            </div>
            <div class="section">
                <h2>🎭 Personajes con Más Huecos</h2>
                <table id="table-personajes-problematicos">
                    <thead><tr><th>#</th><th>Personaje</th><th>Huecos</th></tr></thead>
                    <tbody><tr><td colspan="3" class="loading">Cargando...</td></tr></tbody>
                </table>
            </div>
            <div class="section">
                <h2>📝 Últimos Huecos Registrados</h2>
                <table id="table-huecos-recientes">
                    <thead><tr><th>Fecha</th><th>Pregunta</th><th>Personaje</th></tr></thead>
                    <tbody><tr><td colspan="3" class="loading">Cargando...</td></tr></tbody>
                </table>
            </div>
        </div>

        <div id="tab-errores" class="tab-content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total de Errores</div>
                    <div class="stat-value" id="stat-errores-total">-</div>
                </div>
            </div>
            <div class="section">
                <h2>⚠️ Errores del Sistema</h2>
                <table id="table-errores">
                    <thead><tr><th>Fecha</th><th>Error</th><th>Contexto</th></tr></thead>
                    <tbody><tr><td colspan="3" class="loading">Cargando...</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }

        async function loadGeneralStats() {
            try {
                const res = await fetch('/api/dashboard/stats');
                const data = await res.json();
                document.getElementById('stat-partidas').textContent = data.partidas_totales;
                document.getElementById('stat-ganadas').textContent = data.partidas_ganadas;
                document.getElementById('stat-tasa').textContent = data.tasa_victoria + '%';
                document.getElementById('stat-preguntas').textContent = data.preguntas_totales;

                const tbody1 = document.querySelector('#table-mas-usados tbody');
                tbody1.innerHTML = (data.personajes_mas_usados || []).map((p, i) => `<tr><td>${i+1}</td><td>${p[0]}</td><td>${p[1]}</td></tr>`).join('') || '<tr><td colspan="3">No hay datos</td></tr>';
                const tbody2 = document.querySelector('#table-menos-usados tbody');
                tbody2.innerHTML = (data.personajes_menos_usados || []).map((p, i) => `<tr><td>${i+1}</td><td>${p[0]}</td><td>${p[1]}</td></tr>`).join('') || '<tr><td colspan="3">No hay datos</td></tr>';
            } catch (e) { console.error(e); }
        }

        async function loadPersonajes() {
            try {
                const res = await fetch('/api/dashboard/personajes');
                const data = await res.json();
                const tbody = document.querySelector('#table-personajes tbody');
                tbody.innerHTML = (data.personajes || []).map(p => {
                    let dificultad = 'Normal';
                    if (p.porcentaje_victoria > 70) dificultad = 'Fácil';
                    else if (p.porcentaje_victoria < 30) dificultad = 'Difícil';
                    return `<tr>
                        <td>${p.nombre}</td>
                        <td><span class="badge ${p.tipo === 'real' ? 'badge-success' : 'badge-warning'}">${p.tipo}</span></td>
                        <td>${p.veces_usado}</td>
                        <td>${p.partidas_ganadas}</td>
                        <td>${p.partidas_perdidas}</td>
                        <td>${p.porcentaje_victoria}%</td>
                        <td>${dificultad}</td>
                    </tr>`;
                }).join('') || '<tr><td colspan="7">No hay datos</td></tr>';
            } catch (e) { console.error(e); }
        }

        async function loadHuecos() {
            try {
                const res = await fetch('/api/dashboard/huecos');
                const data = await res.json();
                document.getElementById('stat-huecos-total').textContent = data.total || 0;

                const tbody1 = document.querySelector('#table-huecos-frecuentes tbody');
                tbody1.innerHTML = (data.preguntas_frecuentes || []).map((p, i) => `<tr><td>${i+1}</td><td>${p[0]}</td><td><span class="badge badge-error">${p[1]}</span></td></tr>`).join('') || '<tr><td colspan="3">No hay datos</td></tr>';

                const tbody2 = document.querySelector('#table-personajes-problematicos tbody');
                tbody2.innerHTML = (data.personajes_problematicos || []).map((p, i) => `<tr><td>${i+1}</td><td>${p[0]}</td><td><span class="badge badge-warning">${p[1]}</span></td></tr>`).join('') || '<tr><td colspan="3">No hay datos</td></tr>';

                const tbody3 = document.querySelector('#table-huecos-recientes tbody');
                tbody3.innerHTML = (data.ultimos || []).reverse().slice(0, 30).map(h => `<tr><td>${new Date(h.timestamp).toLocaleString()}</td><td>${h.pregunta_original}</td><td>${h.personaje}</td></tr>`).join('') || '<tr><td colspan="3">No hay datos</td></tr>';
            } catch (e) { console.error(e); }
        }

        async function loadErrores() {
            try {
                const res = await fetch('/api/dashboard/errores');
                const data = await res.json();
                document.getElementById('stat-errores-total').textContent = data.total || 0;
                const tbody = document.querySelector('#table-errores tbody');
                tbody.innerHTML = (data.ultimos || []).reverse().map(e => `<tr><td>${new Date(e.timestamp).toLocaleString()}</td><td><span class="badge badge-error">${e.error}</span></td><td>${e.contexto}</td></tr>`).join('') || '<tr><td colspan="3">No hay errores</td></tr>';
            } catch (e) { console.error(e); }
        }

        async function loadAllData() {
            await Promise.all([loadGeneralStats(), loadPersonajes(), loadHuecos(), loadErrores()]);
        }

        function exportarTXT() {
            window.location.href = '/api/dashboard/exportar-txt';
        }

        loadAllData();
        setInterval(loadAllData, 30000);
    </script>
</body>
</html>
'''

@app.route('/dashboard')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


# ===================================================================
# MAIN
# ===================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("🧠 THE MIND - Backend MEJORADO v4.4 ULTRA + SUGERENCIAS SINCRONIZADAS")
    print("=" * 60)
    print(f"📡 Servidor: http://0.0.0.0:5000")
    print(f"🎭 Personajes: {len(PERSONAJES)}")
    print(f"📊 Dashboard: http://0.0.0.0:5000/dashboard")
    print("✅ Analizador con 100+ patrones (nuevas nacionalidades latinas, ideología, relaciones)")
    print("✅ Sugerencias sincronizadas (todas las categorías tienen su regla)")
    print("✅ Mensaje de error más sincero: 'No dispongo de esa información.'")
    print("=" * 60)
    # Puerto para producción
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
 
