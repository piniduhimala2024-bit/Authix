package com.pinta.anticheat.checks;

import com.pinta.anticheat.PinTaAntiCheatPlugin;
import com.pinta.anticheat.util.PlayerData;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityResurrectEvent;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryOpenEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.inventory.ItemStack;

public class TotemCheck implements Listener {
    private final PinTaAntiCheatPlugin plugin;

    public TotemCheck(PinTaAntiCheatPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(ignoreCancelled = true)
    public void onInventoryOpen(InventoryOpenEvent event) {
        if (event.getPlayer() instanceof Player player) {
            plugin.getPlayerData(player).setLastInventoryOpen(System.currentTimeMillis());
        }
    }

    @EventHandler(ignoreCancelled = true)
    public void onInventoryClick(InventoryClickEvent event) {
        if (!(event.getWhoClicked() instanceof Player player)) {
            return;
        }
        if (event.getSlot() != 40) {
            return;
        }
        ItemStack cursor = event.getCursor();
        ItemStack current = event.getCurrentItem();
        if (isTotem(cursor) || isTotem(current)) {
            plugin.getPlayerData(player).setLastOffhandTotemSwap(System.currentTimeMillis());
        }
    }

    @EventHandler(ignoreCancelled = true)
    public void onTotemPop(EntityResurrectEvent event) {
        if (!(event.getEntity() instanceof Player player)) {
            return;
        }
        PlayerData data = plugin.getPlayerData(player);
        long now = System.currentTimeMillis();
        long sinceSwap = now - data.getLastOffhandTotemSwap();
        long sinceInventory = now - data.getLastInventoryOpen();
        if (sinceSwap <= plugin.getTotemSwapThresholdMs()
            && sinceInventory > plugin.getTotemInventoryGraceMs()) {
            flag(player, "Auto-totem suspected (instant offhand refill)");
        }
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        plugin.removePlayerData(event.getPlayer());
    }

    private boolean isTotem(ItemStack itemStack) {
        return itemStack != null && itemStack.getType() == Material.TOTEM_OF_UNDYING;
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
