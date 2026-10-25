"""
Data Visualizer Module
Provides interactive visualizations using Plotly and statistical plots.
"""

from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class DataVisualizer:
    """Generates charts for exploratory data analysis and quality inspection."""

    @staticmethod
    def plot_missing_summary(df: pd.DataFrame) -> go.Figure:
        """
        Creates a horizontal bar chart showing the percentage of missing values per column.

        Args:
            df: DataFrame to visualize.

        Returns:
            go.Figure: Plotly chart figure.
        """
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="No data available")
            return fig

        missing_series = df.isna().sum()
        missing_pct = (missing_series / len(df)) * 100
        missing_df = pd.DataFrame({
            "Column": missing_series.index,
            "Missing Count": missing_series.values,
            "Missing Percentage": missing_pct.values,
        }).sort_values(by="Missing Percentage", ascending=True)

        fig = px.bar(
            missing_df,
            x="Missing Percentage",
            y="Column",
            orientation="h",
            title="Missing Value Distribution (%) by Column",
            text="Missing Count",
            color="Missing Percentage",
            color_continuous_scale="Reds",
        )
        fig.update_layout(xaxis_title="Percentage (%) Missing", yaxis_title="Column", height=400)
        return fig

    @staticmethod
    def plot_distribution(df: pd.DataFrame, column: str) -> go.Figure:
        """
        Plots a histogram with box plot for a numeric column or count bar for categorical.

        Args:
            df: DataFrame containing the column.
            column: Name of column to plot.

        Returns:
            go.Figure: Plotly figure.
        """
        if column not in df.columns or df[column].empty:
            fig = go.Figure()
            fig.update_layout(title=f"Column '{column}' is empty or not found.")
            return fig

        series = df[column].dropna()
        if pd.api.types.is_numeric_dtype(series):
            fig = px.histogram(
                df,
                x=column,
                marginal="box",
                title=f"Distribution of '{column}'",
                color_discrete_sequence=["#2b6cb0"],
            )
        else:
            value_counts = series.astype(str).value_counts().reset_index()
            value_counts.columns = [column, "Count"]
            fig = px.bar(
                value_counts.head(20),
                x=column,
                y="Count",
                title=f"Top Category Counts for '{column}'",
                color="Count",
                color_continuous_scale="Blues",
            )
        return fig

    @staticmethod
    def plot_correlation_heatmap(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Plots a correlation heatmap for all numeric columns.

        Args:
            df: DataFrame to analyze.

        Returns:
            Optional[go.Figure]: Plotly heatmap or None if insufficient numeric columns.
        """
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.shape[1] < 2:
            return None

        corr = numeric_df.corr().round(2)
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Correlation Heatmap (Numeric Columns)",
            zmin=-1,
            zmax=1,
        )
        return fig
