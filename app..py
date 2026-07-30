from datetime import datetime
import os
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="E-243 KISANGANI", page_icon="🛍️", layout="wide"
)

# Style aux couleurs du drapeau de la RDC (Bleu, Jaune, Rouge)
st.markdown(
    """
    <style>
    .titre-rdc {
        background: linear-gradient(90deg, #007FFF 0%, #FCD116 50%, #CE1126 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

DOSSIER_PROFILS = "profils_images"
DOSSIER_PRODUITS = "produits_images"
DOSSIER_STORIES = "stories_images"
FICHIER_UTILISATEURS = "utilisateurs.txt"
FICHIER_PRODUITS = "catalogue_fournisseurs.txt"
FICHIER_MESSAGES = "messages.txt"
FICHIER_STORIES = "stories.txt"

# Dictionnaire de traduction de base pour l'interface
TRADUCTIONS = {
    "Français": {
        "titre": "E-243 KISANGANI",
        "catalogue": "🛍️ Catalogue des Produits",
        "profil": "👤 Mon Profil & Paramètres",
        "messenger": "💬 Messenger (Discussions)",
        "stories": "📱 Stories des Articles",
        "deconnexion": "Se déconnecter",
    },
    "Lingala": {
        "titre": "E-243 KISANGANI",
        "catalogue": "🛍️ Biloko nionso ya mombongo",
        "profil": "👤 Profile na Ngai & Mibeko",
        "messenger": "💬 Masolo (Discussions)",
        "stories": "📱 Statuts ya Biloko",
        "deconnexion": "Kobima",
    },
    "Swahili": {
        "titre": "E-243 KISANGANI",
        "catalogue": "🛍️ Orodha ya Bidhaa",
        "profil": "👤 Wasifu Wangu & Mipangilio",
        "messenger": "💬 Ujumbe (Mazungumzo)",
        "stories": "📱 Hali za Bidhaa",
        "deconnexion": "Toka nje",
    },
    "Tshiluba": {
        "titre": "E-243 KISANGANI",
        "catalogue": "🛍️ Bintu bia Bukula",
        "profil": "👤 Tshifulu tshia Muntu & Biamba",
        "messenger": "💬 Diyukakana",
        "stories": "📱 Nsombelu ya Bintu",
        "deconnexion": "Kubima",
    },
    "Kikongo": {
        "titre": "E-243 KISANGANI",
        "catalogue": "🛍️ Mambu ya Zandu",
        "profil": "👤 Zina diaku & Mambu",
        "messenger": "💬 Matangi",
        "stories": "📱 Nkinga ya Mambu",
        "deconnexion": "Kunsuka",
    },
    "English": {
        "titre": "E-243 KISANGANI",
        "catalogue": "🛍️ Product Catalog",
        "profil": "👤 My Profile & Settings",
        "messenger": "💬 Messenger (Chats)",
        "stories": "📱 Item Stories",
        "deconnexion": "Log out",
    },
}


# --- FONCTIONS DE GESTION ---
def charger_utilisateurs():
  utilisateurs = {}
  if not os.path.exists(FICHIER_UTILISATEURS):
    return utilisateurs
  with open(FICHIER_UTILISATEURS, "r", encoding="utf-8") as f:
    for ligne in f:
      p = ligne.strip().split(";")
      if len(p) >= 2:
        utilisateurs[p[0]] = {
            "user": p[0],
            "mdp": p[1],
            "role": p[2] if len(p) > 2 else "Acheteur",
            "boutique": p[3] if len(p) > 3 else "",
            "phone": p[4] if len(p) > 4 else "",
            "gmail": p[5] if len(p) > 5 else "",
            "profil_path": p[6] if len(p) > 6 else "",
            "ref_om": p[7] if len(p) > 7 else "",
            "ville": p[8] if len(p) > 8 and p[8] else "Kisangani",
            "commune": p[9] if len(p) > 9 and p[9] else "Non spécifiée",
            "langue": p[10] if len(p) > 10 and p[10] else "Français",
        }
  return utilisateurs


def sauvegarder_utilisateurs(utilisateurs):
  with open(FICHIER_UTILISATEURS, "w", encoding="utf-8") as f:
    for u, data in utilisateurs.items():
      f.write(
          f"{data['user']};{data['mdp']};{data['role']};{data['boutique']};{data['phone']};{data['gmail']};{data['profil_path']};{data['ref_om']};{data['ville']};{data['commune']};{data['langue']}\n"
      )


def inscrire_utilisateur(
    user, mdp, role, boutique, phone, gmail, profil_path, ref_om
):
  utilisateurs = charger_utilisateurs()
  if user in utilisateurs:
    return False, "Ce nom d'utilisateur existe déjà."
  for u, data in utilisateurs.items():
    if data["gmail"] == gmail and gmail != "":
      return False, "Cet e-mail est déjà associé à un compte."

  utilisateurs[user] = {
      "user": user,
      "mdp": mdp,
      "role": role,
      "boutique": boutique,
      "phone": phone,
      "gmail": gmail,
      "profil_path": profil_path,
      "ref_om": ref_om,
      "ville": "Kisangani",
      "commune": "Non spécifiée",
      "langue": "Français",
  }
  sauvegarder_utilisateurs(utilisateurs)
  return True, "Compte créé avec succès ! Bienvenue sur E-243."


def verifier_connexion(user, mdp):
  utilisateurs = charger_utilisateurs()
  if user in utilisateurs and utilisateurs[user]["mdp"] == mdp:
    return utilisateurs[user]
  return None


# --- GESTION DE LA SESSION ---
if "user_connecte" not in st.session_state:
  st.session_state.user_connecte = None

if "chat_actif" not in st.session_state:
  st.session_state.chat_actif = None

user_info = st.session_state.user_connecte

langue_courante = (
    user_info["langue"]
    if user_info and "langue" in user_info
    else "Français"
)
t = TRADUCTIONS.get(langue_courante, TRADUCTIONS["Français"])

# ==========================================
# CAS 1 : PERSONNE N'EST CONNECTÉ (ACCUEIL PUBLIC)
# ==========================================
if user_info is None:
  st.markdown(
      "<h1 class='titre-rdc'>E-243 KISANGANI</h1>", unsafe_allow_html=True
  )
  st.markdown(
      "Découvrez les produits de nos fournisseurs locaux en gros et en"
      " détail."
  )

  st.sidebar.title("Mon Compte")
  menu_auth = st.sidebar.selectbox(
      "Navigation", ["🛍️ Voir le Catalogue", "Se Connecter", "📝 Créer un Compte"]
  )

  if menu_auth == "📝 Créer un Compte":
    st.subheader("Rejoignez E-243 en tant qu'Acheteur ou Fournisseur")
    with st.form("form_inscription"):
      type_compte = st.radio(
          "Je souhaite m'inscrire en tant que :",
          [
              "🛒 Acheteur (Je veux acheter)",
              "🏭 Fournisseur / Vendeur (Je veux vendre mes produits)",
          ],
      )
      reg_user = st.text_input("Nom d'utilisateur (Pseudo)")
      reg_mdp = st.text_input("Mot de passe", type="password")
      reg_gmail = st.text_input("Adresse e-mail (ex: nom@gmail.com)")
      reg_phone = st.text_input("Numéro de téléphone")

      reg_boutique = ""
      reg_ref_om = ""
      if "Fournisseur" in type_compte:
        reg_boutique = st.text_input("Nom de la Boutique / Entreprise")
        reg_ref_om = st.text_input("Référence de transaction / Paiement")

      reg_profil_file = st.file_uploader(
          "Photo de profil ou logo", type=["png", "jpg", "jpeg"]
      )

      btn_reg = st.form_submit_button("S'inscrire")
      if btn_reg:
        role = "Fournisseur" if "Fournisseur" in type_compte else "Acheteur"
        if not reg_user or not reg_mdp or not reg_gmail:
          st.error("❌ Veuillez remplir les champs obligatoires.")
        elif "@gmail.com" not in reg_gmail.lower():
          st.error("❌ L'adresse e-mail doit contenir '@gmail.com'.")
        elif role == "Fournisseur" and (not reg_boutique or not reg_ref_om):
          st.error(
              "❌ Le nom de la boutique et la référence de paiement sont"
              " requis."
          )
        else:
          profil_path = ""
          if reg_profil_file:
            if not os.path.exists(DOSSIER_PROFILS):
              os.makedirs(DOSSIER_PROFILS)
            profil_path = os.path.join(
                DOSSIER_PROFILS, f"profil_{reg_user}_{reg_profil_file.name}"
            )
            with open(profil_path, "wb") as f:
              f.write(reg_profil_file.getbuffer())

          succes, msg = inscrire_utilisateur(
              reg_user.strip(),
              reg_mdp,
              role,
              reg_boutique.strip(),
              reg_phone.strip(),
              reg_gmail.strip(),
              profil_path,
              reg_ref_om.strip(),
          )
          if succes:
            st.success(f"🎉 {msg} Vous pouvez maintenant vous connecter.")
          else:
            st.error(f"⚠️ {msg}")

  elif menu_auth == "Se Connecter":
    st.subheader("Connexion à votre espace E-243")
    with st.form("form_connexion"):
      log_user = st.text_input("Nom d'utilisateur")
      log_mdp = st.text_input("Mot de passe", type="password")
      btn_connexion = st.form_submit_button("Se connecter")

      if btn_connexion:
        utilisateur = verifier_connexion(log_user.strip(), log_mdp)
        if utilisateur:
          st.session_state.user_connecte = utilisateur
          st.success(f"Connexion réussie ! Bienvenue {utilisateur['user']}")
          st.rerun()
        else:
          st.error("❌ Identifiant ou mot de passe incorrect.")

  st.subheader("🛍️ Catalogue Public des Produits")
  if os.path.exists(FICHIER_PRODUITS):
    recherche = st.text_input("🔍 Rechercher un produit ou un fournisseur...")
    with open(FICHIER_PRODUITS, "r", encoding="utf-8") as f_prod:
      for ligne in f_prod:
        p = ligne.strip().split(";")
        if len(p) >= 8:
          boutique_vendeur, nom_p, cat_p, prix_p, stock_p, moq_p, desc_p, img_p = (
              p[0],
              p[1],
              p[2],
              p[3],
              p[4],
              p[5],
              p[6],
              p[7],
          )
          ville_p = p[8] if len(p) > 8 and p[8] else "Kisangani"
          commune_p = p[9] if len(p) > 9 and p[9] else "Non spécifiée"

          if (
              recherche.lower() in nom_p.lower()
              or recherche.lower() in boutique_vendeur.lower()
          ):
            col_img, col_details = st.columns([1, 2])
            with col_img:
              if img_p and os.path.exists(img_p):
                st.image(img_p, width=180)
              else:
                st.info("📷 Pas d'image")
            with col_details:
              st.markdown(f"### 📦 {nom_p} ({prix_p} $)")
              st.write(
                  f"🏭 **Fournisseur :** {boutique_vendeur} | 📂 **Catégorie"
                  f" :** {cat_p}"
              )
              st.write(
                  f"📍 **Adresse :** Ville de {ville_p}, Commune de"
                  f" {commune_p}"
              )
              st.write(f"📝 {desc_p}")
              if st.button(
                  f"💬 Contacter ({boutique_vendeur})",
                  key=f"pub_{boutique_vendeur}_{nom_p}",
              ):
                st.warning("⚠️ Connectez-vous pour contacter ce fournisseur.")
            st.markdown("---")

# ==========================================
# CAS 2 : UTILISATEUR CONNECTÉ
# ==========================================
else:
  st.sidebar.title(f"E-243 ({user_info['role']})")
  if user_info["profil_path"] and os.path.exists(user_info["profil_path"]):
    st.sidebar.image(user_info["profil_path"], width=100)

  st.sidebar.write(f"👤 **{user_info['user']}**")
  if user_info["role"] == "Fournisseur":
    st.sidebar.write(f"🏭 **{user_info['boutique']}**")

  options_menu = [
      "🛍️ Catalogue & Achats",
      "👤 Mon Profil & Paramètres",
      "📱 Stories (Statuts)",
      "💬 Messenger",
  ]
  if user_info["role"] == "Fournisseur":
    options_menu.append("📦 Gérer mes produits")

  menu_principal = st.sidebar.radio("Navigation", options_menu)

  if st.sidebar.button(t["deconnexion"]):
    st.session_state.user_connecte = None
    st.session_state.chat_actif = None
    st.rerun()

  # --- ESPACE PROFIL & PARAMÈTRES ---
  if menu_principal == "👤 Mon Profil & Paramètres":
    st.title("👤 Gestion de votre Profil & Paramètres Professionnels")
    st.markdown(
        "Modifiez vos informations personnelles, votre localisation, votre"
        " langue et votre sécurité en toute simplicité."
    )

    utilisateurs = charger_utilisateurs()
    actuel = utilisateurs[user_info["user"]]

    with st.form("form_modifier_profil"):
      col1, col2 = st.columns(2)
      with col1:
        nouveau_nom = st.text_input("Nom d'utilisateur", value=actuel["user"])
        nouveau_gmail = st.text_input("Adresse Gmail", value=actuel["gmail"])
        nouveau_phone = st.text_input(
            "Numéro de téléphone", value=actuel["phone"]
        )
        nouveau_mdp = st.text_input(
            "Nouveau mot de passe (laisser vide pour ne pas changer)",
            type="password",
        )

      with col2:
        nouvelle_ville = st.text_input("Ville", value=actuel["ville"])
        nouvelle_commune = st.text_input("Commune", value=actuel["commune"])

        langues_dispo = [
            "Français",
            "English",
            "Lingala",
            "Swahili",
            "Tshiluba",
            "Kikongo",
        ]
        index_langue = (
            langues_dispo.index(actuel["langue"])
            if actuel["langue"] in langues_dispo
            else 0
        )
        choix_langue = st.selectbox(
            "Langue de l'application", langues_dispo, index=index_langue
        )

        nouveau_logo = st.file_uploader(
            "Mettre à jour la photo de profil / logo",
            type=["png", "jpg", "jpeg"],
        )

      btn_sauver = st.form_submit_button("Enregistrer les modifications 💾")

      if btn_sauver:
        if "@gmail.com" not in nouveau_gmail.lower() and nouveau_gmail != "":
          st.error("❌ L'adresse e-mail doit impérativement être un compte Gmail.")
        else:
          chemin_img = actuel["profil_path"]
          if nouveau_logo:
            if not os.path.exists(DOSSIER_PROFILS):
              os.makedirs(DOSSIER_PROFILS)
            chemin_img = os.path.join(
                DOSSIER_PROFILS,
                f"profil_{nouveau_nom}_{nouveau_logo.name}",
            )
            with open(chemin_img, "wb") as f:
              f.write(nouveau_logo.getbuffer())

          mot_de_passe_final = (
              nouveau_mdp if nouveau_mdp != "" else actuel["mdp"]
          )

          if nouveau_nom != user_info["user"]:
            if nouveau_nom in utilisateurs:
              st.error(
                  "❌ Ce nom d'utilisateur est déjà pris par un autre compte."
              )
              st.stop()
            del utilisateurs[user_info["user"]]

          utilisateurs[nouveau_nom] = {
              "user": nouveau_nom,
              "mdp": mot_de_passe_final,
              "role": actuel["role"],
              "boutique": (
                  nouveau_nom
                  if actuel["role"] == "Fournisseur"
                  else actuel["boutique"]
              ),
              "phone": nouveau_phone,
              "gmail": nouveau_gmail,
              "profil_path": chemin_img,
              "ref_om": actuel["ref_om"],
              "ville": nouvelle_ville,
              "commune": nouvelle_commune,
              "langue": choix_langue,
          }

          sauvegarder_utilisateurs(utilisateurs)
          st.session_state.user_connecte = utilisateurs[nouveau_nom]
          st.success("🎉 Profil mis à jour avec succès ! Rechargement...")
          st.rerun()

  # --- ESPACE STORIES ---
  elif menu_principal == "📱 Stories (Statuts)":
    st.title("📱 Stories & Nouveautés des Articles")
    st.markdown(
        "Découvrez les publications instantanées et stories partagées par les"
        " vendeurs !"
    )

    if not os.path.exists(FICHIER_STORIES):
      open(FICHIER_STORIES, "w").close()

    with st.expander("➕ Publier une story sur un article"):
      with st.form("form_story", clear_on_submit=True):
        legende_story = st.text_area(
            "Légende / Description rapide de la story"
        )
        img_story_file = st.file_uploader(
            "Photo ou vidéo de l'article pour la story",
            type=["png", "jpg", "jpeg"],
        )
        btn_pub_story = st.form_submit_button("Publier la Story 🚀")
        if btn_pub_story:
          if not img_story_file:
            st.error("❌ Veuillez inclure une image pour votre story.")
          else:
            if not os.path.exists(DOSSIER_STORIES):
              os.makedirs(DOSSIER_STORIES)
            path_story = os.path.join(
                DOSSIER_STORIES,
                f"story_{user_info['user']}_{img_story_file.name}",
            )
            with open(path_story, "wb") as f:
              f.write(img_story_file.getbuffer())

            date_story = datetime.now().strftime("%d/%m/%Y %H:%M")
            with open(FICHIER_STORIES, "a", encoding="utf-8") as fs:
              fs.write(
                  f"{user_info['user']};{legende_story};{path_story};{date_story}\n"
              )
            st.success("🎉 Votre story a été publiée avec succès !")
            st.rerun()

    st.markdown("---")
    if os.path.exists(FICHIER_STORIES):
      with open(FICHIER_STORIES, "r", encoding="utf-8") as fs:
        lignes_stories = fs.readlines()

      if not lignes_stories:
        st.info("ℹ️ Aucune story active pour le moment.")
      else:
        for ligne in reversed(lignes_stories):
          s = ligne.strip().split(";")
          if len(s) >= 4:
            auteur, texte_s, img_s, date_s = s[0], s[1], s[2], s[3]
            with st.container():
              st.markdown(f"**👤 {auteur}** — *{date_s}*")
              if img_s and os.path.exists(img_s):
                st.image(img_s, width=350)
              st.write(f"💬 {texte_s}")
              st.markdown("---")

  # --- ESPACE CATALOGUE & ACHATS ---
  elif menu_principal == "🛍️ Catalogue & Achats":
    st.title("🛒 Catalogue des Produits - E-243")
    if not os.path.exists(FICHIER_PRODUITS):
      st.info("ℹ️ Aucun produit disponible.")
    else:
      recherche = st.text_input(
          "🔍 Rechercher un produit, une commune, un fournisseur..."
      )
      with open(FICHIER_PRODUITS, "r", encoding="utf-8") as f_prod:
        for ligne in f_prod:
          p = ligne.strip().split(";")
          if len(p) >= 8:
            boutique_vendeur, nom_p, cat_p, prix_p, stock_p, moq_p, desc_p, img_p = (
                p[0],
                p[1],
                p[2],
                p[3],
                p[4],
                p[5],
                p[6],
                p[7],
            )
            ville_p = p[8] if len(p) > 8 and p[8] else "Kisangani"
            commune_p = p[9] if len(p) > 9 and p[9] else "Non spécifiée"
            livraison_p = (
                p[10] if len(p) > 10 and p[10] else "À convenir avec le vendeur"
            )

            if (
                recherche.lower() in nom_p.lower()
                or recherche.lower() in boutique_vendeur.lower()
                or recherche.lower() in commune_p.lower()
            ):
              col_img, col_details = st.columns([1, 2])
              with col_img:
                if img_p and os.path.exists(img_p):
                  st.image(img_p, width=180)
                else:
                  st.info("📷 Pas d'image")
              with col_details:
                st.markdown(f"### 📦 {nom_p} ({prix_p} $)")
                st.write(
                    f"🏭 **Fournisseur :** {boutique_vendeur} | 📂"
                    f" **Catégorie :** {cat_p}"
                )
                st.write(
                    f"📍 **Adresse :** Ville de {ville_p}, Commune de"
                    f" {commune_p}"
                )
                st.write(
                    f"📦 **Stock :** {stock_p} pcs | ⚡ **MOQ :** {moq_p} pcs"
                )
                st.write(f"🚚 **Livraison :** {livraison_p}")
                st.write(f"📝 {desc_p}")

                if st.button(
                    f"💬 Contacter le fournisseur ({boutique_vendeur})",
                    key=f"chat_connecte_{boutique_vendeur}_{nom_p}",
                ):
                  date_str = datetime.now().strftime("%d/%m %H:%M")
                  msg_automatique = (
                      f"Bonjour, je suis intéressé par votre produit '{nom_p}'"
                      f" affiché à {prix_p}$."
                  )
                  if not os.path.exists(FICHIER_MESSAGES):
                    open(FICHIER_MESSAGES, "w").close()

                  with open(FICHIER_MESSAGES, "a", encoding="utf-8") as f_m:
                    f_m.write(
                        f"{user_info['user']};{boutique_vendeur};{user_info['user']};{msg_automatique};{date_str}\n"
                    )

                  st.session_state.chat_actif = boutique_vendeur
                  st.success(
                      f"Redirection vers la messagerie avec {boutique_vendeur}..."
                  )
                  st.rerun()
              st.markdown("---")

  # --- ESPACE MESSENGER ---
  elif menu_principal == "💬 Messenger":
    st.title("💬 Messagerie Directe (Style Messenger)")
    if not os.path.exists(FICHIER_MESSAGES):
      open(FICHIER_MESSAGES, "w").close()

    if user_info["role"] == "Fournisseur":
      acheteurs_dispos = set()
      with open(FICHIER_MESSAGES, "r", encoding="utf-8") as f:
        for ligne in f:
          m = ligne.strip().split(";")
          if len(m) >= 4 and m[1] == user_info["boutique"]:
            acheteurs_dispos.add(m[0])

      if not acheteurs_dispos:
        st.info("📭 Aucune discussion pour le moment.")
      else:
        liste_ach = list(acheteurs_dispos)
        if (
            "chat_actif_f" not in st.session_state
            or st.session_state.chat_actif_f not in liste_ach
        ):
          st.session_state.chat_actif_f = liste_ach[0]

        col_l, col_c = st.columns([1, 2], gap="medium")
        with col_l:
          st.markdown("#### 📥 Clients")
          for ach in liste_ach:
            if st.button(f"👤 {ach}", key=f"b_ach_{ach}", use_container_width=True):
              st.session_state.chat_actif_f = ach
              st.rerun()

        with col_c:
          client_choisi = st.session_state.chat_actif_f
          st.markdown(f"#### 💬 Discussion avec : {client_choisi}")
          chat_container = st.container(height=350)
          with chat_container:
            with open(FICHIER_MESSAGES, "r", encoding="utf-8") as f:
              for ligne in f:
                m = ligne.strip().split(";")
                if (
                    len(m) >= 5
                    and m[1] == user_info["boutique"]
                    and m[0] == client_choisi
                ):
                  exp, txt, dt = m[2], m[3], m[4]
                  align = "flex-end" if exp == user_info["user"] else "flex-start"
                  bg = "#0084ff" if exp == user_info["user"] else "#e4e6eb"
                  color = "white" if exp == user_info["user"] else "black"
                  st.markdown(
                      f"<div style='display: flex; justify-content: {align};"
                      f" margin-bottom: 8px;'><div style='background-color:"
                      f" {bg}; color: {color}; padding: 10px 14px; border-radius:"
                      f" 15px; max-width: 75%;'>{txt}<div style='font-size:"
                      f" 9px; text-align: right; opacity: 0.7;'>{dt}</div></div></div>",
                      unsafe_allow_html=True,
                  )

          with st.form(key=f"form_f_{client_choisi}", clear_on_submit=True):
            msg = st.text_input("Message...", label_visibility="collapsed")
            if st.form_submit_button("Envoyer 🚀") and msg:
              dt_str = datetime.now().strftime("%d/%m %H:%M")
              with open(FICHIER_MESSAGES, "a", encoding="utf-8") as f:
                f.write(
                    f"{client_choisi};{user_info['boutique']};{user_info['user']};{msg};{dt_str}\n"
                )
              st.rerun()
    else:
      boutiques_contactees = set()
      with open(FICHIER_MESSAGES, "r", encoding="utf-8") as f:
        for ligne in f:
          m = ligne.strip().split(";")
          if len(m) >= 4 and m[0] == user_info["user"]:
            boutiques_contactees.add(m[1])

      if not boutiques_contactees:
        st.info("ℹ️ Aucune conversation en cours.")
      else:
        liste_bq = list(boutiques_contactees)
        if (
            not st.session_state.chat_actif
            or st.session_state.chat_actif not in liste_bq
        ):
          st.session_state.chat_actif = liste_bq[0]

        col_l, col_c = st.columns([1, 2], gap="medium")
        with col_l:
          st.markdown("#### 🏭 Boutiques")
          for bq in liste_bq:
            if st.button(f"🏢 {bq}", key=f"b_bq_{bq}", use_container_width=True):
              st.session_state.chat_actif = bq
              st.rerun()

        with col_c:
          bq_choisie = st.session_state.chat_actif
          st.markdown(f"#### 💬 Discussion avec : {bq_choisie}")
          chat_container = st.container(height=350)
          with chat_container:
            with open(FICHIER_MESSAGES, "r", encoding="utf-8") as f:
              for ligne in f:
                m = ligne.strip().split(";")
                if (
                    len(m) >= 5
                    and m[0] == user_info["user"]
                    and m[1] == bq_choisie
                ):
                  exp, txt, dt = m[2], m[3], m[4]
                  align = "flex-end" if exp == user_info["user"] else "flex-start"
                  bg = "#0084ff" if exp == user_info["user"] else "#e4e6eb"
                  color = "white" if exp == user_info["user"] else "black"
                  st.markdown(
                      f"<div style='display: flex; justify-content: {align};"
                      f" margin-bottom: 8px;'><div style='background-color:"
                      f" {bg}; color: {color}; padding: 10px 14px; border-radius:"
                      f" 15px; max-width: 75%;'>{txt}<div style='font-size:"
                      f" 9px; text-align: right; opacity: 0.7;'>{dt}</div></div></div>",
                      unsafe_allow_html=True,
                  )

          with st.form(key=f"form_a_{bq_choisie}", clear_on_submit=True):
            msg = st.text_input("Message...", label_visibility="collapsed")
            if st.form_submit_button("Envoyer 🚀") and msg:
              dt_str = datetime.now().strftime("%d/%m %H:%M")
              with open(FICHIER_MESSAGES, "a", encoding="utf-8") as f:
                f.write(
                    f"{user_info['user']};{bq_choisie};{user_info['user']};{msg};{dt_str}\n"
                )
              st.rerun()

  # --- ESPACE GÉRER MES PRODUITS (FOURNISSEUR SEULEMENT) ---
  elif (
      menu_principal == "📦 Gérer mes produits"
      and user_info["role"] == "Fournisseur"
  ):
    st.title(f"📦 Tableau de bord Fournisseur - {user_info['boutique']}")
    tab1, tab2 = st.tabs(["➕ Publier un Produit", "📋 Mon Catalogue"])

    with tab1:
      with st.form("form_pub_prod"):
        nom_prod = st.text_input("Nom du produit")
        cat = st.selectbox(
            "Catégorie",
            [
                "Électronique & High-Tech",
                "Mode & Vêtements",
                "Alimentation & Vivres",
                "Matériaux & Divers",
            ],
        )
        prix = st.number_input("Prix unitaire (USD)", min_value=0.0, step=10.0)
        stock = st.number_input("Stock disponible", min_value=1, step=1)
        qte_min = st.number_input("MOQ (Minimum de commande)", min_value=1, value=1)
        ville_prod = st.text_input("Ville", value=user_info["ville"])
        commune_prod = st.text_input("Commune", value=user_info["commune"])
        livraison = st.text_input("Détails de livraison & Frais")
        desc = st.text_area("Description détaillée")
        img_file = st.file_uploader(
            "Photo du produit", type=["png", "jpg", "jpeg"]
        )

        if st.form_submit_button("Publier l'offre"):
          img_path = ""
          if img_file:
            if not os.path.exists(DOSSIER_PRODUITS):
              os.makedirs(DOSSIER_PRODUITS)
            img_path = os.path.join(
                DOSSIER_PRODUITS,
                f"prod_{user_info['boutique']}_{img_file.name}",
            )
            with open(img_path, "wb") as f:
              f.write(img_file.getbuffer())

          ligne = f"{user_info['boutique']};{nom_prod};{cat};{prix};{stock};{qte_min};{desc};{img_path};{ville_prod};{commune_prod};{livraison}\n"
          with open(FICHIER_PRODUITS, "a", encoding="utf-8") as f:
            f.write(ligne)
          st.success("🎉 Produit publié avec succès !")

    with tab2:
      st.subheader("Vos articles en ligne")
      if os.path.exists(FICHIER_PRODUITS):
        with open(FICHIER_PRODUITS, "r", encoding="utf-8") as f:
          lignes_produits = f.readlines()

        for ligne in lignes_produits:
          p = ligne.strip().split(";")
          if len(p) >= 8 and p[0] == user_info["boutique"]:
            nom_p, prix_p, stock_p, moq_p, img_p = (
                p[1],
                p[3],
                p[4],
                p[5],
                p[7],
            )
            ville_p = p[8] if len(p) > 8 and p[8] else "Kisangani"
            commune_p = p[9] if len(p) > 9 and p[9] else "Non spécifiée"

            st.write(f"### {nom_p} - {prix_p} $")
            if img_p and os.path.exists(img_p):
              st.image(img_p, width=120)
            st.write(
                f"Stock : {stock_p} | MOQ : {moq_p} | Ville : {ville_p},"
                f" Commune : {commune_p}"
            )
            st.markdown("---")
