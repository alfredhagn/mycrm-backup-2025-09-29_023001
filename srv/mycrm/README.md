# MyCRM Installation (Debian 12)

## Schritte:
1. `unzip mycrm.zip && cd mycrm`
2. `bash setup.sh`
3. Browser öffnen: `http://<deine-ip>:8000/`
4. Login: `alfred` / `ddcm9677`

## VOIP
- sipgate Click-to-Call: Environment `SIPGATE_TOKEN_ID`, `SIPGATE_TOKEN`, optional `SIPGATE_CALLER` or `SIPGATE_DEVICE_ID`.
- Fritz!Box Call-Liste: Environment `FRITZBOX_PASSWORD` (and optional `FRITZBOX_ADDRESS`, default `fritz.box`).
- Call-Liste unter `/crm/voip/fritz/calllist/`. Kontakt-Detail: Button für sipgate.
