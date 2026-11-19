import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px

class Visualizer:
    """
    A class for visualizing datasets using various plotting techniques.
    """

    def __init__(self, df: pd.DataFrame, type: str, x_column: str, y_column: str = None):
        """
        Initialize the visualizer with a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to visualize.
            type (str): The type of visualizer to create.
            x_column (str): The column name for the x-axis.
            y_column (str): The column name for the y-axis (optional).
        """
        self.df = df
        self.type = type
        self.x_column = x_column
        self.y_column = y_column

    def plot_histogram(self, column: str, bins: int = 10):
        """
        Plot a histogram for a specified column.

        Args:
            column (str): The column name to plot.
            bins (int): Number of bins for the histogram.
        """
        try:
            if column not in self.df.columns:
                raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
            elif column is not None and not pd.api.types.is_numeric_dtype(self.df[column]):
                raise ValueError(f"Column '{column}' is not numeric and cannot be used for histogram plotting.")
            elif column is not None and self.df[column].isnull().all():
                raise ValueError(f"Column '{column}' contains only NaN values and cannot be used for histogram plotting.")
            elif column is not None and self.df[column].nunique() <= 1:
                raise ValueError(f"Column '{column}' has insufficient unique values for histogram plotting.")
            elif column is not None and self.df[column].nunique() < bins:
                raise ValueError(f"Column '{column}' has fewer unique values than the specified number of bins ({bins}).")
            elif bins <= 0:
                raise ValueError("Number of bins must be a positive integer.")
            else:
                plt.figure(figsize=(10, 6))
                sns.histplot(self.df[column], bins=bins, kde=True)
                plt.title(f'Histogram of {column}')
                plt.xlabel(column)
                plt.ylabel('Frequency')
                plt.show()

        except ValueError as ve:
            print(f"ValueError: {ve}")
    def plot_scatter(self, x_column: str, y_column: str):
        """
        Plot a scatter plot between two specified columns.

        Args:
            x_column (str): The column name for the x-axis.
            y_column (str): The column name for the y-axis.
        """
        try:
            if x_column not in self.df.columns or y_column not in self.df.columns:
                raise ValueError("One or both specified columns do not exist in the DataFrame.")
            
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=self.df, x=x_column, y=y_column)
            plt.title(f'Scatter Plot of {y_column} vs {x_column}')
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.show()
        except ValueError as ve:
            print(f"ValueError: {ve}")  

        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=self.df, x=x_column, y=y_column)
        plt.title(f'Scatter Plot of {y_column} vs {x_column}')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.show()

    def plot_correlation_matrix(self):
        """
        Plot a heatmap of the correlation matrix for the DataFrame.
        """
        plt.figure(figsize=(12, 8))
        correlation_matrix = self.df.corr()
        sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm')
        plt.title('Correlation Matrix Heatmap')
        plt.show()

    def plot_boxplot(self, column: str):
        """
        Plot a boxplot for a specified column.

        Args:
            column (str): The column name to plot.
        """
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=self.df[column])
        plt.title(f'Boxplot of {column}')
        plt.xlabel(column)
        plt.show()

    def plot_line(self, x_column: str, y_column: str):
        """
        Plot a line plot between two specified columns.

        Args:
            x_column (str): The column name for the x-axis.
            y_column (str): The column name for the y-axis.
        """
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=self.df, x=x_column, y=y_column)
        plt.title(f'Line Plot of {y_column} vs {x_column}')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.show()

    result = None
    if type == 'histogram':
        result = plot_histogram
    elif type == 'scatter':
        result = plot_scatter
    elif type == 'correlation_matrix':
        result = plot_correlation_matrix
    elif type == 'boxplot':
        result = plot_boxplot
    elif type == 'line':
        result = plot_line

class interactive_visualizer:
    """
    A class for creating interactive visualizations using Plotly.
    """

    def __init__(self, df: pd.DataFrame, type : str):
        """
        Initialize the interactive visualizer with a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to visualize.
            type (str): The type of visualizer to create.
        """
        self.df = df
        self.type = type

    def plot_interactive_scatter(self, x_column: str, y_column: str, color_column: str = None):
        """
        Create an interactive scatter plot between two specified columns.

        Args:
            x_column (str): The column name for the x-axis.
            y_column (str): The column name for the y-axis.
            color_column (str): The column name for coloring the points (optional).
        """
        fig = px.scatter(self.df, x=x_column, y=y_column, color=color_column,
                         title=f'Interactive Scatter Plot of {y_column} vs {x_column}')
        fig.show()

    def plot_interactive_histogram(self, column: str, nbins: int = 10):
        """
        Create an interactive histogram for a specified column.

        Args:
            column (str): The column name to plot.
            nbins (int): Number of bins for the histogram.
        """
        fig = px.histogram(self.df, x=column, nbins=nbins,
                           title=f'Interactive Histogram of {column}')
        fig.show()

    def plot_interactive_boxplot(self, column: str):
        """
        Create an interactive boxplot for a specified column.

        Args:
            column (str): The column name to plot.
        """
        fig = px.box(self.df, y=column, title=f'Interactive Boxplot of {column}')
        fig.show()

    def interactive_correlation_matrix(self):
        """
        Create an interactive heatmap of the correlation matrix for the DataFrame.
        """
        correlation_matrix = self.df.corr()
        fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto",
                        title='Interactive Correlation Matrix Heatmap')
        fig.show()

    def plot_interactive_line(self, x_column: str, y_column: str):
        """
        Create an interactive line plot between two specified columns.

        Args:
            x_column (str): The column name for the x-axis.
            y_column (str): The column name for the y-axis.
        """
        fig = px.line(self.df, x=x_column, y=y_column,
                      title=f'Interactive Line Plot of {y_column} vs {x_column}')
        fig.show()

    result = None
    if type == 'histogram':
        result = plot_interactive_histogram
    elif type == 'scatter':
        result = plot_interactive_scatter
    elif type == 'correlation_matrix':
        result = interactive_correlation_matrix
    elif type == 'boxplot':
        result = plot_interactive_boxplot
    elif type == 'line':
        result = plot_interactive_line

    

class visualizer_factory:
    """
    A factory class to create instances of visualizer or interactive_visualizer based on user preference.
    """

    @staticmethod
    def get_visualizer(df: pd.DataFrame, type: str, interactive: bool = False):
        """
        Get an instance of visualizer or interactive_visualizer.

        Args:
            df (pd.DataFrame): The DataFrame to visualize.
            interactive (bool): If True, return an instance of interactive_visualizer; otherwise, return visualizer.
            type (str): The type of visualizer to create.
        Returns:
            visualizer or interactive_visualizer: An instance of the requested visualizer class.
        """
        graph_list = ['boxplot', 'histogram', 'scatter', 'line', 'correlation_matrix']

        if type not in graph_list:
            raise ValueError(f"Invalid graph type. Choose from {graph_list}")

        if interactive:
            return interactive_visualizer(df, type=type)
        else:
            return visualizer(df, type=type)
    

        