# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

import discord
import logging
import mimeparse
import os
import io
import json
import yaml
import extensions.util.simplebot as simplebot
import extensions.util.persistentstore as persistentstore
import extensions.util.views as views

logger = logging.getLogger(__name__)


class ClubInfo(simplebot.SimpleCog):
    """
    Implements commands providing club information

    This Cog provides a command 'club' for members to request more information about various
    aspects of the club. The Cog uses the Discord autocomplete feature to produce a dynamic
    list of possible queries based on the bots configuration. This allows the configuration
    to be updated to add/remove information without modifying the code itself.
    """

    def __init__(self, bot: simplebot.SimpleBot):
        super().__init__(bot, config_name='clubInfo')

        self.__dbpath = self.config.get('database_path', None)
        if not self.__dbpath:
            raise SystemExit(f'missing configuration: clubInfo -> database_path')

    def __persistent_store(self, guild_id: int) -> persistentstore.PersistentGuildStore:
        """Returns the object used for persistent storage"""
        return persistentstore.PersistentGuildStore(guild_id, str(self.__dbpath))

    def get_what_values(self, ctx: discord.AutocompleteContext):
        """Provides autocomplete support when a user is inputting the 'what' value for commands"""
        guild_id = ctx.interaction.guild_id or 0
        ps = self.__persistent_store(guild_id)
        return ps.get_keys(ctx.value.lower())

    manage_group = discord.SlashCommandGroup(name="manage_club", description="Commands used to manage content for /club")

    @manage_group.command(name="update", description="Updates (or adds) content to the /club command")
    @discord.option(name="what", description="What do you want to update or add?", autocomplete=get_what_values)
    @discord.option(name="file", description="File containing the new content")
    async def manage_club_update(self, ctx: discord.ApplicationContext, what: str, attachment: discord.Attachment):
        logger.info(f"received attachment guild_id={ctx.guild_id}, guild={ctx.guild}, filename={attachment.filename}, title={attachment.title}, content_type={attachment.content_type}")

        # We want to be case insensitive
        what = what.lower()

        # Parse the mime type to ensure validity
        mime_type, _, mime_args = mimeparse.parse_mime_type(attachment.content_type)
        if mime_type != "text":
            await ctx.respond(
                content=f"Looks like you sent an invalid file of type {mime_type}. Please send a text file.",
                ephemeral=True)
            return
        # Files larger than 5k are rejected
        elif attachment.size > 5120:
            await ctx.respond(
                content=f"Files must be less than 5120 bytes. You sent a file of {attachment.size} bytes. Please send a smaller file.",
                ephemeral=True
            )
            return
        # Don't allow more than 10 messages to be defined
        elif len(self.__persistent_store(ctx.guild_id).get_keys('')) >= 10:
            await ctx.respond(
                content=f"You have already defined your maximum of 10 club messages. Please delete or replace an existing message.",
                ephemeral=True
            )
            return

        # Read and decode the file content based on the specified charset (default to utf-8)
        content = await attachment.read()
        charset = mime_args.get('charset', 'utf-8')
        content = content.decode(mime_args.get("charset", "utf-8"))

        record = { 'content': content, 'charset': charset, 'type': None }

        # Get the file extension to determine type
        _, extension = os.path.splitext(attachment.filename)
        if extension == ".yaml" or extension == ".yml":
            # Parse as a YAML file
            record['type'] = 'yaml'
        else:
            # Parse as a markdown file
            record['type'] = 'markdown'

        # Confirm the change with the user
        yes_no_view = views.YesNoConfirmationView(timeout=120)
        embed = self._generate_embed(record)
        await ctx.respond(
            content=f"Here is a preview of your update. Do you want to save this change to '{what}'?", 
            embed=embed, 
            view=yes_no_view,
            ephemeral=True)

        # Wait for a response
        await yes_no_view.wait()

        # If the response was yes, persist the changes and send a notification to the channel
        if yes_no_view.selection == "yes":
            ps = self.__persistent_store(ctx.guild_id)
            ps.set_value(what, json.dumps(record))

            message = f"OK, I saved this change to '{what}' for you."
        # If the response was no, then don't persist and tell the user.
        elif yes_no_view.selection == "no":
            message = f"OK, I discarded this change to '{what}'."
        # Any other case indicates a timeout. Display a friendly message to the user.
        else:
            message = "Looks like you stepped away. Please try again later"

        # Send the response
        await ctx.interaction.edit(content=message, view=None, embed=None)

    @manage_group.command(name="get", description="Gets the raw content associated with a /club subcommand")
    @discord.option(name="what", description="What raw content do you want to retrieve?", autocomplete=get_what_values)
    async def manage_club_get(self, ctx: discord.ApplicationContext, what: str):
        ps = self.__persistent_store(ctx.guild_id)
        raw_record = ps.get_value(what)
        if not raw_record:
            await ctx.respond(
                content=f"I don't have any information about '{what}'. Add some using **/manage_club update**",
                ephemeral=True
            )
            return

        record = json.loads(raw_record)
        if record['type'] == 'yaml':
            filename = f"{what}.yml"
        else:
            filename = f"{what}.md"

        with io.BytesIO(bytes(record['content'], record['charset'])) as content:
            file = discord.File(filename=filename, fp=content)
            await ctx.respond(
                content="Attached is the raw content associated with /club {what}",
                file=file,
                ephemeral=True
            )

    @discord.command(name="club", description="Provides club information")
    @discord.option(name="what", description="What do you want to know about?", autocomplete=get_what_values)
    async def club(self,  ctx: discord.ApplicationContext, what: str):
        # We want to be case insensitive
        what = what.lower()

        ps = self.__persistent_store(ctx.guild_id)
        raw_record = ps.get_value(what)
        if not raw_record:
            await ctx.respond(content=f"I don't have any information about '{what}'. Ask the admin to add some!",
                              ephemeral=True)
            return

        record = json.loads(raw_record)
        embed = self._generate_embed(record)

        await ctx.respond(embed=embed)

    def _generate_embed(self, record: dict) -> discord.Embed:
        if record['type'] != 'yaml':
            embed = self._embed(description=record['content'])
        else:
            raw_config = record['content']
            config = yaml.safe_load(raw_config)
            embed = self._embed(
                title=config.get('title', None),
                description=config.get('description', None)
            )

            for field in config.get('fields', None):
                embed.add_field(name=field.get('name', None), value=field.get('value', None), inline=field.get('inline', True))
        
        return embed

def setup(bot: simplebot.SimpleBot):
    bot.add_cog(ClubInfo(bot))
