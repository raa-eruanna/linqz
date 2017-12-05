#    Linqz Discord Bot Link and Info Getter
#    Copyright (c) 2017 Rachael Alexanderson
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/python3
import discord
import asyncio
import urllib

from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from bs4 import BeautifulSoup

client = discord.Client()
url = URLValidator()

bottoken = 'INSERT BOT TOKEN HERE'
whitelist = {
	"zdoom.org",
	"drdteam.org",
	"tdgmods.com",
	#"zandronum.com",
	#"doomworld.com",
	#"doomwiki.org",
}

@client.event
async def on_ready():
	print('---Logged in as---')
	print(client.user)
	print(client.user.id)
	appdata = await client.application_info()
	client.owner = appdata.owner
	print('-----My Owner-----')
	print(client.owner)
	print(client.owner.id)
	print('------------------')


@client.event
async def on_message(message):

	link = ''

	for x, value in enumerate(message.content.split()):
		try:
			url(value)
			iswhitelisted = 0
			parsed_uri = urlparse(value)
			parsed_domain = parsed_uri.hostname

			for y, domainlisting in enumerate(whitelist):
				if domainlisting == parsed_domain: iswhitelisted = 1
				if parsed_domain.endswith('.' + domainlisting): iswhitelisted = 1

			if iswhitelisted == 1:
				print("Accepted ({}) #{} {} > {}".format(message.guild.name, message.channel, message.author, value))
				link = value
			else:
				print("Rejected ({}) #{} {} > {}".format(message.guild.name, message.channel, message.author, value))
		except:
			#traceback.print_exc(file=sys.stdout)
			pass

	if (link != ''):
		tmp = await message.channel.send('URL detected')
		httprequest = urllib.request.Request(
			link,
			headers={
				'User-Agent': 'Mozilla/5.0 (compatible; linqz/0.0; +https://drdteam.org/)'
			}
		)
		try:
			webpage = urllib.request.urlopen(httprequest)
			if webpage.getcode() == 200:
				soup = BeautifulSoup(webpage, "lxml")
				title = soup.title.string

				try:
					metadescription = soup.find(
						'meta',
						attrs={'name':'description'}
					)
					description = metadescription["content"]
				except:
					description = 'No description'

				try:
					firstimagesrc = soup.find(
						'img',
						attrs={'name':'src'}
					)
					firstimage = firstimagesrc["content"]
				except:
					firstimage = ''

				await tmp.edit(
					content = "Link `{}` sent by `{}`".format(
						link,
						message.author.name
					),
					embed = discord.Embed(
						title = title,
						type = "rich",
						description = description,
						url = link,
						thumbnail = firstimage
					)
				)
			else:
				await tmp.edit(
					content = "Link `{}` sent by `{}`".format(
						link,
						message.author.name
					),
					embed = discord.Embed(
						title = "Error {}".format(webpage.getcode()),
						type = "rich",
						description = webpage.reason
					)
				)
		except:
			await tmp.edit(
				content = "Error retreiving URL `{}` from `{}`!".format(
					link,
					message.author.name
				)
			)
	if (message.author.id == client.owner.id):
		if message.content.startswith('!quit'):
			await message.channel.send('Logging off, {}!'.format(message.author.name))
			await client.close()

client.run(bottoken)

