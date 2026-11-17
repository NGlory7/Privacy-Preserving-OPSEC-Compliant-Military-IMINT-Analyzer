# Evaluation

Produced by `python tools/evaluate.py` on the Wikimedia Commons set built by
`python tools/build_eval_set.py` (licences and sources in `eval/manifest.csv`).
The set is small, so treat every number as a rough indication with wide error bars.

- Images: **150** · device: `cuda` · median time per image (detection + one CLIP crop): **0.19 s**
- Outbound network attempts during the run: **0** (network guard active)

## 1. Detection (image level)

Share of images where OWLv2 finds the expected category at each score threshold.

| Set | n | ≥0.10 | ≥0.15 | ≥0.20 | ≥0.25 | ≥0.30 | ≥0.40 |
|---|---|---|---|---|---|---|---|
| weapon → weapon found | 54 | 98% | 98% | 96% | 94% | 93% | 85% |
| vehicle → vehicle found | 36 | 97% | 97% | 97% | 94% | 89% | 89% |
| camouflage → personnel found | 48 | 75% | 75% | 75% | 69% | 67% | 44% |
| negatives → weapon (false alarm) | 12 | 0% | 0% | 0% | 0% | 0% | 0% |
| negatives → vehicle (false alarm) | 12 | 17% | 8% | 8% | 0% | 0% | 0% |

Default thresholds used by the app: `{'personnel': 0.3, 'weapon': 0.22, 'vehicle': 0.25, 'gear': 0.25}`.

## 2. Fine-grained identification

Top-k accuracy over the catalog entries of that kind (chance level in brackets).
*Few-shot* = the other eval photos of each class are used as reference images (leave-one-out),
which is what you get by putting a few photos in `data/reference/<kind>/<id>/`.

| Kind | n | classes | zero-shot top-1 | zero-shot top-3 | few-shot top-1 | few-shot top-3 | crop from detector |
|---|---|---|---|---|---|---|---|
| weapon | 54 | 9/9 | 52% (11%) | 78% (33%) | 57% | 91% | 96% |
| vehicle | 36 | 6/6 | 78% (17%) | 94% (50%) | 78% | 94% | 94% |
| camouflage | 48 | 8/14 | 46% (7%) | 62% (21%) | 56% | 69% | 67% |

### Per class (zero-shot top-1 / few-shot top-1)

**weapon:** `wpn_ak12` 2/6 / 3/6 · `wpn_ak74m` 3/6 / 1/6 · `wpn_akm` 3/6 / 4/6 · `wpn_hk416` 4/6 / 3/6 · `wpn_m4a1` 5/6 / 3/6 · `wpn_mpt76` 1/6 / 5/6 · `wpn_pkm` 4/6 / 2/6 · `wpn_qbz95` 5/6 / 5/6 · `wpn_rpg7` 1/6 / 5/6

**vehicle:** `veh_bmp2` 2/6 / 2/6 · `veh_bradley_m2a2` 6/6 / 5/6 · `veh_btr82a` 5/6 / 5/6 · `veh_kirpi` 6/6 / 6/6 · `veh_t72b3` 4/6 / 4/6 · `veh_toyota_hilux` 5/6 / 6/6

**camouflage:** `camo_cadpat_tw` 3/6 / 2/6 · `camo_emr` 4/6 / 4/6 · `camo_flecktarn` 4/6 / 3/6 · `camo_m81_woodland` 0/6 / 2/6 · `camo_m90` 4/6 / 4/6 · `camo_marpat_woodland` 3/6 / 5/6 · `camo_multicam` 2/6 / 5/6 · `camo_type07` 2/6 / 2/6

## What this does not measure

- **Catalog classes without eval images** (no free photos found on Commons): `gear_fast_helmet`, `gear_6b47_helmet`, `camo_turkish_digital`, `camo_atacs_fg`, `camo_idf_olive`, `camo_partizan_autumn`, `camo_black_standard_tactical`, `camo_east_africa_woodland`.
- **Camouflage images without a detected person** (fabric swatches, uniforms on display) are classified on the whole image; see the *crop from detector* column.
- **Hard negatives:** the negatives are everyday COCO scenes (people with bats, skis, rackets…); tractors, hunters or airsoft players were not tested.
- **Personnel / helmet thresholds** are untuned starting values; only weapon and vehicle thresholds were checked against the sweep above.
- **Box accuracy (IoU):** labels are image-level, not hand-drawn boxes.
- **Face redaction recall:** the set has no face annotations. Always check the redacted image yourself.
- **Attribution:** country ranking is a deterministic function of the identifications above and the
  hand-set catalog weights; it is only as good as those inputs.
