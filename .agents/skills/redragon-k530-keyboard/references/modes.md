# Redragon K530 Lighting Modes Reference

| Mode Name (CLI) | Mode ID (Hex) | Vendor Name | Color Mode | Speed Adjust | Direction Adjust |
|:---|:---:|:---|:---:|:---:|:---:|
| `breathing` | `0x01` | Breathing | Custom RGB | Yes | No |
| `wave` | `0x02` | Color Wave | Rainbow / RGB | Yes | Yes |
| `winding` | `0x03` | Winding paths | Rainbow / RGB | Yes | Yes |
| `trial` | `0x04` | The trial of light | Rainbow / RGB | Yes | No |
| `breathing2` | `0x05` | Alternating Breathing | Custom RGB | Yes | No |
| `static` | `0x06` | Normally on | Custom RGB | No | No |
| `pass` | `0x07` | Pass without trace | Rainbow / RGB | Yes | No |
| `ripple` | `0x08` | Ripple graff | Rainbow / RGB | Yes | No |
| `fast_run` | `0x09` | Fast run without trace | Rainbow / RGB | Yes | Yes |
| `snow` | `0x0A` | Snow winter jasmine | Rainbow / RGB | Yes | No |
| `flowers` | `0x0B` | Flowers blooming / Spectrum | Rainbow | Yes | No |
| `swift` | `0x0C` | Swift action | Rainbow / RGB | Yes | Yes |
| `hurricane` | `0x0D` | Hurricane | Rainbow / RGB | Yes | Yes |
| `accumulate` | `0x0E` | Accumulate | Rainbow / RGB | Yes | Yes |
| `digital` | `0x0F` | Digital Times | Rainbow / RGB | Yes | No |
| `both_ways` | `0x10` | Both ways / Visor | Rainbow / RGB | Yes | Yes |
| `surmount` | `0x11` | Surmount | Rainbow / RGB | Yes | Yes |
| `furious` | `0x12` | Fast and the Furious | Rainbow / RGB | Yes | Yes |
| `coastal` | `0x14` | Coastal / Custom Profile | Per-key | No | No |

## Parameters
- **Brightness**: 0 (Off) to 4 (100% Brightness)
- **Speed**: 0 (Fastest) to 10 (Slowest)
- **Direction**: 0 (Left / Default), 1 (Right / Reverse)
- **Random Color Flag**: 0 (Use specified R,G,B), 1 (Automatic cycling / Rainbow)
