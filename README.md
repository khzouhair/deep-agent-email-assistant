# 🤖 Deep Agent Email Assistant

Un assistant intelligent basé sur une architecture **multi-agents** pour lire, analyser, rechercher et répondre automatiquement aux emails de manière professionnelle.

Ce projet utilise **LangChain** et **LangGraph** pour orchestrer un agent principal (coordinateur) capable de déléguer des tâches à des sous-agents spécialisés.

---

## ✨ Fonctionnalités

- 📧 Lecture du dernier email
- 🧠 Planification des tâches avec TODOs
- 🔍 Recherche web automatique si nécessaire
- ✍️ Rédaction d’une réponse professionnelle
- 🗂️ Gestion de fichiers virtuels (context / research)
- 🤝 Délégation intelligente à des sous-agents
- 📤 Export des résultats en JSON

---

## 🧠 Architecture des agents

### Agent principal (Coordinator)
- Analyse l’email
- Planifie les actions
- Délègue les tâches aux sous-agents
- Assemble la réponse finale

### Sous-agents

- **Research Agent**  
  ➜ Recherche et synthèse d’informations depuis le web

- **Response Agent**  
  ➜ Rédaction de la réponse email finale

---

## 📁 Structure du projet

```text
email_agent/
│
├── deep_agent_email_assistant.py   # Implémentation principale de l’agent
├── run_email_agent.py              # Script d’exécution
│
├── email_agent_state.py            # Définition de l’état de l’agent
├── email_tools.py                  # Outils liés aux emails
├── search_tools.py                 # Recherche web et raisonnement
├── file_tools.py                   # Système de fichiers virtuel
├── todo_tools.py                   # Gestion des TODOs
├── subagent_tools.py               # Délégation et sous-agents
├── prompts.py                      # Prompts système des agents
│
└── README.md
## 📌 Objectif pédagogique

Ce projet permet de :

- Comprendre les **agents LLM**
- Implémenter une **architecture multi-agents**
- Gérer un **état complexe**
- Construire un **assistant IA professionnel**

---

## 👩‍💻 Auteur

**Khadija Zouhair**
