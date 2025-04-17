# Unraid Templates by fgrfn

Dies ist eine Sammlung meiner persönlichen Docker-Templates für Unraid.

## 📦 CoreControl

**CoreControl** ist eine moderne Web-App zur Überwachung und Steuerung von CPU-Funktionen und Energiemanagement auf Linux-Systemen.  
Sie basiert auf **Next.js**, **Node.js** und **Prisma** und ist vollständig containerisiert.

### 🖥️ WebUI

- Adresse: [http://[Unraid-IP]:3000](http://[Unraid-IP]:3000)
- Port: `3000` (konfigurierbar)

### ⚙️ Docker Template Info

| Feld             | Beschreibung                                                                 |
|------------------|------------------------------------------------------------------------------|
| Repository       | `fgrfn/corecontrol:latest`                                                   |
| Netzwerk         | `bridge` (Standard)                                                          |
| Port             | `3000:3000`                                                                  |
| Umgebungsvariable| `DATABASE_URL` (optional – z. B. PostgreSQL-Verbindung)                      |
| Icon             | ![icon](https://raw.githubusercontent.com/crocofied/CoreControl/main/public/icon.png) |
| Originalprojekt  | [github.com/crocofied/CoreControl](https://github.com/crocofied/CoreControl) |

### 🛠️ Installation

1. Datei `corecontrol.xml` in folgenden Pfad kopieren:  
   `/boot/config/plugins/dockerMan/templates-user/`

2. Im Unraid WebUI → **Docker → Add Container → Template: CoreControl**

## 📂 Struktur

```plaintext
corecontrol/
├── corecontrol.xml      # Unraid Template
```

---

## 💬 Kontakt

Fragen, Feedback oder PRs willkommen:  
📬 [github.com/fgrfn](https://github.com/fgrfn)

## 🧑‍💻 Lizenz

Dieses Repository basiert teilweise auf [crocofied/CoreControl](https://github.com/crocofied/CoreControl) und steht unter der gleichen Lizenz (AGPL-3.0).
