from datasets import load_from_disk
from transformers import DataCollatorWithPadding

from .base import HuggingFaceBatchFineTuner


class CommonsenseReasoningFineTuner(HuggingFaceBatchFineTuner):
    """
    A bolt for fine-tuning Hugging Face models on commonsense reasoning tasks.

    This bolt extends the HuggingFaceBatchFineTuner to handle the specifics of commonsense reasoning tasks,
    such as the specific format of the datasets and the specific metrics for evaluation.

    The dataset should be in the following format:
    - Each example is a dictionary with the following keys:
        - 'premise': a string representing the premise.
        - 'hypothesis': a string representing the hypothesis.
        - 'label': an integer representing the label (0 for entailment, 1 for neutral, 2 for contradiction).
    """

    def load_dataset(self, dataset_path, **kwargs):
        """
        Load a dataset from a directory.

        Args:
            dataset_path (str): The path to the directory containing the dataset files.
            **kwargs: Additional keyword arguments to pass to the `load_dataset` method.

        Returns:
            Dataset: The loaded dataset.
        """
        # Load the dataset from the directory
        dataset = load_from_disk(dataset_path)

        # Preprocess the dataset
        tokenized_dataset = dataset.map(self.prepare_train_features, batched=True, remove_columns=dataset.column_names)

        return tokenized_dataset

    def prepare_train_features(self, examples):
        """
        Tokenize the examples and prepare the features for training.

        Args:
            examples (dict): A dictionary of examples.

        Returns:
            dict: The processed features.
        """
        # Tokenize the examples
        tokenized_inputs = self.tokenizer(examples["premise"], examples["hypothesis"], truncation=True, padding=False)

        # Prepare the labels
        tokenized_inputs["labels"] = examples["label"]

        return tokenized_inputs

    def data_collator(self, examples):
        """
        Customize the data collator.

        Args:
            examples: The examples to collate.

        Returns:
            dict: The collated data.
        """
        return DataCollatorWithPadding(self.tokenizer)(examples)
