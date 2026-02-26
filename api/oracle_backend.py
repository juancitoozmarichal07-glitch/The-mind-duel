#!/usr/bin/env python3
"""
THE ORACLE - Backend MEJORADO v4.2 ULTRA-COMPATIBLE
Versión: Analizador Astuto + Sugerencias Dinámicas MEJORADAS + Modo Perfilado + Género en sugerencias
- ✅ Analizador con REGEX para variaciones lingüísticas
- ✅ Sistema de sugerencias DINÁMICO, CONTEXTUAL e INTELIGENTE
- ✅ Modo perfilado activable por nivel de información
- ✅ Diferenciación estricta Real vs Ficticio
- ✅ Pistas secuenciales (no aleatorias)
- ✅ Género aplicado correctamente en sugerencias (masculino/femenino)
- ✅ 100% COMPATIBLE con frontend existente
- ✅ Dashboard completo
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
# RUTA RAÍZ - OBLIGATORIA PARA QUE RENDER MUESTRE ALGO EN LA URL BASE
# ===================================================================
# ===================================================================
# DASHBOARD HTML COMPLETO
# ===================================================================

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Oracle Dashboard</title>
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
            <h1>🧠 THE ORACLE</h1>
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
    'questions_count': 0
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
        if re.search(r'\b(rico|rica|millonario|millonaria|adinerado|tiene (mucho )?dinero|fortuna)\b', pregunta_norm):
            rico = personaje.get('rico', False)
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
        
        # ========== FORMATO (NUEVO) ==========
        if re.search(r'\b(comic|historieta|viñetas|comics)\b', pregunta_norm):
            es_comic = personaje.get('formato') == 'comic'
            return {'answer': 'Sí' if es_comic else 'No', 'clarification': ''}
        
        if re.search(r'\b(pelicula|film|cine|películas)\b', pregunta_norm):
            es_pelicula = personaje.get('formato') == 'pelicula'
            return {'answer': 'Sí' if es_pelicula else 'No', 'clarification': ''}
        
        # ========== NACIONALIDAD ==========
        if re.search(r'\b(europa|europeo|europea)\b', pregunta_norm):
            europa = personaje.get('nacionalidad') in ['aleman', 'frances', 'ingles', 'italiano', 'espanol', 'polaca', 'francesa', 'inglesa', 'polaco', 'britanico', 'griego', 'romano', 'serbio']
            return {'answer': 'Sí' if europa else 'No', 'clarification': ''}
        
        if re.search(r'\b(america|americano|americana)\b', pregunta_norm):
            america = personaje.get('nacionalidad') in ['americano', 'estadounidense', 'mexicana', 'mexicano', 'venezolano']
            return {'answer': 'Sí' if america else 'No', 'clarification': ''}
        
        if re.search(r'\b(asia|asiatico|asiatica)\b', pregunta_norm):
            asia = personaje.get('nacionalidad') in ['chino', 'china', 'japones', 'japonesa', 'indio', 'india']
            return {'answer': 'Sí' if asia else 'No', 'clarification': ''}
        
        # Nacionalidades específicas
        if re.search(r'\b(aleman|alemana|de alemania)\b', pregunta_norm):
            return {'answer': 'Sí' if 'aleman' in personaje.get('nacionalidad', '').lower() else 'No', 'clarification': ''}
        
        if re.search(r'\b(frances|francesa|de francia)\b', pregunta_norm):
            return {'answer': 'Sí' if 'frances' in personaje.get('nacionalidad', '').lower() else 'No', 'clarification': ''}
        
        if re.search(r'\b(ingles|inglesa|britanico|britanica|de inglaterra|del reino unido)\b', pregunta_norm):
            nac = personaje.get('nacionalidad', '').lower()
            return {'answer': 'Sí' if 'ingles' in nac or 'britanico' in nac else 'No', 'clarification': ''}
        
        if re.search(r'\b(espanol|espanola|de espana)\b', pregunta_norm):
            return {'answer': 'Sí' if 'espanol' in personaje.get('nacionalidad', '').lower() else 'No', 'clarification': ''}
        
        if re.search(r'\b(estadounidense|de (los )?estados unidos|de usa|norteamericano)\b', pregunta_norm):
            nac = personaje.get('nacionalidad', '').lower()
            return {'answer': 'Sí' if 'estadounidense' in nac or 'americano' in nac else 'No', 'clarification': ''}
        
        # ========== ÉPOCA ==========
        if re.search(r'\b(antigua|antiguo|de la antiguedad|epoca antigua|antes de cristo)\b', pregunta_norm):
            es_antigua = personaje.get('epoca') == 'antigua' or personaje.get('periodo', {}).get('vivio_antiguedad', False)
            return {'answer': 'Sí' if es_antigua else 'No', 'clarification': ''}
        
        if re.search(r'\b(medieval|edad media|medievo)\b', pregunta_norm):
            es_medieval = personaje.get('epoca') == 'medieval' or personaje.get('periodo', {}).get('es_medieval', False)
            return {'answer': 'Sí' if es_medieval else 'No', 'clarification': ''}
        
        if re.search(r'\b(renacimiento|renacentista)\b', pregunta_norm):
            es_renacimiento = 'renacimiento' in personaje.get('epoca', '').lower() or personaje.get('periodo', {}).get('es_renacimiento', False)
            return {'answer': 'Sí' if es_renacimiento else 'No', 'clarification': ''}
        
        if re.search(r'\b(moderna|moderno|contemporaneo|contemporanea|epoca moderna)\b', pregunta_norm):
            es_moderna = personaje.get('epoca') in ['moderna', 'victoriana', 'contemporanea']
            return {'answer': 'Sí' if es_moderna else 'No', 'clarification': ''}
        
        # ========== UNIVERSOS ==========
        if re.search(r'\b(dc|de dc comics|dc comics)\b', pregunta_norm):
            es_dc = personaje.get('universo', '').lower() == 'dc'
            return {'answer': 'Sí' if es_dc else 'No', 'clarification': ''}
        
        if re.search(r'\b(marvel|de marvel)\b', pregunta_norm):
            es_marvel = personaje.get('universo', '').lower() == 'marvel'
            return {'answer': 'Sí' if es_marvel else 'No', 'clarification': ''}
        
        if re.search(r'\b(harry potter|de harry potter|del mundo de harry potter)\b', pregunta_norm):
            es_hp = 'harry potter' in personaje.get('universo', '').lower()
            return {'answer': 'Sí' if es_hp else 'No', 'clarification': ''}
        
        if re.search(r'\b(star wars|de star wars|guerra de las galaxias)\b', pregunta_norm):
            es_sw = 'star wars' in personaje.get('universo', '').lower()
            return {'answer': 'Sí' if es_sw else 'No', 'clarification': ''}
        
        if re.search(r'\b(senor de los anillos|tolkien|middle earth|tierra media)\b', pregunta_norm):
            es_lotr = 'tolkien' in personaje.get('universo', '').lower()
            return {'answer': 'Sí' if es_lotr else 'No', 'clarification': ''}
        
        # ========== FÍSICO ==========
        if re.search(r'\b(gafas|lentes|anteojos|usa gafas|lleva gafas)\b', pregunta_norm):
            usa_gafas = 'gafas' in ' '.join(personaje.get('caracteristicas', [])).lower()
            return {'answer': 'Sí' if usa_gafas else 'No', 'clarification': ''}
        
        if re.search(r'\b(barba|barbudo|barbuda|tiene barba|bigote|pelo facial)\b', pregunta_norm):
            tiene_barba = any(p in ' '.join(personaje.get('caracteristicas', [])).lower() for p in ['barba', 'bigote'])
            return {'answer': 'Sí' if tiene_barba else 'No', 'clarification': ''}
        
        if re.search(r'\b(alto|alta|de estatura alta|es alto|es alta)\b', pregunta_norm):
            es_alto = personaje.get('fisico', {}).get('alto', False)
            return {'answer': 'Sí' if es_alto else 'No', 'clarification': ''}
        
        if re.search(r'\b(bajo|baja|de estatura baja|es bajo|es baja|chaparro|petizo)\b', pregunta_norm):
            es_bajo = personaje.get('fisico', {}).get('bajo', False)
            return {'answer': 'Sí' if es_bajo else 'No', 'clarification': ''}
        
        # ========== PODERES ==========
        if re.search(r'\b(poderes|superpoderes|habilidades sobrenaturales|habilidades magicas)\b', pregunta_norm):
            tiene_poderes = personaje.get('tiene_poderes', False) or personaje.get('habilidades', {}).get('tiene_poderes', False)
            return {'answer': 'Sí' if tiene_poderes else 'No', 'clarification': ''}
        
        if re.search(r'\b(vuela|puede volar|volar|tiene alas|volador)\b', pregunta_norm):
            puede_volar = personaje.get('habilidades', {}).get('vuela', False) or personaje.get('puede_volar', False)
            return {'answer': 'Sí' if puede_volar else 'No', 'clarification': ''}
        
        if re.search(r'\b(inmortal|vive para siempre|no muere|eterno|eterna|vida eterna)\b', pregunta_norm):
            inmortal = personaje.get('habilidades', {}).get('es_inmortal', False) or personaje.get('es_inmortal', False)
            return {'answer': 'Sí' if inmortal else 'No', 'clarification': ''}
        
        # ========== ARMAS ==========
        if re.search(r'\b(arco|tiene arco|usa arco|arquero|arquera)\b', pregunta_norm):
            tiene_arco = personaje.get('armas_objetos', {}).get('tiene_arco', False)
            return {'answer': 'Sí' if tiene_arco else 'No', 'clarification': ''}
        
        if re.search(r'\b(espada|usa espada|espadachin|maneja espada)\b', pregunta_norm):
            tiene_espada = personaje.get('armas_objetos', {}).get('usa_espada', False)
            return {'answer': 'Sí' if tiene_espada else 'No', 'clarification': ''}
        
        if re.search(r'\b(porta|usa) (arma|armas)\b', pregunta_norm):
            porta = personaje.get('armas_objetos', {}).get('porta_armas', False) or personaje.get('armas_objetos', {}).get('usa_armas', False)
            return {'answer': 'Sí' if porta else 'No', 'clarification': ''}
        
        if re.search(r'\b(tecnologia avanzada|alta tecnologia|tech)\b', pregunta_norm):
            tech = personaje.get('armas_objetos', {}).get('usa_tecnologia_avanzada', False)
            return {'answer': 'Sí' if tech else 'No', 'clarification': ''}
        
        # ========== LOGROS ==========
        if re.search(r'\b(premio nobel|nobel|gano el nobel)\b', pregunta_norm):
            impacto = personaje.get('impacto', {})
            tiene_nobel = any('nobel' in str(p).lower() for p in impacto.get('premios', []))
            return {'answer': 'Sí' if tiene_nobel else 'No', 'clarification': ''}
        
        if re.search(r'\b(cambio (el curso de )?la historia)\b', pregunta_norm):
            cambio = personaje.get('impacto', {}).get('cambio_historia', False)
            return {'answer': 'Sí' if cambio else 'No', 'clarification': ''}
        
        if re.search(r'\b(revolucion|revoluciono|revolucionario|revolucionaria)\b', pregunta_norm):
            revoluciono = personaje.get('impacto', {}).get('revoluciono_campo', False)
            return {'answer': 'Sí' if revoluciono else 'No', 'clarification': ''}
        
        if re.search(r'\b(figura iconica|icono|iconico|iconica)\b', pregunta_norm):
            iconico = personaje.get('impacto', {}).get('iconico', False) or personaje.get('impacto', {}).get('figura_iconica', False)
            return {'answer': 'Sí' if iconico else 'No', 'clarification': ''}
        
        # ========== PERFIL MORAL ==========
        if re.search(r'\b(violento|violenta|violencia|agresivo|agresiva)\b', pregunta_norm):
            violento = personaje.get('perfil_moral', {}).get('violento', False)
            return {'answer': 'Sí' if violento else 'No', 'clarification': ''}
        
        if re.search(r'\b(pacifista|de paz|promotor de la paz|no violento)\b', pregunta_norm):
            pacifista = personaje.get('perfil_moral', {}).get('pacifista', False)
            return {'answer': 'Sí' if pacifista else 'No', 'clarification': ''}
        
        # NUEVO: CONQUISTADOR
        if re.search(r'\b(conquistador|conquistadora|conquisto)\b', pregunta_norm):
            conquistador = personaje.get('perfil_moral', {}).get('conquistador', False)
            return {'answer': 'Sí' if conquistador else 'No', 'clarification': ''}
        
        # NUEVO: IMPERIALISTA
        if re.search(r'\b(imperialista|imperio)\b', pregunta_norm):
            imperialista = personaje.get('perfil_moral', {}).get('imperialista', False)
            return {'answer': 'Sí' if imperialista else 'No', 'clarification': ''}
        
        # NUEVO: LUCHÓ POR LA LIBERTAD
        if re.search(r'\b(lucho por la libertad|luchador de la libertad|defensor de la libertad)\b', pregunta_norm):
            lucho = personaje.get('perfil_moral', {}).get('lucho_libertad', False)
            return {'answer': 'Sí' if lucho else 'No', 'clarification': ''}
        
        # ========== ROL ==========
        if re.search(r'\b(lider|líder)\b', pregunta_norm):
            lider = personaje.get('rol', {}).get('lider', False)
            return {'answer': 'Sí' if lider else 'No', 'clarification': ''}
        
        if re.search(r'\b(gobernante|goberno)\b', pregunta_norm):
            gobernante = personaje.get('rol', {}).get('gobernante', False)
            return {'answer': 'Sí' if gobernante else 'No', 'clarification': ''}
        
        # NUEVO: GENERAL
        if re.search(r'\b(general|general del ejercito|comandante)\b', pregunta_norm):
            general = personaje.get('rol', {}).get('general', False)
            return {'answer': 'Sí' if general else 'No', 'clarification': ''}
        
        # NUEVO: POLÍTICO
        if re.search(r'\b(politico|política|político)\b', pregunta_norm):
            politico = personaje.get('rol', {}).get('ocupo_cargo_politico', False)
            return {'answer': 'Sí' if politico else 'No', 'clarification': ''}
        
        # NUEVO: INVENTOR
        if re.search(r'\b(inventor|inventora|invento)\b', pregunta_norm):
            inventor = personaje.get('rol', {}).get('es_inventor', False)
            return {'answer': 'Sí' if inventor else 'No', 'clarification': ''}
        
        # NUEVO: HÉROE
        if re.search(r'\b(heroe|héroe|heroina|heroína)\b', pregunta_norm):
            heroe = personaje.get('rol', {}).get('heroe', False)
            return {'answer': 'Sí' if heroe else 'No', 'clarification': ''}
        
        # NUEVO: ANTAGONISTA
        if re.search(r'\b(antagonista|enemigo)\b', pregunta_norm):
            antagonista = personaje.get('rol', {}).get('antagonista', False)
            return {'answer': 'Sí' if antagonista else 'No', 'clarification': ''}
        
        # ========== IDEOLOGÍA ==========
        if re.search(r'\b(liberal|progresista)\b', pregunta_norm):
            liberal = personaje.get('ideologia', {}).get('liberal', False)
            return {'answer': 'Sí' if liberal else 'No', 'clarification': ''}
        
        if re.search(r'\b(conservador|conservadora)\b', pregunta_norm):
            conservador = personaje.get('ideologia', {}).get('conservador', False)
            return {'answer': 'Sí' if conservador else 'No', 'clarification': ''}
        
        # ========== HABILIDADES ESPECIALES ==========
        if re.search(r'\b(habilidades especiales|habilidades especiales)\b', pregunta_norm):
            especiales = personaje.get('habilidades', {}).get('tiene_habilidades_especiales', False)
            return {'answer': 'Sí' if especiales else 'No', 'clarification': ''}
        
        # ========== FUERZA SOBREHUMANA ==========
        if re.search(r'\b(fuerza sobrehumana|superfuerza)\b', pregunta_norm):
            fuerza = personaje.get('habilidades', {}).get('fuerza_sobrehumana', False)
            return {'answer': 'Sí' if fuerza else 'No', 'clarification': ''}
        
        # NO CLASIFICABLE
        registrar_hueco(pregunta, personaje, pregunta_norm)
        return {'answer': 'No lo sé', 'clarification': 'No estoy seguro de cómo interpretar eso. ¿Podrías reformularlo?'}


# ===================================================================
# GENERADOR DE SUGERENCIAS DINÁMICAS MEJORADO
# ===================================================================

class GeneradorSugerencias:
    """
    Sistema de sugerencias DINÁMICO, CONTEXTUAL e INTELIGENTE.
    
    FUNCIONAMIENTO:
    1. Analiza las preguntas y respuestas previas
    2. Extrae el "estado de conocimiento" actual
    3. Diferencia estrictamente entre personajes REALES y FICTICIOS
    4. Genera sugerencias relevantes según lo que AÚN NO se sabe
    5. Filtra preguntas redundantes o ya hechas
    6. Prioriza estratégicamente las preguntas más útiles
    """
    
    # ===============================================================
    # BANCO DE PREGUNTAS CATEGORIZADO Y EXPANDIDO
    # ===============================================================
    
    PREGUNTAS = {
        # === PREGUNTAS BÁSICAS (SIEMPRE RELEVANTES) ===
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
        
        # === PARA PERSONAJES REALES ÚNICAMENTE ===
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
        
        # === PARA PERSONAJES FICTICIOS ÚNICAMENTE ===
        'ficticio_universo': [
            "¿Es de DC Comics?",
            "¿Es de Marvel?",
            "¿Es de Star Wars?",
            "¿Es de Harry Potter?",
            "¿Es del Señor de los Anillos?",
            "¿Es de un libro?",
            "¿Es de una película?",
            "¿Es de un cómic?",
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
            "¿Es un alien?",
            "¿Es un robot?",
            "¿Es un semidiós?",
            "¿Es de otra especie?",
        ],
        
        'ficticio_rol': [
            "¿Es un héroe?",
            "¿Es un villano?",
            "¿Es el malo de la historia?",
            "¿Salva al mundo?",
        ],
        
        # === CARACTERÍSTICAS FÍSICAS (NEUTRAS - AMBOS TIPOS) ===
        'fisico': [
            "¿Usa gafas?",
            "¿Tiene barba?",
            "¿Es calvo?",
            "¿Es alto?",
            "¿Es bajo?",
            "¿Tiene el pelo largo?",
        ],
        
        # === ECONÓMICO (AMBOS TIPOS) ===
        'economia': [
            "¿Es rico?",
            "¿Tiene mucho dinero?",
            "¿Es pobre?",
        ],
        
        # === FORMATO (NUEVO) ===
        'formato': [
            "¿Es de un cómic?",
            "¿Es de una película?",
            "¿Es de un libro?",
            "¿Es de una serie de TV?",
        ],
    }
    
    # ===============================================================
    # EXTRACCIÓN AVANZADA DE CONOCIMIENTO (CORREGIDA)
    # ===============================================================
    
    @staticmethod
    def extraer_conocimiento(preguntas: List[str], respuestas: List[str]) -> Dict:
        """
        Analiza las preguntas y respuestas previas para determinar qué se sabe.
        AHORA PROCESA TANTO SÍ COMO NO para inferir información.
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
            'tipo_descartado': None,
            'genero_descartado': None,
        }
        
        # Analizar cada pregunta-respuesta
        for i, pregunta in enumerate(preguntas):
            if i >= len(respuestas):
                break
            
            pregunta_norm = Normalizador.normalizar(pregunta)
            respuesta = respuestas[i]
            
            # Detectar si es afirmativa o negativa
            respuesta_norm = Normalizador.normalizar(respuesta)
            es_afirmativa = 'si' in respuesta_norm
            es_negativa = 'no' in respuesta_norm
            
            if not (es_afirmativa or es_negativa):
                continue  # Ignorar respuestas como "No lo sé"
            
            # === DETERMINAR TIPO (real/ficticio) ===
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
            
            # === DETERMINAR GÉNERO ===
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
            
            # === FORMATO (NUEVO) ===
            if re.search(r'\b(comic|historieta|comics)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['formato_conocido'] = True
                    conocimiento['formato'] = 'comic'
                elif es_negativa:
                    conocimiento['formato'] = 'no_comic'
                    
            elif re.search(r'\b(pelicula|film|cine|películas)\b', pregunta_norm):
                if es_afirmativa:
                    conocimiento['formato_conocido'] = True
                    conocimiento['formato'] = 'pelicula'
                elif es_negativa:
                    conocimiento['formato'] = 'no_pelicula'
            
            # === TIPO FICTICIO ESPECÍFICO ===
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
            
            # === ESTADO VITAL ===
            if es_afirmativa:
                if re.search(r'\b(vivo|vive)\b', pregunta_norm):
                    conocimiento['vital_conocido'] = True
                    conocimiento['vivo'] = True
                elif re.search(r'\b(muerto|murio|fallecio)\b', pregunta_norm):
                    conocimiento['vital_conocido'] = True
                    conocimiento['vivo'] = False
                
                # === FAMA ===
                if re.search(r'\b(famoso|conocido|celebre|mundialmente|reconocido|popular)\b', pregunta_norm):
                    conocimiento['fama_conocida'] = True
                
                # === PROFESIÓN ===
                if re.search(r'\b(cientifico|artista|escritor|pintor|militar|politico|inventor|musico|filosofo|matematico)\b', pregunta_norm):
                    conocimiento['profesion_conocida'] = True
                
                # === CONTINENTE ===
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
                
                # === ÉPOCA ===
                if re.search(r'\b(antigua|antiguedad|medieval|renacimiento|moderna|contemporaneo|antes de cristo)\b', pregunta_norm):
                    conocimiento['epoca_conocida'] = True
                
                # === NACIONALIDAD ESPECÍFICA ===
                if re.search(r'\b(aleman|frances|ingles|italiano|espanol|estadounidense|mexicano|chino|japones)\b', pregunta_norm):
                    conocimiento['nacionalidad_conocida'] = True
                
                # === UNIVERSO FICTICIO ===
                if re.search(r'\b(dc|marvel)\b', pregunta_norm):
                    conocimiento['universo_conocido'] = True
                    conocimiento['universo'] = 'comics'
                elif re.search(r'\bstar wars\b', pregunta_norm):
                    conocimiento['universo_conocido'] = True
                    conocimiento['universo'] = 'star_wars'
                elif re.search(r'\bharry potter\b', pregunta_norm):
                    conocimiento['universo_conocido'] = True
                    conocimiento['universo'] = 'harry_potter'
                elif re.search(r'\b(senor de los anillos|tolkien)\b', pregunta_norm):
                    conocimiento['universo_conocido'] = True
                    conocimiento['universo'] = 'lotr'
                
                # === PODERES ===
                if re.search(r'\b(poderes|superpoderes|volar|inmortal|fuerza sobrehumana|magia)\b', pregunta_norm):
                    conocimiento['poderes_conocidos'] = True
                
                # === ARMAS ===
                if re.search(r'\b(arco|espada|arma|gadgets|tecnologia avanzada)\b', pregunta_norm):
                    conocimiento['armas_conocidas'] = True
                
                # === ESPECIE ===
                if re.search(r'\b(humano|elfo|alien|robot|semidios)\b', pregunta_norm):
                    conocimiento['especie_conocida'] = True
                
                # === FÍSICO ===
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
                
                # === ECONOMÍA ===
                if re.search(r'\b(rico|pobre|dinero)\b', pregunta_norm):
                    conocimiento['economia_conocida'] = True
                
                # === LOGROS ===
                if re.search(r'\b(premio|nobel|revoluciono|cambio historia|descubrimientos)\b', pregunta_norm):
                    conocimiento['logros_conocidos'] = True
                
                # === ROL ===
                if re.search(r'\b(lider|gobernante|general|presidente|rey|reina)\b', pregunta_norm):
                    conocimiento['rol_conocido'] = True
                
                # === MORAL ===
                if re.search(r'\b(pacifista|conquistador|libertad|violento)\b', pregunta_norm):
                    conocimiento['moral_conocido'] = True
        
        return conocimiento
    
    # ===============================================================
    # NUEVA FUNCIÓN: GENERAR SUGERENCIAS PERFILADAS
    # ===============================================================
    @staticmethod
    def generate_profiled_suggestions(conocimiento: Dict, preguntas_norm: List[str]) -> List[str]:
        """
        Genera sugerencias específicas para perfilar al personaje cuando ya se tiene suficiente información.
        - Para personajes reales: se enfoca en profesión, logros, rol histórico, moral, etc.
        - Para personajes ficticios: se enfoca en tipo, poderes, universo, armas, especie, etc.
        Solo se incluyen preguntas que aún no se han respondido (según el conocimiento) y que no se hayan preguntado ya.
        """
        perfiladas = []
        
        # Si no se conoce el tipo, no podemos perfilar (devolver vacío)
        if not conocimiento['tipo_conocido']:
            return perfiladas
        
        tipo = conocimiento['tipo']
        
        # === PARA PERSONAJES REALES ===
        if tipo == 'real':
            # Profesión (si no se conoce)
            if not conocimiento['profesion_conocida']:
                if conocimiento['genero'] == 'femenino':
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_femenino'])
                elif conocimiento['genero'] == 'masculino':
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'])
                else:
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'][:5])
            
            # Logros (si no se conocen)
            if not conocimiento['logros_conocidos']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_logros'])
            
            # Rol político/militar (si no se conoce)
            if not conocimiento['rol_conocido']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_rol'])
            
            # Moral (si no se conoce)
            if not conocimiento['moral_conocido']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_moral'])
            
            # Ideología (siempre puede ser relevante)
            perfiladas.extend(GeneradorSugerencias.PREGUNTAS['real_ideologia'])
        
        # === PARA PERSONAJES FICTICIOS ===
        elif tipo == 'ficticio':
            # Tipo específico (si no se conoce) - con género
            if not conocimiento['tipo_ficticio_conocido']:
                if conocimiento['genero'] == 'femenino':
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_tipo_femenino'])
                else:
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_tipo_masculino'])
            
            # Poderes (si no se conocen) - neutro
            if not conocimiento['poderes_conocidos']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_poderes_masculino'])  # Neutro
            
            # Armas (si no se conocen)
            if not conocimiento['armas_conocidas']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_armas'])
            
            # Especie (si no se conoce)
            if not conocimiento['especie_conocida']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_especie'])
            
            # Universo (si no se conoce y no se ha filtrado por tipo)
            if not conocimiento['universo_conocido']:
                # Si es superhéroe, priorizar universos de cómics
                if conocimiento.get('tipo_ficticio') == 'superheroe':
                    perfiladas.extend([
                        "¿Es de DC Comics?",
                        "¿Es de Marvel?",
                    ])
                # Si es mago, priorizar universos de fantasía
                elif conocimiento.get('tipo_ficticio') == 'mago':
                    perfiladas.extend([
                        "¿Es de Harry Potter?",
                        "¿Es del Señor de los Anillos?",
                    ])
                else:
                    perfiladas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_universo'])
            
            # Formato (si no se conoce)
            if not conocimiento['formato_conocido']:
                perfiladas.extend(GeneradorSugerencias.PREGUNTAS['formato'])
        
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
        
        return resultado[:5]  # Limitamos a 5 para no saturar
    
    # ===============================================================
    # GENERACIÓN INTELIGENTE DE SUGERENCIAS (CORREGIDA)
    # ===============================================================
    
    @staticmethod
    def generar(preguntas_hechas: List[str], respuestas: List[str], max_sugerencias: int = 5) -> List[str]:
        """
        Genera sugerencias dinámicas y contextuales basadas en el estado actual.
        AHORA CON MODO PERFILADO ACTIVABLE POR SUFICIENTE INFORMACIÓN.
        """
        
        # FASE 1: Extraer conocimiento
        conocimiento = GeneradorSugerencias.extraer_conocimiento(preguntas_hechas, respuestas)
        
        # FASE 2: Normalizar preguntas hechas para filtrado
        preguntas_norm = [Normalizador.normalizar(p) for p in preguntas_hechas]
        
        # FASE 3: Pool de candidatas
        candidatas = []
        
        # === PRIORIDAD 1: TIPO (si no se conoce) ===
        if not conocimiento['tipo_conocido']:
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['tipo'])
        
        # === PRIORIDAD 2: GÉNERO (si no se conoce) ===
        if not conocimiento['genero_conocido']:
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['genero_masculino'])
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['genero_femenino'])
        
        # === RAMA PARA PERSONAJES REALES ===
        if conocimiento['tipo'] == 'real':
            # Estado vital
            if not conocimiento['vital_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_vital'])
            
            # Fama
            if not conocimiento['fama_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_fama'])
            
            # Profesión adaptada al género
            if not conocimiento['profesion_conocida']:
                if conocimiento['genero'] == 'femenino':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_femenino'])
                elif conocimiento['genero'] == 'masculino':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'])
                else:
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'][:5])
            
            # Continente
            if not conocimiento['continente_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_continente'])
            
            # Nacionalidad específica (si ya se conoce el continente)
            if conocimiento['continente_conocido'] and not conocimiento['nacionalidad_conocida']:
                if conocimiento['continente'] == 'europa':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_nacionalidad_europa'])
                elif conocimiento['continente'] == 'america':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_nacionalidad_america'])
                elif conocimiento['continente'] == 'asia':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_nacionalidad_asia'])
            
            # Época
            if not conocimiento['epoca_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_epoca'])
            
            # Logros
            if not conocimiento['logros_conocidos']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_logros'])
            
            # Rol político/militar
            if not conocimiento['rol_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_rol'])
            
            # Perfil moral
            if not conocimiento['moral_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_moral'])
            
            # Ideología
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_ideologia'])
        
        # === RAMA PARA PERSONAJES FICTICIOS ===
        elif conocimiento['tipo'] == 'ficticio':
            
            # UNIVERSO - FILTRADO POR TIPO DE PERSONAJE
            if not conocimiento['universo_conocido']:
                # Si es superhéroe, priorizar universos de cómics
                if conocimiento.get('tipo_ficticio') == 'superheroe':
                    candidatas.extend([
                        "¿Es de DC Comics?",
                        "¿Es de Marvel?",
                        "¿Es de un cómic?"
                    ])
                # Si es mago, priorizar universos de fantasía
                elif conocimiento.get('tipo_ficticio') == 'mago':
                    candidatas.extend([
                        "¿Es de Harry Potter?",
                        "¿Es del Señor de los Anillos?",
                        "¿Usa magia?",
                        "¿Tiene una varita?"
                    ])
                # Si es villano, puede ser de cualquier universo
                else:
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_universo'])
            
            # Tipo de personaje ficticio (si no se conoce) - CON GÉNERO
            if not conocimiento['tipo_ficticio_conocido']:
                if conocimiento['genero'] == 'femenino':
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_tipo_femenino'])
                else:
                    candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_tipo_masculino'])
            
            # Poderes (si no se conocen) - neutro
            if not conocimiento['poderes_conocidos']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_poderes_masculino'])  # Neutro
            
            # Armas (si no se conocen)
            if not conocimiento['armas_conocidas']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_armas'])
            
            # Especie (si no se conoce)
            if not conocimiento['especie_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_especie'])
            
            # Formato (si no se conoce)
            if not conocimiento['formato_conocido']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['formato'])
            
            # Rol
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_rol'])
        
        # === TIPO DESCONOCIDO: Mix de ambas categorías ===
        else:
            if not conocimiento['fama_conocida']:
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_fama'])
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_continente'][:2])
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['ficticio_universo'][:2])
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['formato'][:2])
            
            if conocimiento['genero'] == 'masculino':
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_masculino'][:3])
            elif conocimiento['genero'] == 'femenino':
                candidatas.extend(GeneradorSugerencias.PREGUNTAS['real_profesion_femenino'][:3])
        
        # === CARACTERÍSTICAS FÍSICAS (siempre relevantes) ===
        for caracteristica in ['gafas', 'barba', 'calvo', 'alto', 'bajo']:
            if caracteristica not in conocimiento['fisico_conocido']:
                preguntas_fisicas = [p for p in GeneradorSugerencias.PREGUNTAS['fisico'] if caracteristica in p.lower()]
                candidatas.extend(preguntas_fisicas)
        
        # === ECONOMÍA (si no se conoce) ===
        if not conocimiento['economia_conocida']:
            candidatas.extend(GeneradorSugerencias.PREGUNTAS['economia'])
        
        # FASE 4: Filtrar preguntas ya hechas o redundantes
        sugerencias_finales = []
        
        for candidata in candidatas:
            candidata_norm = Normalizador.normalizar(candidata)
            
            # Verificar que no se haya preguntado ya
            ya_preguntada = False
            
            for p_norm in preguntas_norm:
                palabras_candidata = set(candidata_norm.split())
                palabras_pregunta = set(p_norm.split())
                
                palabras_especificas = {
                    'real', 'ficticio', 'imaginario', 'inventado', 'existio',
                    'masculino', 'femenino', 'hombre', 'mujer', 'dama', 
                    'vivo', 'muerto', 'fallecio', 
                    'famoso', 'conocido', 'mundialmente', 'celebre', 'reconocido',
                    'rico', 'pobre', 'millonario', 'dinero', 'fortuna',
                    'cientifico', 'artista', 'escritor', 'pintor', 'militar', 'politico',
                    'europa', 'europeo', 'america', 'americano', 'asia', 'asiatico', 'africa',
                    'dc', 'marvel', 'star', 'wars', 'harry', 'potter', 'senor', 'anillos',
                    'poderes', 'superpoderes', 'volar', 'inmortal', 'magia',
                    'arco', 'espada', 'arma', 'gafas', 'barba', 'calvo', 'alto', 'bajo',
                    'antiguedad', 'medieval', 'renacimiento', 'moderna', 'contemporaneo',
                    'comic', 'pelicula', 'libro', 'serie'
                }
                
                palabras_comunes = palabras_candidata & palabras_pregunta & palabras_especificas
                
                if len(palabras_comunes) >= 1:
                    ya_preguntada = True
                    break
                
                if len(palabras_candidata & palabras_pregunta) >= 3:
                    ya_preguntada = True
                    break
            
            # FILTROS DE CONOCIMIENTO
            if conocimiento['genero'] == 'masculino':
                if any(palabra in candidata_norm for palabra in ['mujer', 'femenino', 'dama']):
                    continue
            elif conocimiento['genero'] == 'femenino':
                if any(palabra in candidata_norm for palabra in ['hombre', 'masculino']):
                    continue
            
            if conocimiento['tipo'] == 'real':
                if any(palabra in candidata_norm for palabra in ['ficticio', 'imaginario', 'inventado', 'comic', 'pelicula', 'dc', 'marvel']):
                    continue
            elif conocimiento['tipo'] == 'ficticio':
                if any(palabra in candidata_norm for palabra in ['real', 'existio', 'historico']):
                    continue
            
            # Agregar solo si no está repetida
            if not ya_preguntada and candidata not in sugerencias_finales:
                sugerencias_finales.append(candidata)
            
            if len(sugerencias_finales) >= max_sugerencias * 4:
                break
        
        # ===== NUEVO: MODO PERFILADO =====
        # Si hay suficientes preguntas (≥12), agregar sugerencias perfiladas
        if len(preguntas_hechas) >= 12:
            perfiladas = GeneradorSugerencias.generate_profiled_suggestions(conocimiento, preguntas_norm)
            # Agregar sin duplicar
            for p in perfiladas:
                if p not in sugerencias_finales:
                    sugerencias_finales.append(p)
        # ===== FIN MODO PERFILADO =====
        
        # FASE 5: Mezclar todas las candidatas
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
        
        # ===== START =====
        if action == 'start':
            # Reiniciar completamente el estado de la partida
            current_game = {
                'character': None,
                'questions': [],
                'answers': [],
                'questions_count': 0
            }
            personaje = random.choice(PERSONAJES)
            current_game['character'] = personaje
            current_game['questions'] = []
            current_game['answers'] = []
            current_game['questions_count'] = 0
            
            return jsonify({
                'character': personaje,
                'max_questions': MAX_PREGUNTAS
            })
        
        # ===== ASK =====
        elif action == 'ask':
            if not current_game.get('character'):
                return jsonify({'error': 'No hay partida activa'}), 404
            
            pregunta = data.get('question', '')
            personaje = current_game['character']
            
            resultado = AnalizadorPreguntas.analizar(pregunta, personaje)
            
            current_game['questions'].append(pregunta)
            current_game['answers'].append(resultado['answer'])
            current_game['questions_count'] += 1
            
            metricas_manager.registrar_pregunta(pregunta)
            
            return jsonify(resultado)
        
        # ===== SUGGESTIONS =====
        elif action == 'suggestions':
            if not current_game.get('character'):
                return jsonify({'suggestions': []})
            
            sugerencias = GeneradorSugerencias.generar(
                current_game['questions'],
                current_game['answers'],
                max_sugerencias=5
            )
            
            return jsonify({'suggestions': sugerencias})
        
        # ===== HINT =====
        elif action == 'hint':
            if not current_game.get('character'):
                return jsonify({'hint': 'No hay partida activa'})
            
            pistas = current_game['character'].get('pistas', [])
            hint_level = data.get('hint_level', 1)
            
            # CORREGIDO: Usar hint_level en lugar de random.choice
            if hint_level == 1 and len(pistas) > 0:
                hint = pistas[0]
            elif hint_level == 2 and len(pistas) > 1:
                hint = pistas[1]
            else:
                hint = "No hay más pistas disponibles."
            
            return jsonify({'hint': hint})
        
        # ===== GUESS =====
        elif action == 'guess':
            if not current_game.get('character'):
                return jsonify({'error': 'No hay partida activa'}), 404
            
            guess = data.get('guess', '').strip().lower()
            nombre_real = current_game['character']['nombre'].lower()
            correcto = guess == nombre_real
            
            metricas_manager.registrar_resultado(
                current_game['character']['nombre'],
                correcto
            )
            
            return jsonify({
                'correct': correcto,
                'character': current_game['character']['nombre'],
                'hints': current_game['character'].get('pistas', [])
            })
        
        return jsonify({'error': 'Acción no válida'}), 400
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'personajes': len(PERSONAJES),
        'mensaje': 'The Oracle está funcionando correctamente'
    })


@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    return jsonify(metricas_manager.metricas)


@app.route('/api/dashboard/huecos', methods=['GET'])
def dashboard_huecos():
    huecos = []
    if os.path.exists(REGISTRO_HUECOS_FILE):
        with open(REGISTRO_HUECOS_FILE, 'r', encoding='utf-8') as f:
            huecos = json.load(f)
    return jsonify({'huecos': huecos})


@app.route('/api/dashboard/exportar-txt', methods=['GET'])
def exportar_txt():
    output = StringIO()
    output.write("=" * 80 + "\n")
    output.write("THE ORACLE - REPORTE\n")
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


# ===================================================================
# MAIN
# ===================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🧠 THE ORACLE - Backend HÍBRIDO")
    print("=" * 60)
    print(f"📡 Servidor: http://0.0.0.0:5000")
    print(f"🎭 Personajes: {len(PERSONAJES)}")
    print(f"📊 Dashboard: http://0.0.0.0:5000/dashboard")
    print("✅ Sistema de métricas ACTIVADO")
    print("✅ Analizador con 60+ patrones")
    print("=" * 60)
    # Puerto para producción
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
