# Nama Project

## Problem
Program backup yang otomatis ignore unnecessary file,
membutuhkan path target dan peth destination untuk menjalankan program,
otomatis men copy file kecuali ignore ke folder destination

## Features
- 🔴 Input path target and dst
- 🔴 Copy file 1 per satu dan buat directory nya
- 🔴 Check eksistensi directory dan cek jika bukan file
- 🟡 copy file menggunakan loop dan melakukan filtering untuk ignore list
- 🟢 default nama backup = _backup
- 🟢 

## Struktur
- File_Backuper
  - .venv
  - app
    - main.py
    - ignore
  - PLAN.md
  - .gitignore

## Alur
- User memasukan input manual untuk target dan destination path
- Program mengecek eksistensi target
- Program mengecek eksistensi destination, jika dst ada tapi file akan error, jika tidak ada maka akan dibuat otomatis
- memetakan isi di dalam target
- melakukan looping untuk setiap item, jika ignore maka skip, jika directory, masuk ke dalamnya

## Pseudocode


## Catatan / Ideas
