# data_processor.py

import pandas as pd
from datetime import datetime, timedelta
import pytz  # ✅ Import necessário para timezone

class DataProcessor:
    def process_workflow_runs(self, runs, days_filter):
        """Process workflow runs data into um DataFrame pandas"""
        df = pd.DataFrame(runs)
        
        # Convertendo timestamps UTC -> America/Sao_Paulo
        df['started_at'] = pd.to_datetime(df['started_at']).dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')
        df['updated_at'] = pd.to_datetime(df['updated_at']).dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')

        # Data limite com timezone SP
        cutoff_date = datetime.now(pytz.timezone("America/Sao_Paulo")) - timedelta(days=days_filter)
        df = df[df['started_at'] >= cutoff_date]

        # Duração em minutos
        df['duration_minutes'] = (df['updated_at'] - df['started_at']).dt.total_seconds() / 60

        # Ajuste do status
        df['status'] = df.apply(
            lambda x: x['conclusion'] if x['status'] == 'completed' else x['status'],
            axis=1
        )

        return df

    def calculate_success_rate_trend(self, df):
        """Cálculo da taxa de sucesso diária"""
        df['date'] = df['started_at'].dt.date
        daily_stats = df.groupby('date').agg({
            'id': 'count',
            'status': lambda x: (x == 'success').sum()
        }).reset_index()
        
        daily_stats['success_rate'] = (daily_stats['status'] / daily_stats['id']) * 100
        return daily_stats

    def calculate_repo_metrics(self, df):
        """Cálculo de métricas por repositório"""
        repo_metrics = df.groupby('repository').agg({
            'id': 'count',
            'status': lambda x: (x == 'success').mean() * 100,
            'duration_minutes': 'mean'
        }).reset_index()
        
        repo_metrics.columns = ['repository', 'total_runs', 'success_rate', 'avg_duration']
        repo_metrics.set_index('repository', inplace=True)
        
        return repo_metrics
