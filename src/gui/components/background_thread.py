import streamlit as st
from concurrent.futures import ThreadPoolExecutor, Future
from collections.abc import Callable

def run_in_background(func: Callable, name: str, *args, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    st.session_state[name] = executor.submit(func, *args, **kwargs)
    st.session_state[f"{name}_worker"] = executor

def retrieve_result(name: str, spinner: bool = False, loading_message: str = "Retrieving result..."):
    future = st.session_state.get(name)
    if not isinstance(future, Future):
        raise KeyError(f"There is no Future object at st.session_state.{name}")
    if spinner:
        with st.spinner(loading_message):
            return future.result()
    else:
        return future.result()