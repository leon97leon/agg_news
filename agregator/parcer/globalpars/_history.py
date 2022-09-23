import pandas as pd

from ._utils import Utils


def history(df: pd.DataFrame) -> pd.DataFrame:
    _history_df = df.loc[:, ['Заголовок', 'Ссылка']]
    print(f'Новых строк для обновления истории: {len(df.index)}')
    _history_df['Заголовок'] = [
        Utils.normal_str(title) for title
        in _history_df['Заголовок'].values
    ]
    return _history_df
