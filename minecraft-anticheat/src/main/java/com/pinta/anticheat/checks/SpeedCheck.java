package com.pinta.anticheat.checks;

import com.pinta.anticheat.PinTaAntiCheatPlugin;
import com.pinta.anticheat.util.PlayerData;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.event.player.PlayerQuitEvent;

public class SpeedCheck implements Listener {
    private final PinTaAntiCheatPlugin plugin;

    public SpeedCheck(PinTaAntiCheatPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(ignoreCancelled = true)
    public void onPlayerMove(PlayerMoveEvent event) {
        Player player = event.getPlayer();
        if (player.isInsideVehicle() || player.isFlying() || player.getAllowFlight()) {
            return;
        }

        Location from = event.getFrom();
        Location to = event.getTo();
        if (to == null) {
            return;
        }

        PlayerData data = plugin.getPlayerData(player);
        long now = System.currentTimeMillis();

        if (data.getLastLocation() == null) {
            data.setLastLocation(from);
            data.setLastMoveTime(now);
            return;
        }

        double distance = from.distance(to);
        long elapsedMs = Math.max(1L, now - data.getLastMoveTime());
        double blocksPerSecond = distance / (elapsedMs / 1000.0);

        if (blocksPerSecond > plugin.getMaxBlocksPerSecond()) {
            flag(player, String.format("Speed %.2f b/s", blocksPerSecond));
            if (plugin.isTeleportBackEnabled()) {
                event.setTo(data.getLastLocation());
            }
        } else {
            data.setLastLocation(to);
            data.setLastMoveTime(now);
        }
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        plugin.removePlayerData(event.getPlayer());
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
