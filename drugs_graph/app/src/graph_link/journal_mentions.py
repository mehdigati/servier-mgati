import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

import pandas as pd


@dataclass
class JournalMentions:
    title: str
    drugs_dataFrame: pd.DataFrame
    journal_articles_dataFrame: pd.DataFrame  # Articles of the current journal only
    pubmed_publications: List = field(default_factory=list, init=False)
    clinical_trials_publications: List = field(default_factory=list, init=False)

    def extract_drug_from_publication_title(self, article_title: str) -> List:
        title_words_set = set(article_title.split())

        mentioned_drugs = []

        for drug_id, row in self.drugs_dataFrame.iterrows():
            if row["name"] in title_words_set:
                mentioned_drugs.append([drug_id, row["name"]])

        if mentioned_drugs == []:
            # No drug found, and given our hypothesis, we skip it
            logging.warning(
                f"No drug was mentioned in the following title : `{article_title}`"
            )

        return mentioned_drugs

    def get_article_information_from_id(self, article_id: str) -> Dict:
        current_article_row = self.journal_articles_dataFrame.loc[article_id]

        article_title = current_article_row["title"]
        mention_date = current_article_row["date"]
        article_type = current_article_row["article_type"]

        # Transform date to string
        mention_date_str = datetime.strftime(mention_date, "%Y-%m-%d")

        article_info = {
            "title": article_title,
            "date": mention_date_str,
            "isPubMed": True if article_type == "PubMed" else False,
            "isClinical": True if article_type == "ClinicalTrial" else False,
        }

        return article_info

    def build_links_articles_drug_mentions(self) -> None:
        for article_id in self.journal_articles_dataFrame.index:
            # Get info about articles
            article_info = self.get_article_information_from_id(article_id)

            # Find mentioned drug(s)
            list_mentioned_drugs = self.extract_drug_from_publication_title(
                article_info["title"]
            )

            for mentioned_drug_info in list_mentioned_drugs:
                mentioned_drug_id, mentioned_drug_name = mentioned_drug_info

                currLinkDict = {
                    "article_id": article_id,
                    "article_title": article_info["title"],
                    "mention_date": article_info["date"],
                    "mentioned_drug_id": mentioned_drug_id,
                    "mentioned_drug_name": mentioned_drug_name,
                }

                if article_info["isPubMed"] is True:
                    self.pubmed_publications.append(currLinkDict)
                elif article_info["isClinical"] is True:
                    self.clinical_trials_publications.append(currLinkDict)
                else:
                    raise Exception(
                        f"Something went wrong, the article { article_info['title']} is neither clinical nor pubmed"
                    )

    def generate_article_link_graph_dict(self) -> Dict:
        self.build_links_articles_drug_mentions()

        output = {
            "title": self.title,
            "referenced_in": {
                "pubmed_articles": self.pubmed_publications,
                "clinical_trials": self.clinical_trials_publications,
            },
        }

        return output
