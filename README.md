# Dusklight for PlayStation 5

[![stars](https://img.shields.io/github/stars/griches/PS5_Dusklight?style=flat)](https://github.com/griches/PS5_Dusklight/stargazers)
[![release](https://img.shields.io/github/v/release/griches/PS5_Dusklight)](https://github.com/griches/PS5_Dusklight/releases/latest)
[![Track Dusklight](https://github.com/griches/PS5_Dusklight/actions/workflows/track-dusklight.yml/badge.svg)](https://github.com/griches/PS5_Dusklight/actions/workflows/track-dusklight.yml)
[![licence](https://img.shields.io/badge/licence-GPL--3.0%20as%20built-blue)](LICENSING.md)

A PS5 homebrew port of [Dusklight](https://github.com/TwilitRealm/dusklight), the
reverse-engineered reimplementation of a classic GameCube adventure. It draws
through Dusklight's own renderer ([Aurora](https://github.com/encounter/aurora) on
Dawn's WebGPU) on RADV, Mesa's Vulkan driver, from the
[PS5 Vulkan](https://github.com/mihawk-99/PS5_Vulkan) stack.

It needs a PS5 that already runs homebrew, and a disc image of the game that you
provide. No game data, Nintendo artwork, Sony software or keys are included, here
or in a build.

This is an unofficial port. It is not part of the Dusklight project and is not
supported by it: please do not take PS5 problems to them.


## Start here

Use the original PS5 port’s release page and follow the installation steps below. You need a homebrew-capable PS5 and your own supported GameCube disc image.

[Original project releases](https://github.com/griches/PS5_Dusklight/releases)

## Status

Tested on one console, on 2026-10-10 and 11, with the GameCube USA disc (GZ2E01).
"Seen" means it ran there and was watched, or read in the console's log; nothing
else is claimed.

| Area | Seen on the console | Not yet verified |
| --- | --- | --- |
| Start-up | Finds the disc image in the title's folder, boots into the game | Exit back to the home screen from the game's own menu |
| Rendering | 3840x2160 on a 59.94 Hz display, several minutes of play with no crash | Frame rate over a long session; 120 Hz; later areas of the game |
| Saving | A memory card file is created, and a save survived closing and restarting the title | |
| Button prompts | The DualSense's symbols on the game's buttons, on the file select and in play: Cross (A), Circle (B), Square (X), Triangle (Y), R1 (Z) | Other prompts (L, R, Start, the D-pad and stick pictures); a changed button mapping; the other regions' discs |
| Input | A DualSense plays the game | Each button of the mapping; rumble; a second controller |
| Sound | | Everything: the driver opens, nobody has confirmed what it sounds like |
| Shader cache | Aurora's pipeline cache opens and is written | That it is reused after a restart |

Known limits:

- **Objects can appear a frame late the first time a scene shows them.** Aurora
  compiles each new render pipeline on a worker thread and skips the draw until
  it is ready, as it does on every platform. They are cached once compiled.
- **Disc images: GameCube `.iso` or `.ciso` only.** Upstream reads RVZ, GCZ, WIA
  and WBFS through a Rust library; this port has its own small reader in its
  place (`ps5/nod/`). Wii discs are not supported.
- **No code mods, no updater, no Discord presence, no network.** They are turned
  off in this build. The mods in Dusklight's `mods/` folder (the randomizer, the
  Luau runtime and the rest) are code mods, so none is bundled, and a mod that
  needs the Luau runtime does not run. An asset-only `.dusk` (textures, files
  that replace the disc's) put in `/data/homebrew/PPSA99305/mods/` is listed and
  can be switched on in the Mods menu. Online mods cannot be browsed.
- **"Disc not verified" on the menu is expected.** The disc is found, not
  chosen, so it is never hashed; and a `.ciso` leaves out the disc's filler
  data, so its hash could not match the original's anyway.
- **The button symbols follow the default mapping.** The game draws a button as
  a coloured shape with a white letter, each letter a texture of its own; the
  port replaces those five textures with symbols from Kenney's Input Prompts
  (www.kenney.nl, CC0; `ps5/art/kenney/`, cut to size by `ps5/art/make-glyphs.py`,
  shipped in `res/ps5-glyphs/`, loaded as texture replacements named for the
  USA disc's textures), and turns the green tint of the A button blue. They say Cross for A, Circle for B, Square for X,
  Triangle for Y and R1 for Z, which is Dusklight's default mapping: remap the
  buttons and the symbols no longer match. A replacement of your own for the
  same texture wins, and turning texture replacements off in the settings turns
  these off too.
- **Texture packs: loose files or a `.dusk`, `.png` or `.dds`.** Files named the
  way Dolphin names them (`tex1_256x128_e6a4c7be9bf48305_14.dds`) are picked up
  from `/data/homebrew/PPSA99305/userdata/TwilitRealm/Dusklight/texture_replacements/`
  and its subfolders, or from the `textures/` folder of a `.dusk`. A `.dds` may
  be uncompressed 32-bit RGBA or BGRA, BC1 (DXT1), BC3 (DXT5), BC5 or BC7, with
  or without mipmaps; this port also takes the sRGB-tagged variants of those,
  which upstream refuses. BC2 (DXT3), BC4, BC6H and ASTC are not loaded, and a
  compressed texture's width and height must be multiples of 4. Seen on the
  console on 2026-10-12 with three test files in the loose folder: BC7 tagged
  sRGB with mipmaps, DXT5, and uncompressed RGBA; a real texture pack has not
  been tried. The game makes that folder at its first start, and from this
  build on opens it to the FTP server at every start: with v0.2.0 an upload
  into it is refused until the folder's permissions are changed.
- **No file dialog.** The disc image is found by where it is, not chosen.

## Install

Download `Dusklight-PS5-vX.Y.Z.zip` from the
[latest release](https://github.com/griches/PS5_Dusklight/releases/latest) and
unpack it: it holds one folder, `PPSA99305`. (Or build that folder yourself, see
Build.) It contains no game data.

**What the console needs**

- A PS5 that runs homebrew, with etaHEN (or an equivalent) loaded.
- ShadowMountPlus, which shows the folders in `/data/homebrew` as titles on the
  home screen.
- An FTP server on the console to copy files with (port 2121 here).

**Steps**

1. Unpack the release (or build: the result is the folder `dist/PPSA99305/`).
2. Copy that whole folder to the console as `/data/homebrew/PPSA99305/`, so that
   you have:

   ```text
   /data/homebrew/PPSA99305/eboot.bin
   /data/homebrew/PPSA99305/sce_sys/      (param.json, icon0.png, pic0.dds, pic1.dds)
   /data/homebrew/PPSA99305/sce_module/libc.prx
   /data/homebrew/PPSA99305/res/          (fonts and the menus' documents)
   /data/homebrew/PPSA99305/licenses/
   ```

   Copy `sce_sys/icon0.png` with the first upload: ShadowMountPlus will not
   register a title without its icon, and after two failed tries it skips that
   title until it is restarted.
3. Copy your disc image into the same folder, under any name ending in `.iso` or
   `.ciso`:

   ```text
   /data/homebrew/PPSA99305/your-disc.iso
   ```

   It has to be there, not elsewhere in `/data`: a title can only see its own
   folder. The game takes the first image it finds and remembers it.
4. Wait a few seconds for "Dusklight" to appear on the home screen, and start it.

Saves and settings are written to `/data/homebrew/PPSA99305/userdata/`. Copying a
new build over the folder leaves them, and the disc image, alone.

**The disc image.** Dusklight's own terms apply: dump your own copy of the game
([how](https://wiki.dolphin-emu.org/index.php?title=Ripping_Games)). If your dump
is RVZ or another compressed format, convert it to `.iso` with
[Dolphin](https://dolphin-emu.org/) or `nodtool` first.

## Credits

- [Dusklight](https://github.com/TwilitRealm/dusklight) by Twilit Realm and its
  contributors, on the [Twilight Princess decompilation](https://github.com/zeldaret/tp).
- [Aurora](https://github.com/encounter/aurora), [Borealis](https://github.com/encounter/borealis),
  [nod](https://github.com/encounter/nod) and the Dawn fork by Luke Street (encounter) and contributors.
- [PS5_Vulkan](https://github.com/mihawk-99/PS5_Vulkan), [PS5_Mesa](https://github.com/mihawk-99/PS5_Mesa),
  [PS5_PayloadSDK](https://github.com/mihawk-99/PS5_PayloadSDK) and the
  [PS5 Vulkan Template](https://github.com/mihawk-99/PS5_VulkanTemplate) by Mihawk:
  the driver, the platform layer and the tools this is built with.
- [ps5-payload-dev/sdk](https://github.com/ps5-payload-dev/sdk) by John Törnblom.
- Mesa and RADV, Dawn, SDL, and the libraries listed in [LICENSING.md](LICENSING.md).
- Kenney (www.kenney.nl) for the button symbols, from Input Prompts (CC0).

## Licence

See [LICENSING.md](LICENSING.md). In short: the port's own files are MIT or Zlib,
one tool is GPL-3.0, and a built title is GPL-3.0 because of what it links. The
game itself is Nintendo's and is not part of this.

[Build and developer documentation](BUILDING.md)
