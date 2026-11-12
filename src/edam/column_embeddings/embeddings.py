import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from sklearn.decomposition import PCA


def get_column_embeddings(
    df: pd.DataFrame
) -> pd.DataFrame:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('all-MiniLM-L6-v2')
    df = df.astype(str)
    unique_vals = np.unique(df.to_numpy().flatten())

    print(f"Embedding {len(unique_vals)} unique items...")
    embeddings = model.encode(
        unique_vals,
        batch_size=256,
        show_progress_bar=False
    )

    val_to_emb = dict(zip(unique_vals, embeddings))

    col_embeddings = {
        col: np.mean(
            [val_to_emb[v] for v in df[col]],
            axis=0
        )
        for col in df.columns
    }
    return pd.DataFrame(col_embeddings)


def visualize_column_embeddings(emb_df=None, path = "", title="2D Semantic Space: Column Embeddings"):
    """
    Reduces column embeddings of a single DataFrame to 2D using PCA
    and plots them to visually inspect semantic relationships.

    The input DataFrame has to consist of column vectors.
    """

    if path != "":
        emb_df = pd.read_parquet(path)
    # 1. Extract embedding vectors
    if emb_df is not None:
        emb_df = emb_df.T
    else:
        raise ValueError("You must supply a dataframe or path to parquet file.")
    X = emb_df.copy()
    column_names = X.index

    # 2. Reduce dimensionality using PCA
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X)

    # 3. Build plotting DataFrame
    plot_df = pd.DataFrame(X_2d, columns=["PC1", "PC2"])
    plot_df["Column"] = column_names

    # 4. Create scatter plot
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    ax = sns.scatterplot(
        data=plot_df,
        x="PC1",
        y="PC2",
        s=120,
        color="#C1E3DD"
    )

    # 5. Annotate each point with its column name
    for _, row in plot_df.iterrows():
        plt.annotate(
            row["Column"],
            (row["PC1"] + 0.01, row["PC2"] + 0.01),
            fontsize=10,
            weight="bold",
            alpha=0.85
        )

    # 6. Format plot
    var_exp = pca.explained_variance_ratio_

    plt.title(title, fontsize=14, weight="bold", pad=15)
    plt.xlabel(f"Principal Component 1 ({var_exp[0] * 100:.1f}% Variance)")
    plt.ylabel(f"Principal Component 2 ({var_exp[1] * 100:.1f}% Variance)")

    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()


