# Eidolon Vhar Spellbook

A spellbook for phones for the 2024 fifth edition rules, made for the Eidolon Vhar campaign. This is an unofficial fan project, not made or endorsed by Wizards of the Coast. Install it from your browser ("Add to Home screen") and it works offline.

- All 339 spells from the free SRD 5.2.1, with search and filters
- Several characters, each with their own spellbook and prepared spells
- Spell slot tracker with short and long rests, and concentration
- Write your own homebrew spells and share them by copy and paste

Your data stays on your own phone. Use the backup in the Homebrew tab now and then.

## Licence

This app includes material from the System Reference Document 5.2.1 ("SRD 5.2.1") by Wizards of the Coast LLC, available at https://www.dndbeyond.com/srd. The SRD 5.2.1 is licensed under the Creative Commons Attribution 4.0 International License, available at https://creativecommons.org/licenses/by/4.0/legalcode.

## Updating

The app is built from `src/`: `core.html` (the app), `srd.json` (SRD spells) and `campaign.json` (built-in Eidolon Vhar spells). Run `python3 src/build.py src . <version>` with a higher version number each time, then commit. The version number makes installed apps pick up the update.
