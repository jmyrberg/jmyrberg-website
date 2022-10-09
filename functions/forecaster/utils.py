"""Module for forecaster utils."""


import pandas as pd




def read_file(file, filename):
    ext = filename.split('.')[-1].lower()
    if ext in ('xls', 'xlsx'):
        df = pd.read_excel(file)
    elif ext in ('csv'):
        df = pd.read_csv(file)
    else:
        raise ValueError(f'Unknown file extension "{ext}"')

    return df


def try_convert_date(srs):
    for date_fmt in ['%Y-%m-%d', '%Y-%m', '%Y/%m', '%d.%m.%Y']:
        try:
            srs = pd.to_datetime(srs, format=date_fmt)
            return srs
        except ValueError:
            pass

    return srs


def try_convert_num(srs):
    try:
        return pd.to_numeric(srs, errors='raise')
    except ValueError:
        return srs


def convert_date_cols(df):
    df = df.copy()
    obj_cols = df.iloc[:0].select_dtypes(include=['object']).columns
    df[obj_cols] = df[obj_cols].apply(try_convert_date)
    return df


def convert_num_cols(df):
    df = df.copy()
    test_cols = df.select_dtypes(exclude=['datetime']).columns
    df[test_cols] = df[test_cols].apply(try_convert_num)
    return df


def find_freq(srs):
    return pd.infer_freq(srs)


def find_freqs(df):
    return df.select_dtypes('datetime').apply(find_freq).to_dict()


def humanize_dtype(dtype):
    if 'int' in dtype:
        return 'integer'
    elif 'float' in dtype:
        return 'float'
    elif 'datetime' in dtype:
        return 'date'
    else:
        return 'other'
