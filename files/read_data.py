import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def read_plot(file_path='../reddit-data/ukraine_russia.csv'):
        df=pd.read_csv(file_path)
        print(f'Keyword filter: {len(df)}')
        df['week'] = pd.to_datetime(df['created_utc'], unit='s', utc=True).dt.to_period('W')
        min_posts=100
        domain_counts=df.domain.value_counts().reset_index()
        domain_counts=domain_counts[domain_counts['count']>100]
        df=df[df['domain'].isin(domain_counts['domain'].unique())]
        print(f'Domain frequency filter: {len(df)}')

        weekly_counts = df.groupby('week').count()['id'].reset_index()
        # Plotting
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(weekly_counts['week'].astype(str), weekly_counts['id'], color='skyblue',width=1)
        ax.set_xlabel('Week', fontsize=12)
        ax.set_ylabel('Count of ID', fontsize=12)
        ax.set_title('Weekly ID Counts', fontsize=14, fontweight='bold')
        num_ticks = 10  # Adjust based on your data size
        ax.set_xticks(ax.get_xticks()[::max(len(weekly_counts) // num_ticks, 1)])
        ax.tick_params(axis='x', rotation=45)
        # Grid lines for better readability
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        # Show the plot
        plt.show()
        return df