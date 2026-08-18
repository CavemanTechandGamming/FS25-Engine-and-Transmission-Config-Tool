# Factory Transmission Matrix

Reference for all factory transmission presets. Gear ratios are real-world factory values. Reverse ratios are stored **positive** in JSON (Giants convention). Top speed is **km/h** in presets and the generator.

Source: Caveman real-world ratio + top-speed matrices (2026-08-17). JSON presets: `Presets/Transmission/*.json`.

**Eaton Fuller 13/18:** dual Lo/Hi numbers are baked as separate forward gears (splitters).

**NV4500:** same gear ratios; gas preset **169 km/h**, diesel preset **153 km/h**.

**TorqShift 5R110:** 6 mechanical configs; ECU drives **5 speeds** (1-2-3-5-6). Cold-weather strategy gear **1.09** omitted in JSON.

## Summary

| Preset | Type | Fwd | Rev | Top gear | Max km/h | Cost ($) | JSON |
|--------|------|----:|----:|---------:|---------:|---------:|:----:|
| Allison 1000 Series 5-Speed | Automatic | 5 | 1 | 0.71 | 160 | 8000 | Yes |
| Allison 1000 Series 6-Speed | Automatic | 6 | 1 | 0.61 | 158 | 8500 | Yes |
| Allison 10L1000 | Automatic | 10 | 1 | 0.63 | 158 | 8000 | Yes |
| BorgWarner T18 | Manual | 4 | 1 | 1.0 | 105 | 5000 | Yes |
| Eaton Fuller RTLO-18913A | Manual | 13 | 2 | 0.73 | 137 | 12000 | Yes |
| Eaton Fuller RTLO-22918B | Manual | 18 | 4 | 0.73 | 145 | 15000 | Yes |
| Ford C6 | Automatic | 3 | 1 | 1.0 | 160 | 6500 | Yes |
| Ford E4OD | Automatic | 4 | 1 | 0.71 | 177 | 8000 | Yes |
| Ford TorqShift 5R110 | Automatic | 5 | 1 | 0.71 | 153 | 4500 | Yes |
| Hydra-Matic 4L80-E | Automatic | 4 | 1 | 0.75 | 177 | 8500 | Yes |
| Hydra-Matic 700R4 | Automatic | 4 | 1 | 0.7 | 185 | 7500 | Yes |
| Hydra-Matic TH400 | Automatic | 3 | 1 | 1.0 | 160 | 6500 | Yes |
| Isuzu MSA-5G | Manual | 5 | 1 | 0.78 | 128 | 5500 | Yes |
| Mazda M5OD-R2 | Manual | 5 | 1 | 0.8 | 169 | 5500 | Yes |
| Muncie SM465 | Manual | 4 | 1 | 1.0 | 105 | 5000 | Yes |
| New Process NP435 | Manual | 4 | 1 | 1.0 | 105 | 5000 | Yes |
| New Venture NV4500 | Manual | 5 | 1 | 0.75 | 169 | 6500 | Yes |
| New Venture NV4500 Diesel | Manual | 5 | 1 | 0.75 | 153 | 6500 | Yes |
| Toyota W56 | Manual | 5 | 1 | 0.85 | 137 | 4500 | Yes |
| Willys BorgWarner T-90 | Manual | 3 | 1 | 1.0 | 88 | 3500 | Yes |
| ZF S5-42 | Manual | 5 | 1 | 0.76 | 160 | 6000 | Yes |

## Gear ratio matrix

| Factory name | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th–10th / splits | Reverse |
|--------------|----:|----:|----:|----:|----:|----:|-------------------|--------:|
| New Process NP435 | 6.69 | 3.34 | 1.66 | 1.00 | — | — | — | 8.26 |
| Muncie SM465 | 6.55 | 3.58 | 1.70 | 1.00 | — | — | — | 6.09 |
| BorgWarner T18 | 6.32 | 3.09 | 1.69 | 1.00 | — | — | — | 7.44 |
| Hydra-Matic TH400 | 2.48 | 1.48 | 1.00 | — | — | — | — | 2.07 |
| Ford C6 | 2.46 | 1.46 | 1.00 | — | — | — | — | 2.18 |
| Hydra-Matic 700R4 | 3.06 | 1.63 | 1.00 | 0.70 | — | — | — | 2.29 |
| Ford E4OD | 2.71 | 1.54 | 1.00 | 0.71 | — | — | — | 2.18 |
| Ford TorqShift 5R110 | 3.11 | 2.20 | 1.54 | 1.00 | 0.71 | — | — | 2.88 |
| Mazda M5OD-R2 | 3.91 | 2.24 | 1.49 | 1.00 | 0.80 | — | — | 3.70 |
| ZF S5-42 | 5.72 | 2.94 | 1.61 | 1.00 | 0.76 | — | — | 5.24 |
| New Venture NV4500 (Gas) | 5.61 | 3.04 | 1.67 | 1.00 | 0.75 | — | — | 5.61 |
| New Venture NV4500 (Diesel) | 5.61 | 3.04 | 1.67 | 1.00 | 0.75 | — | — | 5.61 |
| Hydra-Matic 4L80-E | 2.48 | 1.48 | 1.00 | 0.75 | — | — | — | 2.07 |
| Allison 1000 Series (5-Spd) | 3.10 | 1.81 | 1.41 | 1.00 | 0.71 | — | — | 4.49 |
| Allison 1000 Series (6-Spd) | 3.10 | 1.81 | 1.41 | 1.00 | 0.71 | 0.61 | — | 4.49 |
| Allison 10L1000 (10-Spd) | 4.70 | 2.99 | 2.15 | 1.80 | 1.52 | 1.28 | 7th 1.00 · 8th 0.85 · 9th 0.69 · 10th 0.63 | 5.06 |
| Eaton Fuller RTLO-18913A | 12.31 | 8.60 | 6.22 | 4.54 | 3.38 | 2.47/2.11 | 6th 1.74/1.49 · 7th 1.23/1.05 · 8th 0.86/0.73 | 13.23 / 3.78 |
| Eaton Fuller RTLO-22918B | 14.40/12.29 | 8.56/7.30 | 6.05/5.16 | 4.38/3.74 | 3.20/2.73 | 2.28/1.94 | 6th 1.62/1.38 · 7th 1.17/1.00 · 8th 0.86/0.73 | 4 reverses (see detail) |
| Toyota W56 | 3.95 | 2.14 | 1.38 | 1.00 | 0.85 | — | — | 4.09 |
| Willys BorgWarner T-90 | 2.80 | 1.55 | 1.00 | — | — | — | — | 3.79 |
| Isuzu MSA-5G | 4.98 | 2.74 | 1.65 | 1.00 | 0.78 | — | — | 4.62 |

## Top speed matrix (km/h)

| Factory name | Top gear ratio | Maximum speed (km/h) |
|--------------|---------------:|---------------------:|
| Willys BorgWarner T-90 | 1.00 | 88 |
| New Process NP435 | 1.00 | 105 |
| Muncie SM465 | 1.00 | 105 |
| BorgWarner T18 | 1.00 | 105 |
| Toyota W56 | 0.85 | 137 |
| Eaton Fuller RTLO-18913A | 0.73 | 137 |
| Isuzu MSA-5G | 0.78 | 128 |
| Eaton Fuller RTLO-22918B | 0.73 | 145 |
| Hydra-Matic TH400 | 1.00 | 160 |
| Ford C6 | 1.00 | 160 |
| ZF S5-42 | 0.76 | 160 |
| Allison 1000 Series (5-Spd) | 0.71 | 160 |
| Allison 1000 Series (6-Spd) | 0.61 | 158 |
| Allison 10L1000 (10-Spd) | 0.63 | 158 |
| Mazda M5OD-R2 | 0.80 | 169 |
| New Venture NV4500 (Gas) | 0.75 | 169 |
| Hydra-Matic 4L80-E | 0.75 | 177 |
| Ford E4OD | 0.71 | 177 |
| Hydra-Matic 700R4 | 0.70 | 185 |
| New Venture NV4500 (Diesel) | 0.75 | 153 |
| Ford TorqShift 5R110 | 0.71 | 153 |

## Per-transmission baked gears (JSON)

### Allison 1000 Series 5-Speed

- **File:** `Allison 1000 Series 5-Speed.json` · **Type:** Automatic · **Cost:** $8000 · **Top speed:** 160 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 3.1 |
| 2 | 1.81 |
| 3 | 1.41 |
| 4 | 1.0 |
| 5 | 0.71 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 4.49 |

### Allison 1000 Series 6-Speed

- **File:** `Allison 1000 Series 6-Speed.json` · **Type:** Automatic · **Cost:** $8500 · **Top speed:** 158 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 3.1 |
| 2 | 1.81 |
| 3 | 1.41 |
| 4 | 1.0 |
| 5 | 0.71 |
| 6 | 0.61 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 4.49 |

### Allison 10L1000

- **File:** `Allison 10L1000.json` · **Type:** Automatic · **Cost:** $8000 · **Top speed:** 158 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 4.7 |
| 2 | 2.99 |
| 3 | 2.15 |
| 4 | 1.8 |
| 5 | 1.52 |
| 6 | 1.28 |
| 7 | 1.0 |
| 8 | 0.85 |
| 9 | 0.69 |
| 10 | 0.63 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 5.06 |

### BorgWarner T18

- **File:** `BorgWarner T18.json` · **Type:** Manual · **Cost:** $5000 · **Top speed:** 105 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| Granny | 6.32 |
| 2 | 3.09 |
| 3 | 1.69 |
| 4 | 1.0 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 7.44 |

### Eaton Fuller RTLO-18913A

- **File:** `Eaton Fuller RTLO-18913A.json` · **Type:** Manual · **Cost:** $12000 · **Top speed:** 137 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| Lo | 12.31 |
| 1 | 8.6 |
| 2 | 6.22 |
| 3 | 4.54 |
| 4 | 3.38 |
| 5 | 2.47 |
| 5H | 2.11 |
| 6 | 1.74 |
| 6H | 1.49 |
| 7 | 1.23 |
| 7H | 1.05 |
| 8 | 0.86 |
| 8H | 0.73 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R Lo | 13.23 |
| R Hi | 3.78 |

### Eaton Fuller RTLO-22918B

- **File:** `Eaton Fuller RTLO-22918B.json` · **Type:** Manual · **Cost:** $15000 · **Top speed:** 145 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| Lo | 14.4 |
| LoH | 12.29 |
| 1 | 8.56 |
| 1H | 7.3 |
| 2 | 6.05 |
| 2H | 5.16 |
| 3 | 4.38 |
| 3H | 3.74 |
| 4 | 3.2 |
| 4H | 2.73 |
| 5 | 2.28 |
| 5H | 1.94 |
| 6 | 1.62 |
| 6H | 1.38 |
| 7 | 1.17 |
| 7H | 1.0 |
| 8 | 0.86 |
| 8H | 0.73 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R1 | 15.46 |
| R2 | 13.19 |
| R3 | 3.89 |
| R4 | 3.31 |

### Ford C6

- **File:** `Ford C6.json` · **Type:** Automatic · **Cost:** $6500 · **Top speed:** 160 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 2.46 |
| 2 | 1.46 |
| 3 | 1.0 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 2.18 |

### Ford E4OD

- **File:** `Ford E4OD.json` · **Type:** Automatic · **Cost:** $8000 · **Top speed:** 177 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 2.71 |
| 2 | 1.54 |
| 3 | 1.0 |
| 4 | 0.71 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 2.18 |

### Ford TorqShift 5R110

- **File:** `Ford TorqShift 5R110.json` · **Type:** Automatic · **Cost:** $4500 · **Top speed:** 153 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 3.11 |
| 2 | 2.2 |
| 3 | 1.54 |
| 4 | 1.0 |
| 5 | 0.71 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 2.88 |

### Hydra-Matic 4L80-E

- **File:** `Hydra-Matic 4L80-E.json` · **Type:** Automatic · **Cost:** $8500 · **Top speed:** 177 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 2.48 |
| 2 | 1.48 |
| 3 | 1.0 |
| 4 | 0.75 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 2.07 |

### Hydra-Matic 700R4

- **File:** `Hydra-Matic 700R4.json` · **Type:** Automatic · **Cost:** $7500 · **Top speed:** 185 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 3.06 |
| 2 | 1.63 |
| 3 | 1.0 |
| 4 | 0.7 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 2.29 |

### Hydra-Matic TH400

- **File:** `Hydra-Matic TH400.json` · **Type:** Automatic · **Cost:** $6500 · **Top speed:** 160 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 2.48 |
| 2 | 1.48 |
| 3 | 1.0 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 2.07 |

### Isuzu MSA-5G

- **File:** `Isuzu MSA-5G.json` · **Type:** Manual · **Cost:** $5500 · **Top speed:** 128 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 4.98 |
| 2 | 2.74 |
| 3 | 1.65 |
| 4 | 1.0 |
| 5 | 0.78 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 4.62 |

### Mazda M5OD-R2

- **File:** `Mazda M5OD-R2.json` · **Type:** Manual · **Cost:** $5500 · **Top speed:** 169 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 3.91 |
| 2 | 2.24 |
| 3 | 1.49 |
| 4 | 1.0 |
| 5 | 0.8 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 3.7 |

### Muncie SM465

- **File:** `Muncie SM465.json` · **Type:** Manual · **Cost:** $5000 · **Top speed:** 105 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| Granny | 6.55 |
| 2 | 3.58 |
| 3 | 1.7 |
| 4 | 1.0 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 6.09 |

### New Process NP435

- **File:** `New Process NP435.json` · **Type:** Manual · **Cost:** $5000 · **Top speed:** 105 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| Granny | 6.69 |
| 2 | 3.34 |
| 3 | 1.66 |
| 4 | 1.0 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 8.26 |

### New Venture NV4500

- **File:** `New Venture NV4500.json` · **Type:** Manual · **Cost:** $6500 · **Top speed:** 169 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 5.61 |
| 2 | 3.04 |
| 3 | 1.67 |
| 4 | 1.0 |
| 5 | 0.75 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 5.61 |

### New Venture NV4500 Diesel

- **File:** `New Venture NV4500 Diesel.json` · **Type:** Manual · **Cost:** $6500 · **Top speed:** 153 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 5.61 |
| 2 | 3.04 |
| 3 | 1.67 |
| 4 | 1.0 |
| 5 | 0.75 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 5.61 |

### Toyota W56

- **File:** `Toyota W56.json` · **Type:** Manual · **Cost:** $4500 · **Top speed:** 137 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 3.95 |
| 2 | 2.14 |
| 3 | 1.38 |
| 4 | 1.0 |
| 5 | 0.85 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 4.09 |

### Willys BorgWarner T-90

- **File:** `Willys BorgWarner T-90.json` · **Type:** Manual · **Cost:** $3500 · **Top speed:** 88 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 2.8 |
| 2 | 1.55 |
| 3 | 1.0 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 3.79 |

### ZF S5-42

- **File:** `ZF S5-42.json` · **Type:** Manual · **Cost:** $6000 · **Top speed:** 160 km/h

**Forward**

| Gear | Ratio |
|------|------:|
| 1 | 5.72 |
| 2 | 2.94 |
| 3 | 1.61 |
| 4 | 1.0 |
| 5 | 0.76 |

**Reverse**

| Gear | Ratio |
|------|------:|
| R | 5.24 |

