# Nordic Light Gallery - BrightSign Deployment Checklist

## 📋 Pre-Deployment Verification

### Hardware Checklist
- [ ] **BrightSign XD133** (Main Lobby) - Unboxed and inspected
  - [ ] Power adapter connected
  - [ ] HDMI cable connected to display
  - [ ] Ethernet cable connected (or WiFi configured)
  - [ ] Serial number recorded: _______________
  
- [ ] **BrightSign HD102** (Secondary Corridor) - Unboxed and inspected
  - [ ] Power adapter connected
  - [ ] HDMI cable connected to display (portrait orientation)
  - [ ] Ethernet cable connected (or WiFi configured)
  - [ ] Serial number recorded: _______________

### Network Configuration
- [ ] Both devices on same network segment (192.168.1.x)
- [ ] Static IPs assigned (recommended):
  - [ ] Lobby XD133: `192.168.1.100`
  - [ ] Corridor HD102: `192.168.1.101`
- [ ] NTP server accessible: `pool.ntp.org`
- [ ] Firewall rules allow UDP port 8080 (sync traffic)
- [ ] Multicast enabled: `239.255.0.1:8080`

---

## 📦 Package Installation

### Step 1: Prepare BrightSign Devices
- [ ] Update firmware to v9.2.20 or later on both devices
  - Download: https://www.brightsign.biz/support/firmware/
  - XD133 firmware: _______________
  - HD102 firmware: _______________

- [ ] Factory reset both devices (if previously used)
  - [ ] XD133 reset complete
  - [ ] HD102 reset complete

### Step 2: Deploy Package via BrightSign Network
- [ ] Log into BrightSign Network: https://network.brightsign.biz/
- [ ] Create new group: "Nordic Light Gallery"
- [ ] Add both devices to group using serial numbers
- [ ] Upload `nordic_light_sync.bspkg` package
- [ ] Assign package to group
- [ ] Deploy to both devices

### Step 3: Alternative - Local Deployment (USB)
- [ ] Format USB drive as FAT32
- [ ] Copy `nordic_light_sync.bspkg` to USB root
- [ ] Insert USB into XD133 (lobby) - auto-install
- [ ] Insert USB into HD102 (corridor) - auto-install
- [ ] Remove USB after installation complete

---

## ⚙️ Configuration

### Master Device (XD133 - Lobby)
- [ ] Edit `master_config.json`:
  - [ ] Update `DeviceId` with actual serial number
  - [ ] Verify network settings match local network
  - [ ] Confirm playlist paths are correct

### Slave Device (HD102 - Corridor)
- [ ] Edit `slave_config.json`:
  - [ ] Update `DeviceId` with actual serial number
  - [ ] Set `MasterIPAddress` to XD133's IP (default: 192.168.1.100)
  - [ ] Verify network settings match local network

---

## 🧪 Testing & Validation

### Individual Device Testing
- [ ] **XD133 (Lobby) - Power On**
  - [ ] Device boots successfully
  - [ ] Network connected (green LED)
  - [ ] Display shows welcome loop
  - [ ] Audio playing (if enabled)
  - [ ] Logs accessible at `/logs/master_sync.log`

- [ ] **HD102 (Corridor) - Power On**
  - [ ] Device boots successfully
  - [ ] Network connected (green LED)
  - [ ] Display shows welcome loop (portrait)
  - [ ] No audio (slave mode)
  - [ ] Logs accessible at `/logs/slave_sync.log`

### Synchronization Testing
- [ ] **Frame Lock Verification**
  - [ ] Both displays show same video frame simultaneously
  - [ ] No visible drift between displays
  - [ ] Transition points are synchronized

- [ ] **Sync Stability Test** (run for 30 minutes)
  - [ ] No sync dropouts observed
  - [ ] Slave maintains lock with master
  - [ ] Logs show consistent sync pulses

- [ ] **Recovery Test**
  - [ ] Disconnect slave network cable
  - [ ] Wait 10 seconds
  - [ ] Reconnect cable
  - [ ] Slave re-synchronizes automatically within 30 seconds

### Schedule Testing
- [ ] Verify schedule activation at 09:00
- [ ] Verify schedule deactivation at 18:00
- [ ] Confirm timezone is Europe/Copenhagen

---

## ✅ Final Verification

### Visual Inspection
- [ ] Both displays showing identical content
- [ ] No stuttering or frame drops
- [ ] Correct orientation (landscape lobby, portrait corridor)
- [ ] Volume levels appropriate (lobby only)

### Documentation
- [ ] Serial numbers recorded in asset registry
- [ ] IP addresses documented
- [ ] Configuration files backed up
- [ ] Deployment date logged: _______________
- [ ] Technician name: _______________

### Handoff
- [ ] Museum staff trained on basic operation
- [ ] Emergency contact info provided
- [ ] Maintenance schedule established
- [ ] Issue escalation process documented

---

## 🆘 Troubleshooting

### Common Issues

**Slave not syncing with master:**
1. Verify both devices on same network segment
2. Check firewall allows UDP 8080
3. Confirm MasterIPAddress in slave_config.json is correct
4. Restart both devices (master first, then slave)

**Frame drift observed:**
1. Check network latency (<10ms recommended)
2. Verify NTP sync on both devices
3. Reduce SyncIntervalMs if needed (default: 1000ms)
4. Check for network congestion

**Display not showing content:**
1. Verify HDMI connection and display input source
2. Check display power and brightness settings
3. Review device logs for errors
4. Try factory reset and redeploy

**Audio issues:**
1. Verify audio output enabled in master_config.json
2. Check display/external speaker volume
3. Confirm audio codec compatibility (AAC recommended)

---

## 📞 Support Contacts

- **BrightSign Support:** https://www.brightsign.biz/support/
- **Museum AV Team Lead:** _______________
- **IT Network Contact:** _______________
- **Emergency After-Hours:** _______________

---

**Package Version:** 1.0.0  
**Deployment Date:** 2026-03-29  
**PR Reference:** https://github.com/Linzhou4869/nordic-light/pull/1
