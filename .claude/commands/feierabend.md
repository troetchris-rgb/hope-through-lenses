---
description: Überträgt die heutigen Punkte in die Daily Note im Second-Brain-Vault (Feierabend-Ritual)
argument-hint: "[optional: zusätzliche Notiz für heute]"
---

# Feierabend – Daily Note füllen

Übertrage den heutigen Stand in die Daily Note im Obsidian-Vault. Kein Rückfragen, wenn der Ablauf klar ist – einfach ausführen und am Ende kurz berichten, was eingetragen wurde.

## Zielort

- Vault: `/Users/admin/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second Brain`
- Ordner: `00 Inbox/Daily Notes/`
- Dateiname: `<YYYY-MM-DD>, <Wochentag auf Deutsch>.md` (z. B. `2026-08-31, Montag.md`)
- Datum = heute. Wochentag deutsch: Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Samstag, Sonntag.

## Ablauf

1. **Datum + Wochentag** von heute bestimmen (`date +%F` und Wochentag) und daraus den Dateinamen bilden.
2. **Prüfen, ob die Daily Note schon existiert.**
   - Wenn nein: aus `Templates/Daily Note Template.md` anlegen. Dabei `{{title}}` durch `<YYYY-MM-DD>, <Wochentag>` und `{{date:YYYY-MM-DD}}` durch das heutige Datum ersetzen.
   - Wenn ja: bestehenden Inhalt einlesen und nur ergänzen, nichts überschreiben oder löschen.
3. **Inhalte aus dem heutigen Gespräch einsortieren** – in die passenden Abschnitte, jeweils als neue Stichpunkte an das Bestehende angehängt:
   - `## 🎯 Fokus heute` – offene Aufgaben / To-dos, die heute besprochen wurden, als `- [ ]`.
   - `## 📥 Capture` – lose Ideen, Links, Gedankenfetzen aus dem Gespräch.
   - `## 📝 Notizen` – ausformulierte Erkenntnisse, Entscheidungen, Ergebnisse.
   - `## 🔗 Bezug` – `[[Wikilinks]]` zu Projekten/Areas, an denen heute gearbeitet wurde.
   - `## 🌙 Kurzer Rückblick` – 2–4 Sätze: Was ist heute vorangekommen? Was wandert in die nächste Organize-Runde?
4. Falls `$ARGUMENTS` gesetzt ist, den Text zusätzlich unter `## 📥 Capture` aufnehmen.
5. **Datei speichern.**
6. **Prüfen, ob heute noch etwas anderes ins Second Brain gehört** – über die Daily Note hinaus. Das ganze heutige Gespräch daraufhin durchgehen, ob dabei etwas entstanden ist, das dauerhaft an anderer Stelle im Vault gespeichert werden sollte, z. B.:
   - ein **neues oder verändertes Projekt** (`01 Projects/` – eigener Ordner + gleichnamige Index-Note aus `Templates/Projekt Template.md`, mit `status:`, `ziel:`, `fertig-wenn:`)
   - eine **Area** (`02 Areas/`), die berührt oder neu relevant wurde
   - eine **Resource / Referenz / ein Link**, der es wert ist behalten zu werden (`03 Resources/`, aus `Templates/Resource Template.md`)
   - ein **wiederverwendbarer Prompt** (`03 Resources/Prompts/`)
   - ein **Meeting-Ergebnis** (`Templates/Meeting Template.md`)
   - eine **Entscheidung oder ein Rechercheergebnis**, das sonst nur in der Daily Note verschwinden würde
   - Für jeden Fund: entweder direkt die passende Note anlegen/ergänzen (mit korrektem Frontmatter: block-style `tags:` + `created:` ISO-Datum) **oder**, wenn unklar wohin, als Stichpunkt mit Vorschlag unter `## 📥 Capture` der Daily Note vermerken und im Bericht als „noch einzusortieren“ nennen.
   - Wenn nichts weiter anfiel: kurz „sonst nichts fürs Second Brain“ im Bericht festhalten.
7. **Bericht.** In 3–6 Zeilen zusammenfassen: welche Punkte in welchen Abschnitt der Daily Note geschrieben wurden (mit Dateipfad) und welche weiteren Notes im Vault angelegt/ergänzt wurden bzw. dass es sonst nichts gab.

## Regeln

- Bestehende Einträge in der Datei bleiben unverändert – nur anhängen.
- Deutsch, Stichpunkte, knapp.
- Frontmatter (`tags:`, `created:`) nicht anfassen, wenn die Datei schon existiert.
- Wenn heute im Gespräch für einen Abschnitt nichts anfiel, diesen Abschnitt einfach so lassen.
- PARA-Konventionen des Vaults einhalten: Projekte/Areas als eigener Ordner mit gleichnamiger Index-Note; `Templates/` nicht als Vorlage-Quelle verändern; keine neuen Plugins voraussetzen (kein Dataview/Templater).
- Neue Notes außerhalb der Daily Note nur anlegen, wenn der Inhalt klar dauerhaft relevant ist – im Zweifel lieber als Vorschlag in `## 📥 Capture` vermerken.
