# Build and developer documentation

[Back to the user guide](README.md)

## Build

The build runs on Linux (x86-64 or arm64; on a Mac, in a Linux VM) with Mihawk's
stack beside this repository:

```text
somewhere/
  PS5_Dusklight/     this repository
  PS5_Vulkan/        https://github.com/mihawk-99/PS5_Vulkan   (with its RADV release archive built)
  PS5_Mesa/          https://github.com/mihawk-99/PS5_Mesa
  PS5_PayloadSDK/    https://github.com/mihawk-99/PS5_PayloadSDK
```

Set that stack up first, by its own instructions, until `PS5_Vulkan` has
`.deps/native/radv-release/lib/libvulkan_radeon.ps5.a` and
`build/host/ps5-native-tool`. It needs **LLVM 22**: RADV built with an older clang
does not link into a title. Then:

```sh
git clone https://github.com/griches/PS5_Dusklight.git
cd PS5_Dusklight
ps5/tools/build.sh
```

`build.sh` does the rest, and the first run takes a while:

1. checks out Dusklight (`vendor/dusklight`) with Aurora and Borealis, and applies
   `ps5/patches/` to them;
2. fetches Dawn and SDL3 at the revisions Aurora pins into `.deps/`, and patches
   them for the console;
3. installs the payload SDK at this port's pin;
4. configures Dusklight's own CMake build with the SDK's toolchain and
   `ps5/cmake/ps5-game.cmake`, compiles about 3,000 files, links with RADV and
   writes `dist/PPSA99305/`.

Other tools, all in `ps5/tools/`:

| Tool | What it does |
| --- | --- |
| `deploy.sh` | Uploads `dist/PPSA99305/` over FTP (the console's address is `PS5_HOST` in `PS5_Vulkan/.env`). It never touches the disc image or `userdata/`. |
| `run.sh` | Launches the title through PS5_Vulkan's control payload and follows its log; symbolises a crash. |
| `package-release.sh VERSION` | Packs `dist/PPSA99305/` as a release zip with `SOURCE.txt`, the revision of every part. Refuses if a disc image or a save is in the folder. |
| `build-triangle.sh` | Builds a one-triangle WebGPU test in the game's place: the first thing to run when Dawn or the driver changes. |
| `vm.sh TOOL` | From macOS, runs one of the above inside a Lima VM named `ps5`. |
| `update-dusklight.sh` | Moves to upstream Dusklight's latest revision and re-applies the patches. |
| `check-patches.sh` | Says whether the Dawn and SDL3 patches apply to what Aurora now pins. |


## Keeping up with Dusklight

`vendor/dusklight` is a submodule at an upstream revision; nothing of Dusklight is
copied or forked here. What the console needs changed in Dusklight, Aurora and
Borealis is three small patches in `ps5/patches/`; Dawn and SDL3 have theirs
there too.

A [scheduled workflow](.github/workflows/track-dusklight.yml) runs
`update-dusklight.sh` every day. If the patches still apply to upstream's newest
revision, it commits that revision, so a fresh clone builds against the latest
Dusklight the patches fit. If one does not, it commits nothing and opens an issue.
It cannot build the game, so a revision it commits is not known to compile or
run: the Status table above is for the revision it was tested at
(`34a144a493`).


## How it works

```text
  Dusklight (the game's code)                     vendor/dusklight
        |
  Aurora ........ GameCube GX, pads, cards, DVD   vendor/dusklight/extern/aurora
        |              |               |
      Dawn           SDL3             nod
   (WebGPU)     ps5/sdl drivers    ps5/nod: .iso and .ciso
        |
  Vulkan: RADV + PS5 winsys, VK_KHR_display       PS5_Mesa, PS5_Vulkan
        |
  PS5 GPU
```

- **Dawn.** The fork Aurora uses already had a console port (Nintendo Switch):
  a Vulkan driver linked into the program and a native-window surface.
  `ps5/patches/dawn.patch` adds the PS5 beside it: RADV's entry point in place of
  a Vulkan library, and the console's one output as a `VK_KHR_display` surface.
- **SDL3.** Threads, time and files are FreeBSD's. `ps5/sdl/` adds a video driver
  (one display, a window that is the screen), an audio driver (AudioOut, 48 kHz
  stereo) and a joystick driver that presents each controller as a DualSense.
- **nod.** Aurora reads discs through nod, a Rust library. There is no Rust
  toolchain for the console, so `ps5/nod/nod.cpp` implements the part of nod's C
  API that is called, for plain and CISO GameCube images.
- **The console's quirks**, each found the hard way and explained where it is
  handled: constructors that ran in reverse (`ps5/tools/cc-init-array.sh`), an
  `lstat` that does not work for a title and other missing libc functions
  (`ps5/src/shims.c`), and where a title may write (`ps5/src/startup.c`).

