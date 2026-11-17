# Reference photos (optional, improves identification)

Put a few photos of each item you care about here, one folder per catalog id:

```
data/reference/
├── camouflage/
│   ├── camo_multicam/        3–10 photos of people wearing MultiCam
│   └── camo_emr/
├── weapon/
│   └── wpn_ak74m/
├── vehicle/
│   └── veh_t72b3/
└── gear/
    └── gear_6b47_helmet/
```

The classifier then compares each crop with these photos as well as with the text
prompts (few-shot). `EVALUATION.md` shows how much this helps on the eval set.
Folder names must match the `id` fields in `src/database/*.py`.
Photos are only read locally; they are never uploaded anywhere.
