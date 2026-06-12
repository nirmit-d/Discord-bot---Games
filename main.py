import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import asyncio
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ─── Data file ────────────────────────────────────────────────────────────────
DATA_FILE = "data/economy.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "balance": 100,
            "streak": 0,
            "wins": 0,
            "losses": 0,
            "games_played": 0,
            "total_earned": 0,
            "inventory": [],
            "active_ability": None,
            "last_daily": None,
            "last_weekly": None,
            "username": "Unknown"
        }
    return data[uid]

# ─── All 500 games ─────────────────────────────────────────────────────────────
GAMES = {
    1: {"name": "Weekly Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    2: {"name": "Emoji Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    3: {"name": "Casino Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    4: {"name": "Quick Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    5: {"name": "Final Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    6: {"name": "Mega Sky Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    7: {"name": "Shadow Cooking Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    8: {"name": "Math Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    9: {"name": "Sneaky Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    10: {"name": "Space Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    11: {"name": "Super Farm League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    12: {"name": "Lottery Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    13: {"name": "Hidden League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    14: {"name": "Shadow Galaxy Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    15: {"name": "Ultimate Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    16: {"name": "Quick Sports Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    17: {"name": "Cosmic Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    18: {"name": "Stock Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    19: {"name": "Wizard Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    20: {"name": "Stock Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    21: {"name": "Ultra Casino Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    22: {"name": "Last Storm Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    23: {"name": "Fishing Sprint", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    24: {"name": "Savage Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    25: {"name": "Mystic Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    26: {"name": "Desert Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    27: {"name": "Super Casino Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    28: {"name": "Monster Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    29: {"name": "Last Movie Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    30: {"name": "Shadow Word Heist", "category": "Word/Text", "ability": "Reveal Letter", "ability_cost": 50},
    31: {"name": "Daily Pirate Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    32: {"name": "Hidden Mining Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    33: {"name": "Robot Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    34: {"name": "Mega Ice Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    35: {"name": "Random Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    36: {"name": "Brutal Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    37: {"name": "Desert Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    38: {"name": "Galactic Stock Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    39: {"name": "Ocean Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    40: {"name": "Word Match", "category": "Word/Text", "ability": "Reveal Letter", "ability_cost": 50},
    41: {"name": "Cyber Monster Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    42: {"name": "Garden Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    43: {"name": "Turbo Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    44: {"name": "Turbo Dice Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    45: {"name": "Memory Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    46: {"name": "Super Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    47: {"name": "Rapid Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    48: {"name": "Emoji Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    49: {"name": "Hidden Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    50: {"name": "Mystic Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    51: {"name": "Farm Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    52: {"name": "Rapid Wizard Adventure", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    53: {"name": "Blazing Lottery Game", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    54: {"name": "Super Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    55: {"name": "Jungle Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    56: {"name": "Silent Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    57: {"name": "Stock Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    58: {"name": "Brutal Math League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    59: {"name": "Last Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    60: {"name": "Mystic Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    61: {"name": "Infinite Cave Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    62: {"name": "Random Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    63: {"name": "Random Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    64: {"name": "Mining Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    65: {"name": "Brutal Card Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    66: {"name": "Neon Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    67: {"name": "Number Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    68: {"name": "Dragon Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    69: {"name": "Mining Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    70: {"name": "Mega Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    71: {"name": "Pixel Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    72: {"name": "Tiny Movie Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    73: {"name": "Ultra Ice Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    74: {"name": "Trivia Royale", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    75: {"name": "Brutal Cooking Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    76: {"name": "Trivia Riddle", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    77: {"name": "Stock Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    78: {"name": "Blazing Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    79: {"name": "Wizard Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    80: {"name": "Galactic Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    81: {"name": "Dark Jungle Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    82: {"name": "Rapid Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    83: {"name": "Fishing Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    84: {"name": "Sneaky Lottery Match", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    85: {"name": "Wild Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    86: {"name": "Dark Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    87: {"name": "Sneaky Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    88: {"name": "Jungle Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    89: {"name": "Silent Desert Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    90: {"name": "Emoji Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    91: {"name": "Retro Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    92: {"name": "Pixel Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    93: {"name": "Blazing Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    94: {"name": "Number Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    95: {"name": "Dark Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    96: {"name": "Cyber Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    97: {"name": "Number Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    98: {"name": "Shadow Mining Roulette", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    99: {"name": "Desert Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    100: {"name": "Sneaky Emoji Adventure", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    101: {"name": "Trivia Race", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    102: {"name": "Word Saga", "category": "Word/Text", "ability": "Reveal Letter", "ability_cost": 50},
    103: {"name": "Mega Dice Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    104: {"name": "Ultra Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    105: {"name": "Pixel Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    106: {"name": "Lucky Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    107: {"name": "Golden Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    108: {"name": "Quick Cave Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    109: {"name": "Chaos Fishing Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    110: {"name": "Giant Treasure Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    111: {"name": "Mega Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    112: {"name": "Retro Treasure Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    113: {"name": "Treasure Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    114: {"name": "Wild Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    115: {"name": "Tiny Emoji Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    116: {"name": "Cyber Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    117: {"name": "Giant Ocean Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    118: {"name": "Animal Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    119: {"name": "Dice Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    120: {"name": "Savage Roulette", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    121: {"name": "Weekly Jungle League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    122: {"name": "Dragon Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    123: {"name": "Sports Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    124: {"name": "Frozen Ninja Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    125: {"name": "Sneaky Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    126: {"name": "Retro Dice Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    127: {"name": "Super Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    128: {"name": "Number Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    129: {"name": "Wild Number Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    130: {"name": "Mega Wizard Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    131: {"name": "Casino Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    132: {"name": "Infinite Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    133: {"name": "Infinite Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    134: {"name": "Royal Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    135: {"name": "Dragon Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    136: {"name": "Infinite Garden Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    137: {"name": "Neon Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    138: {"name": "Ultra Treasure Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    139: {"name": "Daily Space Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    140: {"name": "Cave Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    141: {"name": "Crazy Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    142: {"name": "Number Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    143: {"name": "Fishing Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    144: {"name": "Savage City Adventure", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    145: {"name": "Last Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    146: {"name": "Silent Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    147: {"name": "Ultimate Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    148: {"name": "Crazy Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    149: {"name": "Dark Cooking Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    150: {"name": "Silent Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    151: {"name": "Mining Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    152: {"name": "Cyber Roulette", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    153: {"name": "Endless Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    154: {"name": "Random Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    155: {"name": "Savage Pirate Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    156: {"name": "Lottery Game", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    157: {"name": "Ultimate Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    158: {"name": "Cyber Robot League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    159: {"name": "Wild Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    160: {"name": "Secret Movie Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    161: {"name": "Frozen Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    162: {"name": "Frozen Fishing Sprint", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    163: {"name": "Tiny Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    164: {"name": "Lucky Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    165: {"name": "Weekly Ice Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    166: {"name": "Silent Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    167: {"name": "Weekly Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    168: {"name": "Fire Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    169: {"name": "Stock Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    170: {"name": "Ultra Farm Roulette", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    171: {"name": "Trivia Tournament", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    172: {"name": "Epic Color Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    173: {"name": "Epic Sky Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    174: {"name": "Cave Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    175: {"name": "Blazing Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    176: {"name": "Cyber Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    177: {"name": "Lucky Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    178: {"name": "Sneaky Storm Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    179: {"name": "Chaos Robot Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    180: {"name": "Fishing Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    181: {"name": "Super Math Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    182: {"name": "Silent Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    183: {"name": "Chaos Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    184: {"name": "Galactic Robot Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    185: {"name": "Silent Sky Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    186: {"name": "Hidden Lottery Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    187: {"name": "Neon Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    188: {"name": "Space Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    189: {"name": "Super Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    190: {"name": "Mega City Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    191: {"name": "Dark Number Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    192: {"name": "Mining Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    193: {"name": "Stock Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    194: {"name": "Blazing Word Wars", "category": "Word/Text", "ability": "Reveal Letter", "ability_cost": 50},
    195: {"name": "Sky Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    196: {"name": "City Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    197: {"name": "Mining Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    198: {"name": "Final Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    199: {"name": "Daily Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    200: {"name": "Garden Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    201: {"name": "Ultimate Dragon Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    202: {"name": "Monster Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    203: {"name": "Secret Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    204: {"name": "Final Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    205: {"name": "Fire Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    206: {"name": "Pixel Number Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    207: {"name": "Golden Wizard Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    208: {"name": "Music Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    209: {"name": "Sports Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    210: {"name": "Mega Ocean Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    211: {"name": "Ultimate City Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    212: {"name": "Tiny Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    213: {"name": "Movie Adventure", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    214: {"name": "Ultra Robot Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    215: {"name": "Pixel Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    216: {"name": "Hidden Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    217: {"name": "Savage Math Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    218: {"name": "Mystic Dice Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    219: {"name": "Rapid Garden Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    220: {"name": "Random Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    221: {"name": "Cosmic Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    222: {"name": "Wild Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    223: {"name": "Secret Galaxy Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    224: {"name": "Crazy Movie Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    225: {"name": "Daily Robot Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    226: {"name": "Shadow Fire Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    227: {"name": "Sports Game", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    228: {"name": "Monster Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    229: {"name": "Shadow Zombie Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    230: {"name": "Golden Math Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    231: {"name": "Treasure Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    232: {"name": "Rapid Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    233: {"name": "Mystic Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    234: {"name": "Cooking Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    235: {"name": "Silent Galaxy Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    236: {"name": "Dark Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    237: {"name": "Savage Desert Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    238: {"name": "Ninja Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    239: {"name": "Neon Dragon Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    240: {"name": "Shadow Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    241: {"name": "Lottery Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    242: {"name": "Ultra Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    243: {"name": "Super Space Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    244: {"name": "Farm Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    245: {"name": "Jungle Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    246: {"name": "Cyber Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    247: {"name": "Endless Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    248: {"name": "Movie League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    249: {"name": "Chaos Adventure", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    250: {"name": "Pixel Ice Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    251: {"name": "Zombie Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    252: {"name": "Cooking Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    253: {"name": "Epic Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    254: {"name": "Mega Game", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    255: {"name": "Ice Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    256: {"name": "Animal Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    257: {"name": "Royal Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    258: {"name": "Final Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    259: {"name": "Sneaky Card Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    260: {"name": "Zombie Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    261: {"name": "Tiny Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    262: {"name": "Ultra Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    263: {"name": "Random Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    264: {"name": "Rapid Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    265: {"name": "Dice Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    266: {"name": "Endless Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    267: {"name": "Rapid Animal Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    268: {"name": "Ninja Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    269: {"name": "Pixel Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    270: {"name": "Hidden Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    271: {"name": "Daily Farm Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    272: {"name": "Fishing Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    273: {"name": "Galactic City Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    274: {"name": "Wild Robot Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    275: {"name": "Wild Zombie Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    276: {"name": "Royal Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    277: {"name": "Brutal Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    278: {"name": "Epic Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    279: {"name": "Stock Sprint", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    280: {"name": "Sneaky Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    281: {"name": "Color Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    282: {"name": "Savage Math Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    283: {"name": "Dice Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    284: {"name": "Dice Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    285: {"name": "Final Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    286: {"name": "Silent Treasure Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    287: {"name": "Ice Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    288: {"name": "Frozen Trivia Dungeon", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    289: {"name": "Infinite Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    290: {"name": "Cosmic Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    291: {"name": "Last Cooking Game", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    292: {"name": "Dark Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    293: {"name": "Daily Cooking Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    294: {"name": "Super Wizard Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    295: {"name": "Secret Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    296: {"name": "Blazing Trivia Maze", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    297: {"name": "Color Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    298: {"name": "Ultra Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    299: {"name": "Sneaky Treasure Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    300: {"name": "Treasure Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    301: {"name": "Treasure Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    302: {"name": "Mega Farm Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    303: {"name": "Blazing Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    304: {"name": "Mining Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    305: {"name": "Robot Game", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    306: {"name": "Desert Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    307: {"name": "Pixel Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    308: {"name": "Crazy Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    309: {"name": "Weekly Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    310: {"name": "Desert Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    311: {"name": "Galaxy Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    312: {"name": "City Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    313: {"name": "Super Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    314: {"name": "Pirate Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    315: {"name": "Lucky Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    316: {"name": "Monster Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    317: {"name": "Sneaky Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    318: {"name": "Quick Space Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    319: {"name": "Weekly Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    320: {"name": "Epic Number Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    321: {"name": "Turbo Stock Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    322: {"name": "Pixel Sprint", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    323: {"name": "Wizard League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    324: {"name": "Brutal Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    325: {"name": "Secret City Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    326: {"name": "Number Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    327: {"name": "Animal Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    328: {"name": "Sneaky Ice Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    329: {"name": "Number Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    330: {"name": "Infinite Cooking Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    331: {"name": "Memory Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    332: {"name": "Word Heist", "category": "Word/Text", "ability": "Reveal Letter", "ability_cost": 50},
    333: {"name": "Frozen Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    334: {"name": "Blazing City Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    335: {"name": "Chaos Farm Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    336: {"name": "Random Storm Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    337: {"name": "Pixel Dragon Raid", "category": "RPG Co-op", "ability": "Revive", "ability_cost": 75},
    338: {"name": "Color Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    339: {"name": "Cooking Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    340: {"name": "Mystic Zombie Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    341: {"name": "Mining Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    342: {"name": "Storm Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    343: {"name": "Math Roulette", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    344: {"name": "Mega Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    345: {"name": "Galaxy Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    346: {"name": "Casino Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    347: {"name": "Galaxy Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    348: {"name": "Ocean Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    349: {"name": "Music Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    350: {"name": "Silent Sprint", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    351: {"name": "Pixel Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    352: {"name": "Zombie Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    353: {"name": "Storm Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    354: {"name": "Jungle Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    355: {"name": "Endless Puzzle", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    356: {"name": "Brutal Dice Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    357: {"name": "Super Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    358: {"name": "Music Game", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    359: {"name": "Last Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    360: {"name": "Epic Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    361: {"name": "Crazy Fishing Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    362: {"name": "Brutal Ocean Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    363: {"name": "Quick Fishing Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    364: {"name": "Lucky Zombie Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    365: {"name": "Giant Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    366: {"name": "Epic Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    367: {"name": "Savage Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    368: {"name": "Infinite Lottery Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    369: {"name": "Retro Game", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    370: {"name": "Royal Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    371: {"name": "Galactic Movie Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    372: {"name": "Storm Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    373: {"name": "Lottery Match", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    374: {"name": "Cyber Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    375: {"name": "Trivia Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    376: {"name": "Hidden Robot Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    377: {"name": "Savage Dragon Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    378: {"name": "Infinite Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    379: {"name": "Ninja Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    380: {"name": "Dark Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    381: {"name": "Retro Card Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    382: {"name": "Infinite Music Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    383: {"name": "Frozen Robot Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    384: {"name": "Endless Sprint", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    385: {"name": "Giant Ninja Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    386: {"name": "Retro Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    387: {"name": "Pixel Sky Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    388: {"name": "Crazy Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    389: {"name": "Farm Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    390: {"name": "Neon Treasure Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    391: {"name": "Silent Pirate Roulette", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    392: {"name": "Lucky League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    393: {"name": "Galactic Stock Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    394: {"name": "Frozen Cave Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    395: {"name": "Shadow Dice League", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    396: {"name": "Random Ice Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    397: {"name": "Cosmic Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    398: {"name": "Lucky Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    399: {"name": "Weekly Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    400: {"name": "Number Roulette", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    401: {"name": "Quick Dragon Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    402: {"name": "Rapid Draw", "category": "Creative", "ability": "Extra Hint", "ability_cost": 50},
    403: {"name": "Secret Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    404: {"name": "Dark Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    405: {"name": "Ninja Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    406: {"name": "Cosmic Robot Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    407: {"name": "Blazing Emoji Clash", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    408: {"name": "Dark Garden Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    409: {"name": "Dice Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    410: {"name": "Random Casino Throne", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    411: {"name": "Pirate Gauntlet", "category": "RPG Survival", "ability": "Extra Life", "ability_cost": 75},
    412: {"name": "Dark Card Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    413: {"name": "Lucky Sports Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    414: {"name": "Brutal Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    415: {"name": "Super Zombie Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    416: {"name": "Farm Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    417: {"name": "Quick Desert Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    418: {"name": "Sneaky Desert Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    419: {"name": "Infinite Cooking Battle", "category": "PvP/RPG", "ability": "Heal", "ability_cost": 50},
    420: {"name": "Frozen Sky Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    421: {"name": "Wild Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    422: {"name": "Neon Game", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    423: {"name": "Fire Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    424: {"name": "Royal Robot Frenzy", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    425: {"name": "Retro Word Match", "category": "Word/Text", "ability": "Reveal Letter", "ability_cost": 50},
    426: {"name": "Dark Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    427: {"name": "Daily Trivia Adventure", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    428: {"name": "Brutal Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    429: {"name": "Brutal Robot Sprint", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    430: {"name": "Fire Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    431: {"name": "Card Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    432: {"name": "Memory Quiz", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    433: {"name": "Lucky Kingdom", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    434: {"name": "Random Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    435: {"name": "Fishing Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    436: {"name": "Hidden Casino Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    437: {"name": "Golden Trivia Vault", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    438: {"name": "Movie Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    439: {"name": "Blazing Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    440: {"name": "Hidden Zombie Hunt", "category": "Adventure", "ability": "Map Reveal", "ability_cost": 50},
    441: {"name": "Brutal Storm Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    442: {"name": "Wizard Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    443: {"name": "Ninja Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    444: {"name": "Royal Card Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    445: {"name": "Lucky Stock Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    446: {"name": "Endless Jungle Wars", "category": "Strategy PvP", "ability": "Undo", "ability_cost": 50},
    447: {"name": "Super Casino Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    448: {"name": "Sports Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    449: {"name": "Shadow Trivia Madness", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    450: {"name": "Jungle Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    451: {"name": "Tiny Casino Sprint", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    452: {"name": "Animal Dungeon", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    453: {"name": "Fire Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    454: {"name": "Weekly Bet", "category": "Casino", "ability": "Double Coin Ball", "ability_cost": 50},
    455: {"name": "Color Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    456: {"name": "Final Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    457: {"name": "Super Duel", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    458: {"name": "Tiny Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    459: {"name": "Infinite Wizard Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    460: {"name": "Random Trivia", "category": "Trivia", "ability": "Insight", "ability_cost": 50},
    461: {"name": "Math Adventure", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    462: {"name": "Pirate Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    463: {"name": "Last Word Match", "category": "Word/Text", "ability": "Reveal Letter", "ability_cost": 50},
    464: {"name": "Brutal Arena", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    465: {"name": "Turbo Jungle Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    466: {"name": "Sneaky Vault", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    467: {"name": "Turbo Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    468: {"name": "Super Stock Royale", "category": "Battle Royale", "ability": "Extra Life", "ability_cost": 75},
    469: {"name": "Ninja Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    470: {"name": "Galactic Stock Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    471: {"name": "Sneaky Number Madness", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    472: {"name": "Crazy Ice Roulette", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    473: {"name": "Quick Casino Race", "category": "Speed", "ability": "Speed Boost", "ability_cost": 50},
    474: {"name": "Golden Word Battle", "category": "Word/Text", "ability": "Reveal Letter", "ability_cost": 50},
    475: {"name": "Ultimate Movie Empire", "category": "Strategy", "ability": "Undo", "ability_cost": 50},
    476: {"name": "Daily Odyssey", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    477: {"name": "Savage Stock Maze", "category": "Puzzle", "ability": "Path Reveal", "ability_cost": 50},
    478: {"name": "Mystic Fire Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    479: {"name": "Endless Tournament", "category": "Competitive", "ability": "Bye Round", "ability_cost": 75},
    480: {"name": "Music Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    481: {"name": "Rapid Sports Saga", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    482: {"name": "Secret Rumble", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    483: {"name": "Silent Mayhem", "category": "Party", "ability": "Extra Vote", "ability_cost": 50},
    484: {"name": "Ocean Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    485: {"name": "Mining Adventure", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    486: {"name": "Royal Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    487: {"name": "Pirate Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    488: {"name": "Pixel Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    489: {"name": "Golden Mining Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    490: {"name": "Tiny Fire Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    491: {"name": "Wild Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    492: {"name": "Crazy Math Puzzle", "category": "Puzzle", "ability": "Hint", "ability_cost": 50},
    493: {"name": "Storm Showdown", "category": "PvP", "ability": "Shield", "ability_cost": 50},
    494: {"name": "Retro Color Match", "category": "Memory", "ability": "Peek", "ability_cost": 50},
    495: {"name": "Wild Ninja Riddle", "category": "Trivia", "ability": "Hint", "ability_cost": 50},
    496: {"name": "Chaos Heist", "category": "Adventure PvP", "ability": "Disguise", "ability_cost": 60},
    497: {"name": "Last Ocean Quest", "category": "RPG", "ability": "Heal", "ability_cost": 50},
    498: {"name": "Frozen Challenge", "category": "General", "ability": "Lucky Charm", "ability_cost": 40},
    499: {"name": "Dice Spin", "category": "Casino", "ability": "Lucky Ball", "ability_cost": 40},
    500: {"name": "Space Adventure", "category": "RPG", "ability": "Heal", "ability_cost": 50},
}

# Build name-to-id lookup
GAME_NAME_LOOKUP = {v["name"].lower(): k for k, v in GAMES.items()}

# ─── Coin formulas per category ───────────────────────────────────────────────
def calc_coins_pvp(difficulty, win, streak, has_shield=False):
    loss_mult = 0.3 if not has_shield else 0.6
    return round(15 * difficulty * (1 if win else loss_mult) + min(streak * 2, 20))

def calc_coins_casino(bet, payout_rate, has_double_coin=False, has_lucky_ball=False):
    if has_lucky_ball:
        payout_rate = min(payout_rate * 1.10, 1.5)
    winnings = round(bet * payout_rate)
    if has_double_coin:
        winnings = round(winnings * 1.5)
    return winnings

def calc_coins_trivia(difficulty, score, max_score, streak, has_insight=False):
    effective_score = score
    if has_insight:
        effective_score = min(score + 1, max_score)
    return round(10 * difficulty * (effective_score / max_score) + min(streak * 2, 20))

def calc_coins_rpg(difficulty, objectives_done, total_objectives, streak, healed=False):
    ratio = objectives_done / max(1, total_objectives)
    if healed:
        ratio = min(ratio + 0.2, 1.0)
    return round(20 * difficulty * ratio + min(streak * 2, 20))

def calc_coins_speed(difficulty, ideal_time, actual_time, streak, has_boost=False):
    ratio = min(1, ideal_time / max(1, actual_time))
    if has_boost:
        ratio = min(ratio * 1.15, 1.0)
    return round(8 * difficulty * ratio + min(streak * 2, 20))

def calc_coins_puzzle(difficulty, mistakes, streak, has_hint=False):
    effective_mistakes = max(0, mistakes - 1) if has_hint else mistakes
    return round(12 * difficulty * (1 / max(1, effective_mistakes + 1)) + min(streak * 2, 20))

def calc_coins_adventure(difficulty, items_found, total_items, streak, has_map=False):
    found = items_found + 1 if has_map else items_found
    return round(20 * difficulty * (min(found, total_items) / total_items) + min(streak * 2, 20))

def calc_coins_strategy(difficulty, territory_held, total_territory, streak, has_undo=False):
    ratio = territory_held / max(1, total_territory)
    return round(15 * difficulty * ratio + min(streak * 2, 20))

def calc_coins_memory(difficulty, attempts, streak, has_peek=False):
    effective = max(1, attempts - 1) if has_peek else attempts
    return round(10 * difficulty * (1 / max(1, effective)) + min(streak * 2, 20))

def calc_coins_word(difficulty, correct_letters, total_letters, streak, has_reveal=False):
    found = correct_letters + 1 if has_reveal else correct_letters
    return round(10 * difficulty * (min(found, total_letters) / total_letters) + min(streak * 2, 20))

def calc_coins_creative(difficulty, guesses_correct, total_players, streak, has_hint=False):
    ratio = guesses_correct / max(1, total_players)
    return round(10 * difficulty * ratio + min(streak * 2, 20))

def calc_coins_coop(difficulty, boss_damage, boss_total_hp, streak, has_revive=False):
    ratio = boss_damage / max(1, boss_total_hp)
    if has_revive:
        ratio = min(ratio + 0.15, 1.0)
    return round(20 * difficulty * ratio + min(streak * 2, 20))

def calc_coins_survival(difficulty, rounds_survived, total_rounds, streak, has_extra_life=False):
    survived = rounds_survived + 1 if has_extra_life else rounds_survived
    return round(20 * difficulty * (min(survived, total_rounds) / total_rounds) + min(streak * 2, 20))

def calc_coins_battle_royale(difficulty, placement, total_players, streak, has_extra_life=False):
    placement_bonus = (total_players - placement + 1) / total_players
    if has_extra_life and placement > 1:
        placement_bonus = min(placement_bonus * 1.2, 1.0)
    return round(20 * difficulty * placement_bonus + min(streak * 2, 20))

def calc_coins_competitive(difficulty, placement, total_players, streak, has_bye=False):
    placement_bonus = (total_players - placement + 1) / total_players
    return round(15 * difficulty * placement_bonus + min(streak * 2, 20))

def calc_coins_party(difficulty, votes_for, total_votes, streak, has_extra_vote=False):
    votes = votes_for + 1 if has_extra_vote else votes_for
    return round(10 * difficulty * (min(votes, total_votes) / max(1, total_votes)) + min(streak * 2, 20))

def calc_coins_general(difficulty, performance_ratio, streak, has_charm=False):
    if has_charm:
        performance_ratio = min(performance_ratio * 1.05, 1.0)
    return round(10 * difficulty * performance_ratio + min(streak * 2, 20))

def calc_coins_adventure_pvp(difficulty, success, streak, has_disguise=False):
    mult = (1 if success else 0.2)
    if not success and has_disguise:
        mult = 0.5
    return round(18 * difficulty * mult + min(streak * 2, 20))

def calc_coins_strategy_pvp(difficulty, win, streak, has_undo=False):
    return round(15 * difficulty * (1 if win else 0.3) + min(streak * 2, 20))

def calc_coins_lottery(bet, jackpot=False, has_lucky_ball=False):
    if jackpot:
        mult = 10
    else:
        mult = random.uniform(0.0, 1.8)
    if has_lucky_ball:
        mult = min(mult * 1.10, 10)
    return round(bet * mult)

# ─── Trivia questions pool ─────────────────────────────────────────────────────
TRIVIA_QUESTIONS = [
    {"q": "What is 7 × 8?", "a": "56", "opts": ["48", "54", "56", "64"]},
    {"q": "What planet is closest to the Sun?", "a": "Mercury", "opts": ["Venus", "Mercury", "Mars", "Earth"]},
    {"q": "How many sides does a hexagon have?", "a": "6", "opts": ["5", "6", "7", "8"]},
    {"q": "What is the capital of France?", "a": "Paris", "opts": ["London", "Rome", "Berlin", "Paris"]},
    {"q": "What gas do plants absorb?", "a": "CO2", "opts": ["O2", "N2", "CO2", "H2"]},
    {"q": "What is 12² (12 squared)?", "a": "144", "opts": ["124", "134", "144", "154"]},
    {"q": "Who wrote Romeo and Juliet?", "a": "Shakespeare", "opts": ["Dickens", "Shakespeare", "Tolkien", "Austen"]},
    {"q": "How many bones are in the human body?", "a": "206", "opts": ["196", "206", "216", "226"]},
    {"q": "What is the chemical symbol for gold?", "a": "Au", "opts": ["Go", "Gd", "Au", "Ag"]},
    {"q": "What year did WW2 end?", "a": "1945", "opts": ["1943", "1944", "1945", "1946"]},
    {"q": "What is the speed of light (approx, km/s)?", "a": "300,000", "opts": ["30,000", "300,000", "3,000,000", "3,000"]},
    {"q": "What is the largest ocean?", "a": "Pacific", "opts": ["Atlantic", "Indian", "Arctic", "Pacific"]},
    {"q": "What is √144?", "a": "12", "opts": ["10", "11", "12", "13"]},
    {"q": "How many continents are there?", "a": "7", "opts": ["5", "6", "7", "8"]},
    {"q": "What is the longest river?", "a": "Nile", "opts": ["Amazon", "Nile", "Yangtze", "Mississippi"]},
    {"q": "What is 15% of 200?", "a": "30", "opts": ["20", "25", "30", "35"]},
    {"q": "What element has atomic number 1?", "a": "Hydrogen", "opts": ["Helium", "Hydrogen", "Carbon", "Oxygen"]},
    {"q": "What is the hardest natural substance?", "a": "Diamond", "opts": ["Gold", "Iron", "Quartz", "Diamond"]},
    {"q": "How many degrees in a triangle?", "a": "180", "opts": ["90", "180", "270", "360"]},
    {"q": "What is 2^10?", "a": "1024", "opts": ["512", "1024", "2048", "256"]},
    {"q": "Which country has the most population?", "a": "China", "opts": ["USA", "India", "China", "Russia"]},
    {"q": "What is the powerhouse of the cell?", "a": "Mitochondria", "opts": ["Nucleus", "Ribosome", "Mitochondria", "Golgi"]},
    {"q": "What is 100 ÷ 4 × 3?", "a": "75", "opts": ["25", "50", "75", "100"]},
    {"q": "What is the tallest mountain?", "a": "Everest", "opts": ["K2", "Everest", "Kangchenjunga", "Makalu"]},
    {"q": "How many players on a football (soccer) team?", "a": "11", "opts": ["9", "10", "11", "12"]},
]

WORD_POOL = [
    "PYTHON", "DRAGON", "CASTLE", "WIZARD", "PIRATE", "JUNGLE", "ROCKET", "KNIGHT",
    "GALAXY", "STORM", "NINJA", "CRYPTO", "DUNGEON", "QUEST", "EMPIRE", "PHANTOM",
    "CIPHER", "BLAZE", "TITAN", "VORTEX", "ECHO", "FROST", "SHADOW", "LEGEND",
    "PORTAL", "COSMIC", "TURBO", "SAVAGE", "PIXEL", "NEON"
]

MATH_PROBLEMS = [
    {"q": "12 + 19 = ?", "a": "31"},
    {"q": "45 - 17 = ?", "a": "28"},
    {"q": "8 × 7 = ?", "a": "56"},
    {"q": "144 ÷ 12 = ?", "a": "12"},
    {"q": "√81 = ?", "a": "9"},
    {"q": "3³ = ?", "a": "27"},
    {"q": "25% of 80 = ?", "a": "20"},
    {"q": "100 - 37 = ?", "a": "63"},
    {"q": "6 × 9 = ?", "a": "54"},
    {"q": "2^8 = ?", "a": "256"},
    {"q": "99 + 88 = ?", "a": "187"},
    {"q": "17 × 5 = ?", "a": "85"},
    {"q": "1000 ÷ 8 = ?", "a": "125"},
    {"q": "√225 = ?", "a": "15"},
    {"q": "50% of 350 = ?", "a": "175"},
    {"q": "13² = ?", "a": "169"},
    {"q": "200 - 87 = ?", "a": "113"},
    {"q": "9 × 12 = ?", "a": "108"},
    {"q": "75 + 48 = ?", "a": "123"},
    {"q": "4⁴ = ?", "a": "256"},
]

# ─── Bot setup ─────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="%", intents=intents, help_command=None)
tree = bot.tree

# ─── Helper: active ability check ─────────────────────────────────────────────
def use_ability_if_active(user_data, ability_name):
    if user_data.get("active_ability") == ability_name:
        user_data["active_ability"] = None
        return True
    return False

# ─── /help slash command ───────────────────────────────────────────────────────
@tree.command(name="help", description="Show all bot commands")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎮 Game Bot — All Commands",
        description="Use `%` prefix for all commands. Use `/help` to see this list.",
        color=0x7289DA
    )
    embed.add_field(name="💰 Economy", value=(
        "`%balance` — Check your coins\n"
        "`%daily` — Claim daily reward (150 coins)\n"
        "`%weekly` — Claim weekly reward (700 coins)\n"
        "`%leaderboard` — Top 10 richest players\n"
        "`%transfer @user <amount>` — Send coins\n"
        "`%profile` — Full stats profile\n"
        "`%shop` — View ability shop\n"
        "`%buy <ability>` — Buy an ability\n"
        "`%inventory` — View your abilities\n"
        "`%use <ability>` — Activate an ability"
    ), inline=False)
    embed.add_field(name="🎰 Games", value=(
        "`%casino [name] <bet>` — Casino game (bet coins)\n"
        "`%trivia [name]` — Answer trivia questions\n"
        "`%pvp @user [name]` — PvP duel\n"
        "`%rpg [name]` — RPG adventure\n"
        "`%speed [name]` — Speed challenge\n"
        "`%puzzle [name]` — Puzzle game\n"
        "`%adventure [name]` — Hunt for items\n"
        "`%strategy [name]` — Strategy game\n"
        "`%memory [name]` — Memory game\n"
        "`%word [name]` — Word guessing game\n"
        "`%creative [name]` — Creative/draw game\n"
        "`%raid [name]` — Co-op boss raid\n"
        "`%heist [name]` — Adventure heist\n"
        "`%survival [name]` — Survival rounds\n"
        "`%royale [name]` — Battle royale\n"
        "`%tournament [name]` — Competitive tournament\n"
        "`%party [name]` — Party vote game\n"
        "`%math [name]` — Math battle\n"
        "`%lottery [name] <bet>` — Lottery (jackpot x10!)"
    ), inline=False)
    embed.add_field(name="📋 Info", value=(
        "`%games [category]` — List all 500 games\n"
        "`%gameinfo <name>` — Game details & formula"
    ), inline=False)
    embed.add_field(name="🔧 Admin Only", value=(
        "`%addmoney @user <amount>`\n"
        "`%removemoney @user <amount>`\n"
        "`%setmoney @user <amount>`\n"
        "`%resetuser @user`\n"
        "`%givemoney @user <amount>`\n"
        "`%announce <message>`"
    ), inline=False)
    embed.set_footer(text="[name] is optional — bot picks a random game if omitted.")
    await interaction.response.send_message(embed=embed)

# ─── Economy commands ──────────────────────────────────────────────────────────
@bot.command(aliases=["bal", "coins", "wallet"])
async def balance(ctx, member: discord.Member = None):
    target = member or ctx.author
    data = load_data()
    user = get_user(data, target.id)
    user["username"] = target.display_name
    save_data(data)
    embed = discord.Embed(title=f"💰 {target.display_name}'s Balance", color=0xF1C40F)
    embed.add_field(name="Coins", value=f"**{user['balance']:,}** 🪙")
    embed.add_field(name="Streak", value=f"{user['streak']} 🔥")
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)
    now = datetime.utcnow()
    last = user.get("last_daily")
    if last:
        last_dt = datetime.fromisoformat(last)
        diff = now - last_dt
        if diff < timedelta(hours=22):
            remaining = timedelta(hours=22) - diff
            h, rem = divmod(int(remaining.total_seconds()), 3600)
            m = rem // 60
            await ctx.send(f"⏳ Daily cooldown: **{h}h {m}m** left.")
            return
    reward = 150
    user["balance"] += reward
    user["total_earned"] += reward
    user["last_daily"] = now.isoformat()
    user["username"] = ctx.author.display_name
    save_data(data)
    await ctx.send(f"✅ {ctx.author.mention} claimed **{reward:,}** 🪙 daily! Balance: **{user['balance']:,}** 🪙")

@bot.command()
async def weekly(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)
    now = datetime.utcnow()
    last = user.get("last_weekly")
    if last:
        last_dt = datetime.fromisoformat(last)
        diff = now - last_dt
        if diff < timedelta(days=6, hours=22):
            remaining = timedelta(days=7) - diff
            d = remaining.days
            h = remaining.seconds // 3600
            await ctx.send(f"⏳ Weekly cooldown: **{d}d {h}h** left.")
            return
    reward = 700
    user["balance"] += reward
    user["total_earned"] += reward
    user["last_weekly"] = now.isoformat()
    user["username"] = ctx.author.display_name
    save_data(data)
    await ctx.send(f"🎉 {ctx.author.mention} claimed **{reward:,}** 🪙 weekly! Balance: **{user['balance']:,}** 🪙")

@bot.command(aliases=["lb", "top"])
async def leaderboard(ctx):
    data = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:10]
    embed = discord.Embed(title="🏆 Leaderboard — Top 10", color=0xF39C12)
    medals = ["🥇", "🥈", "🥉"] + ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, (uid, udata) in enumerate(sorted_users):
        name = udata.get("username", f"User#{uid[:4]}")
        embed.add_field(name=f"{medals[i]} {name}", value=f"{udata['balance']:,} 🪙", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def transfer(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ Amount must be positive.")
        return
    if member.id == ctx.author.id:
        await ctx.send("❌ You can't transfer to yourself.")
        return
    data = load_data()
    sender = get_user(data, ctx.author.id)
    receiver = get_user(data, member.id)
    if sender["balance"] < amount:
        await ctx.send(f"❌ Insufficient funds. You have **{sender['balance']:,}** 🪙")
        return
    sender["balance"] -= amount
    receiver["balance"] += amount
    receiver["username"] = member.display_name
    sender["username"] = ctx.author.display_name
    save_data(data)
    await ctx.send(f"✅ {ctx.author.mention} sent **{amount:,}** 🪙 to {member.mention}!")

@bot.command()
async def profile(ctx, member: discord.Member = None):
    target = member or ctx.author
    data = load_data()
    user = get_user(data, target.id)
    user["username"] = target.display_name
    save_data(data)
    total = user["wins"] + user["losses"]
    winrate = round((user["wins"] / total) * 100, 1) if total > 0 else 0
    embed = discord.Embed(title=f"📊 {target.display_name}'s Profile", color=0x9B59B6)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="💰 Balance", value=f"{user['balance']:,} 🪙")
    embed.add_field(name="🔥 Streak", value=str(user["streak"]))
    embed.add_field(name="🎮 Games Played", value=str(user["games_played"]))
    embed.add_field(name="✅ Wins", value=str(user["wins"]))
    embed.add_field(name="❌ Losses", value=str(user["losses"]))
    embed.add_field(name="📈 Win Rate", value=f"{winrate}%")
    embed.add_field(name="💎 Total Earned", value=f"{user['total_earned']:,} 🪙")
    inv = user.get("inventory", [])
    embed.add_field(name="🎒 Abilities", value=", ".join(inv) if inv else "None", inline=False)
    active = user.get("active_ability", "None")
    embed.add_field(name="⚡ Active Ability", value=active or "None", inline=False)
    await ctx.send(embed=embed)

# ─── Shop & Abilities ──────────────────────────────────────────────────────────
ABILITIES = {
    "Shield": {"cost": 50, "desc": "Cancels one loss penalty in PvP games"},
    "Double Coin Ball": {"cost": 50, "desc": "1.5× winnings in Casino games"},
    "Lucky Ball": {"cost": 40, "desc": "+10% payout modifier in Casino/Lottery"},
    "Hint": {"cost": 50, "desc": "Reveals a clue in Trivia/Puzzle games"},
    "Insight": {"cost": 50, "desc": "Removes one wrong option in Trivia"},
    "Heal": {"cost": 50, "desc": "Restore 20% HP in RPG games"},
    "Speed Boost": {"cost": 50, "desc": "+15% time score in Speed games"},
    "Path Reveal": {"cost": 50, "desc": "Shows next correct step in Puzzle/Maze"},
    "Reveal Letter": {"cost": 50, "desc": "Shows one correct letter in Word games"},
    "Extra Hint": {"cost": 50, "desc": "Reveal a letter in Creative/Draw games"},
    "Revive": {"cost": 75, "desc": "Restore a fallen teammate in Co-op Raids"},
    "Extra Life": {"cost": 75, "desc": "Survive one fatal hit or elimination"},
    "Bye Round": {"cost": 75, "desc": "Skip one elimination round in tournaments"},
    "Undo": {"cost": 50, "desc": "Take back last move in Strategy games"},
    "Map Reveal": {"cost": 50, "desc": "Shows location of one item in Adventure"},
    "Disguise": {"cost": 60, "desc": "1 free escape if caught in Heist games"},
    "Extra Vote": {"cost": 50, "desc": "Cast a second vote in Party games"},
    "Peek": {"cost": 50, "desc": "Briefly reveal two cards in Memory games"},
    "Lucky Charm": {"cost": 40, "desc": "+5% bonus to outcome in General games"},
}

@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="🏪 Ability Shop", description="Use `%buy <ability>` to purchase.", color=0x2ECC71)
    for name, info in ABILITIES.items():
        embed.add_field(name=f"{name} — {info['cost']} 🪙", value=info["desc"], inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, *, ability_name: str):
    ability_name = ability_name.title()
    if ability_name not in ABILITIES:
        await ctx.send(f"❌ Unknown ability. Use `%shop` to see available abilities.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    cost = ABILITIES[ability_name]["cost"]
    if user["balance"] < cost:
        await ctx.send(f"❌ You need **{cost}** 🪙 but have **{user['balance']:,}** 🪙")
        return
    user["balance"] -= cost
    if ability_name not in user.get("inventory", []):
        user.setdefault("inventory", []).append(ability_name)
    save_data(data)
    await ctx.send(f"✅ Bought **{ability_name}** for **{cost}** 🪙! Use `%use {ability_name}` to activate.")

@bot.command(aliases=["inv"])
async def inventory(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)
    inv = user.get("inventory", [])
    active = user.get("active_ability")
    embed = discord.Embed(title=f"🎒 {ctx.author.display_name}'s Inventory", color=0x1ABC9C)
    embed.add_field(name="Abilities", value="\n".join(f"• {a}" for a in inv) if inv else "Empty")
    embed.add_field(name="⚡ Active", value=active or "None")
    await ctx.send(embed=embed)

@bot.command()
async def use(ctx, *, ability_name: str):
    ability_name = ability_name.title()
    data = load_data()
    user = get_user(data, ctx.author.id)
    if ability_name not in user.get("inventory", []):
        await ctx.send(f"❌ You don't have **{ability_name}**. Buy it with `%shop`.")
        return
    user["active_ability"] = ability_name
    save_data(data)
    await ctx.send(f"⚡ **{ability_name}** activated! It will apply to your next game.")

# ─── Game info / listing ───────────────────────────────────────────────────────
@bot.command()
async def games(ctx, *, category: str = None):
    if category:
        cat = category.lower()
        matches = [(gid, g) for gid, g in GAMES.items() if cat in g["category"].lower()]
        if not matches:
            await ctx.send(f"❌ No games found for category `{category}`.")
            return
        embed = discord.Embed(title=f"🎮 Games — {category}", color=0x3498DB)
        chunks = [matches[i:i+20] for i in range(0, len(matches), 20)]
        for chunk in chunks[:2]:
            embed.add_field(
                name="Games",
                value="\n".join(f"#{gid} {g['name']}" for gid, g in chunk),
                inline=False
            )
        embed.set_footer(text=f"{len(matches)} games found.")
    else:
        categories = {}
        for g in GAMES.values():
            c = g["category"]
            categories[c] = categories.get(c, 0) + 1
        embed = discord.Embed(title="🎮 All 500 Games by Category", color=0x3498DB)
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            embed.add_field(name=cat, value=f"{count} games", inline=True)
        embed.set_footer(text="Use %games <category> to list games in a category.")
    await ctx.send(embed=embed)

@bot.command()
async def gameinfo(ctx, *, name: str):
    gid = GAME_NAME_LOOKUP.get(name.lower())
    if not gid:
        await ctx.send(f"❌ Game `{name}` not found. Use `%games` to browse.")
        return
    g = GAMES[gid]
    cat = g["category"]
    formulas = {
        "PvP": "coins = round(15 × difficulty × (1 if win else 0.3) + min(streak×2, 20))",
        "PvP/RPG": "coins = round(15 × difficulty × (1 if win else 0.3) + min(streak×2, 20))",
        "Casino": "winnings = bet × payout_rate (avg ~0.95, house edge 5%)",
        "Trivia": "coins = round(10 × difficulty × (score÷max_score) + min(streak×2, 20))",
        "RPG": "coins = round(20 × difficulty × (objectives÷total) + min(streak×2, 20))",
        "Speed": "coins = round(8 × difficulty × min(1, ideal_time÷actual_time) + min(streak×2, 20))",
        "Puzzle": "coins = round(12 × difficulty × (1÷max(1, mistakes+1)) + min(streak×2, 20))",
        "Adventure": "coins = round(20 × difficulty × (items_found÷total_items) + min(streak×2, 20))",
        "Strategy": "coins = round(15 × difficulty × (territory÷total_territory) + min(streak×2, 20))",
        "Memory": "coins = round(10 × difficulty × (1÷max(1, attempts)) + min(streak×2, 20))",
        "Word/Text": "coins = round(10 × difficulty × (correct_letters÷total_letters) + min(streak×2, 20))",
        "Creative": "coins = round(10 × difficulty × (guesses_correct÷total_players) + min(streak×2, 20))",
        "RPG Co-op": "coins = round(20 × difficulty × (boss_damage÷boss_hp) + min(streak×2, 20))",
        "RPG Survival": "coins = round(20 × difficulty × (rounds_survived÷total_rounds) + min(streak×2, 20))",
        "Battle Royale": "coins = round(20 × difficulty × placement_bonus + min(streak×2, 20))",
        "Competitive": "coins = round(15 × difficulty × placement_bonus + min(streak×2, 20))",
        "Party": "coins = round(10 × difficulty × (votes_for÷total_votes) + min(streak×2, 20))",
        "General": "coins = round(10 × difficulty × performance_ratio + min(streak×2, 20))",
        "Adventure PvP": "coins = round(18 × difficulty × (1 if success else 0.2) + min(streak×2, 20))",
        "Strategy PvP": "coins = round(15 × difficulty × (1 if win else 0.3) + min(streak×2, 20))",
    }
    formula = formulas.get(cat, "coins = round(10 × difficulty × performance_ratio + min(streak×2, 20))")
    embed = discord.Embed(title=f"🎮 #{gid} — {g['name']}", color=0xE74C3C)
    embed.add_field(name="Category", value=cat)
    embed.add_field(name="Unique Ability", value=f"{g['ability']} ({g['ability_cost']} 🪙)")
    embed.add_field(name="Coin Formula", value=f"`{formula}`", inline=False)
    await ctx.send(embed=embed)

# ─── Game picker helper ────────────────────────────────────────────────────────
def pick_game(category_keywords, name_arg=None):
    if name_arg:
        gid = GAME_NAME_LOOKUP.get(name_arg.lower())
        if gid:
            return gid, GAMES[gid]
    matches = [
        (gid, g) for gid, g in GAMES.items()
        if any(kw.lower() in g["category"].lower() for kw in category_keywords)
    ]
    if not matches:
        return None, None
    gid, g = random.choice(matches)
    return gid, g

# ─── CASINO game ───────────────────────────────────────────────────────────────
@bot.command()
async def casino(ctx, *args):
    name_arg = None
    bet = None
    for arg in args:
        try:
            bet = int(arg)
        except ValueError:
            name_arg = (name_arg + " " + arg).strip() if name_arg else arg
    if bet is None:
        await ctx.send("❌ Usage: `%casino [game name] <bet>`  Example: `%casino 100`")
        return
    if bet <= 0:
        await ctx.send("❌ Bet must be positive.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    if user["balance"] < bet:
        await ctx.send(f"❌ Not enough coins! You have **{user['balance']:,}** 🪙")
        return
    gid, game = pick_game(["Casino"], name_arg)
    if not game:
        await ctx.send("❌ No casino game found.")
        return
    has_double = use_ability_if_active(user, "Double Coin Ball")
    has_lucky = use_ability_if_active(user, "Lucky Ball")
    payout_rate = random.uniform(0.0, 1.9)
    win = payout_rate >= 1.0
    winnings = calc_coins_casino(bet, payout_rate, has_double_coin=has_double, has_lucky_ball=has_lucky)
    user["balance"] -= bet
    user["games_played"] += 1
    if win:
        profit = winnings - bet
        user["balance"] += winnings
        user["total_earned"] += profit
        user["wins"] += 1
        user["streak"] += 1
        color = 0x2ECC71
        result_text = f"🎰 **You won!** Payout: `{payout_rate:.2f}x`\n+**{winnings:,}** 🪙 (profit: +{profit:,})"
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result_text = f"💀 **You lost!** Payout: `{payout_rate:.2f}x`\n-**{bet:,}** 🪙"
    save_data(data)
    embed = discord.Embed(title=f"🎰 {game['name']}", color=color)
    embed.add_field(name="Bet", value=f"{bet:,} 🪙")
    embed.add_field(name="Result", value=result_text, inline=False)
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_double:
        embed.set_footer(text="⚡ Double Coin Ball was used!")
    if has_lucky:
        embed.set_footer(text="⚡ Lucky Ball was used!")
    await ctx.send(embed=embed)

# ─── LOTTERY game ──────────────────────────────────────────────────────────────
@bot.command()
async def lottery(ctx, *args):
    name_arg = None
    bet = None
    for arg in args:
        try:
            bet = int(arg)
        except ValueError:
            name_arg = (name_arg + " " + arg).strip() if name_arg else arg
    if bet is None:
        await ctx.send("❌ Usage: `%lottery [game name] <bet>`")
        return
    if bet <= 0:
        await ctx.send("❌ Bet must be positive.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    if user["balance"] < bet:
        await ctx.send(f"❌ Not enough coins! You have **{user['balance']:,}** 🪙")
        return
    lottery_games = {gid: g for gid, g in GAMES.items() if "Lottery" in g["name"] or "Blazing Lottery" in g["name"] or g["name"] in ["Sneaky Lottery Match", "Lottery Game", "Lottery Match"]}
    if name_arg:
        gid = GAME_NAME_LOOKUP.get(name_arg.lower())
        game = GAMES.get(gid) if gid else None
    else:
        gid, game = random.choice(list(lottery_games.items())) if lottery_games else (12, GAMES[12])
    game = game or GAMES[12]
    has_lucky = use_ability_if_active(user, "Lucky Ball")
    jackpot = random.random() < (0.03 if not has_lucky else 0.033)
    winnings = calc_coins_lottery(bet, jackpot=jackpot, has_lucky_ball=has_lucky)
    user["balance"] -= bet
    user["games_played"] += 1
    if winnings >= bet:
        user["balance"] += winnings
        user["total_earned"] += (winnings - bet)
        user["wins"] += 1
        user["streak"] += 1
        color = 0xF39C12 if jackpot else 0x2ECC71
        if jackpot:
            result_text = f"🎊 **JACKPOT!!!** 10× multiplier!\n+**{winnings:,}** 🪙"
        else:
            result_text = f"🎟️ **Won!** +**{winnings:,}** 🪙"
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result_text = f"💸 **No luck.** Lost **{bet:,}** 🪙"
    save_data(data)
    embed = discord.Embed(title=f"🎟️ {game['name']}", color=color)
    embed.add_field(name="Bet", value=f"{bet:,} 🪙")
    embed.add_field(name="Result", value=result_text, inline=False)
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    embed.set_footer(text="Jackpot chance: 3% (x10 multiplier!)")
    await ctx.send(embed=embed)

# ─── TRIVIA game ───────────────────────────────────────────────────────────────
@bot.command()
async def trivia(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Trivia"], name_arg)
    if not game:
        await ctx.send("❌ No trivia game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_insight = use_ability_if_active(user, "Insight")
    has_hint = use_ability_if_active(user, "Hint")
    q = random.choice(TRIVIA_QUESTIONS)
    opts = q["opts"].copy()
    random.shuffle(opts)
    if has_insight:
        wrong_opts = [o for o in opts if o != q["a"]]
        opts.remove(random.choice(wrong_opts))
    letters = ["A", "B", "C", "D"]
    options_text = "\n".join(f"**{letters[i]}**. {opt}" for i, opt in enumerate(opts[:4]))
    hint_text = f"\n\n💡 *Hint: Answer starts with `{q['a'][0]}`*" if has_hint else ""
    embed = discord.Embed(title=f"🧠 {game['name']}", description=f"**{q['q']}**\n\n{options_text}{hint_text}", color=0x3498DB)
    embed.set_footer(text="Type A, B, C, or D within 15 seconds!")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.upper() in ["A", "B", "C", "D"]

    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The answer was **{q['a']}**. No coins earned.")
        data = load_data()
        user = get_user(data, ctx.author.id)
        user["games_played"] += 1
        user["losses"] += 1
        user["streak"] = 0
        save_data(data)
        return

    chosen_idx = ["A", "B", "C", "D"].index(msg.content.upper())
    chosen = opts[chosen_idx] if chosen_idx < len(opts) else ""
    correct = chosen == q["a"]
    data = load_data()
    user = get_user(data, ctx.author.id)
    user["games_played"] += 1
    difficulty = round(random.uniform(1.0, 3.0), 1)
    if correct:
        score = random.randint(4, 5)
        max_score = 5
        coins = calc_coins_trivia(difficulty, score, max_score, user["streak"])
        user["balance"] += coins
        user["total_earned"] += coins
        user["wins"] += 1
        user["streak"] += 1
        color = 0x2ECC71
        result = f"✅ Correct! You earned **{coins}** 🪙\n🔥 Streak: {user['streak']}"
    else:
        coins = calc_coins_trivia(difficulty, 1, 5, 0)
        user["balance"] += coins
        user["total_earned"] += coins
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result = f"❌ Wrong! Answer: **{q['a']}**\nConsolation: +**{coins}** 🪙"
    save_data(data)
    embed = discord.Embed(title="Trivia Result", description=result, color=color)
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    await ctx.send(embed=embed)

# ─── MATH game ─────────────────────────────────────────────────────────────────
@bot.command()
async def math(ctx, *, name_arg: str = None):
    data = load_data()
    user = get_user(data, ctx.author.id)
    prob = random.choice(MATH_PROBLEMS)
    difficulty = round(random.uniform(1.0, 3.0), 1)
    embed = discord.Embed(title=f"🔢 Math Battle", description=f"**Solve this:**\n\n`{prob['q']}`", color=0xE67E22)
    embed.set_footer(text="Type your answer within 20 seconds!")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", timeout=20.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! Answer was **{prob['a']}**.")
        data = load_data()
        user = get_user(data, ctx.author.id)
        user["games_played"] += 1
        user["losses"] += 1
        user["streak"] = 0
        save_data(data)
        return

    data = load_data()
    user = get_user(data, ctx.author.id)
    user["games_played"] += 1
    if msg.content.strip() == prob["a"]:
        coins = calc_coins_pvp(difficulty, True, user["streak"])
        user["balance"] += coins
        user["total_earned"] += coins
        user["wins"] += 1
        user["streak"] += 1
        color = 0x2ECC71
        result = f"✅ Correct! +**{coins}** 🪙 | Streak: {user['streak']}"
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result = f"❌ Wrong! Answer was **{prob['a']}**. Streak reset."
    save_data(data)
    await ctx.send(embed=discord.Embed(title="Math Result", description=result, color=color))

# ─── PVP game ──────────────────────────────────────────────────────────────────
@bot.command()
async def pvp(ctx, opponent: discord.Member = None, *, name_arg: str = None):
    if not opponent:
        await ctx.send("❌ Usage: `%pvp @user [game name]`")
        return
    if opponent.bot or opponent.id == ctx.author.id:
        await ctx.send("❌ Invalid opponent.")
        return
    gid, game = pick_game(["PvP"], name_arg)
    if not game:
        await ctx.send("❌ No PvP game found.")
        return
    embed = discord.Embed(
        title=f"⚔️ {game['name']} Challenge!",
        description=f"{ctx.author.mention} challenges {opponent.mention} to **{game['name']}**!\n\n{opponent.mention}, type `accept` or `decline` within 30s.",
        color=0xE74C3C
    )
    await ctx.send(embed=embed)

    def check(m):
        return m.author == opponent and m.channel == ctx.channel and m.content.lower() in ["accept", "decline"]

    try:
        msg = await bot.wait_for("message", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ {opponent.mention} didn't respond. Challenge cancelled.")
        return

    if msg.content.lower() == "decline":
        await ctx.send(f"🚫 {opponent.mention} declined the challenge.")
        return

    await ctx.send(f"⚔️ **{game['name']}** is starting! Both players, answer this challenge question to determine the winner.")
    prob = random.choice(MATH_PROBLEMS)
    embed = discord.Embed(
        title="⚔️ PvP Battle Question",
        description=f"**First to answer correctly wins!**\n\n`{prob['q']}`",
        color=0xFF6B35
    )
    await ctx.send(embed=embed)

    players = {ctx.author.id: ctx.author, opponent.id: opponent}
    winner_id = None

    def pvp_check(m):
        return m.author.id in players and m.channel == ctx.channel

    try:
        while True:
            msg = await bot.wait_for("message", timeout=20.0, check=pvp_check)
            if msg.content.strip() == prob["a"]:
                winner_id = msg.author.id
                break
    except asyncio.TimeoutError:
        pass

    data = load_data()
    challenger = get_user(data, ctx.author.id)
    opp_user = get_user(data, opponent.id)
    difficulty = round(random.uniform(1.0, 3.0), 1)
    challenger["games_played"] += 1
    opp_user["games_played"] += 1
    challenger["username"] = ctx.author.display_name
    opp_user["username"] = opponent.display_name

    if winner_id is None:
        await ctx.send("⏰ No one answered in time. No coins awarded.")
        save_data(data)
        return

    if winner_id == ctx.author.id:
        w_user, l_user = challenger, opp_user
        w_member, l_member = ctx.author, opponent
    else:
        w_user, l_user = opp_user, challenger
        w_member, l_member = opponent, ctx.author

    has_shield = use_ability_if_active(l_user, "Shield")
    w_coins = calc_coins_pvp(difficulty, True, w_user["streak"])
    l_coins = calc_coins_pvp(difficulty, False, l_user["streak"], has_shield=has_shield)

    w_user["balance"] += w_coins
    w_user["total_earned"] += w_coins
    w_user["wins"] += 1
    w_user["streak"] += 1
    l_user["balance"] += l_coins
    l_user["total_earned"] += l_coins
    l_user["losses"] += 1
    l_user["streak"] = 0
    save_data(data)

    embed = discord.Embed(title=f"⚔️ {game['name']} Result", color=0x2ECC71)
    embed.add_field(name=f"🏆 Winner: {w_member.display_name}", value=f"+**{w_coins}** 🪙")
    embed.add_field(name=f"💀 Loser: {l_member.display_name}", value=f"+**{l_coins}** 🪙 (consolation)" + (" [Shield used!]" if has_shield else ""))
    await ctx.send(embed=embed)

# ─── RPG game ──────────────────────────────────────────────────────────────────
@bot.command()
async def rpg(ctx, *, name_arg: str = None):
    gid, game = pick_game(["RPG"], name_arg)
    if not game:
        await ctx.send("❌ No RPG game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_heal = use_ability_if_active(user, "Heal")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    total_objectives = random.randint(3, 6)
    objectives_done = random.randint(1, total_objectives)
    if has_heal:
        objectives_done = min(objectives_done + 1, total_objectives)
    coins = calc_coins_rpg(difficulty, objectives_done, total_objectives, user["streak"])
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    success = objectives_done >= total_objectives // 2
    if success:
        user["wins"] += 1
        user["streak"] += 1
    else:
        user["losses"] += 1
        user["streak"] = 0
    save_data(data)
    color = 0x8E44AD if success else 0xE74C3C
    embed = discord.Embed(title=f"⚔️ {game['name']}", color=color)
    embed.add_field(name="Objectives", value=f"{objectives_done}/{total_objectives} completed")
    embed.add_field(name="Coins Earned", value=f"+**{coins}** 🪙")
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_heal:
        embed.set_footer(text="⚡ Heal was used! +1 objective")
    await ctx.send(embed=embed)

# ─── SPEED game ────────────────────────────────────────────────────────────────
@bot.command()
async def speed(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Speed"], name_arg)
    if not game:
        await ctx.send("❌ No Speed game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_boost = use_ability_if_active(user, "Speed Boost")
    prob = random.choice(MATH_PROBLEMS)
    embed = discord.Embed(
        title=f"⚡ {game['name']} — Speed Challenge!",
        description=f"**Type the answer as fast as possible!**\n\n`{prob['q']}`",
        color=0xF39C12
    )
    await ctx.send(embed=embed)
    start = datetime.utcnow()

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("⏰ Too slow! No coins.")
        data = load_data()
        u = get_user(data, ctx.author.id)
        u["games_played"] += 1
        u["losses"] += 1
        u["streak"] = 0
        save_data(data)
        return

    actual_time = (datetime.utcnow() - start).total_seconds()
    correct = msg.content.strip() == prob["a"]
    data = load_data()
    user = get_user(data, ctx.author.id)
    difficulty = round(random.uniform(1.0, 3.0), 1)
    ideal_time = 3.0
    user["games_played"] += 1
    if correct:
        coins = calc_coins_speed(difficulty, ideal_time, actual_time, user["streak"], has_boost=has_boost)
        user["balance"] += coins
        user["total_earned"] += coins
        user["wins"] += 1
        user["streak"] += 1
        color = 0x2ECC71
        result = f"✅ Correct in **{actual_time:.2f}s**! +**{coins}** 🪙"
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result = f"❌ Wrong answer. Answer was **{prob['a']}**."
    save_data(data)
    embed = discord.Embed(title="Speed Result", description=result, color=color)
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_boost:
        embed.set_footer(text="⚡ Speed Boost applied!")
    await ctx.send(embed=embed)

# ─── PUZZLE game ───────────────────────────────────────────────────────────────
@bot.command()
async def puzzle(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Puzzle"], name_arg)
    if not game:
        await ctx.send("❌ No Puzzle game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_hint = use_ability_if_active(user, "Hint")
    has_path = use_ability_if_active(user, "Path Reveal")
    word = random.choice(WORD_POOL)
    scrambled = "".join(random.sample(word, len(word)))
    hint_text = f"\n💡 *Hint: Starts with `{word[0]}`*" if has_hint or has_path else ""
    embed = discord.Embed(
        title=f"🧩 {game['name']}",
        description=f"**Unscramble this word:**\n\n`{scrambled}`{hint_text}\n\nType your answer within 20 seconds!",
        color=0x9B59B6
    )
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    mistakes = 0
    solved = False
    for attempt in range(3):
        try:
            msg = await bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            break
        if msg.content.upper() == word:
            solved = True
            break
        else:
            mistakes += 1
            if attempt < 2:
                await ctx.send(f"❌ Not quite! {2 - attempt} attempt(s) left.")

    data = load_data()
    user = get_user(data, ctx.author.id)
    difficulty = round(random.uniform(1.0, 3.0), 1)
    user["games_played"] += 1
    coins = calc_coins_puzzle(difficulty, mistakes, user["streak"], has_hint=(has_hint or has_path))
    user["balance"] += coins
    user["total_earned"] += coins
    if solved:
        user["wins"] += 1
        user["streak"] += 1
        color = 0x2ECC71
        result = f"✅ Correct! The word was **{word}**. +**{coins}** 🪙"
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result = f"❌ The word was **{word}**. Consolation: +**{coins}** 🪙"
    save_data(data)
    embed = discord.Embed(title="Puzzle Result", description=result, color=color)
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    await ctx.send(embed=embed)

# ─── WORD game ─────────────────────────────────────────────────────────────────
@bot.command()
async def word(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Word", "Text"], name_arg)
    if not game:
        await ctx.send("❌ No Word game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_reveal = use_ability_if_active(user, "Reveal Letter")
    target = random.choice(WORD_POOL)
    guessed = set()
    max_wrong = 6
    wrong = 0
    revealed_start = {target[0]} if has_reveal else set()
    guessed |= revealed_start

    async def draw_board():
        display = " ".join(c if c in guessed else "_" for c in target)
        reveal_hint = f"\n💡 *`{target[0]}` revealed by Reveal Letter!*" if has_reveal else ""
        return f"**{game['name']} — Hangman-style**{reveal_hint}\n\n`{display}`\n\nWrong guesses: {wrong}/{max_wrong} | Guessed: `{', '.join(sorted(guessed)) or 'none'}`"

    embed = discord.Embed(title=f"📝 {game['name']}", description=await draw_board(), color=0x1ABC9C)
    embed.set_footer(text="Guess one letter at a time. You have 6 wrong guesses!")
    msg_ref = await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and len(m.content) == 1 and m.content.isalpha()

    while wrong < max_wrong:
        try:
            guess_msg = await bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            break
        letter = guess_msg.content.upper()
        if letter in guessed:
            await ctx.send(f"You already guessed `{letter}`!", delete_after=3)
            continue
        guessed.add(letter)
        if letter not in target:
            wrong += 1
        board = await draw_board()
        color = 0x2ECC71 if all(c in guessed for c in target) else (0xE74C3C if wrong >= max_wrong else 0x1ABC9C)
        await msg_ref.edit(embed=discord.Embed(title=f"📝 {game['name']}", description=board, color=color))
        if all(c in guessed for c in target):
            break

    data = load_data()
    user = get_user(data, ctx.author.id)
    difficulty = round(random.uniform(1.0, 3.0), 1)
    correct_letters = sum(1 for c in set(target) if c in guessed)
    total_letters = len(set(target))
    user["games_played"] += 1
    coins = calc_coins_word(difficulty, correct_letters, total_letters, user["streak"], has_reveal=has_reveal)
    user["balance"] += coins
    user["total_earned"] += coins
    solved = all(c in guessed for c in target)
    if solved:
        user["wins"] += 1
        user["streak"] += 1
        result = f"✅ You guessed **{target}**! +**{coins}** 🪙"
        color = 0x2ECC71
    else:
        user["losses"] += 1
        user["streak"] = 0
        result = f"❌ The word was **{target}**. Consolation: +**{coins}** 🪙"
        color = 0xE74C3C
    save_data(data)
    await ctx.send(embed=discord.Embed(title="Word Game Result", description=result, color=color))

# ─── ADVENTURE game ────────────────────────────────────────────────────────────
@bot.command()
async def adventure(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Adventure"], name_arg)
    if not game:
        await ctx.send("❌ No Adventure game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_map = use_ability_if_active(user, "Map Reveal")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    total_items = random.randint(5, 10)
    items_found = random.randint(1, total_items)
    map_hint = f"\n🗺️ *Map Reveal: One extra item found!*" if has_map else ""
    coins = calc_coins_adventure(difficulty, items_found, total_items, user["streak"], has_map=has_map)
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    success = items_found >= total_items // 2
    if success:
        user["wins"] += 1
        user["streak"] += 1
    else:
        user["losses"] += 1
        user["streak"] = 0
    save_data(data)
    color = 0xE67E22 if success else 0xE74C3C
    embed = discord.Embed(title=f"🏕️ {game['name']}", color=color)
    embed.add_field(name="Items Found", value=f"{items_found}/{total_items}{map_hint}")
    embed.add_field(name="Coins", value=f"+**{coins}** 🪙")
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    await ctx.send(embed=embed)

# ─── STRATEGY game ─────────────────────────────────────────────────────────────
@bot.command()
async def strategy(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Strategy"], name_arg)
    if not game:
        await ctx.send("❌ No Strategy game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_undo = use_ability_if_active(user, "Undo")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    total_territory = 10
    territory_held = random.randint(1, total_territory)
    coins = calc_coins_strategy(difficulty, territory_held, total_territory, user["streak"])
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    if territory_held >= 5:
        user["wins"] += 1
        user["streak"] += 1
    else:
        user["losses"] += 1
        user["streak"] = 0
    save_data(data)
    embed = discord.Embed(title=f"♟️ {game['name']}", color=0x8E44AD)
    embed.add_field(name="Territory", value=f"{territory_held}/{total_territory} zones")
    embed.add_field(name="Coins", value=f"+**{coins}** 🪙")
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_undo:
        embed.set_footer(text="⚡ Undo was ready!")
    await ctx.send(embed=embed)

# ─── MEMORY game ───────────────────────────────────────────────────────────────
@bot.command()
async def memory(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Memory"], name_arg)
    if not game:
        await ctx.send("❌ No Memory game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_peek = use_ability_if_active(user, "Peek")
    sequence_length = random.randint(4, 7)
    emojis = ["🔴", "🔵", "🟢", "🟡", "🟣", "🟠"]
    sequence = [random.choice(emojis) for _ in range(sequence_length)]
    hint = " ".join(sequence[:2]) + " ..." if has_peek else ""
    display = " ".join(sequence)
    embed = discord.Embed(
        title=f"🧠 {game['name']} — Memorize!",
        description=f"**Remember this sequence:**\n\n{display}\n\n{'💡 *Peek: First 2 shown as hint!* ' + hint if has_peek else ''}",
        color=0x1ABC9C
    )
    embed.set_footer(text="You have 8 seconds to memorize!")
    await ctx.send(embed=embed)
    await asyncio.sleep(8)
    await ctx.send(f"🫣 Sequence hidden! {ctx.author.mention}, type the sequence separated by spaces.\nExample: `🔴 🔵 🟢`")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    attempts = 1
    solved = False
    try:
        for attempt in range(1, 4):
            attempts = attempt
            msg = await bot.wait_for("message", timeout=30.0, check=check)
            ans = msg.content.strip().split()
            if ans == sequence:
                solved = True
                break
            else:
                if attempt < 3:
                    await ctx.send(f"❌ Wrong! {3 - attempt} attempt(s) left.")
    except asyncio.TimeoutError:
        pass

    data = load_data()
    user = get_user(data, ctx.author.id)
    difficulty = round(random.uniform(1.0, 3.0), 1)
    user["games_played"] += 1
    coins = calc_coins_memory(difficulty, attempts, user["streak"], has_peek=has_peek)
    user["balance"] += coins
    user["total_earned"] += coins
    if solved:
        user["wins"] += 1
        user["streak"] += 1
        color = 0x2ECC71
        result = f"✅ Correct! +**{coins}** 🪙 | Streak: {user['streak']}"
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result = f"❌ Wrong. Sequence: {' '.join(sequence)}\nConsolation: +**{coins}** 🪙"
    save_data(data)
    await ctx.send(embed=discord.Embed(title="Memory Result", description=result, color=color))

# ─── CREATIVE game ─────────────────────────────────────────────────────────────
@bot.command()
async def creative(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Creative"], name_arg)
    if not game:
        await ctx.send("❌ No Creative game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_hint = use_ability_if_active(user, "Extra Hint")
    word = random.choice(WORD_POOL)
    clue = f"Category: **{random.choice(['Animal', 'Object', 'Place', 'Action', 'Thing'])}**"
    hint_text = f"\n💡 Starts with `{word[0]}`" if has_hint else ""
    embed = discord.Embed(
        title=f"🎨 {game['name']} — Guess the Word!",
        description=f"The artist drew something!\n{clue}{hint_text}\n\n**Guess the word** (20 seconds)!",
        color=0xE91E8C
    )
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", timeout=20.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The word was **{word}**.")
        data = load_data()
        user = get_user(data, ctx.author.id)
        user["games_played"] += 1
        user["losses"] += 1
        user["streak"] = 0
        save_data(data)
        return

    data = load_data()
    user = get_user(data, ctx.author.id)
    difficulty = round(random.uniform(1.0, 3.0), 1)
    user["games_played"] += 1
    correct = msg.content.upper() == word
    total_players = 5
    guesses_correct = random.randint(1, total_players) if correct else 0
    coins = calc_coins_creative(difficulty, guesses_correct if correct else 1, total_players, user["streak"])
    user["balance"] += coins
    user["total_earned"] += coins
    if correct:
        user["wins"] += 1
        user["streak"] += 1
        color = 0x2ECC71
        result = f"✅ Correct! The word was **{word}**! +**{coins}** 🪙"
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result = f"❌ Wrong! The word was **{word}**. Consolation: +**{coins}** 🪙"
    save_data(data)
    await ctx.send(embed=discord.Embed(title="Creative Result", description=result, color=color))

# ─── RAID game ─────────────────────────────────────────────────────────────────
@bot.command()
async def raid(ctx, *, name_arg: str = None):
    gid, game = pick_game(["RPG Co-op"], name_arg)
    if not game:
        await ctx.send("❌ No Raid game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_revive = use_ability_if_active(user, "Revive")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    boss_total_hp = 1000
    boss_damage = random.randint(100, boss_total_hp)
    if has_revive:
        boss_damage = min(boss_damage + 150, boss_total_hp)
    coins = calc_coins_coop(difficulty, boss_damage, boss_total_hp, user["streak"], has_revive=has_revive)
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    if boss_damage >= boss_total_hp // 2:
        user["wins"] += 1
        user["streak"] += 1
    else:
        user["losses"] += 1
        user["streak"] = 0
    save_data(data)
    pct = round((boss_damage / boss_total_hp) * 100)
    embed = discord.Embed(title=f"⚔️ {game['name']} — Boss Raid", color=0x8B0000)
    embed.add_field(name="Boss Damage", value=f"{boss_damage:,}/{boss_total_hp:,} HP ({pct}%)")
    embed.add_field(name="Coins", value=f"+**{coins}** 🪙")
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_revive:
        embed.set_footer(text="⚡ Revive used! +150 bonus damage")
    await ctx.send(embed=embed)

# ─── HEIST game ────────────────────────────────────────────────────────────────
@bot.command()
async def heist(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Adventure PvP"], name_arg)
    if not game:
        await ctx.send("❌ No Heist game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_disguise = use_ability_if_active(user, "Disguise")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    success_chance = 0.55 + (0.1 if has_disguise else 0)
    success = random.random() < success_chance
    coins = calc_coins_adventure_pvp(difficulty, success, user["streak"], has_disguise=has_disguise)
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    if success:
        user["wins"] += 1
        user["streak"] += 1
        color = 0x2ECC71
        result = f"✅ Heist successful! +**{coins}** 🪙"
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
        result = f"🚨 Caught! Consolation: +**{coins}** 🪙" + (" (Disguise reduced penalty!)" if has_disguise else "")
    save_data(data)
    embed = discord.Embed(title=f"🥷 {game['name']}", color=color)
    embed.add_field(name="Outcome", value=result, inline=False)
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    await ctx.send(embed=embed)

# ─── SURVIVAL game ─────────────────────────────────────────────────────────────
@bot.command()
async def survival(ctx, *, name_arg: str = None):
    gid, game = pick_game(["RPG Survival"], name_arg)
    if not game:
        await ctx.send("❌ No Survival game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_life = use_ability_if_active(user, "Extra Life")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    total_rounds = random.randint(5, 10)
    rounds_survived = random.randint(1, total_rounds)
    coins = calc_coins_survival(difficulty, rounds_survived, total_rounds, user["streak"], has_extra_life=has_life)
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    if rounds_survived >= total_rounds // 2:
        user["wins"] += 1
        user["streak"] += 1
    else:
        user["losses"] += 1
        user["streak"] = 0
    save_data(data)
    embed = discord.Embed(title=f"💀 {game['name']} — Survival", color=0xE74C3C)
    embed.add_field(name="Rounds Survived", value=f"{rounds_survived}/{total_rounds}")
    embed.add_field(name="Coins", value=f"+**{coins}** 🪙")
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_life:
        embed.set_footer(text="⚡ Extra Life used!")
    await ctx.send(embed=embed)

# ─── BATTLE ROYALE game ────────────────────────────────────────────────────────
@bot.command()
async def royale(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Battle Royale"], name_arg)
    if not game:
        await ctx.send("❌ No Battle Royale game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_life = use_ability_if_active(user, "Extra Life")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    total_players = random.randint(10, 50)
    placement = random.randint(1, total_players)
    coins = calc_coins_battle_royale(difficulty, placement, total_players, user["streak"], has_extra_life=has_life)
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    if placement <= max(1, total_players // 4):
        user["wins"] += 1
        user["streak"] += 1
        color = 0xF1C40F
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
    save_data(data)
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    place_str = medals.get(placement, f"#{placement}")
    embed = discord.Embed(title=f"🎯 {game['name']} — Battle Royale", color=color)
    embed.add_field(name="Placement", value=f"{place_str} out of {total_players}")
    embed.add_field(name="Coins", value=f"+**{coins}** 🪙")
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_life:
        embed.set_footer(text="⚡ Extra Life used!")
    await ctx.send(embed=embed)

# ─── TOURNAMENT game ───────────────────────────────────────────────────────────
@bot.command()
async def tournament(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Competitive"], name_arg)
    if not game:
        await ctx.send("❌ No Tournament game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_bye = use_ability_if_active(user, "Bye Round")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    total_players = random.randint(8, 32)
    placement = random.randint(1, total_players)
    if has_bye and placement > 1:
        placement = max(1, placement - random.randint(1, 3))
    coins = calc_coins_competitive(difficulty, placement, total_players, user["streak"])
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    if placement <= max(1, total_players // 4):
        user["wins"] += 1
        user["streak"] += 1
        color = 0xF39C12
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
    save_data(data)
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    place_str = medals.get(placement, f"#{placement}")
    embed = discord.Embed(title=f"🏆 {game['name']} — Tournament", color=color)
    embed.add_field(name="Placement", value=f"{place_str} out of {total_players}")
    embed.add_field(name="Coins", value=f"+**{coins}** 🪙")
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_bye:
        embed.set_footer(text="⚡ Bye Round used! Placement improved.")
    await ctx.send(embed=embed)

# ─── PARTY game ────────────────────────────────────────────────────────────────
@bot.command()
async def party(ctx, *, name_arg: str = None):
    gid, game = pick_game(["Party"], name_arg)
    if not game:
        await ctx.send("❌ No Party game found.")
        return
    data = load_data()
    user = get_user(data, ctx.author.id)
    has_vote = use_ability_if_active(user, "Extra Vote")
    difficulty = round(random.uniform(1.0, 3.0), 1)
    total_votes = random.randint(10, 30)
    votes_for = random.randint(0, total_votes)
    coins = calc_coins_party(difficulty, votes_for, total_votes, user["streak"], has_extra_vote=has_vote)
    user["balance"] += coins
    user["total_earned"] += coins
    user["games_played"] += 1
    if votes_for >= total_votes // 2:
        user["wins"] += 1
        user["streak"] += 1
        color = 0xFF69B4
    else:
        user["losses"] += 1
        user["streak"] = 0
        color = 0xE74C3C
    save_data(data)
    embed = discord.Embed(title=f"🎉 {game['name']} — Party Vote", color=color)
    embed.add_field(name="Votes", value=f"{votes_for}/{total_votes}")
    embed.add_field(name="Coins", value=f"+**{coins}** 🪙")
    embed.add_field(name="Balance", value=f"{user['balance']:,} 🪙")
    if has_vote:
        embed.set_footer(text="⚡ Extra Vote used!")
    await ctx.send(embed=embed)

# ─── Admin commands ────────────────────────────────────────────────────────────
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

@bot.command()
@is_admin()
async def addmoney(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ Amount must be positive.")
        return
    data = load_data()
    user = get_user(data, member.id)
    user["balance"] += amount
    user["username"] = member.display_name
    save_data(data)
    await ctx.send(f"✅ Added **{amount:,}** 🪙 to {member.mention}. New balance: **{user['balance']:,}** 🪙")

@bot.command()
@is_admin()
async def givemoney(ctx, member: discord.Member, amount: int):
    await ctx.invoke(bot.get_command("addmoney"), member, amount)

@bot.command()
@is_admin()
async def removemoney(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ Amount must be positive.")
        return
    data = load_data()
    user = get_user(data, member.id)
    user["balance"] = max(0, user["balance"] - amount)
    user["username"] = member.display_name
    save_data(data)
    await ctx.send(f"✅ Removed **{amount:,}** 🪙 from {member.mention}. New balance: **{user['balance']:,}** 🪙")

@bot.command()
@is_admin()
async def setmoney(ctx, member: discord.Member, amount: int):
    if amount < 0:
        await ctx.send("❌ Amount cannot be negative.")
        return
    data = load_data()
    user = get_user(data, member.id)
    user["balance"] = amount
    user["username"] = member.display_name
    save_data(data)
    await ctx.send(f"✅ Set {member.mention}'s balance to **{amount:,}** 🪙")

@bot.command()
@is_admin()
async def resetuser(ctx, member: discord.Member):
    data = load_data()
    uid = str(member.id)
    if uid in data:
        del data[uid]
        save_data(data)
    await ctx.send(f"✅ Reset all data for {member.mention}.")

@bot.command()
@is_admin()
async def announce(ctx, *, message: str):
    embed = discord.Embed(title="📢 Announcement", description=message, color=0xFF0000)
    embed.set_footer(text=f"From {ctx.author.display_name}")
    await ctx.send(embed=embed)

# ─── STATS command ─────────────────────────────────────────────────────────────
@bot.command()
async def stats(ctx):
    data = load_data()
    if not data:
        await ctx.send("📊 No stats yet — no one has played!")
        return

    total_players = len(data)
    total_coins = sum(u.get("balance", 0) for u in data.values())
    total_earned = sum(u.get("total_earned", 0) for u in data.values())
    total_games = sum(u.get("games_played", 0) for u in data.values())
    total_wins = sum(u.get("wins", 0) for u in data.values())
    total_losses = sum(u.get("losses", 0) for u in data.values())
    overall_winrate = round((total_wins / max(1, total_wins + total_losses)) * 100, 1)

    richest = max(data.items(), key=lambda x: x[1].get("balance", 0))
    richest_name = richest[1].get("username", f"User#{richest[0][:4]}")
    richest_coins = richest[1].get("balance", 0)

    top_streak = max(data.items(), key=lambda x: x[1].get("streak", 0))
    streak_name = top_streak[1].get("username", f"User#{top_streak[0][:4]}")
    top_streak_val = top_streak[1].get("streak", 0)

    most_played = max(data.items(), key=lambda x: x[1].get("games_played", 0))
    mp_name = most_played[1].get("username", f"User#{most_played[0][:4]}")
    mp_count = most_played[1].get("games_played", 0)

    avg_balance = round(total_coins / max(1, total_players))

    embed = discord.Embed(title="📊 Server-Wide Game Statistics", color=0x7289DA)
    embed.add_field(name="👥 Total Players", value=f"{total_players:,}", inline=True)
    embed.add_field(name="🎮 Total Games Played", value=f"{total_games:,}", inline=True)
    embed.add_field(name="📈 Overall Win Rate", value=f"{overall_winrate}%", inline=True)
    embed.add_field(name="💰 Coins in Circulation", value=f"{total_coins:,} 🪙", inline=True)
    embed.add_field(name="💎 Total Ever Earned", value=f"{total_earned:,} 🪙", inline=True)
    embed.add_field(name="📊 Avg Balance", value=f"{avg_balance:,} 🪙", inline=True)
    embed.add_field(name="✅ Total Wins", value=f"{total_wins:,}", inline=True)
    embed.add_field(name="❌ Total Losses", value=f"{total_losses:,}", inline=True)
    embed.add_field(name="🎰 Games Available", value="500", inline=True)
    embed.add_field(name="🥇 Richest Player", value=f"{richest_name} — {richest_coins:,} 🪙", inline=False)
    embed.add_field(name="🔥 Top Streak", value=f"{streak_name} — {top_streak_val} wins", inline=False)
    embed.add_field(name="🎮 Most Active", value=f"{mp_name} — {mp_count:,} games", inline=False)
    embed.set_footer(text="Use %leaderboard to see the top 10 richest players.")
    await ctx.send(embed=embed)

# ─── Error handling ────────────────────────────────────────────────────────────
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions) or isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument. Use `/help` or `%help` for usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument. Make sure you mention the correct user/amount.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"⚠️ An error occurred: `{error}`")

# ─── Ready event ───────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user} | {len(GAMES)} games loaded | Slash /help synced")
    await bot.change_presence(activity=discord.Game(name="%help | 500 Games!"))

# ─── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not set. Create a .env file with DISCORD_TOKEN=your_token_here")
    else:
        bot.run(TOKEN)
