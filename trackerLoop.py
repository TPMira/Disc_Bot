import discord
import json
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

import os


token = os.getenv('token')
url = os.getenv('url')


intents = discord.Intents.all()
intents.typing = True
intents.presences = True

class FavouriteGameSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="UniBet", value="UniBet"),
            discord.SelectOption(label="Bet365", value="Bet365"),
            discord.SelectOption(label="1Win", value="1Win"),
            discord.SelectOption(label="1xBet", value="1xBet"),
            discord.SelectOption(label="BCGame", value="BCGame"),
            discord.SelectOption(label="BetWay", value="BetWay"),
            discord.SelectOption(label="Betano", value="Betano"),
            discord.SelectOption(label="Betsson", value="Betsson"),
            discord.SelectOption(label="Bovada", value="Bovada"),
            discord.SelectOption(label="Bwin", value="Bwin"),
            discord.SelectOption(label="CloudBet", value="CloudBet"),
            discord.SelectOption(label="Dafabet", value="Dafabet"),
            discord.SelectOption(label="LeoVegas", value="LeoVegas"),
            discord.SelectOption(label="Parimatch", value="Parimatch"),
            discord.SelectOption(label="Pinnacle", value="Pinnacle"),
            discord.SelectOption(label="Rollbit", value="Rollbit"),
            discord.SelectOption(label="Solcasino", value="Solcasino"),
            discord.SelectOption(label="Stake", value="Stake"),
            discord.SelectOption(label="22Bet", value="22Bet"),
            discord.SelectOption(label="888sport", value="888sport"),
            discord.SelectOption(label="Stoiximan", value="Stoiximan"),
        ]
        super().__init__(options=options, placeholder="Qual casa deseja?")

    async def callback(self, interaction:discord.Interaction):
        await self.view.respond_to_answer2(interaction, self.values)
class SurveyView(discord.ui.View):
    answer1 = None 
    answer2 = None 
    
    @discord.ui.select(
        placeholder="Qual casa voce deseja?",
        options=[
            discord.SelectOption(label="UniBet", value="UniBet"),
            discord.SelectOption(label="Bet365", value="Bet365"),
            discord.SelectOption(label="1Win", value="1Win"),
            discord.SelectOption(label="1xBet", value="1xBet"),
            discord.SelectOption(label="BCGame", value="BCGame"),
            discord.SelectOption(label="BetWay", value="BetWay"),
            discord.SelectOption(label="Betano", value="Betano"),
            discord.SelectOption(label="Betsson", value="Betsson"),
            discord.SelectOption(label="Bovada", value="Bovada"),
            discord.SelectOption(label="Bwin", value="Bwin"),
            discord.SelectOption(label="CloudBet", value="CloudBet"),
            discord.SelectOption(label="Dafabet", value="Dafabet"),
            discord.SelectOption(label="LeoVegas", value="LeoVegas"),
            discord.SelectOption(label="Parimatch", value="Parimatch"),
            discord.SelectOption(label="Pinnacle", value="Pinnacle"),
            discord.SelectOption(label="Rollbit", value="Rollbit"),
            discord.SelectOption(label="Solcasino", value="Solcasino"),
            discord.SelectOption(label="Stake", value="Stake"),
            discord.SelectOption(label="22Bet", value="22Bet"),
            discord.SelectOption(label="888sport", value="888sport"),
            discord.SelectOption(label="Stoiximan", value="Stoiximan"),
        
        ]        
    )
    async def select_age(self, interaction:discord.Interaction, select_item : discord.ui.Select):
        self.answer1 = select_item.values
        self.children[0].disabled= True
        game_select = FavouriteGameSelect()
        self.add_item(game_select)
        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def respond_to_answer2(self, interaction : discord.Interaction, choices):
        self.answer2 = choices 
        self.children[1].disabled= True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Conectado como {bot.user.name}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)



@bot.command()
async def tracker(ctx):
    view = SurveyView()
    await ctx.send(view=view)
    await view.wait()

    results = {
        "a1": view.answer1,
        "a2": view.answer2,
    }

    await ctx.send(f"{results}")

    user_id = ctx.author.id
    user_file_name = f'id_{user_id}.json'

    try:
        with open(user_file_name, 'r') as file:
            id_data = json.load(file)

    except FileNotFoundError:
        with open(f'id_{user_id}.json', 'w') as file:
            id_data = []
            json.dump(id_data, file, indent=2)            

    url  

    while True:
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                bets = data.get("bets", [])

                filtered_bets = []
                for bet in bets:
                    booker1 = bet.get("booker1", {})
                    booker2 = bet.get("booker2", {})

                    if booker1 and booker2:
                        name1 = booker1.get("name")
                        name2 = booker2.get("name")

                        if (name1 in view.answer1 and name2 in view.answer2) or (name1 in view.answer2 and name2 in view.answer1):
                            filtered_bets.append(bet)

                for bet in filtered_bets:
                    id_bet = bet.get('id')

                    if id_bet in id_data:
                        continue
                    else:
                        embed = discord.Embed(title="Detalhes da Aposta", color=discord.Color.green())
                        embed.add_field(name="Booker1", value=f"ID: {id_bet}\n Casa: {bet['booker1']['name']}\nEvento: {bet['booker1']['event']}\nLink: {bet['booker1']['link']}", inline=False)
                        embed.add_field(name="Booker2", value=f"ID: {id_bet}\n Casa: {bet['booker2']['name']}\nEvento: {bet['booker2']['event']}\nLink: {bet['booker2']['link']}", inline=False)
                        await ctx.message.author.send(embed=embed)
                        id_data.append(id_bet)

                with open(user_file_name, 'w') as file:
                    json.dump(id_data, file, indent=2)

                print('finalizado!')

            else:
                print(f'Erro na solicitação: {response.status_code}')
        except Exception as e:
            print(f'Erro na solicitação: {str(e)}')

        #await ctx.message.author.send("No more bets!")
        await asyncio.sleep(30) 





@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Comando não encontrado.')

bot.run(token)
