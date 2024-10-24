import argparse
import logging
import os
from typing import List

import app.src.ad_hoc.json_processing as A
import app.src.data_processing.load as L
import app.src.data_processing.preprocess as C
import app.src.data_processing.transform as T
import app.src.files_processing.files_processing as U
import pandas as pd
from google.cloud import logging as cloud_logging

# LOGGING
LOGGING_GCP_PROJECT_ID = os.getenv("LOGGING_GCP_PROJECT_ID", "")
logging_client = cloud_logging.Client(project=LOGGING_GCP_PROJECT_ID)
logger = logging_client.logger("servier-drugs-graph")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--action",
        type=str,
        choices=["generate_graph", "get_journal_with_most_drugs"],
        help="Action to perform",
        required=True,
    )

    parser.add_argument(
        "--data_path",
        type=str,
        help="The name and path of the data folder. Default value : data",
        default="data",
    )

    parser.add_argument(
        "--output_path",
        type=str,
        help="The name and path of the output json file. Default value : outputs/graph.json",
        default="outputs/graph.json",
    )

    return parser.parse_args()


def clean_dataframes(
    clinical_df: pd.DataFrame, pubmed_df: pd.DataFrame, drugs_df: pd.DataFrame
) -> List:
    """
    This function is simply used to orchestrate the different cleaning steps in the correct order.
    Check the docstring of each function or the in-line comments for more details.
    """
    # Standardize column names
    clinical_df = C.rename_column(clinical_df, {"scientific_title": "title"})
    drugs_df = C.rename_column(drugs_df, {"drug": "name"})
    logging.info("[Cleaning] - Successfully renamed columns.")

    # Standardize the Date format (into %Y-%m-%d)
    clinical_df = C.normalize_dates_format(clinical_df, "date", "%Y-%m-%d")
    pubmed_df = C.normalize_dates_format(pubmed_df, "date", "%Y-%m-%d")
    logging.info("[Cleaning] - Successfully standardized date formats.")

    # Merge duplicate rows together, filling in missing columns based on other rows
    clinical_articles_group = clinical_df.groupby(["title", "date"], group_keys=False)[
        clinical_df.columns.tolist()
    ]
    clinical_df = clinical_articles_group.apply(T.merge_rows).reset_index(drop=True)

    pubmed_articles_group = pubmed_df.groupby(["title", "date"], group_keys=False)[
        clinical_df.columns.tolist()
    ]
    pubmed_df = pubmed_articles_group.apply(T.merge_rows).reset_index(drop=True)
    logging.info("[Cleaning] - Successfully filled in missing data.")

    # Fill in missing IDs
    pubmed_df = C.fill_in_missing_ids_int(pubmed_df, "id")
    logging.info("[Cleaning] - Successfully interpolated missingIDs.")

    # Clean titles and names
    pubmed_df["title"] = pubmed_df["title"].apply(C.clean_titles)
    pubmed_df["journal"] = pubmed_df["journal"].apply(C.clean_titles)

    clinical_df["title"] = clinical_df["title"].apply(C.clean_titles)
    clinical_df["journal"] = clinical_df["journal"].apply(C.clean_titles)

    drugs_df["name"] = drugs_df["name"].apply(C.clean_titles)
    logging.info("[Cleaning] - Successfully cleaned all titles and names.")

    # Standardize the type of IDs used (string)
    pubmed_df = C.cast_id_as_string(pubmed_df, "id")
    clinical_df = C.cast_id_as_string(clinical_df, "id")

    return clinical_df, pubmed_df, drugs_df


def generate_graph(data_path: str, output_path: str) -> None:
    # Define the paths to the data
    clinical_trials_path = U.list_files_in_folder(
        f"{data_path}/clinical_trials", file_types=["csv", "json"]
    )
    pubmed_path = U.list_files_in_folder(
        f"{data_path}/pubmed", file_types=["csv", "json"]
    )
    drugs_path = U.list_files_in_folder(
        f"{data_path}/drugs", file_types=["csv", "json"]
    )

    # Load Data
    clinical_df = L.load_input_data(clinical_trials_path)
    pubmed_df = L.load_input_data(pubmed_path)
    drugs_df = L.load_input_data(drugs_path)

    # Clean dataframes
    clinical_df_cleaned, pubmed_df_cleaned, drugs_df_cleaned = clean_dataframes(
        clinical_df, pubmed_df, drugs_df
    )

    # Enrich the dataframes with the types of articles, before merging
    pubmed_df_cleaned["article_type"] = "PubMed"
    clinical_df_cleaned["article_type"] = "ClinicalTrial"

    # Merge the articles dataframes into one
    all_articles_df = T.merge_dataframes([pubmed_df_cleaned, clinical_df_cleaned])
    logging.info(
        "[Transform] - Successfully merged the pubmed and clinical trials dataframes."
    )

    # Remove empty strings
    all_articles_df_cleaned = C.drop_empty_titles_and_journals(all_articles_df)
    logging.info("[Cleaning] - Successfully droped rows with empty titles and names.")

    # Drop duplicate IDs and index dataframes
    drugs_df_cleaned, all_articles_df_cleaned = C.drop_duplicate_ids_then_index(
        drugs_df_cleaned, all_articles_df_cleaned
    )
    logging.info("[Cleaning] - Successfully droped rows with duplicate IDs.")

    # Finally, generate the graph as json file
    output_graph = T.build_link_graph_from_df(all_articles_df_cleaned, drugs_df_cleaned)
    U.write_dict_to_file(output_path, output_graph)
    logging.info(f"[Transform] - Link graph successfully written to {output_path}.")


def get_journal_with_most_drugs(output_path: str) -> List:
    """
    Returns a list of the name(s) of the journal(s) that has mentioned most unique drugs.
    In the case of a tie, all the tied journal are returned.
    """
    graph_dict = U.import_json_file_as_dict(output_path)

    unique_mentions_mapping = {}

    for journal_object in graph_dict["journals"]:
        (
            curr_pubmed_articles,
            curr_clinical_trials_articles,
        ) = A.get_all_articles_from_journal(journal_object)

        set_curr_mentioned_drugs = A.get_drugs_mentioned_by_journal(
            pubmed_of_journal=curr_pubmed_articles,
            clinical_trials_of_journal=curr_clinical_trials_articles,
            return_drug_names=False,  # Use IDs to be more accurate
        )

        unique_mentions_mapping[journal_object["title"]] = len(set_curr_mentioned_drugs)

    max_nb_unique_mentions = max(unique_mentions_mapping.values())
    journals_with_most_drugs = [
        key
        for key, value in unique_mentions_mapping.items()
        if value == max_nb_unique_mentions
    ]

    logging.info(
        f"The journal(s) {', '.join(journals_with_most_drugs)} has mentioned {max_nb_unique_mentions} unique drugs"
    )

    return journals_with_most_drugs


if __name__ == "__main__":
    args = parse_arguments()

    if args.action == "generate_graph":
        generate_graph(
            data_path=args.data_path,
            output_path=args.output_path,
        )

    elif args.action == "get_journal_with_most_drugs":
        journals_with_most_drugs = get_journal_with_most_drugs(args.output_path)
        print(journals_with_most_drugs)

    else:
        raise ValueError("Invalid action")
