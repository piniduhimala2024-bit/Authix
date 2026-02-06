package com.pinta.anticheat.checks;

import com.pinta.anticheat.PinTaAntiCheatPlugin;
import com.pinta.anticheat.util.PlayerData;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerMoveEvent;

public class FlyCheck implements Listener {
    private final PinTaAntiCheatPlugin plugin;

    public FlyCheck(PinTaAntiCheatPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(ignoreCancelled = true)
    public void onPlayerMove(PlayerMoveEvent event) {
        Player player = event.getPlayer();
        if (player.isFlying() || player.getAllowFlight() || player.isInsideVehicle()) {
            return;
        }

        Location to = event.getTo();
        if (to == null) {
            return;
        }

        PlayerData data = plugin.getPlayerData(player);
        if (player.isOnGround()) {
            data.setAirTicks(0);
            data.setLastGroundLocation(to);
            return;
        }

        data.incrementAirTicks();
        if (data.getAirTicks() > plugin.getMaxAirTicks()) {
            flag(player, "Fly/air time exceeded");
            if (plugin.isTeleportBackEnabled() && data.getLastGroundLocation() != null) {
                event.setTo(data.getLastGroundLocation());
            }
        }
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
