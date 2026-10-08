# Clinique de dépannage des schémas

Entraînez-vous à diagnostiquer des erreurs de schéma avec la ligne de commande et l'API Python. Chaque exercice part d'un fichier volontairement altéré : vous lisez les erreurs, puis vous corrigez le fichier.

!!! note
    Installez ``ddi-l`` en mode éditable (``pip install -e .``) pour que les imports de modules fonctionnent.

## 1. Provoquer un échec de validation

1. Exécutez ``mkdir -p clinic`` pour créer un espace de travail qui isole l'instance altérée des exemples sources.
2. Copiez ``examples/Quality_of_Life.xml`` vers ``clinic/broken-instance.xml``.
3. Supprimez un attribut obligatoire (par exemple ``version`` sur un ``StudyUnit``) depuis votre éditeur.
4. Exécutez ``ddi validate clinic/broken-instance.xml`` pour lister chaque anomalie avec son message, sa ligne et son XPath. Ajoutez ``--format json`` pour obtenir un tableau JSON.
5. Notez l'XPath et le message associés au nœud fautif.

## 2. Reproduire l'erreur par programmation

1. Lancez une session Python et validez le même fichier avec le chargeur de schéma.
   En passant ``raise_error=False``, vous récupérez toute la liste d'erreurs au
   lieu de déclencher une exception dès la première :

    ```python
    from ddi_l.schema_loader import validate

    errors = validate("clinic/broken-instance.xml", raise_error=False)
    for error in errors:
        print("message :", error.message)
        print("xpath :", error.xpath)
        print("ligne :", error.line)
        print("colonne :", error.column)
    ```

2. Comparez la sortie à la structure JSON de la CLI. Les deux surfaces exposent la même métadonnée d'erreur pour choisir l'approche la mieux adaptée à vos outils.

## 3. Relier les constats aux règles de lint

1. Consultez ``docs/validation.md`` pour identifier les règles de lint capables de détecter des erreurs similaires (par exemple, identifiants d'agence manquants).
2. Ajoutez ces règles à votre profil de lint en appelant ``configure_lint()`` dans une session Python ou en éditant le fichier de profil de l'équipe.
3. Dans la même session Python, exécutez ``run_profile`` sur l'instance altérée pour vérifier que l'ensemble de règles signale l'erreur avant l'échec de validation :

    ```python
    from ddi_l.io import read
    from ddi_l.lint import DDI_PROFILE_DEFAULT, configure_lint, run_profile

    configure_lint()  # resserrez éventuellement les agences, citations, etc.
    document = read("clinic/broken-instance.xml")
    result = run_profile(document, DDI_PROFILE_DEFAULT)
    for finding in result.lint_findings:
        print(finding.rule_id, finding.message)
    ```

## 4. Établir une check-list de remédiation

- Vérifiez que le préfixe d'espace de noms du nœud en erreur est enregistré afin que les recherches de schéma retrouvent correctement l'élément.
- Restaurez les attributs obligatoires et relancez ``ddi validate`` jusqu'à obtenir ``Document is valid.``.
- Conservez des exemples représentatifs de l'erreur et de sa correction dans le guide d'exploitation de votre équipe pour accélérer la résolution des incidents futurs.
