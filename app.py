#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 22:53:02 2025

@author: ibrahima-bailodiallo
"""

import os  # Pour sécuriser la clé API
from dotenv import load_dotenv
import chainlit as cl
from groq import Groq
import time
import asyncio  # Pour gérer l'animation



# Charger les variables d'environnement du fichier .env
load_dotenv()
# 🔒 Sécurisation de la clé API (NE PAS exposer dans le code)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("⚠️ ERREUR : La clé API GROQ est manquante. Définissez la variable d'environnement 'GROQ_API_KEY'.")

client = Groq(api_key=api_key)

# 🔐 Avertissement sur la confidentialité
CONFIDENTIALITY_NOTICE = """
⚠️ **Confidentialité & Sécurité**  
Les informations que vous fournissez sont strictement utilisées pour une évaluation préliminaire et ne remplacent **PAS** une consultation médicale.  
🚨 *Veuillez ne pas entrer de données personnelles sensibles (nom, adresse, numéro de sécurité sociale, etc.).*
"""

# Prompt système amélioré avec alerte sur la fiabilité
system_prompt = """**Rôle** : Assistant Médical Cardio-Analytique
**Strict Protocol** :
1. N'utilisez QUE les données fournies
2. Demandez les informations manquantes
3. Pas de suppositions ou de création de données
4. Signalez les limitations des informations
5. Vérifiez les incohérences et mentionnez les incertitudes

**Réponse Requise** :
🛑 Si données manquantes : 
- Lister les informations nécessaires
- Expliquer leur importance clinique

✅ Si données complètes :
- Analyse selon guidelines ESC 2023
- Calcul des scores de risque
- Recommandations personnalisées
- **Mentionner toute incertitude et recommander une consultation si nécessaire**
"""

# Questions médicales
initial_questions = {
    "diabete": "🩸 **Avez-vous un diagnostic de diabète ?** (Oui/Non)",
    "hta": "💓 **Souffrez-vous d'hypertension artérielle ?** (Oui/Non)",
    "tabac": "🚬 **Consommez-vous du tabac ?** (Nombre cigarettes/jour)",
    "antecedents": "🧬 **Avez-vous des antécédents cardiaques familiaux ?** (Décrivez brièvement)"
}

additional_questions = {
    "symptomes": "⚠️ **Quels sont vos symptômes principaux ?** (ex: douleurs thoraciques, essoufflement)",
    "duree_symptomes": "⏳ **Depuis combien de temps avez-vous ces symptômes ?**",
    "medicaments": "💊 **Prenez-vous actuellement des médicaments ?** (Si oui, lesquels ?)",
    "examens": "📊 **Quels sont les résultats de vos examens médicaux ?** (ECG, échocardiogramme, etc.)",
    "analyses": "🧪 **Avez-vous les résultats de vos analyses de sang ?** (lipides, glycémie, etc.)",
    "parents": "👨‍👩‍👧‍👦 **Quel est l'âge et les antécédents médicaux de vos parents ?** (si connus)"
}

async def heart_animation():
    """Affiche une animation de battements de cœur."""
    beats = ["❤️", "💗"]
    for _ in range(1):
        for beat in beats:
            await cl.Message(content=f"# {beat} **Prediagnostique en cours...**").send()
            await asyncio.sleep(0.5)

async def collect_data(questions, existing_data={}):
    """Collecte les données utilisateur et gère les réponses manquantes."""
    collected_data = existing_data.copy()
    
    for key, question in questions.items():
        if key not in collected_data or collected_data[key] == "Non précisé":
            res = await cl.AskUserMessage(content=question, timeout=60).send()
            if isinstance(res, dict) and 'output' in res:
                collected_data[key] = res['output'].strip()
            else:
                collected_data[key] = "Non précisé"
    
    return collected_data

@cl.on_chat_start
async def start():
    """Démarre l'analyse et collecte l'âge."""
    await heart_animation()

    await cl.Message(content=CONFIDENTIALITY_NOTICE).send()

    await cl.Message(content="""
# 🩺 **Chronik-Care Pro 3.0**  
*Système d'évaluation préliminaire des symptômes cardiaques* 

🔍 **Veuillez fournir les informations suivantes :**  
    1️⃣ **Symptômes principaux**  
    2️⃣ **Durée des symptômes**  
    3️⃣ **Antécédents médicaux connus**  
    4️⃣ **Médications actuelles**  

⚠️ *Toute analyse nécessite des données exactes.*
""").send()

    res = await cl.AskUserMessage(content="🎯 **Veuillez entrer votre âge** :", timeout=60).send()
    age = res['output'].strip() if res and 'output' in res else "Non précisé"

    if age == "Non précisé":
        await cl.Message(content="⚠️ **L'âge est obligatoire pour commencer l'analyse.**").send()
        return await start()

    await main(cl.Message(content=age), {"age": age})

@cl.on_message
async def main(message: cl.Message, initial_data=None):
    """Collecte les données et génère l'analyse."""
    try:
        medical_data = initial_data if initial_data else {}

        await heart_animation()

        # Phase 1 : Collecte des données
        medical_data = await collect_data(initial_questions, medical_data)

        # Vérification des données manquantes
        missing_data = [k for k, v in medical_data.items() if v == "Non précisé"]
        while missing_data:
            await cl.Message(content=f"❌ **Données manquantes** : {', '.join(missing_data)}").send()
            medical_data.update(await collect_data({k: initial_questions[k] for k in missing_data}))
            missing_data = [k for k, v in medical_data.items() if v == "Non précisé"]

        # Phase 2 : Collecte d'infos supplémentaires
        additional_data = await collect_data(additional_questions)
        full_data = {**medical_data, **additional_data}

        # Phase 3 : Envoi au modèle
        query = f"""PATIENT - {full_data['age']} ans
Symptômes : {full_data['symptomes']}
Durée : {full_data['duree_symptomes']}
Médicaments : {full_data['medicaments']}
Examens : {full_data['examens']}
Analyses : {full_data['analyses']}
Antécédents : Diabète({medical_data['diabete']}), HTA({medical_data['hta']})
Tabagisme : {medical_data['tabac']}
Histoire familiale : {full_data['parents']}"""

        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": query}],
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=500,
            stop=["##"]
        )

        response = chat_completion.choices[0].message.content
        response += "\n\n🛑 **Une consultation médicale est recommandée en cas de doute.**"

        await cl.Message(content=response).send()

    except Exception as e:
        await cl.Message(content=f"⚠️ **Erreur système** : {str(e)}").send()