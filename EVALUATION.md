# Evaluation

Produced by `python tools/evaluate.py` on the Wikimedia Commons set built by
`python tools/build_eval_set.py` (licences and sources in `eval/manifest.csv`).
The set is small, so treat every number as a rough indication with wide error bars.

- Images: **69** · device: `cuda` · median time per image (detection + one CLIP crop): **0.17 s**
- Outbound network attempts during the run: **0** (network guard active)

## 1. Detection (image level)

Share of images where OWLv2 finds the expected category at each score threshold.

| Set | n | ≥0.10 | ≥0.15 | ≥0.20 | ≥0.25 | ≥0.30 | ≥0.40 |
|---|---|---|---|---|---|---|---|
| weapon → weapon found | 38 | 100% | 100% | 100% | 97% | 95% | 87% |
| vehicle → vehicle found | 19 | 95% | 95% | 95% | 95% | 84% | 84% |
| negatives → weapon (false alarm) | 12 | 0% | 0% | 0% | 0% | 0% | 0% |
| negatives → vehicle (false alarm) | 12 | 17% | 8% | 8% | 0% | 0% | 0% |

Default thresholds used by the app: `{'personnel': 0.3, 'weapon': 0.22, 'vehicle': 0.25, 'gear': 0.25}`.

## 2. Fine-grained identification

Top-k accuracy over the catalog entries of that kind (chance level in brackets).
*Few-shot* = the other eval photos of each class are used as reference images (leave-one-out),
which is what you get by putting a few photos in `data/reference/<kind>/<id>/`.

| Kind | n | classes | zero-shot top-1 | zero-shot top-3 | few-shot top-1 | few-shot top-3 | crop from detector |
|---|---|---|---|---|---|---|---|
| weapon | 38 | 7/9 | 42% (11%) | 71% (33%) | 55% | 84% | 100% |
| vehicle | 19 | 4/6 | 74% (17%) | 89% (50%) | 74% | 89% | 95% |

### Per class (zero-shot top-1 / few-shot top-1)

**weapon:** `wpn_ak12` 2/6 / 5/6 · `wpn_ak74m` 3/6 / 1/6 · `wpn_akm` 3/6 / 4/6 · `wpn_m4a1` 5/6 / 3/6 · `wpn_mpt76` 1/6 / 5/6 · `wpn_pkm` 1/2 / 0/2 · `wpn_rpg7` 1/6 / 3/6

**vehicle:** `veh_bmp2` 2/6 / 3/6 · `veh_bradley_m2a2` 6/6 / 5/6 · `veh_btr82a` 5/6 / 5/6 · `veh_kirpi` 1/1 / 1/1

## What this does not measure

- **Not measured yet: camouflage.** The eval set has no images for it; run `python tools/build_eval_set.py` (Wikimedia Commons rate-limits it heavily, so it can take hours) and re-run this script.
- **Catalog classes without eval images** are not covered by the numbers above (images per label: `{'negative': 12, 'veh_bmp2': 6, 'veh_bradley_m2a2': 6, 'veh_btr82a': 6, 'veh_kirpi': 1, 'wpn_ak12': 6, 'wpn_ak74m': 6, 'wpn_akm': 6, 'wpn_m4a1': 6, 'wpn_mpt76': 6, 'wpn_pkm': 2, 'wpn_rpg7': 6}`).
- **Hard negatives:** the negatives are everyday COCO scenes (people with bats, skis, rackets…); tractors, hunters or airsoft players were not tested.
- **Personnel / helmet thresholds** are untuned starting values; only weapon and vehicle thresholds were checked against the sweep above.
- **Box accuracy (IoU):** labels are image-level, not hand-drawn boxes.
- **Face redaction recall:** the set has no face annotations. Always check the redacted image yourself.
- **Attribution:** country ranking is a deterministic function of the identifications above and the
  hand-set catalog weights; it is only as good as those inputs.
