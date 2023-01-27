"""
Contains all pheval utility methods
"""


from pathlib import Path

import numpy
import pandas as pd
import plotly.express as px

import pheval.utils.file_utils as file_utils


def filter_non_0_score(data: pd.DataFrame, col: str) -> pd.DataFrame:
    """Removes rows that have value equal to 0 based on the given column passed by col parameter

    Args:
        data (pd.DataFrame): Dirty dataframe
        col (str): Column to be filtered

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    return data[data[col] != 0]


def parse_semsim(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Parses semantic similarity profiles converting the score column as a numeric value and dropping the null ones

    Args:
        df (pd.DataFrame): semantic similarity profile dataframe
        cols (list): list of columns that will be selected on semsim data

    Returns:
        pd.Dataframe: parsed semantic similarity dataframe
    """
    df[cols[-1]] = pd.to_numeric(df[cols[-1]], errors="coerce")
    df.replace("None", numpy.nan).dropna(subset=cols[-1], inplace=True)
    return df


def diff_semsim(semsim_left: pd.DataFrame, semsim_right: pd.DataFrame, score_column: str) -> pd.DataFrame:
    """Calculates score difference between two semantic similarity profiles

    Args:
        semsim_left (pd.DataFrame): first semantic similarity dataframe
        semsim_right (pd.DataFrame): second semantic similarity dataframe
        score_column (str): [description]

    Returns:
        pd.DataFrame: A dataframe with terms and its scores differences
    """
    keys = ["subject_id", "object_id"]
    df = pd.merge(semsim_left, semsim_right, on=keys, how="outer")

    df["diff"] = df[f"{score_column}_x"] - df[f"{score_column}_y"]
    return df[["subject_id", "object_id", "diff"]]


def semsim_heatmap_plot(semsim_left: Path, semsim_right: Path, score_column: str):
    """Plots semantic similarity profiles heatmap

    Args:
        semsim_left (Path): File path of the first semantic similarity profile
        semsim_right (Path): File path of the second semantic similarity profile
        score_column (str): Score column that will be computed (e.g. jaccard_similarity)
    """
    if semsim_left == semsim_right:
        errmsg = "Semantic similarity profiles are equal. Make sure you have selected different files to analyze"
        raise Exception(errmsg)
    file_utils.ensure_file_exists(semsim_left, semsim_right)
    cols = ["subject_id", "object_id", score_column]
    semsim_left = pd.read_csv(semsim_left, sep="\t")
    semsim_right = pd.read_csv(semsim_right, sep="\t")
    file_utils.ensure_columns_exists(
        cols=cols,
        err_message="must exist in semsim dataframes",
        dataframes=[semsim_left, semsim_right],
    )
    semsim_left = parse_semsim(semsim_left, cols)
    semsim_right = parse_semsim(semsim_right, cols)
    diff_df = diff_semsim(semsim_left, semsim_right, score_column)
    clean_df = filter_non_0_score(diff_df, "diff")
    df = clean_df.pivot(index="subject_id", columns="object_id", values="diff")
    fig = px.imshow(df, text_auto=True)
    fig.show()
