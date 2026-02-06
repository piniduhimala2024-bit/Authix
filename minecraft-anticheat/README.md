# PinTa AntiCheat

Lightweight Spigot plugin that provides basic speed and fly checks.

**Made By PinTa Tag**

## Build

```bash
mvn -f minecraft-anticheat/pom.xml package
```

The compiled JAR will be located at:

```
minecraft-anticheat/target/pinta-anti-cheat-1.0.0.jar
```

### Step-by-step: create the JAR

1. **Install Java 17 (JDK)** and ensure `java -version` shows 17.
2. **Install Maven** and ensure `mvn -v` works.
3. **Open a terminal** in the repository root (the folder containing `minecraft-anticheat/`).
4. **Run the build**:
   ```bash
   mvn -f minecraft-anticheat/pom.xml clean package
   ```
5. **Find your JAR** at:
   ```
   minecraft-anticheat/target/pinta-anti-cheat-1.0.0.jar
   ```

## Install

### Step-by-step setup

1. **Build the plugin JAR** (or download it if you already have one).
   ```bash
   mvn -f minecraft-anticheat/pom.xml package
   ```
2. **Copy the JAR** to your server's `plugins/` folder.
   ```text
   minecraft-anticheat/target/pinta-anti-cheat-1.0.0.jar
   ```
3. **Start or restart** your server so the plugin loads and generates `config.yml`.
4. **Tune the settings** in `plugins/PinTaAntiCheat/config.yml` to match your server.
5. **Give staff the alert permission** so they receive flags:
   - `pinta.anticheat.alerts`

## Permissions

- `pinta.anticheat.alerts` — receive anti-cheat alerts (default: op)

## How it works

The plugin listens for player movement and applies two lightweight checks:

1. **Speed check**  
   Tracks how fast a player moves between positions. If their blocks-per-second exceeds
   `speed.maxBlocksPerSecond`, the player is flagged and (optionally) teleported back.

2. **Fly/air-time check**  
   Counts how long a player stays off the ground without flight permissions. If their
   air time exceeds `fly.maxAirTicks`, the player is flagged and (optionally) teleported back.

When a player is flagged, staff with the `pinta.anticheat.alerts` permission receive a chat
alert, and the event is logged to the server console.

Additional checks:

3. **X-ray heuristic**  
   Tracks the ratio of hidden ore breaks (ores with few exposed faces) over time. If the
   ratio exceeds `xray.hiddenRatio` once at least `xray.minOreCount` ores are mined within
   `xray.windowSeconds`, the player is flagged. This is a heuristic and can false-positive
   in dense mining areas.

4. **Auto-totem heuristic**  
   Flags when a totem is popped immediately after an offhand refill without a recent
   inventory open event. Tune `totem.swapThresholdMs` and `totem.inventoryGraceMs` to fit
   your server's latency and play style.

## Notes about ESP and client visuals

ESP/X-ray style visual cheats are mostly client-side. This plugin uses **server-side
heuristics** (like hidden ore ratios) and cannot guarantee perfect detection of ESP.
