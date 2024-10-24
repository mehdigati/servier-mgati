import logging
from typing import Dict, List

import pandas as pd
from app.src.graph_link.journal_mentions import JournalMentions


def merge_dataframes(list_dataframes: List) -> pd.DataFrame:
    return pd.concat(list_dataframes)


def merge_rows(group):
    return group.ffill().bfill().iloc[0]


def build_link_graph_from_df(
    df_articles_cleaned: pd.DataFrame, df_drugs_cleaned: pd.DataFrame
) -> Dict:
    list_distinct_journals = df_articles_cleaned["journal"].unique()

    output_dict = {"journals": []}

    for journal in list_distinct_journals:
        logging.info(f"Currently generating graph for {journal}")
        articles_of_journal_condition = df_articles_cleaned["journal"] == journal

        df_articles_of_journal = df_articles_cleaned[articles_of_journal_condition]

        journal_instance = JournalMentions(
            title=journal,
            drugs_dataFrame=df_drugs_cleaned,
            journal_articles_dataFrame=df_articles_of_journal,
        )

        current_graph_dict = journal_instance.generate_article_link_graph_dict()
        output_dict["journals"].append(current_graph_dict)

    return output_dict
