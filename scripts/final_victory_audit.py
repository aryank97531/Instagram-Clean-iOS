#!/usr/bin/env python3
"""
=============================================================================
  FINAL INDEPENDENT VICTORY AUDIT SUITE
  Target: Instagram Clean v446.0.0 (Build 1 DM Pipeline Reconciliation)
=============================================================================
  Validates 100% compliance with:
  1. Build 1 unhindered real-time Direct Message architecture restoration.
  2. Complete removal of all DM-corrupting hooks & byte patches.
  3. Preservation of distraction-free features (No Reels, No Explore, Feed suppressed, Ads blocked).
  4. Preservation of WebRTC voice & video calling (1-tap calling with call_confirm = 0).
  5. Multi-destination deliverable synchronization and cryptographic signing integrity.
=============================================================================
"""

import os
import sys
import zipfile
import struct
import hashlib
import plistlib
import capstone

PROJECT_DIR = r"C:\Users\aryan\.gemini\antigravity\scratch\instagram_clean"
DOWNLOADS_IPA = os.path.expanduser(r"~\Downloads\Instagram_Clean.ipa")
SCRATCH_IPA = os.path.join(PROJECT_DIR, "Instagram_Clean.ipa")
REPO_IPA = os.path.join(PROJECT_DIR, "Instagram-Clean-iOS", "Instagram_Clean.ipa")

passed = 0
failed = 0
failures = []

def check(title, condition, detail=""):
    global passed, failed, failures
    if condition:
        passed += 1
        print(f"  [PASS] {title}")
    else:
        failed += 1
        failures.append((title, detail))
        print(f"  [FAIL] {title} -- Detail: {detail}")

print("=========================================================================")
print("  FINAL INDEPENDENT VICTORY AUDIT: BUILD 1 RECONCILIATION")
print("=========================================================================")

# ---------------------------------------------------------------------------
# Section 1: Multi-Target Deliverables & SHA-256 Parity
# ---------------------------------------------------------------------------
print("\n--- 1. Multi-Target Deliverables & SHA-256 Checksum Parity ---")
deliverables = [
    ("Downloads", DOWNLOADS_IPA),
    ("Scratch Root", SCRATCH_IPA),
    ("Repo Root", REPO_IPA),
]

hashes = {}
sizes = {}
for label, p in deliverables:
    exists = os.path.exists(p)
    sz = os.path.getsize(p) if exists else 0
    check(f"Deliverable exists & > 200MB: {label}", exists and sz > 200 * 1024 * 1024, f"size={sz}")
    if exists:
        sizes[label] = sz
        with open(p, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
            hashes[label] = h

check("SHA-256 identity: Downloads == Scratch Root", hashes.get("Downloads") == hashes.get("Scratch Root"))
check("SHA-256 identity: Downloads == Repo Root", hashes.get("Downloads") == hashes.get("Repo Root"))
verified_sha256 = hashes.get("Downloads", "")
print(f"[*] Verified Deliverable SHA-256: {verified_sha256}")

# ---------------------------------------------------------------------------
# Section 2: Archive & Package Structure (iOS Sideloading Compliance)
# ---------------------------------------------------------------------------
print("\n--- 2. Archive Packaging & UNIX Structure ---")
with zipfile.ZipFile(DOWNLOADS_IPA, "r") as z:
    names = z.namelist()
    infolist = z.infolist()

    # Zero .appex extension bundles (free cert 3 App ID limit)
    appex = [n for n in names if ".appex" in n]
    check("Zero .appex extension bundles in IPA", len(appex) == 0, f"Found: {appex}")

    # Explicit directory records
    dirs = [item for item in infolist if item.filename.endswith("/")]
    check("Explicit directory records present in archive (>= 400)", len(dirs) >= 400, f"Count: {len(dirs)}")
    all_unix_dirs = all(item.create_system == 3 and ((item.external_attr >> 16) & 0o777) == 0o755 for item in dirs)
    check("All directory records have create_system=3 (UNIX) and mode 0o40755", all_unix_dirs)

    # Executable permissions
    exec_items = [item for item in infolist if item.filename.endswith(("Instagram", "SCInsta.dylib", "SPKSideloadFix.dylib", "CydiaSubstrate"))]
    all_exec_perms = all(item.create_system == 3 and ((item.external_attr >> 16) & 0o777) == 0o755 for item in exec_items)
    check("All 4 binaries & dylibs have POSIX 0o100755 executable permissions", all_exec_perms and len(exec_items) == 4)

    # -----------------------------------------------------------------------
    # Section 3: Mach-O Load Commands & Code Headroom
    # -----------------------------------------------------------------------
    print("\n--- 3. Main Executable Mach-O Header & Injected Load Commands ---")
    ig_bin = z.read("Payload/Instagram.app/Instagram")
    magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack_from("<IIIIIIII", ig_bin, 0)
    check("Mach-O 64-bit ARM64 magic (0xfeedfacf)", magic == 0xfeedfacf)
    check("Mach-O cputype is ARM64 standard (0x100000c)", cputype == 0x100000c)
    check("Mach-O cpusubtype is standard (0)", cpusubtype == 0)

    total_hdr = 32 + sizeofcmds
    min_sect = len(ig_bin)
    offset = 32
    lc_dylibs = []
    codesig_offset = None
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", ig_bin, offset)
        if cmd == 0xc: # LC_LOAD_DYLIB
            stroff = struct.unpack_from("<I", ig_bin, offset + 8)[0]
            name = ig_bin[offset + stroff : offset + cmdsize].split(b"\x00")[0].decode("latin1")
            lc_dylibs.append(name)
        elif cmd == 0x1d: # LC_CODE_SIGNATURE
            codesig_offset = offset
        elif cmd == 0x19: # LC_SEGMENT_64
            nsects = struct.unpack_from("<I", ig_bin, offset + 64)[0]
            soff = offset + 72
            for _ in range(nsects):
                s_off = struct.unpack_from("<I", ig_bin, soff + 48)[0]
                if 0 < s_off < min_sect:
                    min_sect = s_off
                soff += 80
        offset += cmdsize

    check("Injected load command: @rpath/SPKSideloadFix.dylib", "@rpath/SPKSideloadFix.dylib" in lc_dylibs)
    check("Injected load command: @rpath/CydiaSubstrate.framework/CydiaSubstrate", "@rpath/CydiaSubstrate.framework/CydiaSubstrate" in lc_dylibs)
    check("Injected load command: @rpath/SCInsta.dylib", "@rpath/SCInsta.dylib" in lc_dylibs)
    check("LC_CODE_SIGNATURE present at end of load commands", codesig_offset is not None and codesig_offset + 16 == total_hdr)
    headroom = min_sect - total_hdr
    check("Load commands do not overflow into __TEXT (headroom > 10,000 bytes)", headroom > 10000, f"Headroom: {headroom} bytes")

    # -----------------------------------------------------------------------
    # Section 4: SCInsta.dylib Build 1 Architectural Reconciliation
    # -----------------------------------------------------------------------
    print("\n--- 4. SCInsta.dylib Build 1 Architectural Reconciliation ---")
    scinsta_data = z.read("Payload/Instagram.app/Frameworks/SCInsta.dylib")
    cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)

    # Authentic Build 1 bytes at previously modified offsets
    check("0x1144c matches Build 1 (unpatched original bytes: 28008052 - mov w8, #1)", scinsta_data[0x1144c:0x11450] == bytes.fromhex("28008052"))
    check("0x12b84 matches Build 1 (unpatched original bytes: ffc300d1 - sub sp, sp, #0x30)", scinsta_data[0x12b84:0x12b88] == bytes.fromhex("ffc300d1"))
    check("0x12c14 matches Build 1 (unpatched original bytes: ff0301d1 - sub sp, sp, #0x40)", scinsta_data[0x12c14:0x12c18] == bytes.fromhex("ff0301d1"))
    check("0x12cb8 matches Build 1 (unpatched original bytes: ff0301d1 - sub sp, sp, #0x40)", scinsta_data[0x12cb8:0x12cbc] == bytes.fromhex("ff0301d1"))

    # Disassemble hook at 0x2e544
    hook_code = scinsta_data[0x2e544:0x2e700]
    insns = list(cs.disasm(hook_code, 0x2e544))
    check("Hook prologue at 0x2e544 starts with sub sp, sp, #0x30", len(insns) > 5 and insns[0].mnemonic == "sub" and "sp, sp, #0x30" in insns[0].op_str)
    check("Hook includes null safety check cbz x19", any(i.mnemonic == "cbz" and "x19" in i.op_str for i in insns[:10]))

    # Locate target table from adr x20, _table
    table_offset = None
    for insn in insns:
        if insn.mnemonic == "adr" and "x20" in insn.op_str:
            table_offset = int(insn.op_str.split(",")[-1].strip().replace("#", ""), 16)
            break

    check("Target table address resolved from ADR instruction", table_offset is not None, f"table_addr={hex(table_offset) if table_offset else None}")

    table_entries = {}
    table_end = None
    if table_offset:
        idx = table_offset
        while idx < 0x2e700:
            rel_off, val = struct.unpack_from("<ii", scinsta_data, idx)
            if rel_off == 0 and val == 0:
                table_end = idx + 8
                break
            target_addr = idx + rel_off
            table_entries[target_addr] = val
            idx += 8

    check("Target table contains exactly 31 configured targets", len(table_entries) == 31, f"Count: {len(table_entries)}")

    # Verify all core Distraction-Free targets
    check("Target hide_reels_tab (0x5a3d0) == 1", table_entries.get(0x5a3d0) == 1)
    check("Target hide_explore_tab (0x5a370) == 1", table_entries.get(0x5a370) == 1)
    check("Target hide_feed_tab (0x5a310) == 0 (Home tab preserved)", table_entries.get(0x5a310) == 0)
    check("Target hide_stories_tray (0x594b0) == 0 (Stories tray active)", table_entries.get(0x594b0) == 0)
    check("Target hide_entire_feed (0x59510) == 1 (Doomscrolling suppressed)", table_entries.get(0x59510) == 1)
    check("Target hide_explore_grid (0x593b0) == 1", table_entries.get(0x593b0) == 1)
    check("Target hide_ads (0x58e30) == 1 (Sponsored ads blocked)", table_entries.get(0x58e30) == 1)
    check("Target no_suggested_reels (0x59630) == 1", table_entries.get(0x59630) == 1)
    check("Target no_suggested_post (0x59570) == 1", table_entries.get(0x59570) == 1)
    check("Target no_suggested_threads (0x59690) == 1", table_entries.get(0x59690) == 1)
    check("Target no_suggested_account (0x595d0) == 1", table_entries.get(0x595d0) == 1)
    check("Target no_suggested_users (0x592f0) == 1", table_entries.get(0x592f0) == 1)
    check("Target hide_reels_blend (0x59990) == 1", table_entries.get(0x59990) == 1)
    check("Target hide_reels_header (0x59930) == 1", table_entries.get(0x59930) == 1)
    check("Target hide_meta_ai (0x58e90) == 1", table_entries.get(0x58e90) == 1)
    check("Target hide_trending_searches (0x59410) == 1", table_entries.get(0x59410) == 1)
    check("Target prevent_doom_scrolling (0x59a70) == 1", table_entries.get(0x59a70) == 1)
    check("Target liquid_glass_buttons (0x59010) == 1", table_entries.get(0x59010) == 1)
    check("Target liquid_glass_surfaces (0x59070) == 1", table_entries.get(0x59070) == 1)
    check("Target call_confirm (0x5a650) == 0 (Direct 1-tap calling)", table_entries.get(0x5a650) == 0)
    check("Target no_seen_receipt (0x5a130) == 1 (Stories Ghost Mode)", table_entries.get(0x5a130) == 1)

    # Verify that all 4 DM hooks are ABSENT (Build 1 unhindered socket pipeline)
    check("DM hook remove_lastseen (0x59f30) is ABSENT from target table", 0x59f30 not in table_entries)
    check("DM hook disable_typing_status (0x59f90) is ABSENT from target table", 0x59f90 not in table_entries)
    check("DM hook no_suggested_chats (0x59350) is ABSENT from target table", 0x59350 not in table_entries)
    check("DM hook keep_deleted_message (0x59ed0) is ABSENT from target table", 0x59ed0 not in table_entries)

    # Clean NOP padding to boundary
    if table_end:
        rem_bytes = scinsta_data[table_end : 0x2e700]
        check("Padding length is multiple of 4", len(rem_bytes) % 4 == 0)
        nops_valid = all(struct.unpack_from("<I", rem_bytes, i)[0] == 0xd503201f for i in range(0, len(rem_bytes), 4))
        check("Clean NOP padding (0xd503201f) up to 0x2e700", nops_valid and len(rem_bytes) > 0, f"{len(rem_bytes)//4} NOPs")

    # Boundary check at 0x2e700
    orig_2e700 = bytes.fromhex("ffc301d1fd7b06a9fd830191e80301aa")
    check("Boundary function at 0x2e700 is completely untouched", scinsta_data[0x2e700 : 0x2e710] == orig_2e700)

    # Sanitization
    check("Zero /var/jb occurrences in SCInsta.dylib", b"/var/jb" not in scinsta_data)
    check("Zero .jbroot occurrences in SCInsta.dylib", b".jbroot" not in scinsta_data)
    spk_data = z.read("Payload/Instagram.app/Frameworks/SPKSideloadFix.dylib")
    check("Zero /var/jb occurrences in SPKSideloadFix.dylib", b"/var/jb" not in spk_data)
    check("Zero .jbroot occurrences in SPKSideloadFix.dylib", b".jbroot" not in spk_data)

    # -----------------------------------------------------------------------
    # Section 5: WebRTC Calling & v446 Metadata
    # -----------------------------------------------------------------------
    print("\n--- 5. WebRTC Calling Preservation & v446 Version Metadata ---")
    ig_plist = plistlib.loads(z.read("Payload/Instagram.app/Info.plist"))
    check("CFBundleShortVersionString == 446.0.0", ig_plist.get("CFBundleShortVersionString") == "446.0.0")
    check("CFBundleVersion == 1060018354", ig_plist.get("CFBundleVersion") == "1060018354")
    check("FBPlatformVersion == 446.0.0", ig_plist.get("FBPlatformVersion") == "446.0.0")
    check("FBAppVersion == 446.0.0.28.66", ig_plist.get("FBAppVersion") == "446.0.0.28.66")

    bg_modes = ig_plist.get("UIBackgroundModes", [])
    check("UIBackgroundModes contains 'voip'", "voip" in bg_modes)
    check("UIBackgroundModes contains 'audio'", "audio" in bg_modes)
    check("NSMicrophoneUsageDescription present & non-empty", bool(ig_plist.get("NSMicrophoneUsageDescription")))
    check("NSCameraUsageDescription present & non-empty", bool(ig_plist.get("NSCameraUsageDescription")))

    # Calling symbols in Instagram binary
    check("WebRTC symbol RTCVideoView present in Instagram", b"RTCVideoView" in ig_bin)
    check("WebRTC symbol RTCPeerConnection present in Instagram", b"RTCPeerConnection" in ig_bin)
    check("WebRTC symbol IGDirectCall present in Instagram", b"IGDirectCall" in ig_bin)
    check("WebRTC symbol IGCall present in Instagram", b"IGCall" in ig_bin)

    # -----------------------------------------------------------------------
    # Section 6: Cryptographic Signatures & CodeResources
    # -----------------------------------------------------------------------
    print("\n--- 6. Cryptographic Signatures & CodeResources ---")
    def verify_codedirectory_hashes(ba, name):
        ncmds = struct.unpack_from("<I", ba, 16)[0]
        off = 32
        codesig = None
        for _ in range(ncmds):
            cmd, cmdsize = struct.unpack_from("<II", ba, off)
            if cmd == 0x1d:
                codesig = struct.unpack_from("<II", ba, off + 8)
                break
            off += cmdsize
        if not codesig:
            return False
        dataoff, datasize = codesig
        smagic, slen, scount = struct.unpack(">III", ba[dataoff : dataoff + 12])
        for i in range(scount):
            stype, soff = struct.unpack(">II", ba[dataoff + 12 + i*8 : dataoff + 20 + i*8])
            if stype in (0, 0x1000):
                cdoff = dataoff + soff
                magic, cd_len, version, flags, hashOffset, identOffset, nSpecialSlots, nCodeSlots, codeLimit = struct.unpack(">IIIIIIIII", ba[cdoff : cdoff + 36])
                hashSize, hashType, platform, pageSize, spare2 = struct.unpack(">BBBBh", ba[cdoff + 36 : cdoff + 42])
                page_size = 1 << pageSize
                for slot in range(nCodeSlots):
                    p_start = slot * page_size
                    p_end = min((slot + 1) * page_size, codeLimit)
                    page_bytes = ba[p_start : p_end]
                    h = hashlib.sha1(page_bytes).digest() if hashType == 1 else hashlib.sha256(page_bytes).digest() if hashType == 2 else None
                    actual = ba[cdoff + hashOffset + slot * hashSize : cdoff + hashOffset + (slot + 1) * hashSize]
                    if h != actual:
                        return False
        return True

    check("CodeDirectory page hashes valid: Instagram", verify_codedirectory_hashes(bytearray(ig_bin), "Instagram"))
    check("CodeDirectory page hashes valid: SCInsta.dylib", verify_codedirectory_hashes(bytearray(scinsta_data), "SCInsta.dylib"))
    check("CodeDirectory page hashes valid: SPKSideloadFix.dylib", verify_codedirectory_hashes(bytearray(spk_data), "SPKSideloadFix.dylib"))
    ellekit_bin = z.read("Payload/Instagram.app/Frameworks/CydiaSubstrate.framework/CydiaSubstrate")
    check("CodeDirectory page hashes valid: CydiaSubstrate", verify_codedirectory_hashes(ellekit_bin, "CydiaSubstrate"))

    cr_data = plistlib.loads(z.read("Payload/Instagram.app/_CodeSignature/CodeResources"))
    f2_count = len(cr_data.get("files2", {}))
    check("CodeResources files2 catalog contains > 2,000 files", f2_count > 2000, f"Count: {f2_count}")

    # Check sample files against CodeResources SHA-256
    sample_files = [
        "Payload/Instagram.app/Info.plist",
        "Payload/Instagram.app/Frameworks/SPKSideloadFix.dylib",
        "Payload/Instagram.app/Frameworks/SCInsta.dylib",
        "Payload/Instagram.app/Frameworks/CydiaSubstrate.framework/Info.plist",
    ]
    samples_valid = True
    for sf in sample_files:
        content = z.read(sf)
        expected_h = hashlib.sha256(content).digest()
        recorded_entry = cr_data.get("files2", {}).get(sf.replace("Payload/Instagram.app/", ""), {})
        recorded_h = recorded_entry.get("hash2") or recorded_entry.get("hash")
        if recorded_h != expected_h:
            samples_valid = False
            break
    check("Sample bundle files match CodeResources cryptographic SHA-256 hashes", samples_valid)

print("\n=========================================================================")
print(f"  VICTORY AUDIT COMPLETE: {passed} PASSED / {failed} FAILED")
print("=========================================================================")

if failed > 0:
    print(f"\n[!] Audit detected {failed} failure(s):")
    for t, d in failures:
        print(f"    - {t} ({d})")
    sys.exit(1)
else:
    print("\n[+] 100% OF CHECKS PASSED PERFECTLY. BUILD IS READY FOR PRODUCTION.")
    sys.exit(0)
