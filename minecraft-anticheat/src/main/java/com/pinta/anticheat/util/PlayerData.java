package com.pinta.anticheat.util;

import org.bukkit.Location;

public class PlayerData {
    private Location lastLocation;
    private long lastMoveTime;
    private int airTicks;
    private Location lastGroundLocation;
    private int xrayOreCount;
    private int xrayHiddenOreCount;
    private long xrayWindowStart;
    private long lastOffhandTotemSwap;
    private long lastInventoryOpen;

    public Location getLastLocation() {
        return lastLocation;
    }

    public void setLastLocation(Location lastLocation) {
        this.lastLocation = lastLocation;
    }

    public long getLastMoveTime() {
        return lastMoveTime;
    }

    public void setLastMoveTime(long lastMoveTime) {
        this.lastMoveTime = lastMoveTime;
    }

    public int getAirTicks() {
        return airTicks;
    }

    public void setAirTicks(int airTicks) {
        this.airTicks = airTicks;
    }

    public void incrementAirTicks() {
        this.airTicks++;
    }

    public Location getLastGroundLocation() {
        return lastGroundLocation;
    }

    public void setLastGroundLocation(Location lastGroundLocation) {
        this.lastGroundLocation = lastGroundLocation;
    }

    public int getXrayOreCount() {
        return xrayOreCount;
    }

    public void incrementXrayOreCount() {
        this.xrayOreCount++;
    }

    public int getXrayHiddenOreCount() {
        return xrayHiddenOreCount;
    }

    public void incrementXrayHiddenOreCount() {
        this.xrayHiddenOreCount++;
    }

    public long getXrayWindowStart() {
        return xrayWindowStart;
    }

    public void setXrayWindowStart(long xrayWindowStart) {
        this.xrayWindowStart = xrayWindowStart;
    }

    public void resetXrayWindow(long now) {
        this.xrayWindowStart = now;
        this.xrayOreCount = 0;
        this.xrayHiddenOreCount = 0;
    }

    public long getLastOffhandTotemSwap() {
        return lastOffhandTotemSwap;
    }

    public void setLastOffhandTotemSwap(long lastOffhandTotemSwap) {
        this.lastOffhandTotemSwap = lastOffhandTotemSwap;
    }

    public long getLastInventoryOpen() {
        return lastInventoryOpen;
    }

    public void setLastInventoryOpen(long lastInventoryOpen) {
        this.lastInventoryOpen = lastInventoryOpen;
    }
}
