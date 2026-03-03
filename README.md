# Study With PinTa Elite (Windows Desktop A/L Performance Engine)

A full offline Windows desktop application for Sri Lankan A/L preparation built with **Python + PyQt5 + SQLite + matplotlib + plyer**.

## Platform & Runtime
- Windows desktop (offline)
- No login system
- No internet required
- Local SQLite database (`study_with_pinta.db` auto-created)
- Timezone: `Asia/Colombo`
- Subjects included: Combined Maths, Physics, ICT
- Exam target: August 1

## Implemented Modules
- Smart Dashboard (live Sri Lanka time, exam countdown, daily/weekly study minutes, focus/discipline, subject balance, prediction, recommendation)
- Final Sprint Mode (< 30 days)
- Intelligent Timetable (7-day planning, start/pause/stop/done/partial + live countdown)
- Lock Mode (blocked app list + distraction tracking during active sessions)
- AI Prediction Engine (A/B/C probability + confidence)
- Past Paper Analytics (accuracy + trends + weak areas)
- Subject rotation recommendation
- Streak and discipline engine
- Reflection popup at 9:30 PM
- Advanced statistics page with multi-graph analytics
- System notifications (session start, 5 mins remaining, completion, 6PM no-study warning)
- Local data backup from Settings

## Project Folder Structure

```text
Authix/
├── main.py
├── requirements.txt
├── README.md
├── study_with_pinta.db               # auto-created on first run
└── backup_study_with_pinta_*.db      # generated when backup is triggered
```

## Database Tables
Auto-created on first run:
- `sessions`
- `timetable_blocks`
- `past_papers`
- `reflections`
- `subject_stats`
- `discipline_logs`
- `predictions`
- `app_settings`

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build Windows .exe (PyInstaller)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py --name StudyWithPinTaElite
```

Generated executable:
- `dist/StudyWithPinTaElite.exe`

## Distribution Steps
1. Install Python (3.11+ recommended).
2. Install dependencies with `pip install -r requirements.txt`.
3. Build with:
   - `pyinstaller --onefile --windowed main.py --name StudyWithPinTaElite`
4. Zip the project folder or package `dist/StudyWithPinTaElite.exe`.
5. On target PC, extract and run `StudyWithPinTaElite.exe`.

## Notes
- Lock mode process detection is Windows-only (active process check).
- App remains usable on non-Windows, but active-process distraction detection is skipped.
