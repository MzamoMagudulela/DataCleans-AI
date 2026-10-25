"""
Data Visualizer Module
Provides interactive visualizations using Plotly for exploratory data analysis,
outlier inspection, and quality audits.
"""

from typing import Optional, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class DataVisualizer:
    """Generates charts for exploratory data analysis, distributions, and quality comparisons."""

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
        fig.update_layout(xaxis_title="Percentage (%) Missing", yaxis_title="Column", height=420)
        return fig

    @staticmethod
    def plot_distribution(df: pd.DataFrame, column: str) -> go.Figure:
        """
        Plots a histogram with marginal box plot for numeric columns or count bar for categorical.

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
                title=f"Distribution & Outlier Bounds: '{column}'",
                color_discrete_sequence=["#1E40AF"],
            )
            fig.update_layout(height=420)
        else:
            value_counts = series.astype(str).value_counts().reset_index()
            value_counts.columns = [column, "Count"]
            fig = px.bar(
                value_counts.head(20),
                x=column,
                y="Count",
                title=f"Category Frequency: '{column}'",
                color="Count",
                color_continuous_scale="Blues",
            )
            fig.update_layout(height=420)
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
        fig.update_layout(height=450)
        return fig

    @staticmethod
    def plot_bivariate_relationship(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        color_col: Optional[str] = None
    ) -> go.Figure:
        """
        Plots relationship between two columns (scatter or boxplot based on types).

        Args:
            df: DataFrame.
            x_col: X-axis column.
            y_col: Y-axis column.
            color_col: Optional grouping color column.

        Returns:
            go.Figure: Plotly chart.
        """
        if x_col not in df.columns or y_col not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="Selected columns not found in dataset.")
            return fig

        x_num = pd.api.types.is_numeric_dtype(df[x_col])
        y_num = pd.api.types.is_numeric_dtype(df[y_col])

        if x_num and y_num:
            # Numeric vs Numeric -> Scatter plot with trendline
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col if color_col and color_col in df.columns else None,
                trendline="ols" if len(df.dropna(subset=[x_col, y_col])) > 5 else None,
                title=f"Bivariate Scatter: {x_col} vs {y_col}",
            )
        elif not x_num and y_num:
            # Categorical vs Numeric -> Box plot
            fig = px.box(
                df,
                x=x_col,
                y=y_col,
                color=color_col if color_col and color_col in df.columns else None,
                title=f"Box Plot: {y_col} across {x_col}",
            )
        else:
            # Categorical vs Categorical or Numeric vs Categorical
            fig = px.histogram(
                df,
                x=x_col,
                color=y_col,
                barmode="group",
                title=f"Grouped Distribution: {x_col} by {y_col}",
            )

        fig.update_layout(height=450)
        return fig

    @staticmethod
    def plot_quality_comparison(
        initial_metrics: Dict[str, Any],
        cleaned_metrics: Dict[str, Any]
    ) -> go.Figure:
        """
        Creates a side-by-side bar chart showing pre vs post-cleaning metric improvements.

        Args:
            initial_metrics: Baseline metrics dict.
            cleaned_metrics: Cleaned metrics dict.

        Returns:
            go.Figure: Plotly comparison chart.
        """
        categories = ["Duplicate Rows", "Missing Cells (%)", "Health Score"]
        initial_vals = [
            initial_metrics.get("duplicate_rows", 0),
            initial_metrics.get("missing_percentage", 0),
            initial_metrics.get("health_score", 0),
        ]
        cleaned_vals = [
            cleaned_metrics.get("duplicate_rows", 0),
            cleaned_metrics.get("missing_percentage", 0),
            cleaned_metrics.get("health_score", 0),
        ]

        fig = go.Figure(data=[
            go.Bar(name="Initial (Raw)", x=categories, y=initial_vals, marker_color="#EF4444"),
            go.Bar(name="Cleaned", x=categories, y=cleaned_vals, marker_color="#10B981"),
        ])
        fig.update_layout(
            barmode="group",
            title="Data Quality Improvement (Pre-Clean vs Post-Clean)",
            height=380,
        )
        return fig
