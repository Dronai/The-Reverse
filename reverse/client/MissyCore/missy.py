from discord.ext import commands
from discord import Guild
import asyncio, datetime
from urllib import parse
from reverse.core._service import SqliteService
from reverse.core._models import Context, Role
from reverse.core import utils
from reverse.client.MissyCore._model import MissyCore

class Missy(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.db = SqliteService()
		self.schedule = []
		self.missys = MissyCore()

	@commands.command()
	async def whoismissy(self, ctx):
		await ctx.send("Une horreur lovecraftienne... Tempus edax rerum.")
	
	async def debugSQL(self, ctx, table="missy", column="id integer PRIMARY KEY, name text"):
		self.db.createTable(table, column)

	@commands.command()
	async def showTable(self, ctx):
		record = self.db._fetchAll(self.db.listTable())
		for v in record:
			await ctx.send("Table {}.".format(*v))

	async def tableToList(self, ctx) -> list:
		await ctx.send(SqliteService.tableToList(self.db.listTable()))

	@commands.command()
	async def debugInsertAllMembers(self, ctx):
		guild = ctx.guild
		await ctx.send("Fetch all members from {} called by {}".format(ctx.guild.name, ctx.author.name))
		self.db.createTable(guild.name, "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, discordID TEXT, UNIQUE(id, discordID)")
		for v in guild.members:
			self.db.insertion(guild.name, ["name", "discordID"], [v.name, str(v.id)], ignore=True)
		await ctx.send("Successfully inserted {} entries to Table {} ".format(len(guild.members), guild.name))

	@commands.command()
	async def initServerEvent(self, ctx):
		ctx = Context(ctx)
		guild = ctx.guild
		table = "{}_event".format(guild.name)
		if(self.db.isTableExist(table)):
			await ctx.send("Starting initialization to host event on this server.")
			self.db.createTable("{}_event".format(guild.name), "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT")
			return
		await ctx.send("Server already initalized.")

	@commands.command()
	async def members(self, ctx, *args):
		ctx = Context(ctx)
		guild = ctx.guild
		_kwargs, _args = utils.parse_args(args)
		if("role" in _kwargs.keys()):
			r_id = _kwargs["role"][3:-1]
			_m = utils.getAllMembers(guild, int(r_id))

			if(len(_m) >= 1):
				for v in _m:
					await ctx.send("User: {}".format(v))
			else:
				await ctx.send("This role is unused.")

	# Command to initialize Target
	@commands.command()
	async def tt(self, ctx, *args):
		_kwargs, _args = utils.parse_args(args)

		if "role" in _kwargs.keys() and "name" in _kwargs.keys() and "channel" in _kwargs.keys():	
			self.missys.initialisation(ctx.guild, _kwargs)
		else:
			ctx.send("Argument missing in : 'name', 'role',  'channel'\n Impossible Target's initialization")
	
	# Command to roll for a target
	@commands.command()
	async def ll(self, ctx, *args):
		_kwargs, _args = utils.parse_args(args)

		if "target" in _kwargs.keys() and "date" in _kwargs.keys():
			if(self.validate(ctx, _kwargs["date"])):
				for target in self.missys.listTargets:
					if target.role.id == int(_kwargs["target"][3:-1]):
						await self.missys.roll(_kwargs["date"], target)
						break
			else:
				await ctx.send("Incorrect data format, should be DD-MM-YYYY")
		else:
			await ctx.send("Argument missing in : 'role',  'date'\n Impossible Target's initialization")

	def validate(self, ctx, date_text):
		try:
			datetime.datetime.strptime(date_text, '%d-%m-%Y')
		except ValueError:
			return False
		
		return True

def setup(bot):
	bot.add_cog(Missy(bot))