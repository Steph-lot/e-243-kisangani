import streamlit as st
import os
import pandas as pd
from datetime import datetime
import hashlib
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="E-243 KISANGANI - Marketplace Pro",
    layout="wide",
    page_icon="🛍️"
)

# Fichiers de données
FICHIER_UTILISATEURS = "utilisateurs.txt"
FICHIER_CATALOGUE = "catalogue_produits.txt"
FICHIER_VENTES = "historique_ventes.txt"
FICHIER_AVIS = "avis_produits.txt"
FICHIER_MESSAGES = "messages_chat.txt"
DOSSIER_IMAGES = "images_produits"
DOSSIER_PROFILS = "images_profils"

# Numéro Orange Money pour les frais d'inscription vendeur (2 000 FC)
NUMERO_ORANGE_MONEY = "+243 895 341 914"

if not os.path.exists(DOSSIER_IMAGES):
    os.makedirs(DOSSIER_IMAGES)
if not os.path.exists(DOSSIER_PROFILS):
    os.makedirs(DOSSIER_PROFILS)

# Initialisation de la session utilisateur
if "panier" not in st.session_state:
    st.session_state["panier"] = []

if "theme" not in st.session_state:
    st.session_state["theme"] = "Clair"

if "user_connecte" not in st.session_state:
    st.session_state["user_connecte"] = None
if "role_connecte" not in st.session_state:
    st.session_state["role_connecte"] = None
if "boutique_connecte" not in st.session_state:
    st.session_state["boutique_connecte"] = ""
if "chat_actif" not in st.session_state:
    st.session_state["chat_actif"] = None


# --- FONCTIONS HASHING & UTILISATEURS ---
def hacher_mdp(mdp):
    return hashlib.sha256(mdp.encode()).hexdigest()


def lire_utilisateurs():
    users = {}
    if os.path.exists(FICHIER_UTILISATEURS):
        with open(FICHIER_UTILISATEURS, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) >= 4:
                    u, m, r, b, t, g, profil, ref = "", "", "", "", "", "", "", ""
                    for p in parts:
                        if ":" in p:
                            k, val = p.split(":", 1)
                            k, val = k.strip(), val.strip()
                            if k == "User":
                                u = val
                            elif k == "Mdp":
                                m = val
                            elif k == "Role":
                                r = val
                            elif k == "Boutique":
                                b = val
                            elif k == "Phone":
                                t = val
                            elif k == "Gmail":
                                g = val
                            elif k == "Profil":
                                profil = val
                            elif k == "RefOM":
                                ref = val
                    if u:
                        users[u] = {"mdp": m, "role": r, "boutique": b, "phone": t, "gmail": g, "profil": profil}
    return users


def inscrire_utilisateur(user, mdp, role, boutique="", phone="", gmail="", chemin_profil="", ref_om=""):
    users = lire_utilisateurs()
    if user in users:
        return False, "Ce nom d'utilisateur existe déjà !"

    mdp_h = hacher_mdp(mdp)
    ligne = f"User : {user} | Mdp : {mdp_h} | Role : {role} | Boutique : {boutique} | Phone : {phone} | Gmail : {gmail} | Profil : {chemin_profil} | RefOM : {ref_om}\n"
    with open(FICHIER_UTILISATEURS, "a", encoding="utf-8") as f:
        f.write(ligne)
    return True, "Compte créé avec succès !"


def verifier_connexion(user, mdp):
    users = lire_utilisateurs()
    if user in users:
        if users[user]["mdp"] == hacher_mdp(mdp):
            return True, users[user]["role"], users[user]["boutique"]
    return False, None, None


def obtenir_infos_utilisateur(nom_user):
    users = lire_utilisateurs()
    return users.get(nom_user, {})


# --- FONCTIONS MESSAGERIE CHAT ---
def lire_messages():
    messages = []
    if os.path.exists(FICHIER_MESSAGES):
        with open(FICHIER_MESSAGES, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) >= 4:
                    exp, dest, date_m, texte = "", "", "", ""
                    for p in parts:
                        if ":" in p:
                            k, v = p.split(":", 1)
                            k, v = k.strip(), v.strip()
                            if k == "Expediteur":
                                exp = v
                            elif k == "Destinataire":
                                dest = v
                            elif k == "Date":
                                date_m = v
                            elif k == "Texte":
                                texte = v
                    messages.append({"exp": exp, "dest": dest, "date": date_m, "texte": texte})
    return messages


def sauvegarder_message(expediteur, destinataire, texte):
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    with open(FICHIER_MESSAGES, "a", encoding="utf-8") as f:
        f.write(f"Expediteur : {expediteur} | Destinataire : {destinataire} | Date : {date_str} | Texte : {texte}\n")


# --- FONCTIONS CATALOGUE & VENTES ---
def lire_catalogue():
    produits = []
    if os.path.exists(FICHIER_CATALOGUE):
        with open(FICHIER_CATALOGUE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) >= 4:
                    item = {}
                    for p in parts:
                        if ":" in p:
                            k, v = p.split(":", 1)
                            item[k.strip()] = v.strip()
                    produits.append(item)
    return produits


def sauvegarder_produit(nom, prix, stock, categorie, boutique, quartier, phone, chemin_image=""):
    with open(FICHIER_CATALOGUE, "a", encoding="utf-8") as f:
        f.write(
            f"Article : {nom} | Prix : {prix} FC | Stock : {stock} | Categorie : {categorie} | Boutique : {boutique} | Quartier : {quartier} | Phone : {phone} | Image : {chemin_image}\n")


def lire_avis():
    avis_dict = {}
    if os.path.exists(FICHIER_AVIS):
        with open(FICHIER_AVIS, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) >= 4:
                    art = parts[0].replace("Article :", "").strip()
                    auteur = parts[1].replace("Auteur :", "").strip()
                    note = int(parts[2].replace("Note :", "").strip())
                    com = parts[3].replace("Com :", "").strip()
                    if art not in avis_dict:
                        avis_dict[art] = []
                    avis_dict[art].append({"auteur": auteur, "note": note, "com": com})
                elif len(parts) >= 3:
                    art = parts[0].replace("Article :", "").strip()
                    note = int(parts[1].replace("Note :", "").strip())
                    com = parts[2].replace("Com :", "").strip()
                    if art not in avis_dict:
                        avis_dict[art] = []
                    avis_dict[art].append({"auteur": "Anonyme", "note": note, "com": com})
    return avis_dict


def sauvegarder_avis(article, auteur, note, commentaire):
    with open(FICHIER_AVIS, "a", encoding="utf-8") as f:
        f.write(f"Article : {article} | Auteur : {auteur} | Note : {note} | Com : {commentaire}\n")


def mettre_a_jour_stock(nom_article, qte_vendue):
    if not os.path.exists(FICHIER_CATALOGUE):
        return False
    mis_a_jour = False
    nouvelles_lignes = []
    with open(FICHIER_CATALOGUE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if f"Article : {nom_article} |" in line or f"Article : {nom_article} " in line:
            parts = line.strip().split(" | ")
            d = {}
            for p in parts:
                if ":" in p:
                    k, v = p.split(":", 1)
                    d[k.strip()] = v.strip()

            stock_actuel = int(d.get("Stock", 0))
            if stock_actuel >= qte_vendue:
                nouveau_stock = stock_actuel - qte_vendue
                d["Stock"] = str(nouveau_stock)
                line = f"Article : {d.get('Article')} | Prix : {d.get('Prix')} | Stock : {d.get('Stock')} | Categorie : {d.get('Categorie', 'Divers')} | Boutique : {d.get('Boutique', 'Générale')} | Quartier : {d.get('Quartier', 'Makiso')} | Phone : {d.get('Phone', '')} | Image : {d.get('Image', '')}\n"
                mis_a_jour = True
        nouvelles_lignes.append(line)

    if mis_a_jour:
        with open(FICHIER_CATALOGUE, "w", encoding="utf-8") as f:
            f.writelines(nouvelles_lignes)
    return mis_a_jour


def generer_recu_panier_pdf(client, panier, total_general, date_str):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 750, "E-243 KISANGANI MARKETPLACE")
    p.setFont("Helvetica", 12)
    p.drawString(210, 730, "Facture & Reçu de Commande")
    p.line(50, 715, 550, 715)
    p.setFont("Helvetica", 10)
    p.drawString(50, 685, f"Date : {date_str}")
    p.drawString(50, 670, f"Client : {client}")
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, 640, "Détails du Panier :")
    y = 615
    p.setFont("Helvetica", 10)
    for item in panier:
        p.drawString(60, y, f"• {item['article']} x {item['qte']} — Total: {item['subtotal']:,} FC".replace(",", " "))
        y -= 20
        if y < 150:
            p.showPage()
            y = 700
    p.line(50, y - 10, 550, y - 10)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y - 35, f"TOTAL GÉNÉRAL PAYÉ : {total_general:,} FC".replace(",", " "))
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(180, y - 80, "Merci de votre confiance sur E-243 Kisangani !")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# --- CSS STYLES ---
bg_color = "#121212" if st.session_state["theme"] == "Sombre" else "#f8f9fa"
text_color = "#ffffff" if st.session_state["theme"] == "Sombre" else "#212529"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .hero-header {{
        background: linear-gradient(135deg, #1b4965 0%, #2b6cb0 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }}
    .hero-header h1 {{ color: white !important; margin: 0; }}
    .chat-bubble-sent {{
        background-color: #dcf8c6;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        text-align: right;
        color: #000;
    }}
    .chat-bubble-recv {{
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        text-align: left;
        color: #000;
        border: 1px solid #ddd;
    }}
    </style>
""", unsafe_allow_html=True)

# --- EN-TÊTE PRINCIPAL ---
st.markdown("""
    <div class="hero-header">
        <h1>🛍️ E-243 KISANGANI</h1>
        <p>Marketplace & Plateforme Commerciale Multi-communes de Kisangani</p>
    </div>
""", unsafe_allow_html=True)

# --- BARRE LATÉRALE : GESTION DES COMPTES & AUTHENTIFICATION ---
st.sidebar.title("🔐 Espace Utilisateur")

if st.session_state["user_connecte"] is None:
    menu_auth = st.sidebar.selectbox("Action :", ["🔑 Se Connecter", "📝 Créer un Compte"])

    if menu_auth == "🔑 Se Connecter":
        st.sidebar.subheader("Connexion")
        with st.sidebar.form("form_login"):
            u_input = st.text_input("Nom d'utilisateur")
            m_input = st.text_input("Mot de passe", type="password")
            btn_login = st.form_submit_button("Se Connecter")
            if btn_login:
                ok, role, boutique = verifier_connexion(u_input, m_input)
                if ok:
                    st.session_state["user_connecte"] = u_input
                    st.session_state["role_connecte"] = role
                    st.session_state["boutique_connecte"] = boutique
                    st.success(f"Bienvenue {u_input} !")
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")

    elif menu_auth == "📝 Créer un Compte":
        st.sidebar.subheader("Inscription")
        type_compte = st.sidebar.radio("Type de compte :", ["Acheteur (Gratuit)", "Vendeur (2 000 FC)"])

        if "Vendeur" in type_compte:
            st.sidebar.markdown(f"""
                <div style="font-size: 12px; background-color: #ff6600; color: white; padding: 10px; border-radius: 6px;">
                    <b>Paiement Orange Money :</b><br>
                    Envoyez <b>2 000 FC</b> au <b>{NUMERO_ORANGE_MONEY}</b> avant de valider votre inscription.
                </div>
            """, unsafe_allow_html=True)

        with st.sidebar.form("form_register"):
            reg_user = st.text_input("Choisir un pseudo")
            reg_mdp = st.text_input("Mot de passe", type="password")
            reg_gmail = st.text_input("Adresse Gmail (ex: nom@gmail.com)")
            reg_phone = st.text_input("Téléphone / WhatsApp (+243...)")

            reg_boutique = ""
            reg_ref_om = ""
            if "Vendeur" in type_compte:
                reg_boutique = st.text_input("Nom de la Boutique")
                reg_ref_om = st.text_input("Référence / ID Transaction Orange Money")

            reg_profil_file = st.file_uploader("Photo de profil", type=["png", "jpg", "jpeg"])

            btn_reg = st.form_submit_button("S'inscrire")
            if btn_reg:
                role = "Vendeur" if "Vendeur" in type_compte else "Acheteur"
                if not reg_user or not reg_mdp or not reg_gmail:
                    st.sidebar.warning("Veuillez remplir le pseudo, le mot de passe et l'adresse Gmail.")
                elif "@gmail.com" not in reg_gmail.lower():
                    st.sidebar.warning("Veuillez entrer une adresse Gmail valide.")
                elif role == "Vendeur" and (not reg_boutique or not reg_ref_om):
                    st.sidebar.warning("Veuillez indiquer le nom de votre boutique et la référence Orange Money.")
                else:
                    profil_path = ""
                    if reg_profil_file:
                        profil_path = os.path.join(DOSSIER_PROFILS,
                                                   f"profil_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{reg_profil_file.name}")
                        with open(profil_path, "wb") as f:
                            f.write(reg_profil_file.getbuffer())

                    succes, msg = inscrire_utilisateur(reg_user, reg_mdp, role, reg_boutique, reg_phone, reg_gmail,
                                                       profil_path, reg_ref_om)
                    if succes:
                        st.sidebar.success("Compte créé avec succès ! Connectez-vous.")
                    else:
                        st.sidebar.error(msg)
else:
    user_infos = obtenir_infos_utilisateur(st.session_state["user_connecte"])
    profil_path_connecte = user_infos.get("profil", "")

    if profil_path_connecte and os.path.exists(profil_path_connecte):
        st.sidebar.image(profil_path_connecte, width=80)

    st.sidebar.success(
        f"Connecté : **{st.session_state['user_connecte']}**\n\nRôle : **{st.session_state['role_connecte']}**")
    if st.sidebar.button("🚪 Se Déconnecter"):
        st.session_state["user_connecte"] = None
        st.session_state["role_connecte"] = None
        st.session_state["boutique_connecte"] = ""
        st.session_state["chat_actif"] = None
        st.rerun()

st.sidebar.write("---")

# Bascule Thème
theme_choisi = st.sidebar.radio("🎨 Mode d'affichage :", ["Clair", "Sombre"],
                                index=0 if st.session_state["theme"] == "Clair" else 1)
if theme_choisi != st.session_state["theme"]:
    st.session_state["theme"] = theme_choisi
    st.rerun()

st.sidebar.write("---")

# Navigation globale de l'application
pages_disponibles = ["🛒 Marketplace & Produits", "🛍️ Voir mon Panier", "💬 Messagerie Interne"]
if st.session_state["role_connecte"] == "Vendeur":
    pages_disponibles.extend(["➕ Publier un Produit", "📊 Bilan & Graphiques Ventes"])

nb_items_panier = sum(item['qte'] for item in st.session_state["panier"])
st.sidebar.markdown(f"🛒 **Mon Panier :** `{nb_items_panier}` article(s)")
page = st.sidebar.radio("Navigation :", pages_disponibles)

# ==========================================
# 1. MARKETPLACE
# ==========================================
if page == "🛒 Marketplace & Produits":
    st.subheader("🔍 Recherche, Communes & Filtres")

    col_search, col_quartier = st.columns([2, 1])
    with col_search:
        recherche = st.text_input("Recherche", placeholder="Nom d'article...", label_visibility="collapsed")
    with col_quartier:
        commune_filtre = st.selectbox("Commune / Zone", ["Toutes", "Makiso", "Tshopo", "Mangobo", "Kabondo", "Lubunga",
                                                         "Kisangani (Centre)"], label_visibility="collapsed")

    produits = lire_catalogue()
    avis_data = lire_avis()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        boutiques_existantes = list(set([p.get("Boutique", "Toutes") for p in produits]))
        boutiques_existantes.insert(0, "Toutes les boutiques")
        filtre_boutique = st.selectbox("🏬 Filtrer par boutique :", boutiques_existantes)
    with col_f2:
        max_prix = st.slider("💰 Prix max (FC) :", 1000, 500000, 500000, step=5000)

    categories = ["Toutes", "Électronique", "Alimentation", "Vêtements", "Artisanat", "Divers"]
    choix_cat = st.radio("Catégories :", categories, horizontal=True)

    st.write("---")

    if recherche:
        produits = [p for p in produits if recherche.lower() in p.get("Article", "").lower()]
    if choix_cat != "Toutes":
        produits = [p for p in produits if p.get("Categorie") == choix_cat]
    if filtre_boutique != "Toutes les boutiques":
        produits = [p for p in produits if p.get("Boutique") == filtre_boutique]
    if commune_filtre != "Toutes":
        produits = [p for p in produits if p.get("Quartier") == commune_filtre]

    produits_filtrés = []
    for p in produits:
        p_str = p.get("Prix", "0").replace("FC", "").strip()
        p_int = int(p_str) if p_str.isdigit() else 0
        if p_int <= max_prix:
            produits_filtrés.append(p)

    st.subheader(f"📦 {len(produits_filtrés)} article(s) disponible(s)")

    users_global = lire_utilisateurs()

    if not produits_filtrés:
        st.info("Aucun produit ne correspond à vos critères.")
    else:
        cols = st.columns(2)
        for idx, prod in enumerate(produits_filtrés):
            col = cols[idx % 2]
            with col:
                with st.container():
                    art_nom = prod.get('Article')
                    cat = prod.get("Categorie", "Divers")
                    img_path = prod.get("Image", "")
                    quartier = prod.get("Quartier", "Makiso")
                    nom_boutique = prod.get('Boutique', 'Générale')

                    # Trouver le nom du vendeur propriétaire de cette boutique et son profil
                    vendeur_proprio = ""
                    profil_vendeur_path = ""
                    for u, u_data in users_global.items():
                        if u_data.get("boutique") == nom_boutique:
                            vendeur_proprio = u
                            profil_vendeur_path = u_data.get("profil", "")
                            break

                    # En-tête de la carte avec photo de profil du vendeur
                    col_p1, col_p2 = st.columns([1, 4])
                    with col_p1:
                        if profil_vendeur_path and os.path.exists(profil_vendeur_path):
                            st.image(profil_vendeur_path, width=45)
                        else:
                            st.markdown("👤")
                    with col_p2:
                        st.markdown(
                            f"**{cat.upper()}**<br><span style='font-size: 13px; color: #555;'>🏬 {nom_boutique} (📍 {quartier})</span>",
                            unsafe_allow_html=True)

                    st.write("")

                    if img_path and os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                    else:
                        icone = "📱" if cat == "Électronique" else "🍚" if cat == "Alimentation" else "👕" if cat == "Vêtements" else "🛍️"
                        st.markdown(f"<h1 style='text-align: center; font-size: 50px;'>{icone}</h1>",
                                    unsafe_allow_html=True)

                    st.markdown(f"### {art_nom}")
                    st.markdown(f"<h4 style='color: #8b1e1e;'>{prod.get('Prix')} FC</h4>", unsafe_allow_html=True)

                    avis_art = avis_data.get(art_nom, [])
                    if avis_art:
                        moy_note = sum(a['note'] for a in avis_art) / len(avis_art)
                        st.caption(f"⭐ {moy_note:.1f}/5 ({len(avis_art)} avis)")

                        with st.expander("💬 Voir les avis détaillés"):
                            for av in avis_art:
                                auteur_nom = av.get("auteur", "Anonyme")
                                auteur_profil = users_global.get(auteur_nom, {}).get("profil", "")

                                c_av1, c_av2 = st.columns([1, 6])
                                with c_av1:
                                    if auteur_profil and os.path.exists(auteur_profil):
                                        st.image(auteur_profil, width=30)
                                    else:
                                        st.markdown("👤")
                                with c_av2:
                                    st.markdown(f"**{auteur_nom}** : {'⭐' * av['note']}<br>*{av['com']}*",
                                                unsafe_allow_html=True)
                                st.write("---")
                    else:
                        st.caption("⭐ Pas encore d'avis")

                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        qte_aj = st.number_input("Qté", min_value=1, max_value=int(prod.get("Stock", 1)), value=1,
                                                 key=f"qte_{idx}")
                        if st.button(f"🛒 Ajouter au Panier", key=f"add_{idx}"):
                            p_str = prod.get("Prix", "0").replace("FC", "").strip()
                            pu = int(p_str) if p_str.isdigit() else 0

                            st.session_state["panier"].append({
                                "article": art_nom,
                                "qte": qte_aj,
                                "pu": pu,
                                "subtotal": pu * qte_aj
                            })
                            st.success(f"{qte_aj} x {art_nom} ajouté(s) au panier !")
                            st.rerun()

                    with c_btn2:
                        # Bouton de discussion interne direct vers le vendeur
                        if vendeur_proprio:
                            if st.button(f"💬 Discuter", key=f"chat_{idx}"):
                                if st.session_state["user_connecte"] is None:
                                    st.warning("Veuillez vous connecter pour discuter avec le vendeur.")
                                else:
                                    st.session_state["chat_actif"] = vendeur_proprio
                                    st.rerun()
                        else:
                            st.caption("Vendeur direct non répertorié")

                    with st.expander("📝 Laisser un avis"):
                        if st.session_state["user_connecte"] is None:
                            st.warning("Veuillez vous connecter pour laisser un avis.")
                        else:
                            with st.form(f"form_avis_{idx}"):
                                note_donnee = st.slider("Note", 1, 5, 5, key=f"star_{idx}")
                                com_donne = st.text_input("Votre commentaire", key=f"txt_{idx}")
                                if st.form_submit_button("Envoyer l'Avis"):
                                    sauvegarder_avis(art_nom, st.session_state["user_connecte"], note_donnee, com_donne)
                                    st.success("Avis enregistré !")
                                    st.rerun()

                st.write("---")

# ==========================================
# 2. PANIER D'ACHAT
# ==========================================
elif page == "🛍️ Voir mon Panier":
    st.header("🛍️ Mon Panier d'Achat")

    if not st.session_state["panier"]:
        st.info("Votre panier est vide pour l'instant. Allez sur la Marketplace pour ajouter des articles !")
    else:
        df_panier = pd.DataFrame(st.session_state["panier"])
        st.table(df_panier[["article", "qte", "pu", "subtotal"]])

        total_general = sum(item["subtotal"] for item in st.session_state["panier"])
        st.markdown(f"### Total Général : **{total_general:,} FC**".replace(",", " "))

        if st.button("🗑️ Vider le panier"):
            st.session_state["panier"] = []
            st.rerun()

        st.write("---")
        st.subheader("📋 Finaliser la Commande")

        with st.form("form_commande_panier"):
            nom_client = st.text_input("Nom complet de l'acheteur",
                                       value=st.session_state["user_connecte"] if st.session_state[
                                           "user_connecte"] else "")
            btn_valider_panier = st.form_submit_button("✅ Valider la commande & Générer Reçu PDF")

            if btn_valider_panier:
                if nom_client.strip():
                    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                    date_iso = datetime.now().strftime("%Y-%m-%d")

                    tout_ok = True
                    for item in st.session_state["panier"]:
                        if mettre_a_jour_stock(item["article"], item["qte"]):
                            with open(FICHIER_VENTES, "a", encoding="utf-8") as f:
                                f.write(
                                    f"[{date_str}] DateISO : {date_iso} | Client : {nom_client.strip()} | Article : {item['article']} | Qté : {item['qte']} | Total : {item['subtotal']} FC\n")
                        else:
                            tout_ok = False

                    if tout_ok:
                        st.balloons()
                        st.success("Commande effectuée avec succès !")

                        pdf_bytes = generer_recu_panier_pdf(nom_client, st.session_state["panier"], total_general,
                                                            date_str)
                        st.download_button(
                            label="📄 Télécharger le Reçu PDF Global",
                            data=pdf_bytes,
                            file_name=f"Recu_Panier_{nom_client}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf",
                            mime="application/pdf"
                        )
                        st.session_state["panier"] = []
                    else:
                        st.error("Problème de stock sur un des articles !")
                else:
                    st.warning("Veuillez remplir votre nom.")

# ==========================================
# 3. MESSAGERIE INTERNE (CHAT E-243)
# ==========================================
elif page == "💬 Messagerie Interne":
    st.header("💬 Messagerie Directe E-243")

    if st.session_state["user_connecte"] is None:
        st.warning("🔒 Veuillez vous connecter pour accéder à votre messagerie.")
    else:
        user_actuel = st.session_state["user_connecte"]
        role_actuel = st.session_state["role_connecte"]

        users_global = lire_utilisateurs()

        if role_actuel == "Acheteur":
            correspondants = [u for u, d in users_global.items() if d.get("role") == "Vendeur"]
        else:
            correspondants = [u for u, d in users_global.items() if u != user_actuel]

        if not correspondants:
            st.info("Aucun correspondant disponible pour le moment.")
        else:
            index_defaut = 0
            if st.session_state["chat_actif"] in correspondants:
                index_defaut = correspondants.index(st.session_state["chat_actif"])

            destinataire_choisi = st.selectbox("Choisir un interlocuteur :", correspondants, index=index_defaut)
            st.session_state["chat_actif"] = destinataire_choisi

            st.write("---")
            st.subheader(f"Conversation avec : **{destinataire_choisi}**")

            tous_messages = lire_messages()
            messages_conversation = [
                m for m in tous_messages
                if (m["exp"] == user_actuel and m["dest"] == destinataire_choisi) or
                   (m["exp"] == destinataire_choisi and m["dest"] == user_actuel)
            ]

            chat_container = st.container()
            with chat_container:
                if not messages_conversation:
                    st.info("Aucun message échangé pour l'instant. Envoyez le premier message ci-dessous !")
                else:
                    for msg in messages_conversation:
                        if msg["exp"] == user_actuel:
                            st.markdown(f"""
                                <div style="text-align: right; margin-bottom: 8px;">
                                    <span style="background-color: #2b6cb0; color: white; padding: 8px 12px; border-radius: 10px; display: inline-block; max-width: 70%; text-align: left;">
                                        <b>Moi :</b> {msg['texte']}<br><sub style="font-size: 9px; opacity: 0.8;">{msg['date']}</sub>
                                    </span>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div style="text-align: left; margin-bottom: 8px;">
                                    <span style="background-color: #e2e8f0; color: #000; padding: 8px 12px; border-radius: 10px; display: inline-block; max-width: 70%;">
                                        <b>{msg['exp']} :</b> {msg['texte']}<br><sub style="font-size: 9px; color: #555;">{msg['date']}</sub>
                                    </span>
                                </div>
                            """, unsafe_allow_html=True)

            st.write("")
            with st.form("form_envoi_message", clear_on_submit=True):
                texte_message = st.text_input("Votre message...", placeholder="Écrivez votre message ici...")
                btn_envoyer = st.form_submit_button("Envoyer 📤")
                if btn_envoyer:
                    if texte_message.strip():
                        sauvegarder_message(user_actuel, destinataire_choisi, texte_message.strip())
                        st.rerun()
                    else:
                        st.warning("Le message ne peut pas être vide.")

# ==========================================
# 4. PUBLIER UN PRODUIT (RESERVÉ AUX VENDEURS)
# ==========================================
elif page == "➕ Publier un Produit":
    st.header("➕ Publier un article & Gérer sa Boutique")

    if st.session_state["role_connecte"] != "Vendeur":
        st.error("⛔ Accès refusé. Vous devez vous connecter avec un compte Vendeur pour publier des articles.")
    else:
        nom_boutique_actuelle = st.session_state["boutique_connecte"] if st.session_state[
            "boutique_connecte"] else "Ma Boutique"

        with st.form("form_pub"):
            nom = st.text_input("Nom de l'article")
            boutique = st.text_input("Boutique", value=nom_boutique_actuelle)
            quartier = st.selectbox("Commune / Zone de Kisangani",
                                    ["Makiso", "Tshopo", "Mangobo", "Kabondo", "Lubunga", "Kisangani (Centre)"])
            phone = st.text_input("Numéro WhatsApp (+243...)")
            prix = st.number_input("Prix (FC)", min_value=100, step=500)
            stock = st.number_input("Stock disponible", min_value=1, step=1)
            categorie = st.selectbox("Catégorie", ["Électronique", "Alimentation", "Vêtements", "Artisanat", "Divers"])

            st.write("---")
            st.markdown("📷 **Photo de l'article :**")
            image_file = st.file_uploader("Sélectionner l'image de l'article", type=["png", "jpg", "jpeg"],
                                          key="img_art")

            if st.form_submit_button("🚀 Publier l'Annonce"):
                if nom.strip():
                    img_path = ""
                    if image_file:
                        img_path = os.path.join(DOSSIER_IMAGES,
                                                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_file.name}")
                        with open(img_path, "wb") as f:
                            f.write(image_file.getbuffer())

                    sauvegarder_produit(nom.strip(), prix, stock, categorie, boutique, quartier, phone, img_path)
                    st.success("Article publié avec succès !")
                else:
                    st.warning("Veuillez saisir un nom d'article.")

# ==========================================
# 5. BILAN ET GRAPHIQUES (RESERVÉ AUX VENDEURS)
# ==========================================
elif page == "📊 Bilan & Graphiques Ventes":
    st.header("📊 Bilan & Suivi Financier Vendeur")

    if st.session_state["role_connecte"] != "Vendeur":
        st.error("⛔ Accès restreint aux vendeurs.")
    else:
        total_ca = 0
        ventes_data = []

        if os.path.exists(FICHIER_VENTES):
            with open(FICHIER_VENTES, "r", encoding="utf-8") as f:
                for line in f:
                    if "Total :" in line:
                        parts = line.strip().split(" | ")
                        date_val = parts[0].split("]")[0].replace("[", "").split()[0]
                        art_val = [p for p in parts if "Article :" in p][0].split(":")[1].strip()
                        m_val = [p for p in parts if "Total :" in p][0].split(":")[1].replace("FC", "").strip()
                        if m_val.isdigit():
                            montant = int(m_val)
                            total_ca += montant
                            ventes_data.append({"Date": date_val, "Article": art_val, "Montant": montant})

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Chiffre d'Affaires Total", f"{total_ca:,} FC".replace(",", " "))
        with col_s2:
            st.metric("Nombre total de ventes", f"{len(ventes_data)}")

        st.write("---")

        if ventes_data:
            st.subheader("📈 Graphique des Ventes par Article")
            df_ventes = pd.DataFrame(ventes_data)
            chart_data = df_ventes.groupby("Article")["Montant"].sum().reset_index()
            st.bar_chart(chart_data.set_index("Article"))
        else:
            st.info("Aucune donnée de vente enregistrée pour le moment.")