def summarize_dataset(df):
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "columns_list": list(df.columns)
    }
