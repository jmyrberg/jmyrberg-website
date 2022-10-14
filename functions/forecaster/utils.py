"""Module for forecaster utils."""


import pandas as pd

from werkzeug.datastructures import FileStorage


def read_file(file: FileStorage, filename: str) -> pd.DataFrame:
    ext = filename.split('.')[-1].lower()
    if ext in ('xls', 'xlsx'):
        df = pd.read_excel(file)
    elif ext in ('csv'):
        df = pd.read_csv(file)
    else:
        raise ValueError(f'Unknown file extension "{ext}"')

    return df


def try_convert_date(srs: pd.Series) -> pd.Series:
    for date_fmt in ['%Y-%m-%d', '%Y-%m', '%Y/%m', '%d.%m.%Y']:
        try:
            return pd.to_datetime(srs, format=date_fmt)
        except ValueError:
            return srs


def try_convert_num(srs: pd.Series) -> pd.Series:
    try:
        return pd.to_numeric(srs, errors='raise')
    except ValueError:
        return srs


def convert_date_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    obj_cols = df.iloc[:0].select_dtypes(include=['object']).columns
    df[obj_cols] = df[obj_cols].apply(try_convert_date)
    return df


def convert_num_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    maybe_num_cols = df.select_dtypes(exclude=['datetime']).columns
    df[maybe_num_cols] = df[maybe_num_cols].apply(try_convert_num)
    return df


def find_freq(srs: pd.Series) -> pd.Series:
    # TODO: Smarter / more complex logic
    return pd.infer_freq(srs)


def find_freqs(df: pd.DataFrame) -> dict:
    return df.select_dtypes('datetime').apply(find_freq).to_dict()


def humanize_dtype(dtype: str) -> str:
    if 'int' in dtype:
        return 'integer'
    elif 'float' in dtype:
        return 'float'
    elif 'datetime' in dtype:
        return 'date'
    else:
        return 'other'
