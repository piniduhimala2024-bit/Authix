package com.pinta.anticheat;

import com.pinta.anticheat.checks.FlyCheck;
import com.pinta.anticheat.checks.SpeedCheck;
import com.pinta.anticheat.checks.TotemCheck;
import com.pinta.anticheat.checks.XrayCheck;
import com.pinta.anticheat.util.PlayerData;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.bukkit.ChatColor;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

public class PinTaAntiCheatPlugin extends JavaPlugin {
    private final Map<UUID, PlayerData> playerData = new ConcurrentHashMap<>();
    private String prefix;
    private String madeBy;

    @Override
    public void onEnable() {
        saveDefaultConfig();
        loadBranding();

        getServer().getPluginManager().registerEvents(new SpeedCheck(this), this);
        getServer().getPluginManager().registerEvents(new FlyCheck(this), this);
        getServer().getPluginManager().registerEvents(new XrayCheck(this), this);
        getServer().getPluginManager().registerEvents(new TotemCheck(this), this);

        getLogger().info(prefix + " Anti-cheat enabled. " + madeBy);
    }

    @Override
    public void onDisable() {
        playerData.clear();
    }

    public PlayerData getPlayerData(Player player) {
        return playerData.computeIfAbsent(player.getUniqueId(), id -> new PlayerData());
    }

    public void removePlayerData(Player player) {
        playerData.remove(player.getUniqueId());
    }

    public double getMaxBlocksPerSecond() {
        return getConfig().getDouble("speed.maxBlocksPerSecond", 9.0);
    }

    public int getMaxAirTicks() {
        return getConfig().getInt("fly.maxAirTicks", 40);
    }

    public boolean isTeleportBackEnabled() {
        return getConfig().getBoolean("actions.teleportBack", true);
    }

    public boolean isNotifyEnabled() {
        return getConfig().getBoolean("actions.notify", true);
    }

    public int getXrayWindowSeconds() {
        return getConfig().getInt("xray.windowSeconds", 300);
    }

    public int getXrayMinOreCount() {
        return getConfig().getInt("xray.minOreCount", 8);
    }

    public double getXrayHiddenRatio() {
        return getConfig().getDouble("xray.hiddenRatio", 0.7);
    }

    public int getXrayMaxExposedFaces() {
        return getConfig().getInt("xray.maxExposedFaces", 1);
    }

    public long getTotemSwapThresholdMs() {
        return getConfig().getLong("totem.swapThresholdMs", 150);
    }

    public long getTotemInventoryGraceMs() {
        return getConfig().getLong("totem.inventoryGraceMs", 1500);
    }

    public String getPrefix() {
        return prefix;
    }

    private void loadBranding() {
        this.prefix = colorize(getConfig().getString("branding.prefix", "&6[PinTaAC]&r"));
        this.madeBy = colorize(getConfig().getString("branding.madeBy", "Made By PinTa Tag"));
    }

    public String colorize(String message) {
        return ChatColor.translateAlternateColorCodes('&', message);
    }
}
