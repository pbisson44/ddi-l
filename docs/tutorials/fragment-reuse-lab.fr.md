# Atelier de réutilisation de fragments

Cet atelier prolonge le script de reconstruction de fragments dans ``examples`` pour apprendre à empaqueter des fragments réutilisables, les distribuer à d'autres équipes et les réutiliser dans de nouvelles instances DDI.

!!! note
    Installez le projet en mode éditable (``pip install -e .``) afin que les exemples puissent localiser les modules ``ddi_l``.

!!! warning "Localiser les exemples empaquetés"
    Les scripts de fragments chargent les fichiers XML inclus dans la wheel sous
    ``ddi_l.examples`` plutôt que dans un dépôt cloné. Résolvez ces fichiers
    empaquetés avec ``importlib.resources`` et passez le chemin obtenu aux
    chargeurs (par exemple ``DDIDocument.from_xml``) :

    ```python
    from importlib import resources
    from ddi_l import examples

    with resources.as_file(
        resources.files(examples) / "example_fragment.xml"
    ) as fragment_path:
        print(fragment_path)
    ```

## 1. Reconstruire le paquet de fragments d'exemple

1. Exécutez ``python -m ddi_l.examples.build_and_validate --refresh --refresh-fragment``
   pour régénérer l'exemple. Le script réécrit
   ``examples/example_instance.xml`` et le fragment par défaut situé dans
   ``examples/example_fragment.xml`` tout en affichant une confirmation de la
   validation des deux charges utiles.
2. Inspectez les sorties XML régénérées de l'instance et du fragment pour voir
   comment les maintainables sont empaquetés et comment les messages de
   validation décrivent la reconstruction.
3. Relancez la commande avec ``--fragment-output`` si vous souhaitez écrire le
   fragment dans un autre emplacement (par exemple
   ``--fragment-output fragments/catalog/example_fragment.xml``) afin que les
   équipes sachent où récupérer l'artefact réutilisable.

## 2. Publier des fragments pour l'équipe

!!! caution "Contrôle de conformité avant diffusion"
    Dé-identifiez les charges utiles des fragments, supprimez les URN de
    production et alignez-vous sur les règles internes de gestion des données
    avant de partager des archives avec d'autres équipes. Suivez les
    [consignes d'expurgation du playbook d'automatisation CLI](automation-playbook.fr.md#5-mettre-en-evidence-les-constats-dans-les-tableaux-de-bord-ci)
    pour assurer un message cohérent entre les tutoriels.

1. Copiez les fragments générés dans un emplacement partagé (par exemple ``fragments/catalog``).
2. Rédigez un README qui décrit l'objectif du fragment, les identifiants des maintainables et le schéma de versionnage.
3. Optionnellement, regroupez les fragments et le rapport de validation dans une archive afin que les consommateurs aval téléchargent un seul artefact.

## 3. Consommer des fragments dans un nouveau projet

1. Créez un script Python et chargez à la fois le document cible et le fragment :

    ```python
    from ddi_l import MaintainableBase
    from ddi_l.document import DDIDocument, DDIFragment

    document = DDIDocument.from_xml("instances/source.ddi.xml")
    fragment = DDIFragment.from_xml("fragments/catalog/study-fragment.xml")
    ```

2. Itérez sur :meth:`ddi_l.document.DDIFragment.iter_fragment_payloads` et attachez explicitement chaque maintainable au document :

    ```python
    for payload in fragment.iter_fragment_payloads():
        maintainable_cls = MaintainableBase.for_tag(payload.tag)
        if maintainable_cls is None:
            raise ValueError(f"Unsupported payload: {payload.tag}")
        document.add_maintainable(maintainable_cls.from_xml(payload))
    ```

3. Sérialisez l'instance enrichie et exécutez ``ddi validate`` pour confirmer l'intégration correcte des fragments.

## 4. Maintenir la provenance des fragments

- Suivez les versions de fragments dans votre système de contrôle de version et taguez les publications afin que les équipes consommatrices puissent se caler sur des builds précis.
- Ajoutez un changelog à chaque release de fragment en précisant les versions de schéma et les attentes de lint.
- Automatisez la reconstruction des fragments dans la CI pour vous assurer que les nouvelles modifications restent compatibles avec l'instance canonique.
