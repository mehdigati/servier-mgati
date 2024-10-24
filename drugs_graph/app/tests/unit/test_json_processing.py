# Built-in packages
import unittest

# My Custom packages
from app.src.ad_hoc.json_processing import (get_all_articles_from_journal,
                                            get_drugs_mentioned_by_journal)


class TestJsonProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pubmed_of_journal = [
            {
                "article_id": "1",
                "article_title": "Aricle 1",
                "mention_date": "2019-01-01",
                "mentioned_drug_id": "D001",
                "mentioned_drug_name": "DrugB",
            },
            {"mentioned_drug_id": "D002", "mentioned_drug_name": "DrugC"},
        ]

        cls.clinical_trials_of_journal = [
            {
                "article_title": "Aricle 3",
                "mentioned_drug_id": "D001",
                "mentioned_drug_name": "DrugB",
            },
            {
                "article_id": "4",
                "article_title": "Aricle 4",
                "mention_date": "2020-05-01",
                "mentioned_drug_id": "D005",
                "mentioned_drug_name": "DrugD",
            },
            {
                "article_id": "5",
                "article_title": "Aricle 5",
                "mention_date": "2020-06-01",
                "mentioned_drug_id": "D007",
                "mentioned_drug_name": "DrugF",
            },
        ]

        # 4 different types of journals
        cls.journal_dict_complete = {
            "title": "Test Journal Title",
            "referenced_in": {
                "pubmed_articles": cls.pubmed_of_journal,
                "clinical_trials": cls.clinical_trials_of_journal,
            },
        }

        cls.journal_dict_pubmed_only = {
            "title": "Test Journal Title",
            "referenced_in": {
                "pubmed_articles": cls.pubmed_of_journal,
                "clinical_trials": [],
            },
        }

        cls.journal_dict_clinical_only = {
            "title": "Test Journal Title",
            "referenced_in": {
                "pubmed_articles": [],
                "clinical_trials": cls.clinical_trials_of_journal,
            },
        }

        cls.journal_dict_empty = {
            "title": "Test Journal Title",
            "referenced_in": {
                "pubmed_articles": [],
                "clinical_trials": [],
            },
        }

    def test_handles_missing_keys_in_articles(self):
        """Handles cases where the article object has missing keys (other than the drug-relted keys)."""
        result = get_drugs_mentioned_by_journal(
            self.pubmed_of_journal,
            self.clinical_trials_of_journal,
            return_drug_names=False,
        )
        expected_result = {"D001", "D002", "D005", "D007"}
        self.assertEqual(result, expected_result)

    def test_returns_drug_ids_when_return_drug_names_is_false(self):
        result = get_drugs_mentioned_by_journal(
            self.pubmed_of_journal,
            self.clinical_trials_of_journal,
            return_drug_names=False,
        )
        expected_result = {"D001", "D002", "D005", "D007"}
        self.assertEqual(result, expected_result)

    def test_returns_drug_names_when_return_drug_names_is_true(self):
        result = get_drugs_mentioned_by_journal(
            self.pubmed_of_journal,
            self.clinical_trials_of_journal,
            return_drug_names=True,
        )
        expected_result = {"DrugB", "DrugC", "DrugD", "DrugF"}
        self.assertEqual(result, expected_result)

    def test_extract_articles_from_journal_dict(self):
        # Expectations
        expected_result_complete = [
            self.pubmed_of_journal,
            self.clinical_trials_of_journal,
        ]
        expected_result_pubmed_only = [self.pubmed_of_journal, []]
        expected_result_clinical_only = [[], self.clinical_trials_of_journal]
        expected_result_empty = [[], []]

        # Run function
        result_complete = get_all_articles_from_journal(self.journal_dict_complete)
        result_pubmed_only = get_all_articles_from_journal(
            self.journal_dict_pubmed_only
        )
        result_clinical_only = get_all_articles_from_journal(
            self.journal_dict_clinical_only
        )
        result_empty = get_all_articles_from_journal(self.journal_dict_empty)

        # Assertions
        self.assertEqual(result_complete, expected_result_complete)
        self.assertEqual(result_pubmed_only, expected_result_pubmed_only)
        self.assertEqual(result_clinical_only, expected_result_clinical_only)
        self.assertEqual(result_empty, expected_result_empty)

    def test_journal_dict_missing_keys(self):
        journal_dict_no_keys = {}
        journal_dict_no_referenced_by = {"title": "myArticle"}
        journal_dict_no_clinical = {
            "title": "myArticle",
            "referenced_in": {"pubmed_articles": []},
        }
        journal_dict_no_pubmed = {
            "title": "myArticle",
            "referenced_in": {"clinical_trials": []},
        }

        # Check that the dictionaries raises errors
        with self.assertRaises(KeyError):
            get_all_articles_from_journal(journal_dict_no_keys)

        with self.assertRaises(KeyError):
            get_all_articles_from_journal(journal_dict_no_referenced_by)

        with self.assertRaises(KeyError):
            get_all_articles_from_journal(journal_dict_no_clinical)

        with self.assertRaises(KeyError):
            get_all_articles_from_journal(journal_dict_no_pubmed)

        # Check that well formed dictionaries do NOT raise errors
        get_all_articles_from_journal(self.journal_dict_complete)
        get_all_articles_from_journal(self.journal_dict_pubmed_only)
        get_all_articles_from_journal(self.journal_dict_clinical_only)
        get_all_articles_from_journal(self.journal_dict_empty)


if __name__ == "__main__":
    unittest.main()
