import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLOR_SEQUENCE = ["#1f7a7a", "#70b9bd", "#f2b84b", "#d85b5b", "#6c8fac", "#7f9b6c"]


def apply_chart_theme(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=44, b=24),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#1f2937"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, linecolor="#d9e2ea")
    fig.update_yaxes(gridcolor="#edf2f6", linecolor="#d9e2ea")
    return fig


def count_bar(frame: pd.DataFrame, column: str, title: str, x_label: str | None = None, y_label: str = "Number of Records") -> go.Figure:
    counts = frame[column].fillna("Unknown").astype(str).value_counts().reset_index()
    counts.columns = [column, "records"]
    fig = px.bar(
        counts,
        x=column,
        y="records",
        color=column,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text=x_label or column.replace("_", " ").title())
    fig.update_yaxes(title_text=y_label)
    return apply_chart_theme(fig)


def histogram(frame: pd.DataFrame, column: str, title: str, nbins: int = 30, x_label: str | None = None, y_label: str = "Number of Records") -> go.Figure:
    fig = px.histogram(
        frame,
        x=column,
        nbins=nbins,
        title=title,
        color_discrete_sequence=["#1f7a7a"],
    )
    fig.update_xaxes(title_text=x_label or column.replace("_", " ").title())
    fig.update_yaxes(title_text=y_label)
    return apply_chart_theme(fig)


def box_by_category(frame: pd.DataFrame, x: str, y: str, title: str, x_label: str | None = None, y_label: str | None = None) -> go.Figure:
    fig = px.box(
        frame,
        x=x,
        y=y,
        color=x,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text=x_label or x.replace("_", " ").title())
    fig.update_yaxes(title_text=y_label or y.replace("_", " ").title())
    return apply_chart_theme(fig)


def scatter_segment(frame: pd.DataFrame, x: str, y: str, color: str, title: str, x_label: str | None = None, y_label: str | None = None) -> go.Figure:
    fig = px.scatter(
        frame,
        x=x,
        y=y,
        color=color,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
        opacity=0.72,
    )
    fig.update_xaxes(title_text=x_label or x.replace("_", " ").title())
    fig.update_yaxes(title_text=y_label or y.replace("_", " ").title())
    return apply_chart_theme(fig)
