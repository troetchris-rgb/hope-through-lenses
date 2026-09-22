# Hope through Lenses – Persönliche Landing Page (Schritt 1)

Datum: 2026-09-22

## Zweck

Persönliche, mehrseitige Website als Visitenkarte für die Ansprache
internationaler NGOs (Tierschutz/Naturschutz). Erster Schritt eines größeren
Vorhabens; spätere Erweiterungen (z.B. Blog/Storytelling) sind nicht Teil
dieser Spec.

Zielgruppe: NGO-Entscheider:innen (siehe `hope-through-lenses-branding`
Skill) – professionell, aber warm angesprochen ("Sie").

## Leitprinzip

Die Seite soll **emotional und sympathisch** wirken, nicht steril-corporate.
Vorbild: das "Hope Through The Lens"-Framework (Wonder → Connection →
Knowledge → Action → Hope) aus dem Branding-Skill. Business-Inhalte
(Leistungen, Werdegang) werden über persönliche Geschichten und Bilder
transportiert statt als nüchterne Aufzählung.

## Seitenstruktur

Vier statische HTML-Seiten mit gemeinsamem Layout (Header/Nav/Footer):

1. **Start (`index.html`)** – emotionaler Einstieg (Bild + Claim „Gemeinsam
   handeln. Gemeinsam Wirkung schaffen."), kurze persönliche Mission,
   Überleitung zu Über mich / Leistungen.
2. **Über mich (`ueber-mich.html`)** – persönliche Geschichte: warum diese
   Mission, Tierarzt-/Wissenschafts-/Executive-Hintergrund erzählerisch statt
   als CV-Liste.
3. **Leistungen (`leistungen.html`)** – Angebot für NGOs, formuliert als „so
   helfen wir gemeinsam eure Wirkung zu vergrößern", nicht als Preisliste/
   Leistungskatalog.
4. **Kontakt (`kontakt.html`)** – einladender Call-to-Action + Kontaktformular.

## Inhalt & Ton

Siehe `hope-through-lenses-branding` Skill Abschnitt 5 (Tonalität) und
Abschnitt 7 (Storytelling-Framework). Texte werden von Claude neu entworfen
und dem Nutzer zur Freigabe vorgelegt (nicht vorab final).

## Visuelle Gestaltung

- Basis: Farben/Typografie/Komponenten aus `webdesign-guidelines-hope-through-lenses`
  (Blau `#1B4B73`, Petrol `#0E4B44`, Mintblau `#8ED9D0`, Schwarz, Weiß;
  Fraunces für Überschriften, Inter für Fließtext).
- Abweichung vom rein professionellen Look: mehr Mintblau/Petrol-Wärme statt
  viel kühles Blau/Weiß, großzügige emotionale Bildflächen, organische statt
  scharfkantige Formsprache, wo sinnvoll.
- Bildmaterial: eigenes Material des Nutzers (Fotos von ihm, Projekten,
  Tieren/Natur) – keine Stockfotos, keine gestellten Szenen (siehe Branding
  Abschnitt 6, Bildsprache).

## Technik

- **Stack:** statisches HTML/CSS (Tailwind-Klassen) + minimales Vanilla-JS
  (z.B. mobiles Menü). Kein Framework, kein Build-Prozess.
- **Struktur im Repo:**
  - `index.html`, `ueber-mich.html`, `leistungen.html`, `kontakt.html`
  - `styles.css` (gemeinsam)
  - `/images` für Fotos
- **Kontaktformular:** Netlify Forms (kein eigenes Backend), Benachrichtigung
  an die E-Mail-Adresse des Nutzers.
- **Responsive:** Mobile-first, gleichwertige Darstellung auf
  Handy/Tablet/Desktop.
- **Barrierefreiheit:** aussagekräftige Alt-Texte, ausreichender Kontrast
  trotz warmer Töne, klare Schriftgrößen/-hierarchie.
- **Performance:** Bilder komprimiert/optimiert eingebunden.
- **SEO-Basics:** individuelle `<title>` und Meta-Description je Seite.

## Hosting & Deployment

- **Hosting:** Netlify (kostenlos, automatisches HTTPS, Git-basiertes
  Auto-Deployment, eingebautes Formular-Handling).
- **Domain:** noch keine vorhanden – Domain-Wahl/-Registrierung ist nicht
  Teil dieser ersten Umsetzung; Start über die kostenlose Netlify-Subdomain,
  eigene Domain kann später angebunden werden.
- **Versionierung:** lokales Git-Repository im Projektordner, das mit
  Netlify verbunden wird, sodass ein `git push` automatisch neu deployt.

## Out of Scope (Schritt 1)

- Blog/Storytelling-Bereich
- Mehrsprachigkeit
- CMS/Redaktionssystem
- Eigene Domain-Registrierung
- Analytics/Tracking

## Testing

- Manuelle Prüfung aller 4 Seiten in Desktop- und Mobile-Ansicht im Browser
  vor Abschluss.
- Kontaktformular-Test (Testeinsendung prüfen, ob Netlify-Benachrichtigung
  ankommt) nach Deployment.
