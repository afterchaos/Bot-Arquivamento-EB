import discord
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

# Lista de status
STATUS_LIST = [
    discord.Activity(type=discord.ActivityType.watching, name="Registros 📂"),
    discord.Activity(type=discord.ActivityType.playing, name="Sistema de Arquivamento"),
    discord.Activity(type=discord.ActivityType.listening, name="Relatórios 🎧"),
    discord.Activity(type=discord.ActivityType.competing, name="Organização ⚖️"),
    discord.Activity(type=discord.ActivityType.playing, name="Desenvolvido por witheringfeelings"),
    discord.Activity(type=discord.ActivityType.listening, name="Apoiado por guilhukifi2")
]

# Lista de patentes
PATENTES_LISTA = {
    "Governo Federal": "GOV",
    "Comandante": "Cmt",
    "Subcomandante": "SCmt",
    "General-de-Exército": "Gen-Ex",
    "General-de-Divisão": "Gen-Div",
    "General-de-Brigada": "Gen-Bda",
    "Coronel": "Cel",
    "Tenente-Coronel": "TenCel",
    "Major": "Maj",
    "Capitão": "Cap",
    "1º Tenente": "1º Ten",
    "2º Tenente": "2º Ten",
    "Aspirante": "Asp",
    "Subtenente": "ST",
    "Primeiro-Sargento": "1º Sgt",
    "Segundo-Sargento": "2º Sgt",
    "Terceiro-Sargento": "3º Sgt",
    "Cabo": "Cb",
    "Soldado": "Sd",
    "Recruta": "Rcr",
    "Civil" : "Cv"
}

HIERARQUIA_PATENTES = {
    "GOV": 20,
    "Cmt": 19,
    "SCmt": 18,
    "Gen-Ex": 17,
    "Gen-Div": 16,
    "Gen-Bda": 15,
    "Cel": 14,
    "TenCel": 13,
    "Maj": 12,
    "Cap": 11,
    "1º Ten": 10,
    "2º Ten": 9,
    "Asp": 8,
    "ST": 7,
    "1º Sgt": 6,
    "2º Sgt": 5,
    "3º Sgt": 4,
    "Cb": 3,
    "Sd": 2,
    "Rcr": 1,
    "Cv": 0
}

PATENTES_ESCOLHA = [
    app_commands.Choice(name=nome, value=sigla)
    for nome, sigla in PATENTES_LISTA.items()
]

TIPOS_ARQUIVO = {
    'exilio': {
        'cor': 0x3498db, 
        'titulo': 'SISTEMA DE ARQUIVAMENTO | EXILIO',
        'canal_id': 1486917972407619614
    },
    'exilio_perm': {
        'cor': 0x2c3e50, 
        'titulo': 'SISTEMA DE ARQUIVAMENTO | EXILIO PERMANENTE',
        'canal_id': 1489058634028679240
    },
    'castigo': {
        'cor': 0xe67e22, 
        'titulo': 'SISTEMA DE ARQUIVAMENTO | CASTIGO',
        'canal_id': 1496677727506272357
    },
    'banimento': {
        'cor': 0xe74c3c, 
        'titulo': 'SISTEMA DE ARQUIVAMENTO | BANIMENTO',
        'canal_id': 1489059104025608254
    },
    'rebaixamento': {
        'cor': 0xf1c40f, 
        'titulo': 'SISTEMA DE ARQUIVAMENTO | REBAIXAMENTO',
        'canal_id': 1489058973909913600
    },
    'afastamento': {
        'cor': 0x1abc9c, 
        'titulo': 'SISTEMA DE ARQUIVAMENTO | AFASTAMENTO',
        'canal_id': 1496758491237585026
    },
    'relacionamento': {
        'cor': 0x9b59b6, 
        'titulo': 'SISTEMA DE ARQUIVAMENTO | RELACIONAMENTO',
        'canal_id': 1489059444296781957
    }
}
