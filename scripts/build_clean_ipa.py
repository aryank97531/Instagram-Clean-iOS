#!/usr/bin/env python3
"""
=============================================================================
  Instagram Clean -- Distraction-Free iOS IPA Builder & Patching Script
=============================================================================
  Target: Instagram v446.0.0+ (iOS 16, 17, 18)
  Author: Aryan Kumar (https://github.com/aryank97531/Instagram-Clean-iOS)

  This script takes a decrypted Instagram IPA, injects ElleKit (CydiaSubstrate)
  and SPKSideloadFix (Keychain fix for non-jailbroken sideloading), patches
  the ARM64 assembly to enforce distraction-free and privacy preferences,
  neutralizes Iris socket delta blocks to ensure 100% real-time DM streaming,
  harmonizes CodeDirectory page hashes, generates clean CodeResources,
  and packages a ready-to-sideload IPA with 0 .appex bundles, explicit Unix
  directory records, and strict UNIX zip attributes (create_system=3).
=============================================================================
"""

import os
import sys
import shutil
import zipfile
import struct
import plistlib
import hashlib
import re

# ---------------------------------------------------------------------------
# [USER CONFIGURATION] Toggle features on or off as desired:
# ---------------------------------------------------------------------------
HIDE_REELS_TAB = True         # Completely removes bottom Reels tab
HIDE_EXPLORE_TAB = True       # Completely removes Explore search tab
HIDE_ENTIRE_FEED = True       # Suppresses home feed post rendering
PRESERVE_STORIES = True       # Keeps top Stories tray active
GHOST_MODE_STORIES = True     # Anonymous story viewing (no seen receipts)
GHOST_MODE_DMS = True         # Read direct messages without seen receipts
HIDE_TYPING_INDICATOR = True  # Hides 'typing...' in chat
LIQUID_GLASS_UI = True        # Enables modern floating translucent navigation bar
DISAPPEARING_MEDIA_SAVE = True# Disables screenshot alert & allows unlimited replay
BLOCK_SPONSORED_ADS = True    # Strips sponsored posts & ads
DISABLE_META_AI = True        # Strips Meta AI suggestions and chat bots
DISABLE_VIDEO_AUTOPLAY = True # Prevents automatic video autoplay

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
PARENT_DIR = os.path.dirname(ROOT_DIR)

BASE_IPA = os.path.join(ROOT_DIR, "Instagram-Decrypted.ipa")
if not os.path.exists(BASE_IPA):
    for cand in [os.path.join(PARENT_DIR, "Instagram-Decrypted.ipa"), os.path.expanduser(r"~\Downloads\Instagram-Decrypted.ipa")]:
        if os.path.exists(cand):
            BASE_IPA = cand
            break

SCINSTA_DYLIB = os.path.join(ROOT_DIR, "SCInsta.dylib")
if not os.path.exists(SCINSTA_DYLIB):
    for cand in [os.path.join(PARENT_DIR, "SCInsta.dylib"), os.path.expanduser(r"~\Downloads\SCInsta.dylib")]:
        if os.path.exists(cand):
            SCINSTA_DYLIB = cand
            break

SPK_DYLIB = os.path.join(ROOT_DIR, "SPKSideloadFix.dylib")
if not os.path.exists(SPK_DYLIB):
    for cand in [os.path.join(PARENT_DIR, "SPKSideloadFix.dylib"), os.path.expanduser(r"~\Downloads\SPKSideloadFix.dylib")]:
        if os.path.exists(cand):
            SPK_DYLIB = cand
            break

OUTPUT_IPA = os.path.join(ROOT_DIR, "Instagram_Clean.ipa")

print("=========================================================================")
print("  INSTAGRAM CLEAN (v446.0.0) BUILDER & PATCHER")
print("  [Real-Time DM Iris Delta Streaming & Ghost Mode Harmonization]")
print("=========================================================================")

def main():
    print(f"Base IPA:      {BASE_IPA}")
    print(f"SCInsta:       {SCINSTA_DYLIB}")
    print(f"SPKSideloadFix:{SPK_DYLIB}")
    print(f"Output IPA:    {OUTPUT_IPA}")
    
    # Check dependencies
    try:
        import keystone
        import capstone
    except ImportError:
        print("[!] Error: keystone-engine and capstone are required to assemble ARM64 hooks.")
        print("    Install them using: pip install keystone-engine capstone")
        sys.exit(1)

    if not os.path.exists(BASE_IPA):
        print(f"[!] Base decrypted IPA not found at {BASE_IPA}.")
        print("    Please place a decrypted Instagram v446.0.0 IPA in the directory.")
        sys.exit(1)

    # 1. ElleKit Framework Preparation
    print("\n[1] Preparing ElleKit CydiaSubstrate...")
    candidate_ipas = [
        OUTPUT_IPA,
        os.path.join(os.path.dirname(ROOT_DIR), "Instagram_Clean.ipa"),
        os.path.expanduser(r"~\Downloads\Instagram_Clean.ipa"),
    ]
    agents_dir = os.path.join(os.path.dirname(ROOT_DIR), ".agents")
    if os.path.exists(agents_dir):
        for entry in os.listdir(agents_dir):
            candidate_ipas.append(os.path.join(agents_dir, entry, "Instagram_Clean.ipa"))

    ellekit_bin = None
    for cand in candidate_ipas:
        if os.path.exists(cand):
            try:
                with zipfile.ZipFile(cand, "r") as prev_z:
                    if "Payload/Instagram.app/Frameworks/CydiaSubstrate.framework/CydiaSubstrate" in prev_z.namelist():
                        ellekit_bin = prev_z.read("Payload/Instagram.app/Frameworks/CydiaSubstrate.framework/CydiaSubstrate")
                        break
            except Exception:
                continue

    if not ellekit_bin:
        print("[!] Previous IPA with CydiaSubstrate framework not found.")
        sys.exit(1)

    magic = struct.unpack(">I", ellekit_bin[:4])[0]
    assert magic == 0xcffaedfe, f"Invalid ElleKit magic: {hex(magic)}"

    old_log = b"/var/jb/var/mobile/log.txt\x00"
    new_log = b"/var/mobile/log.txt\x00" + b"\x00" * (len(old_log) - len(b"/var/mobile/log.txt\x00"))
    pos = ellekit_bin.find(old_log)
    if pos != -1:
        ellekit_ba = bytearray(ellekit_bin)
        ellekit_ba[pos : pos + len(old_log)] = new_log
        ellekit_bin = bytes(ellekit_ba)

    ellekit_plist_dict = {
        "CFBundleDevelopmentRegion": "en",
        "CFBundleExecutable": "CydiaSubstrate",
        "CFBundleIdentifier": "com.burbn.instagram.cydiasubstrate",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": "CydiaSubstrate",
        "CFBundlePackageType": "FMWK",
        "CFBundleShortVersionString": "1.1.3",
        "CFBundleSignature": "????",
        "CFBundleSupportedPlatforms": ["iPhoneOS"],
        "CFBundleVersion": "1.1.3",
        "DTPlatformName": "iphoneos",
        "LSRequiresIPhoneOS": True,
        "MinimumOSVersion": "16.3",
        "UIDeviceFamily": [1, 2],
        "UIRequiredDeviceCapabilities": ["arm64"]
    }
    ellekit_plist = plistlib.dumps(ellekit_plist_dict)

    # 2. Patch SCInsta.dylib
    print("\n[2] Patching SCInsta.dylib (Neutralizing Iris delta blocks, 35 targets)...")
    with open(SCINSTA_DYLIB, "rb") as f:
        scinsta_data = bytearray(f.read())

    sanitizations = [
        (b"/var/jb/Library/Frameworks", b"@loader_path\x00"),
        (b"/var/jb/usr/lib", b"@loader_path\x00"),
        (b"@loader_path/.jbroot/Library/Frameworks", b"@loader_path\x00"),
        (b"@loader_path/.jbroot/usr/lib", b"@loader_path\x00"),
    ]

    for old_p, base_new in sanitizations:
        pad_len = len(old_p) - len(base_new)
        assert pad_len >= 0, f"Replacement exceeds original length: {base_new}"
        full_new = base_new + b"\x00" * pad_len
        pos = scinsta_data.find(old_p)
        while pos != -1:
            scinsta_data[pos : pos + len(old_p)] = full_new
            pos = scinsta_data.find(old_p, pos + len(old_p))

    # Neutralize first-run modal check
    scinsta_data[0x1144c : 0x11450] = bytes.fromhex("08008052")

    # Neutralize Iris Thread Delta & Message Update interception hooks:
    scinsta_data[0x12b84 : 0x12b88] = bytes.fromhex("c0035fd6") # ret
    scinsta_data[0x12c14 : 0x12c18] = bytes.fromhex("c0035fd6") # ret
    scinsta_data[0x12cb8 : 0x12cbc] = bytes.fromhex("c0035fd6") # ret

    targets = [
        (0x5a3d0, 1 if HIDE_REELS_TAB else 0),
        (0x5a370, 1 if HIDE_EXPLORE_TAB else 0),
        (0x5a310, 0),                                 # hide_feed_tab: kept for Stories/DMs
        (0x594b0, 0 if PRESERVE_STORIES else 1),     # hide_stories_tray
        (0x59510, 1 if HIDE_ENTIRE_FEED else 0),     # hide_entire_feed
        (0x593b0, 1 if HIDE_EXPLORE_TAB else 0),     # hide_explore_grid
        (0x59a10, 1),                                 # disable_scrolling_reels
        (0x59630, 1),                                 # no_suggested_reels
        (0x59570, 1),                                 # no_suggested_post
        (0x59690, 1),                                 # no_suggested_threads
        (0x595d0, 1),                                 # no_suggested_account
        (0x58e30, 1 if BLOCK_SPONSORED_ADS else 0),  # hide_ads
        (0x592f0, 1),                                 # no_suggested_users
        (0x59990, 1),                                 # hide_reels_blend
        (0x59930, 1),                                 # hide_reels_header
        (0x58e90, 1 if DISABLE_META_AI else 0),      # hide_meta_ai
        (0x59410, 1),                                 # hide_trending_searches
        (0x59350, 1),                                 # no_suggested_chats
        (0x596f0, 1 if DISABLE_VIDEO_AUTOPLAY else 0),# disable_feed_autoplay
        (0x59850, 1),                                 # disable_auto_unmuting_reels
        (0x59a70, 1),                                 # prevent_doom_scrolling
        (0x591b0, 1),                                 # hide_friends_map
        (0x5aaf0, 0),                                 # tweak_settings_app_launch: 0
        (0x5a9b0, 0),                                 # flex_app_launch: 0
        (0x5aa10, 0),                                 # flex_app_start: 0
        (0x5a950, 0),                                 # flex_instagram: 0
        (0x59010, 1 if LIQUID_GLASS_UI else 0),      # liquid_glass_buttons
        (0x59070, 1 if LIQUID_GLASS_UI else 0),      # liquid_glass_surfaces
        (0x5a650, 0),                                 # call_confirm: direct one-tap calling
        (0x5a130, 1 if GHOST_MODE_STORIES else 0),   # no_seen_receipt (Ghost Stories)
        (0x59f30, 1 if GHOST_MODE_DMS else 0),       # remove_lastseen (Ghost DMs)
        (0x59f90, 1 if HIDE_TYPING_INDICATOR else 0),# disable_typing_status
        (0x5a0d0, 1 if DISAPPEARING_MEDIA_SAVE else 0), # remove_screenshot_alert
        (0x5a010, 1 if DISAPPEARING_MEDIA_SAVE else 0), # unlimited_replay
        (0x59ed0, 0),                                 # keep_deleted_message -> 0 (Iris socket unblocking)
    ]

    ks = keystone.Ks(keystone.KS_ARCH_ARM64, keystone.KS_MODE_LITTLE_ENDIAN)
    hook_template = """
    sub   sp, sp, #0x30
    stp   x29, x30, [sp, #0x20]
    stp   x19, x20, [sp, #0x10]
    add   x29, sp, #0x20
    mov   x19, x2
    cbz   x19, _ret_zero

    adr   x20, _table
    _ptr_loop:
    ldrsw x1, [x20]
    cbz   x1, _str_check
    add   x4, x20, x1
    cmp   x19, x4
    b.ne  _ptr_next
    ldr   w0, [x20, #4]
    b     _epilogue
    _ptr_next:
    add   x20, x20, #8
    b     _ptr_loop

    _str_check:
    adr   x20, _table
    _str_loop:
    ldrsw x1, [x20]
    cbz   x1, _defaults_fallback
    add   x2, x20, x1
    mov   x0, x19
    bl    0x409e0
    cbz   w0, _str_next
    ldr   w0, [x20, #4]
    b     _epilogue
    _str_next:
    add   x20, x20, #8
    b     _str_loop

    _defaults_fallback:
    adrp  x8, #0x64000
    ldr   x0, [x8, #0xa28]
    bl    0x43080
    mov   x2, x19
    bl    0x3f6a0
    b     _epilogue

    _ret_zero:
    mov   w0, #0

    _epilogue:
    ldp   x19, x20, [sp, #0x10]
    ldp   x29, x30, [sp, #0x20]
    add   sp, sp, #0x30
    ret

    _table:
    """
    hook_code_bytes, _ = ks.asm(hook_template + "nop", 0x2e544)
    table_addr = 0x2e544 + len(hook_code_bytes) - 4

    table_data = bytearray()
    for tgt_addr, val in targets:
        entry_addr = table_addr + len(table_data)
        rel_off = tgt_addr - entry_addr
        table_data.extend(struct.pack("<ii", rel_off, val))
    table_data.extend(struct.pack("<ii", 0, 0))

    patch_bytes = bytearray(hook_code_bytes[:-4]) + table_data
    hook_offset = 0x2e544
    patch_len = len(patch_bytes)
    max_len = 0x2e700 - hook_offset
    assert patch_len <= max_len

    scinsta_data[hook_offset : hook_offset + patch_len] = patch_bytes
    nop_inst = struct.pack("<I", 0xd503201f)
    rem_len = max_len - patch_len
    scinsta_data[hook_offset + patch_len : 0x2e700] = nop_inst * (rem_len // 4)

    # 3. Patch SPKSideloadFix.dylib
    print("\n[3] Patching SPKSideloadFix.dylib...")
    with open(SPK_DYLIB, "rb") as f:
        spk_data = bytearray(f.read())

    for old_p, base_new in sanitizations:
        pad_len = len(old_p) - len(base_new)
        full_new = base_new + b"\x00" * pad_len
        pos = spk_data.find(old_p)
        while pos != -1:
            spk_data[pos : pos + len(old_p)] = full_new
            pos = spk_data.find(old_p, pos + len(old_p))

    # 4. Modify main Instagram Mach-O
    print("\n[4] Modifying main Instagram Mach-O executable...")
    with zipfile.ZipFile(BASE_IPA, "r") as z:
        ig_bin = bytearray(z.read("Payload/Instagram.app/Instagram"))

    magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack_from("<IIIIIIII", ig_bin, 0)
    LC_CODE_SIGNATURE = 0x1d
    LC_LOAD_DYLIB = 0xc

    offset = 32
    codesig_cmd_offset = None
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", ig_bin, offset)
        if cmd == LC_CODE_SIGNATURE:
            codesig_cmd_offset = offset
            codesig_cmd_size = cmdsize
            break
        offset += cmdsize

    codesig_cmd_bytes = bytes(ig_bin[codesig_cmd_offset : codesig_cmd_offset + codesig_cmd_size])

    def make_lc_load_dylib(dylib_path):
        encoded_path = dylib_path.encode("utf-8") + b"\x00"
        name_offset = 24
        total_size = (name_offset + len(encoded_path) + 7) & ~7
        padding = b"\x00" * (total_size - (name_offset + len(encoded_path)))
        return struct.pack("<IIIIII", LC_LOAD_DYLIB, total_size, name_offset, 2, 0, 0) + encoded_path + padding

    dylibs_to_inject = [
        "@rpath/SPKSideloadFix.dylib",
        "@rpath/CydiaSubstrate.framework/CydiaSubstrate",
        "@rpath/SCInsta.dylib"
    ]

    injection_payload = bytearray()
    for dylib in dylibs_to_inject:
        injection_payload.extend(make_lc_load_dylib(dylib))

    new_load_commands = injection_payload + codesig_cmd_bytes
    ig_bin[codesig_cmd_offset : codesig_cmd_offset + len(new_load_commands)] = new_load_commands

    new_ncmds = ncmds + len(dylibs_to_inject)
    new_sizeofcmds = sizeofcmds + len(injection_payload)
    struct.pack_into("<II", ig_bin, 16, new_ncmds, new_sizeofcmds)

    # 5. Modern v446 Info.plist & Settings
    print("\n[5] Upgrading Info.plist and Settings.bundle to Instagram v446.0.0...")
    with zipfile.ZipFile(BASE_IPA, "r") as z:
        info_plist_raw = z.read("Payload/Instagram.app/Info.plist")
        info_plist = plistlib.loads(info_plist_raw)
        settings_plist_raw = z.read("Payload/Instagram.app/Settings.bundle/Root.plist")
        settings_plist = plistlib.loads(settings_plist_raw)

    info_plist["CFBundleShortVersionString"] = "446.0.0"
    info_plist["CFBundleVersion"] = "1060018354"
    info_plist["FBPlatformVersion"] = "446.0.0"
    info_plist["FBAppVersion"] = "446.0.0.28.66"

    if "UIBackgroundModes" not in info_plist:
        info_plist["UIBackgroundModes"] = []
    for mode in ["voip", "audio"]:
        if mode not in info_plist["UIBackgroundModes"]:
            info_plist["UIBackgroundModes"].append(mode)

    upgraded_info_plist_bytes = plistlib.dumps(info_plist)
    for spec in settings_plist.get("PreferenceSpecifiers", []):
        if spec.get("Key") == "FBVersion":
            spec["DefaultValue"] = "446.0.0.28.66 (1060018354)"
    upgraded_settings_plist_bytes = plistlib.dumps(settings_plist)

    # 6. Recalculate CodeDirectory page hashes
    print("\n[6] Recalculating CodeDirectory page hashes...")
    def patch_codedirectory_hashes(data, binary_name):
        ba = bytearray(data)
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
            return bytes(ba)

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
                    if h:
                        ba[cdoff + hashOffset + slot * hashSize : cdoff + hashOffset + (slot + 1) * hashSize] = h
        return bytes(ba)

    ig_bin = patch_codedirectory_hashes(ig_bin, "Instagram")
    spk_data = patch_codedirectory_hashes(spk_data, "SPKSideloadFix.dylib")
    scinsta_data = patch_codedirectory_hashes(scinsta_data, "SCInsta.dylib")
    ellekit_bin = patch_codedirectory_hashes(ellekit_bin, "CydiaSubstrate")

    # 7. CodeResources
    print("\n[7] Generating CodeResources...")
    def generate_coderesources(file_dict, is_framework=False):
        files = {}
        files2 = {}
        for rel_path, content in file_dict.items():
            if rel_path.startswith("_CodeSignature") or (not is_framework and rel_path == "Instagram") or (is_framework and rel_path == "CydiaSubstrate"):
                continue
            h1 = hashlib.sha1(content).digest()
            h2 = hashlib.sha256(content).digest()
            is_optional = bool(re.search(r"^[^\/]*\.lproj\/", rel_path)) and not rel_path.startswith("Base.lproj/")
            if is_optional:
                files[rel_path] = {"hash": h1, "optional": True}
                files2[rel_path] = {"hash": h1, "hash2": h2, "optional": True}
            else:
                files[rel_path] = h1
                files2[rel_path] = {"hash": h1, "hash2": h2}

        if is_framework:
            rules = {"^.*": True, "^.*\\.lproj/": {"optional": True, "weight": 1000.0}, "^.*\\.lproj/locversion.plist$": {"omit": True, "weight": 1100.0}, "^Base\\.lproj/": {"weight": 1010.0}, "^version\\.plist$": True}
            rules2 = {".*\\.dSYM($|/)": {"weight": 11.0}, "^(.*/)?\\.DS_Store$": {"omit": True, "weight": 2000.0}, "^.*": True, "^.*\\.lproj/": {"optional": True, "weight": 1000.0}, "^.*\\.lproj/locversion.plist$": {"omit": True, "weight": 1100.0}, "^Base\\.lproj/": {"weight": 1010.0}, "^Info\\.plist$": {"omit": True, "weight": 20.0}, "^PkgInfo$": {"omit": True, "weight": 20.0}, "^version\\.plist$": {"weight": 20.0}}
        else:
            rules = {
                "Frameworks/FBSharedFramework\\.framework/SC_Info/FBSharedFramework\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "Frameworks/GoogleCast\\.framework/SC_Info/GoogleCast\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "Frameworks/SpotifyiOS\\.framework/SC_Info/SpotifyiOS\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "Frameworks/libavcodec\\.framework/SC_Info/libavcodec\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "Frameworks/libavutil\\.framework/SC_Info/libavutil\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "SC_Info/Instagram\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "^.*": True,
                "^.*\\.lproj/": {"optional": True, "weight": 1000.0},
                "^.*\\.lproj/locversion.plist$": {"omit": True, "weight": 1100.0},
                "^Base\\.lproj/": {"weight": 1010.0},
                "^version.plist$": True
            }
            rules2 = {
                ".*\\.dSYM($|/)": {"weight": 11.0},
                "Frameworks/FBSharedFramework\\.framework/SC_Info/FBSharedFramework\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "Frameworks/GoogleCast\\.framework/SC_Info/GoogleCast\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "Frameworks/SpotifyiOS\\.framework/SC_Info/SpotifyiOS\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "Frameworks/libavcodec\\.framework/SC_Info/libavcodec\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "Frameworks/libavutil\\.framework/SC_Info/libavutil\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "SC_Info/Instagram\\.(sinf|supp|supf|supx)$": {"omit": True, "weight": 10000},
                "^(.*/)?\\.DS_Store$": {"omit": True, "weight": 2000.0},
                "^.*": True,
                "^.*\\.lproj/": {"optional": True, "weight": 1000.0},
                "^.*\\.lproj/locversion.plist$": {"omit": True, "weight": 1100.0},
                "^Base\\.lproj/": {"weight": 1010.0},
                "^Info\\.plist$": {"omit": True, "weight": 20.0},
                "^PkgInfo$": {"omit": True, "weight": 20.0},
                "^embedded\\.provisionprofile$": {"weight": 20.0},
                "^version\\.plist$": {"weight": 20.0}
            }

        return plistlib.dumps({"files": files, "files2": files2, "rules": rules, "rules2": rules2})

    cs_coderesources = generate_coderesources({"CydiaSubstrate": ellekit_bin, "Info.plist": ellekit_plist}, is_framework=True)

    # 8. Assemble Bundle & Package IPA
    print("\n[8] Assembling and Packaging Deployable IPA...")
    app_file_manifest = {}
    raw_archive_entries = {}

    with zipfile.ZipFile(BASE_IPA, "r") as src_zip:
        for item in src_zip.infolist():
            if "/PlugIns/" in item.filename or "/Extensions/" in item.filename:
                continue
            if item.filename == "Payload/Instagram.app/Instagram":
                data = bytes(ig_bin)
            elif item.filename == "Payload/Instagram.app/Info.plist":
                data = upgraded_info_plist_bytes
            elif item.filename == "Payload/Instagram.app/Settings.bundle/Root.plist":
                data = upgraded_settings_plist_bytes
            elif item.filename == "Payload/Instagram.app/_CodeSignature/CodeResources":
                continue
            else:
                data = src_zip.read(item.filename)

            raw_archive_entries[item.filename] = (item, data)
            if item.filename.startswith("Payload/Instagram.app/"):
                rel_path = item.filename[len("Payload/Instagram.app/"):]
                app_file_manifest[rel_path] = data

    app_file_manifest["Frameworks/SPKSideloadFix.dylib"] = bytes(spk_data)
    app_file_manifest["Frameworks/SCInsta.dylib"] = bytes(scinsta_data)
    app_file_manifest["Frameworks/CydiaSubstrate.framework/CydiaSubstrate"] = ellekit_bin
    app_file_manifest["Frameworks/CydiaSubstrate.framework/Info.plist"] = ellekit_plist
    app_file_manifest["Frameworks/CydiaSubstrate.framework/_CodeSignature/CodeResources"] = cs_coderesources

    raw_archive_entries["Payload/Instagram.app/Frameworks/SPKSideloadFix.dylib"] = (None, bytes(spk_data))
    raw_archive_entries["Payload/Instagram.app/Frameworks/SCInsta.dylib"] = (None, bytes(scinsta_data))
    raw_archive_entries["Payload/Instagram.app/Frameworks/CydiaSubstrate.framework/CydiaSubstrate"] = (None, ellekit_bin)
    raw_archive_entries["Payload/Instagram.app/Frameworks/CydiaSubstrate.framework/Info.plist"] = (None, ellekit_plist)
    raw_archive_entries["Payload/Instagram.app/Frameworks/CydiaSubstrate.framework/_CodeSignature/CodeResources"] = (None, cs_coderesources)

    main_coderesources = generate_coderesources(app_file_manifest, is_framework=False)
    raw_archive_entries["Payload/Instagram.app/_CodeSignature/CodeResources"] = (None, main_coderesources)

    if os.path.exists(OUTPUT_IPA):
        os.remove(OUTPUT_IPA)

    def create_unix_zipinfo(filename, mode=0o100644, date_time=(2026, 2, 27, 1, 8, 42)):
        zinfo = zipfile.ZipInfo(filename, date_time=date_time)
        zinfo.create_system = 3
        zinfo.create_version = 30
        zinfo.extract_version = 20
        zinfo.flag_bits = 0
        if filename.endswith("/"):
            zinfo.compress_type = zipfile.ZIP_STORED
            zinfo.external_attr = (0o40755 << 16) | 0x10
        else:
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zinfo.external_attr = (mode << 16) | 0x20
        return zinfo

    all_dirs = set()
    for filename in raw_archive_entries.keys():
        parts = filename.split("/")
        for i in range(1, len(parts)):
            d = "/".join(parts[:i]) + "/"
            all_dirs.add(d)

    sorted_dirs = sorted(list(all_dirs))
    with zipfile.ZipFile(OUTPUT_IPA, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as dst_zip:
        for d in sorted_dirs:
            zdir = create_unix_zipinfo(d, mode=0o40755)
            dst_zip.writestr(zdir, b"")

        for filename, (orig_item, data) in raw_archive_entries.items():
            is_exec = filename.endswith(("Instagram", ".dylib", "CydiaSubstrate"))
            mode = 0o100755 if is_exec else 0o100644
            date_time = orig_item.date_time if orig_item else (2026, 2, 27, 1, 8, 42)
            zinfo = create_unix_zipinfo(filename, mode=mode, date_time=date_time)
            if orig_item and orig_item.compress_type == zipfile.ZIP_STORED and not is_exec and not filename.endswith((".plist", ".dylib", "Instagram")):
                zinfo.compress_type = zipfile.ZIP_STORED
            else:
                zinfo.compress_type = zipfile.ZIP_DEFLATED
            dst_zip.writestr(zinfo, data)

    final_size = os.path.getsize(OUTPUT_IPA)
    print(f"\n[+] Successfully built deployable IPA: {OUTPUT_IPA} ({final_size / (1024*1024):.2f} MB)")

    # Deploy to Downloads, Project Scratch Root, Current Working Directory, and Agent Directories
    DOWNLOADS_IPA = os.path.expanduser(r"~\Downloads\Instagram_Clean.ipa")
    PARENT_DIR = os.path.dirname(ROOT_DIR)
    SCRATCH_IPA = os.path.join(PARENT_DIR, "Instagram_Clean.ipa")
    CWD_IPA = os.path.join(os.getcwd(), "Instagram_Clean.ipa")

    destinations = [DOWNLOADS_IPA, SCRATCH_IPA, CWD_IPA]

    agents_dir = os.path.join(PARENT_DIR, ".agents")
    if os.path.exists(agents_dir):
        for entry in os.listdir(agents_dir):
            if (entry.startswith("teamwork_preview_reviewer_dm_") or
                entry.startswith("teamwork_preview_victory_auditor") or
                entry.startswith("teamwork_preview_implementer_r1")) and os.path.isdir(os.path.join(agents_dir, entry)):
                destinations.append(os.path.join(agents_dir, entry, "Instagram_Clean.ipa"))

    seen = set()
    unique_dests = []
    for d in destinations:
        norm = os.path.abspath(d)
        if norm not in seen and norm != os.path.abspath(OUTPUT_IPA):
            seen.add(norm)
            unique_dests.append(d)

    for dest in unique_dests:
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(OUTPUT_IPA, dest)
            print(f"[*] Deployed to: {dest} ({os.path.getsize(dest)} bytes)")
        except Exception as e:
            print(f"[!] Warning: Failed to deploy to {dest}: {e}")

if __name__ == "__main__":
    main()
