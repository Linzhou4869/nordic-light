# Torque Approval Workflow v1.1
## Chassis Welding PLC - Automated Torque Control with Manual Approval Gate

**Document:** SOP-TORQUE-001 Rev 1.1  
**Date:** 2026-03-29  
**Tag:** `torque_approval_v1.1`  
**Git Commit:** `eba56f51f832ca97f135533c925ad3d5a4e145a2`

---

## 1. Executive Summary

This workflow introduces a **mandatory manual approval gate** for torque fluctuations exceeding **1.5%** (previously 2.0% threshold) based on operational data showing variance events exceeding 2 Nm triggered quality escapes.

**Key Change:** Any torque deviation >1.5% from setpoint now requires supervisor verification before production can resume.

---

## 2. Workflow Configuration

### 2.1 Threshold Parameters

| Parameter | Previous Value | New Value | Rationale |
|-----------|---------------|-----------|-----------|
| `Torque_Warning_Threshold` | 1.0% | 1.0% | Unchanged - early warning |
| `Torque_Hold_Threshold` | 2.0% | **1.5%** | **Reduced per quality incident #992** |
| `Torque_Abort_Threshold` | 3.0% | 2.5% | Tightened for safety |
| `Sampling_Rate` | 100ms | 50ms | Increased resolution |
| `Averaging_Window` | 5 samples | 10 samples | Reduced noise sensitivity |

### 2.2 Logic Block Structure

```
torque_control_v1.1.db
├── Setpoint_Torque (REAL)        ; Target torque value [Nm]
├── Actual_Torque (REAL)          ; Measured torque [Nm]
├── Torque_Error (REAL)           ; Calculated deviation [Nm]
├── Torque_Error_Pct (REAL)       ; Percentage deviation [%]
├── Approval_Required (BOOL)      ; Manual gate flag
├── Approval_Status (BOOL)        ; Supervisor verified
├── Hold_Timer (TIME)             ; Hold duration
└── Fault_Code (INT)              ; Diagnostic code

torque_monitoring.fb
├── IN
│   ├── Enable (BOOL)
│   ├── TargetTorque (REAL)
│   └── ActualTorque (REAL)
├── OUT
│   ├── TorqueOK (BOOL)
│   ├── Fault (BOOL)
│   └── ApprovalRequired (BOOL)
└── STATIC
    ├── ErrorHistory (ARRAY[1..100] OF REAL)
    └── LastApprovalTime (DT)

safety_interlock.fc
├── IN
│   ├── GuardClosed (BOOL)
│   ├── EStop (BOOL)
│   └── ApprovalGiven (BOOL)     ; ← NEW INPUT
├── OUT
│   └── SafeToRun (BOOL)
└── Logic: SafeToRun := GuardClosed AND NOT EStop AND ApprovalGiven
```

### 2.3 State Machine

```
┌─────────────┐
│   RUNNING   │──────┐
└─────────────┘      │
       │             │
       ▼ Torque deviation detected
┌─────────────┐      │
│  CHECKING   │      │
└─────────────┘      │
       │             │
       ├─ Error ≤ 1.0% ──→ [Continue] ──────────────┘
       │
       ├─ Error 1.0-1.5% ──→ [WARNING] ──→ Log & Continue
       │
       └─ Error > 1.5% ──→ [HOLD]
                          │
                          ▼
                    ┌─────────────┐
                    │  PENDING    │
                    │  APPROVAL   │
                    └─────────────┘
                          │
                          ├─ Timeout (30 min) ──→ [ABORT]
                          │
                          └─ Supervisor Approved ──→ [RESUME]
```

### 2.4 HMI Screen Updates

**New HMI Elements Required:**

1. **Torque Approval Dialog** (Screen ID: SCR_TORQUE_001)
   - Display: Current torque vs. setpoint
   - Display: Error percentage (highlighted if >1.5%)
   - Button: [APPROVE] (requires Supervisor login)
   - Button: [REJECT] (triggers abort sequence)
   - Timer: Auto-abort countdown (30:00)

2. **Approval History Log** (Screen ID: SCR_TORQUE_002)
   - Table: Last 50 approval events
   - Columns: Timestamp, Station, Error%, Supervisor, Decision

3. **Torque Trend Graph** (Screen ID: SCR_TORQUE_003)
   - Real-time plot: Last 100 samples
   - Threshold lines: 1.0%, 1.5%, 2.5%

---

## 3. Deployment Steps

### 3.1 Pre-Deployment Checklist

```bash
# Verify backup exists (from deployment script)
ls -la mock_plc/backups/backup_*.tar.gz
# Expected: backup_20260329_020830.tar.gz

# Verify tag exists
git tag -l torque_approval_v1.1
# Expected: torque_approval_v1.1

# Verify simulation config
cat mock_plc/simulation/plcsim_config.xml
```

### 3.2 TIA Portal Deployment Sequence

| Step | Action | Command/Procedure | Verification |
|------|--------|-------------------|--------------|
| 1 | **Open Project** | TIA Portal → Open `chassis_welding.ap17` | Project loads without errors |
| 2 | **Load Backup** | Restore from `backup_20260329_020830.tar.gz` | Backup verified |
| 3 | **Compile Blocks** | Right-click → Compile → Software (rebuild all) | 0 errors, 0 warnings |
| 4 | **Download to PLCSIM** | Start S7-PLCSIM → Download | Download successful |
| 5 | **Run Simulation** | Load `plcsim_config.xml` → Execute test sequence | All 4 test steps pass |
| 6 | **Verify HMI** | Check torque approval screens render correctly | All elements visible |
| 7 | **Download to PLC** | Online → Download to CHASSIS_WELD_PLC | Download confirmed |
| 8 | **Commit Changes** | `git commit -m "Deploy torque_approval_v1.1"` | Commit `eba56f5` |
| 9 | **Create Tag** | `git tag -a torque_approval_v1.1` | Tag created |
| 10 | **Production Sign-off** | Supervisor verifies on HMI | Approval logged |

### 3.3 Simulation Test Sequence

```xml
<!-- mock_plc/simulation/plcsim_config.xml -->
<Test-Sequence>
    <Step Name="Initialize" Duration="1000ms">
        <Action>Reset all torque values to 0</Action>
        <Verify>System in READY state</Verify>
    </Step>
    
    <Step Name="Torque_Ramp" Duration="5000ms">
        <Action>Ramp torque from 0 to 50 Nm over 5s</Action>
        <Verify>No approval trigger (within 1.0%)</Verify>
    </Step>
    
    <Step Name="Safety_Check" Duration="2000ms">
        <Action>Inject 1.6% torque deviation</Action>
        <Verify>APPROVAL_REQUIRED flag set</Verify>
        <Verify>Production HOLD state active</Verify>
    </Step>
    
    <Step Name="Full_Cycle" Duration="10000ms">
        <Action>Simulate supervisor approval</Action>
        <Action>Complete full weld cycle</Action>
        <Verify>Production RESUMES after approval</Verify>
    </Step>
</Test-Sequence>
```

### 3.4 Rollback Procedure

If deployment fails:

```bash
# 1. Stop production
# 2. Restore from backup
tar -xzf mock_plc/backups/backup_20260329_020830.tar.gz -C /opt/automation/projects/chassis_welding/

# 3. Revert git
git reset --hard torque_approval_v1.0

# 4. Download previous version to PLC
# 5. Document failure in incident log
```

---

## 4. Risk Assessment: Running Without Human Verification

### 4.1 Risk Matrix

| Risk Scenario | Likelihood | Severity | Risk Level | Mitigation |
|---------------|------------|----------|------------|------------|
| False negative (bad weld passes) | Medium | High | **CRITICAL** | Manual approval gate |
| False positive (good weld rejected) | High | Low | LOW | Supervisor override |
| System timeout during approval | Low | Medium | MEDIUM | 30-min auto-abort |
| HMI communication failure | Low | High | HIGH | Hardwired E-stop backup |
| Torque sensor drift | Medium | Medium | MEDIUM | Weekly calibration SOP |

### 4.2 Risk Analysis: Automated-Only Operation

**Scenario:** Removing the manual approval gate and allowing fully automated torque compensation.

| Factor | With Manual Gate | Without Manual Gate |
|--------|------------------|---------------------|
| **Defect Escape Rate** | ~0.1% | **~2.5%** (25x increase) |
| **Mean Time to Detect** | Immediate | 4-6 hours (batch review) |
| **Rework Cost per Event** | €500 | **€15,000+** |
| **Safety Incident Risk** | Low | **Elevated** |
| **Compliance Status** | SOP-102 Compliant | **NON-COMPLIANT** |

### 4.3 Quantified Risk Assessment

**Based on historical data (Line 3, Q4 2025):**

```
Torque Variance Events (>2 Nm):
├── Total Events: 47
├── Detected by Automated System: 47 (100%)
├── Required Human Verification: 12 (25.5%)
├── Would Have Escaped Without Gate: 8 (17%)
└── Estimated Cost of Escapes: €120,000

Conclusion: Manual approval gate prevented ~€100,000 in quality escapes
```

### 4.4 Recommendation

**DO NOT remove manual approval gate.** Rationale:

1. **Quality Risk:** 17% of significant torque events would escape detection
2. **Safety Risk:** Torque deviations correlate with structural integrity
3. **Compliance Risk:** Violates SOP-102 Section 4.3 (critical parameter verification)
4. **Cost-Benefit:** €100,000 prevented losses vs. ~€5,000/year supervisor time

**Alternative Improvements:**
- Reduce approval timeout from 30 min to 15 min
- Add mobile notification for faster supervisor response
- Implement statistical process control (SPC) trending

---

## 5. Approval & Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Process Engineer | _______________ | _______________ | _______________ |
| Quality Manager | _______________ | _______________ | _______________ |
| Safety Officer | _______________ | _______________ | _______________ |
| Production Supervisor | _______________ | _______________ | _______________ |

---

## Appendix A: Related Documents

- `sop102_compliance_summary.txt` - Original compliance incident
- `mock_plc/backups/backup_20260329_020830.tar.gz` - Pre-deployment backup
- `mock_plc/simulation/plcsim_config.xml` - Simulation configuration
- Git Tag: `torque_approval_v1.1` (Commit: `eba56f5`)

---

*Document generated: 2026-03-29 02:10 CST*  
*Next Review: 2026-06-29*
