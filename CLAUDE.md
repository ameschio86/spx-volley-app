# SPX Volley — App Genitori — Project Brief

> Documento di contesto per Claude Code / repo GitHub. Contiene tutte le decisioni confermate finora con Ale (Segretario CDA SPX Volley). Da usare come `CLAUDE.md` nella root del progetto.

---

## 1. Cos'è il progetto

Una **Progressive Web App (PWA)**, non un'app nativa. Motivazioni:
- Nessun account sviluppatore Apple (€99/anno), nessuna revisione store, nessun team di sviluppo dedicato
- Installabile su Android e iOS via "Aggiungi a schermata Home" — diventa un'icona a tutti gli effetti
- Zero costo, manutenzione minima

**Stack consigliato**: HTML/CSS/JS statico, `manifest.json` per installabilità, service worker minimo per funzionamento offline-friendly delle pagine statiche (no dati sensibili cachati). Nessun backend necessario: le azioni "pesanti" (iscrizione, pagamento, ordini) sono link esterni verso sistemi già esistenti (Gestionale SPX / TeamOrg).

## 2. Identità visiva

**Logo**: scudo SPX oro (SB stilizzato) con "1972" in alto, file sorgente `logo_nuovo_Giallo.png` (664×900px, PNG trasparente, oro pieno #FFC72C circa su trasparenza) — fornito da Ale, va incluso negli assets del progetto.

**Palette**:
- Sfondo: nero/antracite pieno `#0a0a0a` / `#0d0d0f`
- Oro primario: `#FFC72C`
- Card/superfici: `#141414`, bordi `#232323`
- Verde conferma (usato con parsimonia): `#3ecf5c` su sfondo `#0f1f10` / bordo `#1f3a20`
- Giallo/oro per box di attenzione: sfondo `#2b2306`, bordo `#4a3d0a`, testo `#e0d3a0`

**Font**: Poppins (400/600/700/800/900), coerente col brand esistente. Titoli in peso 800-900.

**Elementi decorativi ricorrenti**: linee geometriche sottili oro in angolo alto-destra (stile "constellation"), badge/pill oro pieno con testo nero per CTA, divider oro corto (40-50px) sotto i titoli.

**Direzione estetica scelta**: mix tra stile "futurista pulito" e "pallavolo-centrico", poi convertito nello **stile reale del club** (dalle slide Instagram fornite da Ale: nero pieno, scudo oro, font condensed bold, check verde/warning triangolare per gli stati). Niente rosa/fucsia nell'app — quello è un codice riservato ai contenuti social femminili, non entra nell'app.

**Layout preferito**: liste verticali di righe (icon + label + descrizione breve + freccia), non griglie di icone. Più leggibile su mobile per un genitore che deve scegliere velocemente.

## 3. Struttura dell'app (menu principale)

5 voci, in quest'ordine:

1. **Iscrizione**
2. **Quote**
3. **Materiale**
4. **Moduli**
5. **FAQ**

Contatti/segnalazioni non è una voce a sé — vive dentro la FAQ e come riga "Dubbi? spxvolley@gmail.com" in fondo a ogni schermata.

---

## 4. Contenuto confermato per sezione

### 4.1 Iscrizione

**Link diretto (bottone "ISCRIVITI", URL mai visibile a video)**:
```
http://teamorg.it/2231
```

**Nessuna data di chiusura iscrizioni** — restano aperte tutta la stagione (apertura 3 agosto 2026, poi confermata/festeggiata sui social come "Si riparte!").

**Struttura schermata**: bivio a due bottoni, nessun colore extra oltre oro/nero:
- 🆕 **"Prima volta SPX"**
- 🏐 **"Sei già atleta SPX"**

**Sotto-slide "Prima volta SPX"** (3 step numerati):
1. Inserisci il codice fiscale **dell'atleta** (mai quello del genitore) → il sistema non lo trova, riconosce come nuovo
2. Compila i campi vuoti:
   - Dati anagrafici dell'atleta
   - Dati del genitore/tutore (se minorenne)
   - Foto della visita medica + data di scadenza
   - Squadra 2026/27
3. Salva → "Ecco, il gioco è fatto"

Bottone finale: **ISCRIVITI** (pieno, oro)

**Sotto-slide "Sei già atleta SPX"**:
- Box "DA SAPERE" in cima:
  - Visita medica valida e non in scadenza? → non devi fare nulla
  - Visita scaduta e hai già in mano quella nuova? → segui i passaggi sotto
- 4 step numerati:
  1. Inserisci il codice fiscale dell'atleta → sistema riconosce, dati già compilati
  2. Vai alla visita medica → unico campo che può servire aggiornare
  3. Cancella la vecchia, carica la nuova → sostituisci foto certificato + data scadenza
  4. Salva → "Ecco, il gioco è fatto"

Bottone finale: **AGGIORNA I DATI** (ghost, bordo oro)

**Meccanismo di sfondo importante**: il sistema manda in automatico un **alert via email un mese prima della scadenza** della visita medica di ogni atleta. Se il genitore non aggiorna, l'alert si ripete ogni mese finché non agisce.

**Nota tecnica**: cambio squadra/categoria a stagione in corso è gestito **internamente dai dirigenti**, il genitore non se ne occupa — non va menzionato nell'app come azione del genitore.

---

### 4.2 Quote

**Tabella prezzi per categoria (ordine crescente)**:

| Categoria | Quota |
|---|---|
| S3 / Minivolley | €400 |
| Amatoriali | €470 |
| Squadre U12 M/F e superiori | €550 |

(Serie CM e Serie CF — le prime squadre — giocano gratis, ma questa riga **non va mostrata** nell'app: informazione interna, non serve comunicarla ai genitori delle giovanili.)

**Rateizzazione**:
- S3 / Minivolley: €220 + €180
- U12 M/F e superiori: €300 + €250
- Amatoriali: **gestione a parte**, pagano mensilmente di persona in palestra ("se vengono") — troppa variabilità per uno schema fisso, per ora non mostrare rate per questa categoria nell'app, solo la nota "pagamento gestito direttamente in palestra"

**Scadenze**: 1ª rata entro fine settembre 2026, saldo/2ª rata entro gennaio 2027

**Cosa è incluso**: accesso palestra tutta la stagione (settembre-maggio) + assicurazione FIPAV
**Cosa NON è incluso**: merchandising/materiale (sezione a parte, non menzionare qui)

**Nota sconto famiglia** (senza importo specifico, non inventare percentuali):
> "Più figli/e in società? Sono previste agevolazioni per i nuclei familiari con più atleti — contatta la segreteria per i dettagli."

**Sotto-slide "Come pagare"** (accessibile da bottone dedicato, non inline nella slide principale):

- **Intestatario**: Gruppo Sportivo San Pio X — Ass. Sportiva
- **IBAN**: `IT79D0707213000000411616` — deve essere **selezionabile e copiabile** con un tap (bottone "COPIA" + clipboard API, fallback a selezione testo)
- **Causale obbligatoria**: Nome Cognome atleta — Squadra — Prima rata/Seconda rata/Saldo
  - Esempio: *"Mario Rossi — Under 16 Maschile — Prima rata"*
- **Spiegazione del perché è obbligatoria** (box di attenzione, non solo un avviso secco):
  > "Senza nome, cognome e squadra il bonifico arriva ma resta anonimo. Non riusciamo a risalire a chi ha pagato, e rischiamo di segnarti come 'in attesa' anche se hai già versato."

---

### 4.3 Materiale — **in corso di definizione, domande aperte**

Ancora da chiarire con Ale:
1. Link diretto pubblico allo store TeamOrg (per parallelismo con l'iscrizione)
2. Cosa si ordina da lì — solo extra facoltativi o anche capi obbligatori del kit gara
3. Tempi di consegna indicativi
4. Policy riconsegna divisa gara a fine stagione
5. Gestione taglie sbagliate/resi — chi contattare

### 4.4 Moduli — bozza, da completare

Sezione a lista verticale (non griglia), ogni riga = nome modulo + bottone "Scarica PDF". Contenuti previsti (da confermare quali esistono già come PDF e quali vanno creati):
- Richiesta visita medica ASL Emilia-Romagna (minorenni)
- Richiesta visita medica studio privato convenzionato (se esiste davvero)
- Richiesta crediti scolastici studente-atleta
- Consenso pubblicazione immagini minore (privacy/social)
- Eventuali altri moduli societari

### 4.5 FAQ — bozza da validare

Struttura ad accordion, raggruppata per temi:
- 🩺 Visite mediche e certificati
- 🚌 Trasferte e trasporti
- 🛡️ Assicurazione e infortuni
- 📱 Privacy e foto minori
- 📞 Contatti e segnalazioni

Bozza di 20 domande-tipo già scritta in conversazione precedente, con alcune risposte da fonti reali (FIPAV, ASL Emilia-Romagna) e altre segnate "da definire" in attesa di dati societari specifici.

---

## 5. Mockup HTML già realizzati (riferimento visivo)

File di riferimento per lo stile approvato da Ale (nero/oro, scudo reale, layout a lista):
- `spx-app-stile-reale.html` — home/menu principale, approvata
- `spx-iscrizione-bivio.html` — bivio Prima volta/Già atleta
- `spx-prima-volta.html` — sotto-slide nuovo atleta
- `spx-gia-atleta.html` — sotto-slide già iscritto/aggiornamento visita
- `spx-quote.html` — slide quote con tabella e rate
- `spx-come-pagare.html` — sotto-slide con IBAN copiabile

Questi vanno presi come riferimento di stile e struttura, non necessariamente come codice finale da riusare 1:1 — ma la palette, il font, gli spazi e il tono dei testi sono quelli approvati.

---

## 6. Contatti di riferimento

- **Email società**: spxvolley@gmail.com
- **TeamOrg (contatto tecnico)**: Gianmario Malfatto — per problemi tecnici sul Gestionale/store

---

## 7. Cose da NON fare

- Non mostrare mai l'URL grezzo dei link esterni (iscrizione, materiale) — sempre bottoni con label pulita
- Non inventare cifre (sconto famiglia, tempi di consegna) se non confermate da Ale
- Non menzionare il cambio squadra come azione del genitore — è gestito dai dirigenti
- Non mostrare la riga "Serie CM/CF gratis" nell'app pubblica
- Nessun rosa/fucsia nell'estetica app (riservato ai contenuti social femminili)
- Nessun colore oltre nero/oro/verde-conferma/giallo-attenzione — mantenere la palette essenziale
