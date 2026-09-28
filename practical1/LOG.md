# Log — Practical I

All timestamps local session time (session runs 2026-09-28, Africa/Kampala UTC+03:00 for the
requester; the underlying container clock may differ — timestamps below are wall-clock at time of
action as recorded by the tool environment).

---

### 2026-09-28 — Stage 1: Sourcing
- Cloned `masakhane-io/masakhane-ner` (commit `ba5843cd08aa491d5f96a5e809e71eb9ec461391`,
  authored 2025-10-15) read-only, via `git clone --depth 1`.
- Located Luganda folders: `data/lug/` (MasakhaNER 1.0) and `MasakhaNER2.0/data/lug/`
  (MasakhaNER 2.0). Chose `data/lug/` (MasakhaNER 1.0) — see DECISIONS.md D1.
- Copied `train.txt` (34,431 lines), `dev.txt` (3,971 lines), `test.txt` (10,248 lines) verbatim
  into `practical1/data/raw/`. Verified byte-identical via MD5 checksum against source.
- Read root `README.md`, `data/README.md`, and `LICENSE` in the source repo. Recorded dataset
  info, primary/secondary classification, license (CC BY-NC 4.0 for data, Apache 2.0 for code),
  and citation in `DATASET_INFO.md`.
- Wrote `DECISIONS.md` with D1–D4.
