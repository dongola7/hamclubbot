# Description

A discord bot intended for use in servers for Amateur Radio Clubs. Provides a series of
useful tools for managing the club, looking up weather conditions for radio operation, etc.

The bot is built using the [Pycord](https://pycord.dev) framework.

# Current Commands

## Conditions

The following commands provide access to ham band conditions

* `/cond` - Posts an image of current ham band conditions from [hamqsl.com](https://hamqsl.com)
* `/muf` - Posts an image of the current MUF (Maximum Usable Frequency) map from [prop.kc2g.com](https://prop.kc2g.com)

Results for the above commands are cached and refreshed on-demand, but no more than once every 15 minutes.

## Parks on the Air (POTA)

The following commands provide access to data from [Parks on the Air](https://pota.app).

* `/pota callstats <callsign>` - Posts the hunter/activator statistics for the given callsign
* `/pota activations <park>` - Posts the 5 most recent activations for the given park number (e.g. US-8081)

Results for the above commands are cached and refreshed on-demand, but no more than once every 15 minutes.

## Club Information

The bot is intended for use by Ham Radio Clubs, and so provides a way for discord users to request static club
information. This can be used to provide details on meeting schedules, nets, repeaters, etc. Each server connected
to the bot is limited to storing 10 information responses each 5 KB or less.

* `/club <what>` - This is the user facing command and is used to post the static information identified by the `what`
  field. The `what` field is simply an identifier defined at the time the static information is stored in the bot.

The following commands provide access to add/edit/delete the static information stored in the bot. As such it is **highly
recommended** that the `/manage_club` command group be restricted to privileged users of the Discord server.

* `/manage_club update <what> <attachment>` - Given an identifier, `what`, and a file in Markdown or YAML format (see
  below for more details in file formats), stores the static information for later retrievel using `/club <what>`
* `/manage_club delete <what>` - Given an identifier, `what`, deletes the static information associated with the
  identifier. Returns the stored information as an attachment in case a mistake is made.
* `/manage_club get <what>` - Given an identifier, `what`, returns the raw static information in Markdown or YAML format
  as an attachment. This is used typically to download content, modify, and then repost using `/manage_club update`.

### File Formats

The attachments may be in either Markdown or YAML format. A file extension of `.yml` or `.yaml` is used to indicate
YAML format, all others are assumed to be Markdown.

For Markdown formatted files, the content is posted directly and Discord converts the Markdown format to the display
format. Therefore you should use only the Markdown syntax supported by Discord (see [here](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline).

For YAML formatted files, you may add a title, description, and one or more fields to be displayed. For example:

```yaml
# Title to be displayed
title: Club Repeaters

# Description is the main body of the content and may contain markdown
description: >-
  The club hosts a repeater, located in Brooklyn, operating under
  the KC2RC callsign.

# Zero or more fields to be displayed. The values may contain markdown. Fields
# are displayed almost as sections, with the field name displayed as the section
# header, and the field value displayed as the section content.
#
# If a field uses the optional 'inline: false', value, then it is displayed on its
# own. Otherwise, it will float next to other fields in a row.
fields:
  - name: Transmit
    value: 146.130 MHz
  - name: Receive
    value: 146.730 MHz
  - name: PL Tone
    value: 88.5 Hz
  - name: EchoLink
    value: >-
      Operators not within range of the repeater may use
      [EchoLink](https://echolink.org) by connecting to the KC2RC-R
      callsign.
    inline: false
```

# Running the Bot

## Running Directly

```bash
# Install system dependencies (requires Homebrew from https://brew.sh)
brew bundle

# Create and activate a python virtual environment
python3 -m venv local-env
source local-env/bin/activate

# Install required packages
pip install -e ".[dev]"

# Generate the config file from 1Password
op inject -i ./config/config.yaml.tmpl -o ./config/config.yaml

# Run the bot
./bot.py --config ./config/config.yaml
```

## Running using a Docker Image

You can run the bot directly or build a Docker image using the included Dockerfile
to run the bot. If using a Docker image, the Dockerfile is configured to expect
the configuration to be located in /app/config.yaml. You need to mount the
configuration file accordingly.

For example:

```bash
# Build the docker image and tag it as hamclubbot
docker build -t hamclubbot .

# Run a docker container, exposing $(HOME)/config.yaml as the bot configuration
docker run -v $(HOME)/config.yaml:/app/config.yaml hamclubbot
```

# Acknowledgements

This bot is inspired by [hambot](https://github.com/alekm/hambot), but was
written directly so I could brush up on my Python skills and learn a bit
about Discord bots and how they operate.
