package com.pinta.anticheat.checks;

import com.pinta.anticheat.PinTaAntiCheatPlugin;
import com.pinta.anticheat.util.PlayerData;
import java.util.EnumSet;
import java.util.Set;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.player.PlayerQuitEvent;

public class XrayCheck implements Listener {
    private static final Set<Material> WATCHED_ORES = EnumSet.of(
        Material.DIAMOND_ORE,
        Material.DEEPSLATE_DIAMOND_ORE,
        Material.ANCIENT_DEBRIS,
        Material.EMERALD_ORE,
        Material.DEEPSLATE_EMERALD_ORE
    );

    private final PinTaAntiCheatPlugin plugin;

    public XrayCheck(PinTaAntiCheatPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        Player player = event.getPlayer();
        Block block = event.getBlock();
        if (!WATCHED_ORES.contains(block.getType())) {
            return;
        }

        PlayerData data = plugin.getPlayerData(player);
        long now = System.currentTimeMillis();
        if (data.getXrayWindowStart() == 0L
            || now - data.getXrayWindowStart() > plugin.getXrayWindowSeconds() * 1000L) {
            data.resetXrayWindow(now);
        }

        data.incrementXrayOreCount();
        if (countExposedFaces(block) <= plugin.getXrayMaxExposedFaces()) {
            data.incrementXrayHiddenOreCount();
        }

        int total = data.getXrayOreCount();
        if (total < plugin.getXrayMinOreCount()) {
            return;
        }

        double ratio = data.getXrayHiddenOreCount() / (double) total;
        if (ratio >= plugin.getXrayHiddenRatio()) {
            flag(player, String.format("Xray pattern: %d ores (%.0f%% hidden)",
                total, ratio * 100));
            data.resetXrayWindow(now);
        }
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        plugin.removePlayerData(event.getPlayer());
    }

    private int countExposedFaces(Block block) {
        int exposed = 0;
        for (org.bukkit.block.BlockFace face : org.bukkit.block.BlockFace.values()) {
            if (!face.isCartesian()) {
                continue;
            }
            Material neighbor = block.getRelative(face).getType();
            if (neighbor == Material.AIR || neighbor == Material.CAVE_AIR) {
                exposed++;
            }
        }
        return exposed;
    }

    private void flag(Player player, String reason) {
        if (!plugin.isNotifyEnabled()) {
            return;
        }
        String message = plugin.getPrefix() + " " + player.getName() + " flagged: " + reason;
        player.getServer().getOnlinePlayers().stream()
            .filter(target -> target.hasPermission("pinta.anticheat.alerts"))
            .forEach(target -> target.sendMessage(message));
        plugin.getLogger().warning(message);
    }
}
