# applemusic-mcp

**Contrôler Apple Music depuis Claude (ou ton terminal) sur Linux.** Sans clé API ni compte développeur, et sans aucune dépendance Python.

```
toi    › mets-moi du Kavinsky
claude › play_song("Kavinsky Nightcall")
       ▶ Kavinsky – Nightcall  (Nightcall)
```

Il n'existe pas de connecteur Apple Music officiel pour les assistants IA. Ce projet en fabrique un avec deux choses qui existent déjà :

1. **[Sidra](https://github.com/wimpysworld/sidra)**, un client Apple Music pour Linux, qui s'expose sur D-Bus via **MPRIS** et accepte `OpenUri` en `https`.
2. **L'API iTunes Search (`itunes.apple.com/search`)**, publique et sans authentification. Son `trackId` est le même que l'ID du catalogue Apple Music.

```
« Kavinsky Nightcall »
        │  itunes.apple.com/search  (country=ca)
        ▼
   25 candidats ──► score « meilleure version » ──► trackId 1442447970
        │
        │  D-Bus : org.mpris.MediaPlayer2.Player.OpenUri
        ▼
   https://music.apple.com/song/1442447970  ──►  Sidra joue la chanson
```

## Ce que ça fait

| | CLI `applemusic` | Outil MCP |
|---|---|---|
| Chercher + jouer la meilleure version | `play "artiste titre"` | `play_song` |
| Voir les candidats et leur score | `search "..."` | `search_songs` |
| Jouer une liste dans l'ordre | `queue liste.txt` | `play_queue` |
| État / arrêt de la file | — | `queue_status`, `stop_queue` |
| Ce qui joue | `now` | `now_playing` |
| Pause, reprise, suivant, précédent | `pause` `resume` `toggle` `next` `prev` | `control` |
| Volume, shuffle | `vol 0.7`, `shuffle on` | `set_volume`, `set_shuffle` |

### « La meilleure version »

Une recherche comme « Help I'm Alive » retourne l'original, des sessions live, des covers en quatuor à cordes, des remixes… Le score :

- **pénalise les variantes non demandées** : slowed, sped up, remix, live, acoustic, instrumental, karaoke, iTunes Session…
- **pénalise toute parenthèse non demandée** (`(Pete Heller's Stylus)`), mais pas les `(feat. …)` ;
- **favorise la variante quand tu la demandes** : `pursuit super slowed` donne la version super slowed ;
- **pénalise les covers** : si l'artiste demandé existe dans les résultats, un autre artiste est rejeté ;
- **refuse de deviner** : si le titre et l'artiste ne concordent pas, rien ne joue. Par exemple, une toune retirée du catalogue canadien ne sera pas remplacée par une homonyme.

`applemusic search "..."` montre le score de chaque candidat pour comprendre un choix.

## Installation

Prérequis : Linux avec D-Bus (`busctl`, fourni par systemd), Python ≥ 3.9, et Sidra ouvert et connecté à ton compte Apple Music.

```bash
git clone https://github.com/theodorebeaupre-prog/applemusic-mcp.git ~/Developer/applemusic-mcp
ln -s ~/Developer/applemusic-mcp/applemusic     ~/.local/bin/applemusic
ln -s ~/Developer/applemusic-mcp/applemusic-mcp ~/.local/bin/applemusic-mcp
```

### Avec Claude Code

```bash
claude mcp add --scope user applemusic -- ~/.local/bin/applemusic-mcp
```

Les outils apparaissent dans la prochaine session.

### Avec un autre client MCP (Claude Desktop, etc.)

```json
{
  "mcpServers": {
    "applemusic": { "command": "/home/<toi>/.local/bin/applemusic-mcp" }
  }
}
```

## Files d'attente

Sidra n'offre pas l'interface MPRIS `TrackList`, donc on ne peut pas lui envoyer une file. `queue` ouvre chaque chanson une par une : il surveille la position et passe à la suivante à la fin de la toune, ou dès que tu changes de chanson dans Sidra (le skip est respecté).

Format de liste : une chanson par ligne. Les numéros et les tirets sont tolérés, et les lignes `#` sont des commentaires.

```
# SHIP MODE
1. Trent Reznor & Atticus Ross – In Motion
Kavinsky - Nightcall
isq pursuit super slowed
```

Exemple complet : [`examples/shipmode.txt`](examples/shipmode.txt).

Avec le MCP, la file tourne dans un **process détaché** et continue même si le chat se ferme. Son état vit dans `~/.cache/applemusic/` (`queue.pid`, `queue.log`, `queue.txt`). `play_song` arrête la file d'abord, sinon elle prendrait ta chanson pour un skip.

## Limites connues

- **Sidra seulement** pour jouer une chanson précise : Firefox, Chromium et Zen exposent MPRIS mais pas `OpenUri`. Les autres commandes (pause, next…) pourraient marcher avec d'autres lecteurs en changeant `BUS`.
- **Catalogue par pays** : la recherche se fait dans le catalogue `ca`. Change `COUNTRY` dans `applemusic` pour le tien.
- **Pas d'accès à ta bibliothèque** : pas de lecture de tes playlists, de likes ni de création de playlists. Ça demanderait MusicKit, avec un developer token et un user token.
- Les messages de l'outil sont en français.

## Comment ça marche (le MCP)

`applemusic-mcp` est un serveur MCP stdio écrit à la main : du JSON-RPC 2.0, un message par ligne, sans SDK. Il importe `applemusic` comme module et redirige son `stdout` pendant chaque appel, parce qu'en stdio, stdout est réservé au protocole et un seul `print()` corromprait la session.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Les tests du scoring sont hors-ligne : la recherche iTunes est simulée.

## Transparence

Ce projet a été conçu et testé avec Théodore Beaupré. Le code d'implémentation a été majoritairement généré par un agent IA (Claude Code).

Projet non affilié à Apple. Apple Music est une marque d'Apple Inc.

## Licence

[MIT](LICENSE)
