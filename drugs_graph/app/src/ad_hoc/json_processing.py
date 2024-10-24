import logging
from typing import Dict, List, Set


def get_all_articles_from_journal(journal_dict: Dict) -> List:
    """
    Extracts all articles from a journal dictionary
    """
    if (
        "referenced_in" not in journal_dict
        or "pubmed_articles" not in journal_dict["referenced_in"]
        or "clinical_trials" not in journal_dict["referenced_in"]
    ):
        raise KeyError(
            f"The following journal is broken and missing important keys : {journal_dict} "
        )

    pubmed = journal_dict["referenced_in"]["pubmed_articles"]
    clinical_trials = journal_dict["referenced_in"]["clinical_trials"]

    return [pubmed, clinical_trials]


def get_drugs_mentioned_by_journal(
    pubmed_of_journal: List,
    clinical_trials_of_journal: List,
    return_drug_names: bool = False,
) -> Set:
    """
    Extracts all drugs mentioned in a journal"""
    mentioned_drugs_no_duplicates = set()
    all_articles = pubmed_of_journal + clinical_trials_of_journal

    for article_object in all_articles:
        if return_drug_names:
            mentioned_drugs_no_duplicates.add(article_object["mentioned_drug_name"])
        else:
            mentioned_drugs_no_duplicates.add(article_object["mentioned_drug_id"])

    return mentioned_drugs_no_duplicates
