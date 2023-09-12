import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

import os

channel_id_str = os.getenv('channel')
channel_id = int(channel_id_str)
token = os.getenv('token')
role_id_str = os.getenv('role_id')
role_id = int(role_id_str)
wallet_destination = os.getenv('wallet_destination')


intents = discord.Intents.all()
intents.typing = True
intents.presences = True


bot = commands.Bot(command_prefix='/', intents=intents)


class SimpleView(discord.ui.View):

    

    foo : bool = None

    # async def disable_all_items(self):
    #     for item in self.children:
    #         item.disabled = True
    #     await self.message.edit(view=self)

    # async def on_timeout(self) -> None:
    #     await self.message.channel.send("Timeout")
    #     await self.disable_all_items()

    @discord.ui.button(label="Cadastro/Editar Wallet",
                       style= discord.ButtonStyle.green)
    async def cadastro(self, interaction: discord.Integration, button:discord.ui.Button):
        cadastro_modal = CadastroModal()
        cadastro_modal.user =  interaction.user
        await interaction.response.send_modal(cadastro_modal)
        self.foo = True

    @discord.ui.button(label="Comprar/Renovar VIP",
                       style= discord.ButtonStyle.blurple)
    async def compra(self, interaction: discord.Integration, button:discord.ui.Button):
        user_id = interaction.user.id
        feedback_modal = FeedbackModal(user_id)
        feedback_modal.user =  interaction.user
        await interaction.response.send_modal(feedback_modal)
        self.foo = True

    @discord.ui.button(label="Informacao", style=discord.ButtonStyle.blurple)
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        user_id = interaction.user.id
        user_file_name = f'user_{user_id}.json'

        try:
            with open(user_file_name, 'r') as file:
                data = json.load(file)
                data_expiracao_str = data.get('vip', '')
            
            registration_date_str = data.get('registration_date', '')
            registration_date = datetime.strptime(registration_date_str, '%d/%m/%Y')
            current_date = datetime.now()
            months_passed = (current_date.year - registration_date.year) * 12 + (current_date.month - registration_date.month)
            discount = min(35, months_passed * 5)

            wallet = data.get('wallet', '')

            #channel = interaction.guild.get_channel(channel_id)
            user_name = interaction.user.nick or interaction.user.name
            user_avatar_url = interaction.user.avatar

            embed = discord.Embed(title="Informacao", color=discord.Color.yellow())
            embed.set_author(name=user_name)
            embed.add_field(name="Wallet : ", value= f'{wallet}', inline=False)
            embed.add_field(name="Preco atual : ", value= f'{70 - discount} USDC - Desconto de {discount} USDC.', inline=False)
            embed.add_field(name="VIP ate : ", value=f'{data_expiracao_str}', inline=False)
            embed.set_footer(text=f"By Mira", icon_url='https://cliply.co/wp-content/uploads/2021/08/372108630_DISCORD_LOGO_400.gif')
            embed.set_thumbnail(url=f'{user_avatar_url}')
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except FileNotFoundError:
           
           await interaction.response.send_message('Faca o cadastro primeiro!', ephemeral=True)

        

        #await interaction.response.send_message(f'Wallet: {wallet}\nPreco atual: {70 - discount} USDC - Desconto de {discount} USDC.\nVIP: {data_expiracao_str}', ephemeral=True)
        self.foo = True


class FeedbackModal(discord.ui.Modal, title='Solana Comprar/Renovar VIP'):

    def get_registration_date(self, user_id: int) -> str:
        user_file_name = f'user_{user_id}.json'

        try:
            with open(user_file_name, 'r') as file:
                data = json.load(file)
                return data.get('registration_date', '')
        except FileNotFoundError:
            return ""

        
    def get_user_wallet(self, user_id:int) -> str:
        user_file_name = f'user_{user_id}.json'

        try:
            with open(user_file_name, 'r') as file:
                data = json.load(file)
                return data.get('wallet', '')
        except FileNotFoundError:
            return ""
        
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        wallet = self.get_user_wallet(self.user_id)

        self.fb_title = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Carteira de Origem",
            required=True,
            placeholder='Carteira de Origem',
            default=wallet,
        )

    message = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Hash da transacao",
        required=True,
        max_length=500,
        placeholder='Hash da transacao'
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = interaction.guild.get_channel(channel_id)

        user_name = self.user.nick or self.user.name
        user_id = interaction.user.id
        wallet = self.get_user_wallet(user_id)

        registration_date_str = self.get_registration_date(user_id)
        registration_date = datetime.strptime(registration_date_str, '%d/%m/%Y')
        current_date = datetime.now()
        months_passed = (current_date.year - registration_date.year) * 12 + (current_date.month - registration_date.month)
        discount = min(35, months_passed * 5)

        user = interaction.guild.get_member(user_id)

        data_envio = datetime.now()
    
        data_expiracao = data_envio + timedelta(days=30)
        
        data_envio_str = data_envio.strftime('%d/%m/%Y')
        data_expiracao_str = data_expiracao.strftime('%d/%m/%Y')

        wallet = self.fb_title.value
        hash = self.message.value

        headers = {
            'accept': 'application/json',
        }

        response = requests.get(
            f'https://public-api.solscan.io/transaction/{hash}',
            headers=headers,
        )

        data = response.json()

        if response.status_code == 200:
            for tokenTransfers in data.get('tokenTransfers', []):
                source = tokenTransfers.get('source_owner', '')
                destination = tokenTransfers.get('destination_owner', '')
                amount = int(tokenTransfers.get('amount', 0))
                token_symbol = tokenTransfers.get('token', {}).get('symbol', '')
                token_decimal = tokenTransfers.get('token', {}).get('decimals', 0)

                amount_true = amount / 10 ** token_decimal

                shortened_source = source[:3] + '...' + source[-3:]
                shortened_wallet = wallet[:3] + '...' + wallet[-3:]
                shortened_destination = destination[:3] + '...' + destination[-3:]

                try:
                    user_file_name = f'user_{user_id}Pagamento.json'
                    with open(user_file_name, 'r') as file:
                        data = json.load(file)
                        hash_r = data.get('hash', '')
                except:
                    pass
                    

                if hash_r == None or hash != hash_r:

                    if source == wallet and amount_true >= (70 - discount) and destination == f'{wallet_destination}':
                        if user:
                            role = interaction.guild.get_role(role_id)
                            await user.add_roles(role)

                            embed = discord.Embed(title="Nova Renovação", color=discord.Color.yellow())
                            embed.set_author(name=user_name)
                            embed.add_field(name="Carteira de Origem", value=self.fb_title.value, inline=False)
                            embed.add_field(name="Hash da Transação", value=self.message.value, inline=False)
                            embed.add_field(name="Data de Envio", value=data_envio_str, inline=False)
                            embed.add_field(name="Data de Expiração", value=data_expiracao_str, inline=False)

                            await channel.send(embed=embed)

                            with open(f'user_{user_id}Pagamento.json', 'w') as file:
                                data = {
                                    "user_name": user_name,
                                    "wallet": self.fb_title.value,
                                    "hash": self.message.value,
                                    "data_envio_str": data_envio_str,
                                    "data_expiracao_str": data_expiracao_str
                                }
                                json.dump(data, file, indent=2)

                            user_file_name = f'user_{user_id}.json'
                            with open(user_file_name, 'r') as file:
                                data = json.load(file)
                                wallet_r = data.get('wallet', '')
                                registration_date_r = data.get('registration_date', '')
                                data.get('vip', '')
                            
                            with open(user_file_name, 'w') as file:
                                data = {

                                "wallet": wallet_r,
                                "registration_date": registration_date_r,
                                'vip': data_expiracao_str
                            }
                                json.dump(data, file, indent=2)

                                
                        
                        print(f"Transação de {amount_true} {token_symbol} de {source} para {destination}")
                        await interaction.response.send_message(f'Transação de {amount_true} {token_symbol} de {shortened_source} para {shortened_destination}, Sucesso! Você recebeu o cargo {role.name} <@{user_id}>, sua mensalidade expira em: {data_expiracao_str}', ephemeral=True)
                    else:
                        errors = []

                        if source != wallet:
                            print("Erro: Wallet de envio não é igual a wallet da hash")
                            errors.append(f'Erro: Wallet de envio {shortened_source} não é igual a wallet {shortened_wallet} da hash')

                        if amount_true < (70 - discount):
                            print(f"Erro: Valor enviado é menor que {(70 - discount)}")
                            errors.append(f'"Erro: Valor enviado {amount_true} {token_symbol} é menor que {(70 - discount)} USDC')

                        if destination != f'{wallet_destination}':
                            print(f"Erro: Wallet de destino {shortened_destination} não é igual a '{wallet_destination}'")
                            errors.append(f"Erro: Wallet de destino {shortened_destination} não é igual a '{wallet_destination}'")

                        if errors:
                            await interaction.response.send_message(errors, ephemeral=True)
                else:

                    await interaction.response.send_message('Hash ja utilizada antes', ephemeral=True)
            else:
                await interaction.response.send_message(f'{response.status_code}', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error):
        ...


class CadastroModal(discord.ui.Modal, title='Cadastro de Novo Usuario'):
    
    cd_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Carteira de Origem",
        required=True,
        placeholder='Carteira de Origem',
    )

    async def on_submit(self, interaction: discord.Interaction):

        user_name = self.user.nick or self.user.name
        user_id = self.user.id
        wallet = self.cd_title.value

        data_expiracao_str = 'Nao possui vip.'

        user_file_name = f'user_{user_id}.json'

        try:
            with open(user_file_name, 'r') as file:
                data = json.load(file)

            if "wallet" in data:
                existing_wallet = data["wallet"]
                data["wallet"] = wallet

                with open(user_file_name, 'w') as file:
                    json.dump(data, file, indent=2)
                await interaction.response.send_message(f'Wallet alterada com Sucesso!', ephemeral=True)
            else:
                current_date = datetime.now()
                registration_date_str = current_date.strftime('%d/%m/%Y')

                data = {
                    "wallet": wallet,
                    "registration_date": registration_date_str,
                    'vip': data_expiracao_str
                }

                with open(user_file_name, 'w') as file:
                    json.dump(data, file, indent=2)
                await interaction.response.send_message(f'Cadastro feito com Sucesso!', ephemeral=True)
        except FileNotFoundError:
            current_date = datetime.now()
            registration_date_str = current_date.strftime('%d/%m/%Y')

            data = {
                "wallet": wallet,
                "registration_date": registration_date_str,
                'vip': data_expiracao_str
            }

            with open(user_file_name, 'w') as file:
                json.dump(data, file, indent=2)
            
            with open(f'user_{user_id}Pagamento.json', 'w') as file:
                data = {
                    "user_name": user_name,
                    "wallet": None,
                    "hash": None,
                    "data_envio_str": None,
                    "data_expiracao_str": None,
                }
                json.dump(data, file, indent=2)

            await interaction.response.send_message(f'Cadastro feito com Sucesso!', ephemeral=True)





@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Conectado como {bot.user.name}')

    # view = SimpleView()
    
    # list_channel_ids = [
    #     
    # ]

    # for channel_id in list_channel_ids:
    #     channel = bot.get_channel(channel_id)

    #     if channel:
    #         message = await channel.send("Clique em um botão:", view=view)
    #         view.message = message

    # await view.wait()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

@bot.command()
async def ola(ctx):
    await ctx.send(f'Olá, {ctx.author.mention}!')

@bot.command()
async def soma(ctx, num1: int, num2: int):
    resultado = num1 + num2
    await ctx.send(f'A soma de {num1} e {num2} é igual a {resultado}.')

@bot.command()
async def button(ctx):

    view= SimpleView()

    # button = discord.ui.Button(label='Click me')
    # view.add_item(button)

    message = await ctx.send(view=view)
    view.message = message

    await view.wait()
    # await view.disable_all_items()

@bot.tree.command()
async def feedback(interaction: discord.Interaction):
    feedback_modal = FeedbackModal()
    feedback_modal.user =  interaction.user
    await interaction.response.send_modal(feedback_modal)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Comando não encontrado.')

bot.run(token)
