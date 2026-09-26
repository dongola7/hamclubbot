# hamclubbot — Technology-Agnostic Rewrite Specification

## 1. Purpose and Scope

hamclubbot is a Discord bot for amateur radio (ham) club servers. It answers
slash commands with radio-propagation data pulled from third-party sites,
serves per-club reference content (meeting schedules, repeater info, nets)
that club admins maintain themselves, and reports its own health/uptime.

This document specifies *behavior and requirements*, not implementation. It
is written so the bot can be rebuilt in a different language/runtime while
preserving the current feature set, configuration surface, and security
posture — and while closing a known authorization gap in the current
implementation (see §6.1).

Out of scope: this is a single-process bot serving multiple Discord guilds
(servers) from one deployment; no web UI, no REST API, no multi-tenant
billing.

## 2. Platform Requirements

- Must integrate with Discord's slash-command ("Application Command") and
  message-component (buttons) APIs, including:
  - Global or per-guild slash command registration, including subcommands
    and command groups.
  - Autocomplete callbacks for command options.
  - File attachments as both command input and response output.
  - Embeds (title, description, color, fields with inline/block layout,
    image, footer).
  - Ephemeral (caller-only) responses.
  - Interactive components (Yes/No confirmation buttons) with a timeout.
- Must support one bot process serving many guilds concurrently, with
  guild-scoped data isolation (see §5).
- Target a Discord API wrapper/SDK appropriate to the chosen language
  (equivalent in capability to discord.py/Pycord, discord.js, Discord4J,
  Serenity, etc.) rather than raw gateway/REST calls, unless there is a
  specific reason to go lower-level.

## 3. Functional Requirements

### 3.1 `/about`
Returns an embed with:
- Static bot description and link to project source.
- Bot owner (mention/tag), resolved from configured owner ID.
- Current uptime, formatted as a human-readable duration since process
  start.
- Current gateway latency in milliseconds.

No external calls, no persistence.

### 3.2 `/cond` — Solar/band conditions
- Fetches an image from `https://www.hamqsl.com/solar101pic.php`.
- Returns it as an embed with the image attached, titled "Current Solar
  Conditions," crediting hamqsl.com, with a footer showing how long ago the
  underlying data was refreshed (e.g., "Refreshed 4 minutes ago").
- Must not fetch on every invocation — see caching requirements (§4.2).

### 3.3 `/muf` — Maximum Usable Frequency map
- Fetches an SVG from `https://prop.kc2g.com/renders/current/mufd-normal-now.svg`.
- Converts SVG → PNG server-side before sending (Discord embeds do not
  reliably render SVG); the converted PNG must itself be cached alongside
  the source fetch so conversion doesn't repeat on every cache hit.
- Returns embed titled "Current MUF Map," crediting prop.kc2g.com, with the
  same "refreshed N minutes ago" footer semantics as `/cond`.

### 3.4 `/pota activations <park>`
- `park` is a POTA park reference (e.g. `US-8081`); normalize to uppercase
  and URL-encode before use.
- Concurrently queries three pota.app endpoints for the given park:
  stats, park metadata, and the 5 most recent activations.
- Any endpoint returning a string payload instead of an object indicates an
  upstream error — surface it to the user as an ephemeral error message
  quoting the upstream text, do not attempt to render a partial embed.
- On success, renders one embed with: linked park name/reference, overall
  activation/QSO stats, and a formatted list of the 5 most recent
  activations (date, callsign, total QSOs, breakdown by mode: CW/Data/Phone).
- Cache per the shared web-cache policy (§4.2); footer shows refresh time.

### 3.5 `/pota callstats <callsign>`
- Normalizes callsign to uppercase, URL-encodes it, queries
  `https://api.pota.app/stats/user/<callsign>`.
- String response = upstream error → ephemeral error message.
- Object response → embed with activator stats (activations/attempts,
  parks, QSOs) and hunter stats (parks, QSOs), a link to the user's public
  POTA profile, and the standard refresh-time footer.

### 3.6 `/club <what>` and content management
Each guild can store up to **10** named pieces of static reference content
(club meeting info, nets, repeaters, join instructions, etc.), each up to
**5,120 bytes**. Content lives in two supported formats:

- **Markdown**: raw text passed straight into an embed description, using
  only Discord-supported Markdown syntax.
- **YAML**: structured content with `title`, `description`, and a `fields`
  list, each field having `name`, `value`, and optional `inline` (default
  `true`) — mirrors Discord embed field layout exactly.

Format is inferred from the uploaded file's extension: `.yaml`/`.yml` →
YAML, anything else → Markdown.

Commands (grouped under a `manage_club` namespace):

- **`/manage_club update <what> <file>`**
  - `what` is a free-text identifier (case-insensitive; store/compare
    lowercased), with autocomplete suggesting existing identifiers for this
    guild as the admin types.
  - Reject non-text attachments (validate declared MIME type).
  - Reject attachments over 5,120 bytes.
  - Reject if the guild already has 10 stored entries and `what` doesn't
    match an existing one (i.e. block adding an 11th, but allow overwriting
    1–10).
  - Decode the attachment using the charset declared in its MIME type
    (default UTF-8).
  - **Before saving**, show the admin a preview of the rendered content
    (as it would appear via `/club <what>`) with Yes/No confirmation
    buttons, timeout 120 seconds. Only persist on explicit "Yes." On "No"
    or timeout, discard and tell the user nothing was saved.
  - Record who made the change and when (user ID + timestamp) alongside
    the content, for audit purposes.
  - This command is destructive to existing content on overwrite and
    **must be restricted to privileged guild members** — see §6.1.

- **`/manage_club get <what>`**
  - Returns the raw stored content (Markdown or YAML) as a downloadable
    file attachment, named `<what>.md` or `<what>.yml`, so an admin can
    edit and re-upload it. Ephemeral response.
  - Same privilege restriction as `update`.

- **`/manage_club delete <what>`**
  - Deletes the stored entry and returns its content as a downloadable
    attachment (so the admin has a backup of what was just deleted).
  - Same privilege restriction as `update`.

- **`/club <what>`**
  - Public, unrestricted command. Case-insensitive lookup; if not found,
    ephemeral message inviting the user to ask an admin to add it.
  - Renders the stored content (Markdown → embed description; YAML →
    title/description/fields) as a normal (non-ephemeral) embed.
  - Autocomplete on `what`, scoped to the invoking guild's stored keys,
    filtered by the user's partial input as a prefix (case-insensitive).

### 3.7 Command usage telemetry
Track, per command, counts of: invocations received, invocations completed
successfully, and invocations that errored. Periodically (every 5 minutes)
log these counters. This is operational telemetry, not user-facing.

### 3.8 Startup and shutdown behavior
- Load all extensions/modules independently; a single extension failing to
  load must be logged as an error but must not prevent the others from
  loading or the bot from starting.
- On authentication failure, gateway close, or unexpected fatal error
  during run, log at critical severity with the specific reason and exit
  the process with a non-zero/error status (so an orchestrator — systemd,
  Docker, Kubernetes — can detect and restart it).
- Log bot username, guild count, and readiness once the gateway connection
  is fully established.

## 4. Cross-Cutting Technical Requirements

### 4.1 Configuration
Single external config file (path supplied via required command-line
argument, e.g. `--config`), loaded once at startup. Must **fail fast**
(clear error, non-zero exit) if the file is missing or invalid — never
run with partial/default config for security-sensitive values.

The bot's authentication secret (the Discord token) is read from the
`DISCORD_TOKEN` environment variable rather than the config file, so it
never has to be rendered to disk. Fail fast with a clear error if unset.

Required/known keys:

| Key | Required | Purpose |
|---|---|---|
| `ownerId` | no | Discord user ID shown as bot owner in `/about`. |
| `clubInfo.database_path` | yes (if club-info feature enabled) | Path to the club-content store. Fatal error at startup if missing. |
| `embeds.color` | no | Default embed accent color; falls back to a sane default. |
| `logging.*` | no | Passed through to the logging subsystem's structured config mechanism; if absent, use a sensible default (INFO level, timestamped single-line format to stdout). |

The config format should support external secret injection (e.g. templated
and filled by a secrets manager/1Password/Vault at deploy time) rather than
committing real secrets to source control. Ship a `.tmpl` example config
with placeholder values plus documented generation instructions, and ensure
real config files are excluded from version control.

### 4.2 HTTP response caching
All outbound calls to third-party HTTP data sources must go through a
shared cache layer:
- Keyed by exact URL.
- Configurable TTL, default **15 minutes**.
- On cache hit (not expired), return cached bytes with no network call.
- On miss/expiry, fetch synchronously-from-the-caller's-perspective but
  without blocking the event loop/other concurrent work, store raw
  response bytes, and reset the TTL clock.
- Support an optional derived/secondary value cached alongside the raw
  bytes (used by `/muf` to cache the SVG→PNG conversion so it isn't
  redone on every cache hit).
- Expose "time since last refresh" as a human string (e.g. "Just
  refreshed", "Refreshed 1 minute ago", "Refreshed N minutes ago") for
  display in command footers.
- Network failures from the upstream site are expected (this is a known
  gap in the current implementation — see TODO) and **must** be caught and
  surfaced to the user as a friendly error rather than crashing the
  command handler or the process.

### 4.3 Persistence
- Per-guild key/value store for club content, scoped so no guild can read
  or write another guild's keys.
- All queries against user-influenced values (guild ID, key name) must use
  parameterized queries/prepared statements — never string-concatenated
  SQL or equivalent.
- Store must self-initialize its schema on first use (no separate manual
  migration step required for a fresh deployment); support a stored schema
  version for future migrations.
- Default implementation is an embedded, file-based store (SQLite in the
  current version) — no external database dependency required for a
  single-instance deployment. If the rewrite targets a horizontally-scaled
  deployment, this should become a pluggable interface so the backing
  store can be swapped for a networked database.

### 4.4 Logging
- Structured, leveled logging (DEBUG/INFO/WARNING/ERROR/CRITICAL at
  minimum) to stdout by default, with the format/handlers/sinks
  externally configurable.
- Never log secrets (bot token, etc).
- Log command receipt, completion, and errors (with the triggering
  exception detail) for every slash command.
- Log extension load success/failure per extension at startup.

### 4.5 Extensibility model
Preserve the current "extension/cog" pattern: each feature area (radio
conditions, club info, POTA, about/health) is an independently loadable
module that:
- Declares its own slash commands/command groups.
- Reads only its own named section of the shared config.
- Shares a common helper for building consistently-styled embeds (shared
  accent color, consistent title/footer conventions).
- Can fail to load without taking down unrelated modules.

This keeps the bot easy to extend with new clubs' needs (e.g. new data
sources) without touching unrelated code.

## 5. Data Model

### 5.1 Club content record (per guild, per `what` key)
```
{
  content: string,            // raw markdown or yaml text
  charset: string,            // encoding used to decode the source file
  type: "markdown" | "yaml",
  what: string,                // lowercase identifier, redundant w/ key but stored for export
  last_updated: {
    user_id: <discord user id>,
    timestamp: <unix time>
  }
}
```
Constraints: max 10 records per guild; each record's `content` ≤ 5,120
bytes as originally uploaded.

### 5.2 Command statistics (in-memory, not persisted across restarts)
Per command name: received count, completed count, error count.

## 6. Security Requirements

These are non-negotiable requirements for the rewrite, informed by a prior
security review of the existing implementation.

### 6.1 Authorization on administrative commands (fixes a known gap)
The current implementation has **no server-side authorization check** on
`/manage_club update|get|delete` — any guild member can overwrite or
delete club content, relying entirely on server owners remembering to
restrict the command via Discord's own integration permission UI. **The
rewrite must not repeat this.** Requirements:
- Administrative commands must declare a default required permission
  (equivalent to Discord's "Manage Server" permission) at the command
  level, enforced by the platform itself, not just documented as a
  recommendation.
- Administrative commands must be unusable outside of a guild context (no
  DM invocation).
- `delete` must require the same confirmation step already required for
  `update` (currently `delete` executes immediately with no
  confirmation) — a destructive action should never be a single
  unconfirmed keystroke away, however it returns the deleted content as a
  backup attachment either way.

### 6.2 Input validation
- Validate declared MIME type of uploaded attachments and reject non-text
  content before parsing.
- Enforce hard size limits on uploaded content server-side (do not trust
  client-declared size alone if the platform allows re-verification of
  actual bytes read).
- Enforce a hard cap on number of stored items per guild.
- Treat all YAML parsing as **safe-load only** — never enable arbitrary
  object construction/tag resolution from user-supplied YAML.
- Parameterize all persistence queries; never build queries by string
  interpolation of guild IDs, keys, or any user input.
- URL-encode any user-supplied value (park references, callsigns) before
  interpolating into outbound HTTP requests; never let user input reach
  outbound URLs as raw path segments.

### 6.3 Secrets handling
- Bot token and other secrets are supplied via the config file only —
  never hardcoded, never logged, never echoed back in any command
  response or error message.
- Config files containing real secrets must be excluded from version
  control; provide a template with placeholder/injectable values instead.

### 6.4 Least-privilege deployment
- Container images must run as a dedicated non-root user, not root.
- Use a multi-stage build so build-time tooling and source are not present
  in the final runtime image.
- Install only the minimal OS packages required at runtime (the current
  image needs a Cairo-equivalent SVG rendering library; equivalent
  minimal native deps for whatever SVG→raster approach the rewrite uses).

### 6.5 Outbound network surface
- All third-party HTTP destinations should be fixed, hardcoded endpoints
  (hamqsl.com, prop.kc2g.com, pota.app) — never construct an outbound
  request's *host* from user input, to avoid SSRF. User input may only
  ever appear as URL-encoded path/query segments against these fixed
  hosts.

### 6.6 Error handling
- Unhandled exceptions in a single command must not crash the process;
  catch at the command-dispatch boundary, log with full detail
  server-side, and return a generic-but-friendly ephemeral error to the
  user without leaking internal exception detail/stack traces to Discord.

## 7. Non-Functional Requirements

- **Multi-guild**: a single running instance serves any number of Discord
  guilds; per-guild state must never leak across guilds.
- **Resilience**: transient upstream HTTP failures (hamqsl.com,
  prop.kc2g.com, pota.app) must degrade to a user-facing error, not a
  crash or hang.
- **Statelessness of process, statefulness of data**: the bot process
  itself should be freely restartable (e.g. by an orchestrator) without
  data loss, because durable state lives only in the persistence layer,
  not in memory (except transient command stats, which are expected to
  reset on restart).
- **Observability**: enough logging to diagnose, per guild and per
  command, what happened without needing to reproduce interactively.
- **Deployability**: runnable directly from source (with a documented
  dependency-install path) and via a container image; both paths take the
  same config file shape.
- **Testability**: core non-Discord-API logic (caching, persistence,
  content-record formatting/validation) should be unit-testable in
  isolation from the Discord gateway connection.

## 8. Explicit Non-Goals / Preserve-As-Is

- No web dashboard or REST API — Discord is the only interface.
- No multi-language/i18n requirement — English only, matching current
  scope.
- No requirement to preserve data compatibility with the existing SQLite
  file format if migrating to a different storage engine, **but** provide
  a one-time migration/export path if the rewrite changes storage engines,
  so existing clubs don't lose their stored `/club` content.
- No requirement to preserve the Python/Pycord-specific extension
  mechanism verbatim — only its *properties* (independent load/failure,
  scoped config, shared embed styling) need to carry over.

## 9. Acceptance Checklist

- [ ] All commands in §3 implemented with matching behavior and copy tone.
- [ ] Web cache: TTL-based, per-URL, supports derived/secondary cached
      values, survives upstream fetch failure without crashing a command.
- [ ] Club content: 10-item/5KB-per-item limits enforced; Markdown + YAML
      both supported with the documented YAML schema; guild isolation
      verified by test.
- [ ] `/manage_club update|get|delete` require Manage-Server-equivalent
      permission, enforced by the platform, not just documented.
- [ ] `/manage_club update` and `/manage_club delete` both require
      explicit confirmation before mutating stored data.
- [ ] Attachment MIME-type and size validated server-side before parsing.
- [ ] All persistence queries parameterized; verified no string-built
      queries exist.
- [ ] YAML parsing uses a safe-only loader.
- [ ] Container runs as non-root; multi-stage build; minimal installed
      packages.
- [ ] Config load failure (missing file, missing required key) causes a
      clear, immediate, non-zero-exit failure — no silent partial startup.
- [ ] Secrets never appear in logs or command responses.
- [ ] Single extension load failure does not prevent other extensions or
      the bot from starting.
- [ ] Command telemetry (received/completed/errored) logged periodically.
