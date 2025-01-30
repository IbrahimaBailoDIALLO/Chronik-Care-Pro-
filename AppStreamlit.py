#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 21:44:59 2025

@author: ibrahima-bailodiallo
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Jan 29 22:53:02 2025

@author: ibrahima-bailodiallo
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Charger les variables d'environnement
load_dotenv()
api_key = st.secrets("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ ERREUR : La clé API GROQ est manquante. Définissez la variable d'environnement 'GROQ_API_KEY'.")
    st.stop()

client = Groq(api_key=api_key)

# 🔐 Avertissement sur la confidentialité
CONFIDENTIALITY_NOTICE = """
⚠️ **Confidentialité & Sécurité**  
Les informations que vous fournissez sont strictement utilisées pour une évaluation préliminaire et ne remplacent **PAS** une consultation médicale.  
🚨 *Veuillez ne pas entrer de données personnelles sensibles (nom, adresse, numéro de sécurité sociale, etc.).*
"""

# Définition des questions médicales
initial_questions = {
    "diabete": "🩸 **Avez-vous un diagnostic de diabète ?**",
    "hta": "💓 **Souffrez-vous d'hypertension artérielle ?**",
    "tabac": "🚬 **Consommez-vous du tabac ?**",
    "antecedents": "🧬 **Avez-vous des antécédents cardiaques familiaux ?**"
}

additional_questions = {
    "symptomes": "⚠️ **Quels sont vos symptômes principaux ?**",
    "duree_symptomes": "⏳ **Depuis combien de temps avez-vous ces symptômes ?**",
    "medicaments": "💊 **Prenez-vous actuellement des médicaments ?**",
    "examens": "📊 **Quels sont les résultats de vos examens médicaux ?**",
    "analyses": "🧪 **Avez-vous les résultats de vos analyses de sang ?**",
    "parents": "👨‍👩‍👧‍👦 **Quel est l'âge et les antécédents médicaux de vos parents ?**"
}

# Interface Streamlit
st.title("🩺 Chronik-Care Pro 3.0")
st.markdown(CONFIDENTIALITY_NOTICE)

st.header("🔍 Évaluation préliminaire des symptômes cardiaques")
st.write("""
Veuillez remplir les informations suivantes pour une analyse plus précise.
⚠️ *Toute analyse nécessite des données exactes !*
""")

# Animation de battements de cœur
heart_placeholder = st.empty()
for beat in ["❤️", "💗"]:
    heart_placeholder.markdown(f"# {beat} **Pré-diagnostic en cours...**")
    time.sleep(0.5)
heart_placeholder.empty()

# Stockage des réponses dans `st.session_state`
if "responses" not in st.session_state:
    st.session_state.responses = {}

# Collecte des informations de base
st.subheader("🩸 Informations de base")

st.session_state.responses["age"] = st.text_input("🎯 **Veuillez entrer votre âge** :")
if not st.session_state.responses["age"]:
    st.warning("⚠️ L'âge est obligatoire pour commencer l'analyse.")
    st.stop()

# Formulaire des premières questions
for key, question in initial_questions.items():
    st.session_state.responses[key] = st.selectbox(question, ["Non précisé", "Oui", "Non"])

# Vérification des réponses manquantes
missing_data = [k for k, v in st.session_state.responses.items() if v == "Non précisé"]
if missing_data:
    st.warning(f"❌ Données manquantes : {', '.join(missing_data)}")
    st.stop()

# Collecte des informations supplémentaires
st.subheader("📊 Informations Complémentaires")
for key, question in additional_questions.items():
    st.session_state.responses[key] = st.text_input(question)

# Vérification des réponses manquantes
missing_additional = [k for k, v in st.session_state.responses.items() if v == ""]
if missing_additional:
    st.warning(f"🛑 Informations manquantes : {', '.join(missing_additional)}")
    st.stop()

# Création de la requête pour le modèle IA
query = f"""PATIENT - {st.session_state.responses['age']} ans
Symptômes : {st.session_state.responses['symptomes']}
Durée : {st.session_state.responses['duree_symptomes']}
Médicaments : {st.session_state.responses['medicaments']}
Examens : {st.session_state.responses['examens']}
Analyses : {st.session_state.responses['analyses']}
Antécédents : Diabète({st.session_state.responses['diabete']}), HTA({st.session_state.responses['hta']})
Tabagisme : {st.session_state.responses['tabac']}
Histoire familiale : {st.session_state.responses['parents']}"""

# Analyse et réponse du modèle IA
if st.button("🩺 Lancer l'analyse"):
    with st.spinner("🔍 Analyse en cours..."):
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Assistant Médical Cardio-Analytique"},
                      {"role": "user", "content": query}],
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=500,
            stop=["##"]
        )
        response = chat_completion.choices[0].message.content
        response += "\n\n🛑 **Une consultation médicale est recommandée en cas de doute.**"
    
    st.success("✅ Analyse terminée !")
    st.write(response)

# Proposition de relancer une nouvelle analyse
if st.button("🔄 Effectuer une nouvelle analyse"):
    st.session_state.responses = {}
    st.experimental_rerun()
