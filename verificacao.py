import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
from datetime import datetime
import json
import asyncio
import time

load_dotenv()

channel_id_str = os.getenv('channel')
channel_id = int(channel_id_str)
token = os.getenv('token')
role_id_str = os.getenv('role_id')
role_id = int(role_id_str)
discord_str = os.getenv('discord')
discord_id = int(discord_str)

intents = discord.Intents.all()
intents.typing = True
intents.presences = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def verificar_e_remover_cargo():
    
    while True:
        
        guild = bot.get_guild(discord_id)
        if guild is None:
            print("Servidor não encontrado.")
            return

        current_date = datetime.now()
        
        for member in guild.members:
            user_id = member.id
            user_file_name = f'user_{user_id}.json'

            try:
                with open(user_file_name, 'r') as file:
                    data = json.load(file)
                    wallet = data.get('wallet', '')
                    registration_date = data.get('registration_date', '')
                    vip = data.get('vip', '')
                    
                    print(member.name) 

                    if vip == 'Nao possui vip.':

                        pass

                    else:    
                                        
                        vip_date = datetime.strptime(vip, '%d/%m/%Y')
                        
                        # Verificar se a data de expiração é anterior à data atual
                        if vip_date < current_date:
                            # A data de expiração passou, remova o cargo aqui
                            role = discord.utils.get(guild.roles, id=role_id)
                            if role is not None:
                                await member.remove_roles(role)
                                print(f"Removeu o cargo de {member.name}")

                                with open(f'user_{user_id}.json', 'w') as file:
                                    data = {
                                        "wallet": wallet,
                                        "registration_date": registration_date,
                                        "vip": 'Nao possui vip.',
                                    }
                                    json.dump(data, file, indent=2)

                                try:
                                    await member.send(f"Seu cargo foi removido porque sua assinatura VIP expirou.")
                                except discord.Forbidden:
                                    print(f"Não foi possível enviar uma mensagem privada para {member.name}")
        
            except FileNotFoundError:
                pass

        await asyncio.sleep(300)
        

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await verificar_e_remover_cargo()

bot.run(token)
