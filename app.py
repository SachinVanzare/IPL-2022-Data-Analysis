import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="IPL 2022 Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 17px;
        color: #666;
        margin-top: 0;
        margin-bottom: 25px;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.20);
        padding: 14px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Data loading + feature engineering
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "IPL.csv"


@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        st.error(f"IPL.csv was not found at: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)

    # Same cleaning logic used in the notebook
    player_name_mapping = {
        "K L Rahul": "KL Rahul",
        "Suruakumar Yadav": "Suryakumar Yadav",
        "Shardul Takur": "Shardul Thakur",
        "R Aswin": "R Ashwin",
        "W. Saha": "Wriddhiman Saha"
    }

    player_cols = [
        "toss_winner",
        "match_winner",
        "player_of_the_match",
        "top_scorer",
        "best_bowling",
    ]

    for col in player_cols:
        if col in df.columns:
            df[col] = df[col].replace(player_name_mapping)

    team_mapping = {"Banglore": "Bangalore"}
    team_cols = ["team1", "team2", "toss_winner", "match_winner"]
    for col in team_cols:
        if col in df.columns:
            df[col] = df[col].replace(team_mapping)

    # Date cleaning from notebook
    df["date"] = df["date"].astype(str).str.replace(
        r"([A-Za-z]+)(\d{1,2},\d{4})", r"\1 \2", regex=True
    )
    df["date"] = pd.to_datetime(df["date"], format="%B %d,%Y")

    # Date features
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()
    df["day_name"] = df["date"].dt.day_name()
    df["match_day_type"] = np.where(
        df["day_name"].isin(["Sunday", "Saturday"]),
        "Weekend",
        "Weekday",
    )

    # Match result features
    df["losing_team"] = np.where(
        df["team1"] == df["match_winner"],
        df["team2"],
        df["team1"],
    )
    df["won_by_runs"] = df["won_by"].eq("Runs")
    df["run_margin"] = np.where(df["won_by"] == "Runs", df["margin"], np.nan)
    df["wicket_margin"] = np.where(
        df["won_by"] == "Wickets", df["margin"], np.nan
    )

    # Innings features
    df["score_difference"] = (
        df["first_ings_score"] - df["second_ings_score"]
    )

    df["first_ings_team"] = np.where(
        df["toss_decision"] == "Bat",
        df["toss_winner"],
        np.where(
            df["toss_winner"] == df["team1"],
            df["team2"],
            df["team1"],
        ),
    )

    df["second_ings_team"] = np.where(
        df["first_ings_team"] == df["team1"],
        df["team2"],
        df["team1"],
    )

    df["first_ings_win"] = df["first_ings_team"] == df["match_winner"]
    df["second_ings_win"] = ~df["first_ings_win"]

    # Player bowling features
    df[["best_bowling_wickets", "best_bowling_runs"]] = (
        df["best_bowling_figure"].str.split("--", expand=True).astype(int)
    )

    # Score ranges used in the notebook
    score_bins = [0, 140, 160, 180, 200, 250]
    score_labels = ["Below 140", "140-159", "160-179", "180-199", "200+"]

    df["first_ings_score_range"] = pd.cut(
        df["first_ings_score"],
        bins=score_bins,
        labels=score_labels,
        right=False,
    )

    df["second_ings_score_range"] = pd.cut(
        df["second_ings_score"],
        bins=score_bins,
        labels=score_labels,
        right=False,
    )

    return df


df = load_data()


# ---------------------------------------------------------
# Reproduce notebook analysis tables
# ---------------------------------------------------------
teams = sorted(pd.unique(pd.concat([df["team1"], df["team2"]])))

matches_played = df["team1"].value_counts().add(
    df["team2"].value_counts(), fill_value=0
).astype(int)
matches_won = df["match_winner"].value_counts()

team_kpi = pd.DataFrame(index=teams)
team_kpi["matches_played"] = matches_played
team_kpi["matches_won"] = matches_won
team_kpi["matches_lost"] = team_kpi["matches_played"] - team_kpi["matches_won"]
team_kpi["win_rate(%)"] = (
    team_kpi["matches_won"] / team_kpi["matches_played"] * 100
).round(2)
team_kpi = team_kpi.reset_index(names="team")

first_innings_wins = df[df["first_ings_win"]]["match_winner"].value_counts()
batting_first = df["first_ings_team"].value_counts()
chasing_wins = df[~df["first_ings_win"]]["match_winner"].value_counts()
batting_second = df["second_ings_team"].value_counts()

team_kpi["first_ings_wins"] = team_kpi["team"].map(first_innings_wins).fillna(0).astype(int)
team_kpi["batted_first"] = team_kpi["team"].map(batting_first).fillna(0).astype(int)
team_kpi["batting_first_win_rate(%)"] = (
    team_kpi["first_ings_wins"] / team_kpi["batted_first"] * 100
).round(2)
team_kpi["chasing_wins"] = team_kpi["team"].map(chasing_wins).fillna(0).astype(int)
team_kpi["batted_second"] = team_kpi["team"].map(batting_second).fillna(0).astype(int)
team_kpi["chasing_win_rate(%)"] = (
    team_kpi["chasing_wins"] / team_kpi["batted_second"] * 100
).round(2)
team_kpi["bat_first_vs_chase_diff"] = (
    team_kpi["batting_first_win_rate(%)"] - team_kpi["chasing_win_rate(%)"]
).round(2)

score_strategy = (
    df.groupby("first_ings_score_range", observed=True)["first_ings_win"]
    .agg(["count", "sum", "mean"])
)
score_strategy["win_rate(%)"] = (score_strategy["mean"] * 100).round(2)
score_strategy = score_strategy.drop(columns="mean")
score_strategy = score_strategy.rename(
    columns={"count": "matches", "sum": "first_ings_wins"}
)

second_score_strategy = (
    df.groupby("second_ings_score_range", observed=True)["second_ings_win"]
    .agg(["count", "sum", "mean"])
)
second_score_strategy["win_rate(%)"] = (
    second_score_strategy["mean"] * 100
).round(2)
second_score_strategy = second_score_strategy.drop(columns="mean")
second_score_strategy = second_score_strategy.rename(
    columns={"count": "matches", "sum": "second_ings_wins"}
)

score_comparison = pd.DataFrame(
    {
        "Score Range": score_strategy.index.astype(str),
        "Batting First Win Rate (%)": score_strategy["win_rate(%)"].values,
        "Chasing Win Rate (%)": second_score_strategy["win_rate(%)"].values,
    }
)

pom_counts = df["player_of_the_match"].value_counts().head(10)
top_scorers_counts = df["top_scorer"].value_counts().head(10)
highest_scores = df[["match_id", "top_scorer", "highscore"]].sort_values(
    "highscore", ascending=False
).head(10)

bowling_figures = df.sort_values(
    by=["best_bowling_wickets", "best_bowling_runs"], ascending=[False, True]
)[["match_id", "best_bowling", "best_bowling_figure"]].head(10)

pom = df["player_of_the_match"].value_counts().rename("pom_awards")
top_scorer = df["top_scorer"].value_counts().rename("top_scorer_appearances")
bowling = df["best_bowling"].value_counts().rename("best_bowling_appearances")
player_impact = pd.concat([pom, top_scorer, bowling], axis=1).fillna(0).astype(int)
player_impact["impact_dimensions"] = (
    (player_impact["pom_awards"] > 0).astype(int)
    + (player_impact["best_bowling_appearances"] > 0).astype(int)
    + (player_impact["top_scorer_appearances"] > 0).astype(int)
)
player_impact = player_impact.sort_values(
    by=[
        "impact_dimensions",
        "pom_awards",
        "top_scorer_appearances",
        "best_bowling_appearances",
    ],
    ascending=[False, False, False, False],
)

venue_counts = df["venue"].value_counts()
venue_scoring = (
    df.groupby("venue")["first_ings_score"]
    .agg(["count", "mean", "min", "max"])
    .sort_values("mean", ascending=False)
)
venue_outcomes = df.groupby("venue")["first_ings_win"].agg(["count", "sum", "mean"])
venue_outcomes["first_ings_win_rate(%)"] = (
    venue_outcomes["mean"] * 100
).round(2)
venue_outcomes["chasing_win_rate(%)"] = (
    100 - venue_outcomes["first_ings_win_rate(%)"]
).round(2)
venue_outcomes = venue_outcomes.drop(columns="mean")
venue_outcomes = venue_outcomes.rename(
    columns={"count": "matches_played", "sum": "first_ings_wins"}
)
venue_outcomes["preferred_result"] = np.where(
    venue_outcomes["first_ings_win_rate(%)"] > venue_outcomes["chasing_win_rate(%)"],
    "Batting First",
    np.where(
        venue_outcomes["first_ings_win_rate(%)"] < venue_outcomes["chasing_win_rate(%)"],
        "Chasing",
        "Balanced",
    ),
)
venue_outcomes_filtered = venue_outcomes[
    venue_outcomes["matches_played"] >= 5
].sort_values("first_ings_win_rate(%)", ascending=False)

run_margin_kpi = (
    df[df["won_by"] == "Runs"]
    .groupby("match_winner")["margin"]
    .agg(["count", "mean", "max"])
)
run_margin_kpi["mean"] = run_margin_kpi["mean"].round(2)
run_margin_kpi = run_margin_kpi.rename(
    columns={"count": "run_wins", "mean": "avg_run_margin", "max": "max_run_margin"}
).sort_values("avg_run_margin", ascending=False)

wicket_margin_kpi = (
    df[df["won_by"] == "Wickets"]
    .groupby("match_winner")["margin"]
    .agg(["count", "mean", "max", "min"])
)
wicket_margin_kpi["mean"] = wicket_margin_kpi["mean"].round(2)
wicket_margin_kpi = wicket_margin_kpi.rename(
    columns={
        "count": "wicket_wins",
        "mean": "avg_wicket_margin",
        "max": "max_wicket_margin",
        "min": "min_wicket_margin",
    }
).sort_values("avg_wicket_margin", ascending=False)

# Toss analysis
df["toss_winner_won"] = df["toss_winner"] == df["match_winner"]
toss_win = df["toss_winner"].value_counts()
toss_match_win = df[df["toss_winner_won"]]["match_winner"].value_counts()
toss_performance = pd.DataFrame(
    {
        "tosses_win": toss_win,
        "matches_won_by_toss_winner": toss_match_win,
    }
).fillna(0)
toss_performance["tosses_win"] = toss_performance["tosses_win"].astype(int)
toss_performance["matches_won_by_toss_winner"] = toss_performance[
    "matches_won_by_toss_winner"
].astype(int)
toss_performance["toss_to_match_win_rate(%)"] = (
    toss_performance["matches_won_by_toss_winner"]
    / toss_performance["tosses_win"]
    * 100
).round(2)
toss_performance = toss_performance.sort_values(
    "toss_to_match_win_rate(%)", ascending=False
)

toss_decision_analysis = (
    df.groupby("toss_decision")["toss_winner_won"].agg(["count", "sum", "mean"])
)
toss_decision_analysis["win_rate"] = (
    toss_decision_analysis["mean"] * 100
).round(2)
toss_decision_analysis = toss_decision_analysis.rename(
    columns={"count": "matches", "sum": "wins"}
)[["matches", "wins", "win_rate"]]

# Group-stage KPI
group_stage_df = df[df["stage"] == "Group"].copy()
group_stage_kpi = pd.DataFrame(
    index=sorted(
        pd.unique(pd.concat([group_stage_df["team1"], group_stage_df["team2"]]))
    )
)
group_stage_kpi["matches_played"] = (
    group_stage_df["team1"].value_counts()
    .add(group_stage_df["team2"].value_counts(), fill_value=0)
    .astype(int)
)
group_stage_kpi["matches_won"] = group_stage_df["match_winner"].value_counts()
group_stage_kpi["matches_lost"] = (
    group_stage_kpi["matches_played"] - group_stage_kpi["matches_won"]
)
group_stage_kpi["win_rate(%)"] = (
    group_stage_kpi["matches_won"] / group_stage_kpi["matches_played"] * 100
).round(2)
group_stage_kpi = group_stage_kpi.sort_values("win_rate(%)", ascending=False).reset_index(
    names="team"
)


# ---------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------
st.sidebar.title("🏏 IPL 2022 Analytics")
st.sidebar.caption("Interactive version of the completed capstone project")

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "Team Performance",
        "Innings & Strategy",
        "Player Performance",
        "Venue Analysis",
        "Toss Analysis",
        "Key Insights",
        "Data Explorer",
    ],
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def plotly_layout(fig, height=480):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=70, b=30),
        legend_title_text="",
    )
    return fig


# ---------------------------------------------------------
# Overview
# ---------------------------------------------------------
if page == "Overview":
    st.markdown('<p class="main-title">IPL 2022 Analytics Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Interactive analysis of team performance, scoring strategy, players, venues, toss outcomes and winning margins.</p>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Matches", len(df))
    c2.metric("Teams", df["team1"].nunique() + 0 if False else len(teams))
    c3.metric("Batting-First Wins", int(df["first_ings_win"].sum()))
    c4.metric("Chasing Wins", int((~df["first_ings_win"]).sum()))
    c5.metric("Toss Conversion", f"{df['toss_winner_won'].mean() * 100:.2f}%")

    st.divider()
    st.subheader("Project Scope")
    st.write(
        "This dashboard is the interactive presentation layer for the completed IPL 2022 capstone notebook. "
        "The calculations reproduce the notebook's cleaning, feature engineering, analysis and KPI logic."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Main Analytical Areas")
        st.markdown(
            """
            - Team performance and win rates
            - Batting-first vs chasing outcomes
            - First- and second-innings scoring strategy
            - Player contributions
            - Venue scoring and match outcomes
            - Toss decisions and toss-to-match conversion
            - Winning margins and advanced KPIs
            """
        )
    with col2:
        st.subheader("Dataset Snapshot")
        st.dataframe(
            pd.DataFrame(
                {
                    "Metric": ["Rows", "Columns", "Duplicate Rows", "Missing Values", "Unique Teams"],
                    "Value": [
                        len(df),
                        20,
                        int(df.duplicated().sum()),
                        int(df.isna().sum().sum()),
                        len(teams),
                    ],
                }
            ),
            hide_index=True,
            use_container_width=True,
        )


# ---------------------------------------------------------
# Team Performance
# ---------------------------------------------------------
elif page == "Team Performance":
    st.title("🏆 Team Performance")
    st.caption("Team KPIs reproduced from the notebook's overall and match-strategy analysis.")

    selected_team = st.selectbox("Select a team", ["All Teams"] + teams)

    if selected_team == "All Teams":
        display_team = team_kpi.sort_values("win_rate(%)", ascending=False)
    else:
        display_team = team_kpi[team_kpi["team"] == selected_team]

    st.dataframe(
        display_team[
            [
                "team",
                "matches_played",
                "matches_won",
                "matches_lost",
                "win_rate(%)",
                "batting_first_win_rate(%)",
                "chasing_win_rate(%)",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Team Win Rate")
    chart_df = team_kpi.sort_values("win_rate(%)", ascending=True)
    fig = px.bar(
        chart_df,
        x="win_rate(%)",
        y="team",
        orientation="h",
        text="win_rate(%)",
        labels={"win_rate(%)": "Win Rate (%)", "team": "Team"},
        title="IPL 2022 Team Win Rate",
    )
    fig.add_vline(x=50, line_dash="dash", annotation_text="50% Win Rate")
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_xaxes(range=[0, 80])
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

    st.subheader("Batting First vs Chasing")
    comparison = team_kpi[
        ["team", "batting_first_win_rate(%)", "chasing_win_rate(%)"]
    ].melt(id_vars="team", var_name="strategy", value_name="win_rate")
    comparison["strategy"] = comparison["strategy"].map(
        {
            "batting_first_win_rate(%)": "Batting First",
            "chasing_win_rate(%)": "Chasing",
        }
    )
    fig = px.bar(
        comparison,
        x="team",
        y="win_rate",
        color="strategy",
        barmode="group",
        text="win_rate",
        labels={"win_rate": "Win Rate (%)", "team": "Team", "strategy": "Strategy"},
        title="Batting First vs Chasing Win Rate by Team",
    )
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(plotly_layout(fig, 520), use_container_width=True)

    st.subheader("Biggest Run-Margin Victories")
    run_wins = df[df["won_by"] == "Runs"].copy()
    run_wins["against"] = np.where(
        run_wins["team1"] == run_wins["match_winner"],
        run_wins["team2"],
        run_wins["team1"],
    )
    st.dataframe(
        run_wins.sort_values("margin", ascending=False)
        .head(10)[["match_id", "match_winner", "against", "margin"]]
        .rename(columns={"margin": "run_margin"}),
        hide_index=True,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Innings & Strategy
# ---------------------------------------------------------
elif page == "Innings & Strategy":
    st.title("📊 Innings & Strategy")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Batting-First Wins", int(df["first_ings_win"].sum()))
    with c2:
        st.metric("Chasing Wins", int((~df["first_ings_win"]).sum()))

    st.subheader("First-Innings Score Range vs Win Rate")
    score_plot = score_strategy.reset_index()
    score_plot["first_ings_score_range"] = score_plot["first_ings_score_range"].astype(str)
    fig = px.bar(
        score_plot,
        x="first_ings_score_range",
        y="win_rate(%)",
        text="win_rate(%)",
        labels={
            "first_ings_score_range": "First-Innings Score Range",
            "win_rate(%)": "Win Rate (%)",
        },
        title="First-Innings Score Range vs Win Rate",
    )
    fig.add_hline(y=50, line_dash="dash", annotation_text="50% Win Rate")
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

    st.subheader("Batting First vs Chasing by Score Range")
    fig = px.bar(
        score_comparison.melt(
            id_vars="Score Range", var_name="strategy", value_name="win_rate"
        ),
        x="Score Range",
        y="win_rate",
        color="strategy",
        barmode="group",
        text="win_rate",
        labels={"win_rate": "Win Rate (%)", "strategy": "Strategy"},
        title="Win Rate by Score Range: Batting First vs Chasing",
    )
    fig.add_hline(y=50, line_dash="dash", annotation_text="50% Win Rate")
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(plotly_layout(fig, 520), use_container_width=True)

    st.subheader("First-Innings Score Summary")
    score_summary = df.groupby("first_ings_win")["first_ings_score"].agg(
        ["count", "min", "max", "mean", "median"]
    )
    score_summary.index = score_summary.index.map(
        {True: "First-Innings Win", False: "First-Innings Loss"}
    )
    st.dataframe(score_summary.round(2), use_container_width=True)


# ---------------------------------------------------------
# Player Performance
# ---------------------------------------------------------
elif page == "Player Performance":
    st.title("👤 Player Performance")

    st.subheader("Player of the Match Awards")
    pom_df = pom_counts.sort_values().reset_index()
    pom_df.columns = ["player", "awards"]
    fig = px.bar(
        pom_df,
        x="awards",
        y="player",
        orientation="h",
        text="awards",
        title="Top Player of the Match Award Winners",
        labels={"awards": "Awards", "player": "Player"},
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top-Scorer Appearances")
        ts_df = top_scorers_counts.sort_values().reset_index()
        ts_df.columns = ["player", "appearances"]
        fig = px.bar(
            ts_df,
            x="appearances",
            y="player",
            orientation="h",
            text="appearances",
            labels={"appearances": "Appearances", "player": "Player"},
            title="Players Most Frequently Recorded as Top Scorer",
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_layout(fig, 450), use_container_width=True)

    with col2:
        st.subheader("Highest Individual Scores")
        st.dataframe(
            highest_scores.rename(
                columns={"top_scorer": "player", "highscore": "score"}
            ),
            hide_index=True,
            use_container_width=True,
        )

    st.subheader("Best Bowling Performances")
    st.dataframe(bowling_figures, hide_index=True, use_container_width=True)

    st.subheader("Player Impact Across Three Measured Dimensions")
    impact_display = player_impact.head(10).reset_index(names="player")
    st.dataframe(impact_display, hide_index=True, use_container_width=True)
    st.caption(
        "Impact dimensions count whether a player appeared in Player of the Match awards, "
        "top-scorer appearances and best-bowling appearances. It is a dataset-specific indicator, "
        "not a complete player-performance rating."
    )


# ---------------------------------------------------------
# Venue Analysis
# ---------------------------------------------------------
elif page == "Venue Analysis":
    st.title("🏟️ Venue Analysis")
    st.caption("Venue-level patterns are shown separately for regularly used venues (5+ matches) where appropriate.")

    st.subheader("Matches Hosted by Venue")
    venue_df = venue_counts.sort_values().reset_index()
    venue_df.columns = ["venue", "matches"]
    fig = px.bar(
        venue_df,
        x="matches",
        y="venue",
        orientation="h",
        text="matches",
        title="Matches Hosted by Venue",
        labels={"matches": "Matches", "venue": "Venue"},
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

    st.subheader("Average First-Innings Score by Venue")
    venue_plot = venue_scoring[venue_scoring["count"] >= 5].sort_values("mean").reset_index()
    fig = px.bar(
        venue_plot,
        x="mean",
        y="venue",
        orientation="h",
        text="mean",
        title="Average First-Innings Score by Venue (5+ Matches)",
        labels={"mean": "Average First-Innings Score", "venue": "Venue"},
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

    st.subheader("Batting First vs Chasing by Venue")
    vo = venue_outcomes_filtered.reset_index()
    vo_long = vo.melt(
        id_vars=["venue", "matches_played"],
        value_vars=["first_ings_win_rate(%)", "chasing_win_rate(%)"],
        var_name="strategy",
        value_name="win_rate",
    )
    vo_long["strategy"] = vo_long["strategy"].map(
        {
            "first_ings_win_rate(%)": "Batting First",
            "chasing_win_rate(%)": "Chasing",
        }
    )
    fig = px.bar(
        vo_long,
        x="venue",
        y="win_rate",
        color="strategy",
        barmode="group",
        text="win_rate",
        labels={"win_rate": "Win Rate (%)", "venue": "Venue"},
        title="Match Outcome by Venue (5+ Matches)",
    )
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(plotly_layout(fig, 520), use_container_width=True)

    st.subheader("Venue Outcome Table")
    st.dataframe(venue_outcomes_filtered.reset_index(), hide_index=True, use_container_width=True)


# ---------------------------------------------------------
# Toss Analysis
# ---------------------------------------------------------
elif page == "Toss Analysis":
    st.title("🪙 Toss Analysis")

    toss_rate = df["toss_winner_won"].mean() * 100
    c1, c2, c3 = st.columns(3)
    c1.metric("Toss Winners Who Won Match", f"{toss_rate:.2f}%")
    c2.metric("Toss Wins Converted", int(df["toss_winner_won"].sum()))
    c3.metric("Toss Wins Not Converted", int((~df["toss_winner_won"]).sum()))

    st.subheader("Toss Decision Distribution")
    decision_counts = df["toss_decision"].value_counts().reset_index()
    decision_counts.columns = ["decision", "matches"]
    fig = px.bar(
        decision_counts,
        x="decision",
        y="matches",
        text="matches",
        title="Toss Decision Distribution",
        labels={"decision": "Toss Decision", "matches": "Matches"},
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(plotly_layout(fig, 400), use_container_width=True)

    st.subheader("Toss-to-Match Win Conversion by Team")
    tp = toss_performance.reset_index(names="team")
    fig = px.bar(
        tp.sort_values("toss_to_match_win_rate(%)"),
        x="toss_to_match_win_rate(%)",
        y="team",
        orientation="h",
        text="toss_to_match_win_rate(%)",
        labels={
            "toss_to_match_win_rate(%)": "Toss-to-Match Win Rate (%)",
            "team": "Team",
        },
        title="Toss-to-Match Win Conversion by Team",
    )
    fig.add_vline(x=50, line_dash="dash", annotation_text="50%")
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_xaxes(range=[0, 80])
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

    st.subheader("Did Toss Decision Affect Toss-Winner Match Win Rate?")
    td = toss_decision_analysis.reset_index(names="toss_decision")
    st.dataframe(td, hide_index=True, use_container_width=True)

    fig = px.bar(
        td,
        x="toss_decision",
        y="win_rate",
        text="win_rate",
        title="Toss-Winner Match Win Rate by Toss Decision",
        labels={"win_rate": "Toss-Winner Match Win Rate (%)", "toss_decision": "Decision"},
    )
    fig.add_hline(y=50, line_dash="dash", annotation_text="50%")
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(plotly_layout(fig, 400), use_container_width=True)


# ---------------------------------------------------------
# Key Insights
# ---------------------------------------------------------
elif page == "Key Insights":
    st.title("💡 Key Insights")

    best_team = team_kpi.sort_values("win_rate(%)", ascending=False).iloc[0]
    highest_score_range = score_strategy["win_rate(%)"].idxmax()
    highest_score_value = score_strategy.loc[highest_score_range, "win_rate(%)"]
    highest_score_matches = score_strategy.loc[highest_score_range, "matches"]
    highest_venue = venue_scoring[venue_scoring["count"] >= 5].iloc[0]
    batting_first_venue = venue_outcomes_filtered.iloc[0]
    chasing_venue = venue_outcomes_filtered.sort_values("chasing_win_rate(%)", ascending=False).iloc[0]

    st.info(
        f"**Overall team performance:** {best_team['team']} recorded {int(best_team['matches_won'])} wins "
        f"from {int(best_team['matches_played'])} matches, giving a {best_team['win_rate(%)']:.2f}% win rate."
    )

    st.info(
        f"**Scoring strategy:** teams scoring in the **{highest_score_range}** first-innings range won "
        f"{highest_score_value:.2f}% of {int(highest_score_matches)} matches in that range. "
        "This is an association within the IPL 2022 dataset, not proof of causation."
    )

    st.info(
        f"**Venue scoring:** {highest_venue.name} recorded an average first-innings score of "
        f"{highest_venue['mean']:.2f} runs among venues with at least five matches."
    )

    st.info(
        f"**Venue outcome patterns:** {batting_first_venue.name} had a {batting_first_venue['first_ings_win_rate(%)']:.2f}% "
        f"batting-first win rate, while {chasing_venue.name} had a {chasing_venue['chasing_win_rate(%)']:.2f}% chasing win rate "
        "among regularly used venues."
    )

    st.info(
        f"**Toss impact:** toss winners won {int(df['toss_winner_won'].sum())} of {len(df)} matches, "
        f"a {toss_rate:.2f}% conversion rate."
    )

    st.warning(
        "**Scope limitation:** the dashboard is based on IPL 2022 match-level data only. "
        "It does not include ball-by-ball information, pitch/weather variables, injuries, player availability "
        "or other detailed match-context factors."
    )


# ---------------------------------------------------------
# Data Explorer
# ---------------------------------------------------------
elif page == "Data Explorer":
    st.title("🔎 Data Explorer")
    st.caption("Explore the cleaned and feature-engineered IPL 2022 dataset used by the dashboard.")

    col1, col2 = st.columns(2)
    with col1:
        team_filter = st.multiselect("Filter by team", teams, default=[])
    with col2:
        venue_filter = st.multiselect("Filter by venue", sorted(df["venue"].unique()), default=[])

    filtered_df = df.copy()
    if team_filter:
        filtered_df = filtered_df[
            filtered_df["team1"].isin(team_filter) | filtered_df["team2"].isin(team_filter)
        ]
    if venue_filter:
        filtered_df = filtered_df[filtered_df["venue"].isin(venue_filter)]

    st.metric("Filtered Matches", len(filtered_df))
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)
