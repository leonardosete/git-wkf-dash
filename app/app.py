# app.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

from github_api import GitHubAPI
from data_processor import DataProcessor
from config import GITHUB_TOKEN, DEFAULT_REPOS

# Page configuration
st.set_page_config(
    page_title="GitHub Actions Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Initialize the API client and data processor
api_client = GitHubAPI(GITHUB_TOKEN)
data_processor = DataProcessor()

# Title and description
st.title("🚀 GitHub Actions Workflows Dashboard")
st.markdown("Monitor and analyze GitHub Actions workflows across multiple repositories")

# Repository selection
repos_input = st.text_area(
    "Enter repositories (one per line, format: owner/repo)",
    value="\n".join(DEFAULT_REPOS),
    height=100
)
repositories = [repo.strip() for repo in repos_input.split("\n") if repo.strip()]

# Date range filter
col1, col2 = st.columns(2)
with col1:
    days_ago = st.slider("Show data from last X days", 1, 30, 7)
with col2:
    status_filter = st.multiselect(
        "Filter by status",
        ["success", "failure", "cancelled", "skipped", "in_progress"],
        default=["success", "failure"]
    )

# Fetch and process data
try:
    @st.cache_data(ttl=300)
    def load_workflow_data(repos, days):
        all_runs = []
        for repo in repos:
            runs = api_client.get_workflow_runs(repo)
            all_runs.extend(runs)
        return data_processor.process_workflow_runs(all_runs, days)
    
    df = load_workflow_data(repositories, days_ago)
    
    # Apply filters
    df_filtered = df[df['status'].isin(status_filter)]
    
    # Dashboard layout
    col1, col2 = st.columns(2)
    
    # Status Overview
    with col1:
        st.subheader("Workflow Status Overview")
        status_counts = df_filtered['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Workflow Run Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Success Rate Trend
    with col2:
        st.subheader("Success Rate Trend")
        success_rate = data_processor.calculate_success_rate_trend(df_filtered)
        fig_trend = px.line(
            success_rate,
            x='date',
            y='success_rate',
            title="Daily Success Rate (%)"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Repository Performance
    st.subheader("Repository Performance")
    repo_metrics = data_processor.calculate_repo_metrics(df_filtered)
    
    fig_repo = go.Figure(data=[
        go.Bar(name='Success Rate', x=repo_metrics.index, y=repo_metrics['success_rate']),
        go.Bar(name='Avg Duration (min)', x=repo_metrics.index, y=repo_metrics['avg_duration'])
    ])
    fig_repo.update_layout(barmode='group', title="Repository Metrics")
    st.plotly_chart(fig_repo, use_container_width=True)
    
    # Recent Workflow Runs Table
    st.subheader("Recent Workflow Runs")
    st.dataframe(
        df_filtered[['repository', 'workflow_name', 'status', 'started_at', 'duration_minutes']]
        .sort_values('started_at', ascending=False)
        .head(10),
        use_container_width=True
    )

except Exception as e:
    st.error(f"Error fetching data: {str(e)}")
    st.warning("Please check your GitHub token and repository names.")