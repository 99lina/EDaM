import pandas as pd
import functools
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar
import zipfile
import io

def representation_selection_key(column: str, transformation: str, group: str) -> str:
    return f'uiselection_{column.replace(" ", "")}_{transformation.replace(" ", "")}_{group.replace(" ", "")}'

def transformation_selection_key(column: str) -> str:
    return f'transformation_selection_{column.replace(" ", "")}'

# Type Variables für sauberes Typing (unterstützt beliebige Argumente und Rückgabewerte)
P = ParamSpec('P')
R = TypeVar('R')

def timeit(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.perf_counter()
        
        # Funktion ausführen
        result = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        
        print(f"⏱️  Funktion '{func.__name__}' ausgeführt in {elapsed_time:.6f} Sekunden.")
        return result
        
    return wrapper

def create_zip_archive(files: dict[str, str | bytes]) -> io.BytesIO:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files.items():
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

def df_to_parquet_bytes(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    data.to_parquet(buffer)
    return buffer.getvalue()