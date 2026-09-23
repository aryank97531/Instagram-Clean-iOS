# 📵 Instagram Clean (v446.0.0) — iOS Distraction-Free Edition

> **Reclaim your focus & eliminate mindless doomscrolling without sacrificing your social life.**  
> Keep in touch with friends through **Stories, Direct Messages, and HD Voice/Video Calls** while completely removing algorithmic video feeds, Explore traps, and ads. Built on the modern **September 2026 release of Instagram (v446.0.0)** with full **Liquid Glass UI** support.

---

[![GitHub Release](https://img.shields.io/github/v/release/aryank97531/Instagram-Clean-iOS?color=007AFF&logo=github&style=for-the-badge)](https://github.com/aryank97531/Instagram-Clean-iOS/releases)
[![iOS Support](https://img.shields.io/badge/iOS-16%20%7C%2017%20%7C%2018-black?logo=apple&style=for-the-badge)]()
[![Instagram Base](https://img.shields.io/badge/Instagram-v446.0.0-E4405F?logo=instagram&style=for-the-badge)]()
[![Reels Blocked](https://img.shields.io/badge/Reels-Blocked-red?style=for-the-badge)]()
[![Calls & DMs](https://img.shields.io/badge/Calls%20%26%20DMs-100%25%20Working-success?style=for-the-badge)]()
[![Ghost Mode](https://img.shields.io/badge/Ghost%20Mode-Enabled-purple?style=for-the-badge)]()

---

## 🌟 Why Instagram Clean?

Modern social media apps are intentionally engineered to steal your attention. Instagram's **Reels algorithm** and **Explore discovery grid** are infinite slot machines designed to keep you trapped in endless doomscrolling loops.

**Instagram Clean** rewrites the rules:
- ❌ **No Reels Tab:** The infinite short-form video tab is completely erased.
- ❌ **No Explore Discovery:** The algorithmic search grid is disabled—no clickbait rabbit holes.
- ❌ **No Infinite Home Feed:** Home feed posts are suppressed, leaving your feed empty once you've checked your messages.
- ❌ **No Sponsored Ads:** All commercial ads and promotional stories are stripped out.
- ❌ **No Meta AI:** AI chat suggestions and search bar bots are disabled.
- ✅ **Stories Carousel Preserved:** Your friends' Stories tray remains active and functional at the top of your screen.
- ✅ **Direct Messages & Chat Active:** 100% full access to chats, threads, and photo sharing.
- ✅ **Audio & Video Calling Restored:** Built on **Instagram v446.0.0 (build 1060018354)** with active WebRTC VoIP endpoints, so DM voice and video calls connect seamlessly.
- 👻 **Pre-Enabled Ghost Mode:** Stealth story viewing (watch without appearing on viewer lists), hide DM "Seen" read receipts, and hidden "typing..." status.
- 🔮 **Liquid Glass UI:** Modern translucent floating navigation bar and updated iOS 18 glassmorphic aesthetics.

---

## ⚡ Feature Matrix

| Feature | Official App | Traditional Modded IPAs | **Instagram Clean (This Build)** |
|---|:---:|:---:|:---:|
| **Reels Tab** | 🚨 Intrusive | ⚠️ Often Present | ❌ **Completely Removed** |
| **Explore Algorithmic Grid** | 🚨 Addictive | ⚠️ Often Present | ❌ **Completely Removed** |
| **Feed Doomscrolling** | 🚨 Infinite | ⚠️ Infinite | ❌ **Suppressed & Clean** |
| **Top Stories Tray** | ✅ Present | ✅ Present | ✅ **Fully Preserved** |
| **Direct Messages (DMs)** | ✅ Present | ✅ Present | ✅ **Fully Preserved** |
| **Voice & Video Calling** | ✅ Working | ❌ Deprecated / Broken | ✅ **100% Working (v446 WebRTC)** |
| **Ghost Mode (Stories & DMs)** | ❌ None | ⚠️ Manual Config | 👻 **Pre-Enabled by Default** |
| **Free Apple ID Sideloading** | N/A | ❌ Fails App-ID Limit | ✅ **Optimized (0 `.appex` bundles)** |
| **Keychain Crash Prevention** | N/A | ❌ Crashes on Login | ✅ **Integrated `SPKSideloadFix`** |
| **iOS 18 PAC Stability** | N/A | ❌ Outdated Substrate Crash | ✅ **Modern ElleKit Framework** |

---

## 🚀 Quick Start: How to Sideload (3 Minutes)

You do **not** need a jailbroken iPhone. You can install this on any iPhone running **iOS 16, 17, or 18** using your free Apple ID.

### Option A: Using Sideloadly (Recommended for Windows & Mac)

1. **Download the IPA:**
   * Download the latest **`Instagram_Clean.ipa`** from [Releases](https://github.com/aryank97531/Instagram-Clean-iOS/releases).
2. **Download Sideloadly:**
   * Get [Sideloadly](https://sideloadly.io/) and ensure iTunes/Apple USB drivers are installed.
3. **Connect Your iPhone:**
   * Plug your iPhone into your computer via USB (tap **Trust** if prompted).
4. **Deploy:**
   * Open Sideloadly.
   * Drag & drop `Instagram_Clean.ipa` into the large IPA box.
   * Enter your Apple ID email.
   * Click **Start**!
   * Enter your Apple ID password and the 2FA code when prompted.
5. **Trust on iPhone (First Time Only):**
   * On your iPhone, go to **Settings > General > VPN & Device Management**.
   * Tap your Apple ID email under *Developer App* and select **Trust**.
   * *(iOS 16/17/18)*: Go to **Settings > Privacy & Security > Developer Mode**, toggle it **ON**, and restart your device when prompted.

---

### Option B: Using AltStore / SideStore

1. Download `Instagram_Clean.ipa` on your iPhone.
2. In **AltStore** or **SideStore**, tap the **+** (Add) button in the *My Apps* tab.
3. Select `Instagram_Clean.ipa` and wait for installation to finish.

---

### Option C: Using TrollStore (iOS 14.0 – 17.0)

1. Download `Instagram_Clean.ipa` directly in Safari.
2. Tap the Share sheet and select **TrollStore**.
3. It will install permanently with zero certificate expiration!

---

## 🔧 DIY: Customize Your Own Settings

Want to build your own version with custom toggles? We provide a modular Python build script that patches the base binary at the ARM64 assembly level:

```bash
# Clone the repository
git clone https://github.com/aryank97531/Instagram-Clean-iOS.git
cd Instagram-Clean-iOS

# Inspect or customize toggles in scripts/build_clean_ipa.py
python scripts/build_clean_ipa.py
```

### Key Toggles inside `scripts/build_clean_ipa.py`:
```python
# Customization Flags
HIDE_REELS_TAB = True         # Completely removes bottom Reels tab
HIDE_EXPLORE_TAB = True       # Completely removes Explore discovery tab
HIDE_ENTIRE_FEED = True       # Suppresses home feed post rendering
PRESERVE_STORIES = True       # Keeps top Stories tray active
GHOST_MODE_STORIES = True     # Anonymous story viewing (no seen receipts)
GHOST_MODE_DMS = True         # Read direct messages without seen receipts
HIDE_TYPING_INDICATOR = True  # Hides 'typing...' in chat
LIQUID_GLASS_UI = True        # Enables modern floating translucent navigation bar
```

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>Does voice and video calling work in this version?</b></summary>
<br>
<b>Yes!</b> Older sideloaded Instagram IPAs (such as v418) fail to make calls because Meta server-side deprecated their legacy WebRTC handshake protocols. This build is based on <b>Instagram v446.0.0</b>, ensuring full compatibility with Meta's current active voice and video calling infrastructure.
</details>

<details>
<summary><b>Why did older tweaked versions crash when I clicked 'Save Password'?</b></summary>
<br>
Unmodified Instagram binaries attempt to write login tokens into Apple's private developer Keychain access groups. On sideloaded apps with changed bundle identifiers, iOS blocks this permission, causing an instant <code>-34018</code> fatal assertion crash. 
<br><br>
<b>Instagram Clean</b> fixes this at the binary level by injecting <code>SPKSideloadFix.dylib</code>, which dynamically hooks <code>SecItemAdd</code>, <code>SecItemCopyMatching</code>, and <code>SecItemUpdate</code> to safely redirect credentials.
</details>

<details>
<summary><b>Why was the weekly 3-App ID limit an issue?</b></summary>
<br>
Free Apple Developer accounts are restricted to 10 App IDs per week (typically 3 active apps). Official Instagram contains up to 8 separate <code>.appex</code> extension bundles (Share Extension, Widget, Notification Service, etc.). If an installer signs all extensions, it burns your weekly quota in a single installation. 
<br><br>
<b>Instagram Clean</b> automatically strips all unused <code>.appex</code> bundles during packaging while keeping the main app and call services 100% intact.
</details>

<details>
<summary><b>How often do I need to refresh the app?</b></summary>
<br>
If sideloading with a free Apple ID via Sideloadly or AltStore, Apple requires re-signing every <b>7 days</b>. 
- Sideloadly and AltStore can automatically refresh the app in the background over local Wi-Fi while your computer is on the same network.
- TrollStore users never need to refresh.
</details>

---

## ⚖️ Disclaimer

This project is an open-source productivity and digital wellness modification intended for personal use and mental health optimization. This repository is not affiliated with, endorsed by, or associated with Instagram, Meta Platforms, Inc., or Apple Inc. All trademarks belong to their respective owners.

---

## 🤝 Contributing & Support

- Found an issue or want to request a feature? Open an [Issue](https://github.com/aryank97531/Instagram-Clean-iOS/issues)!
- Star ⭐ the repository if this helped you reclaim your attention and time!
