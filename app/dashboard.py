import dash
from dash import html, dcc, Input, Output, ctx
import pandas as pd
import plotly.express as px
import numpy as np

print("Running Enhanced dashboard.py")

# ----- Sample Data -----
np.random.seed(0)
sample_data = [
    {"post": "Post A about climate change", "likes": 10, "engagement": 50, "misinfo": False},
    {"post": "Breaking news: stock market", "likes": 200, "engagement": 10, "misinfo": True},
    {"post": "New tech gadget released", "likes": 80, "engagement": 120, "misinfo": False},
    {"post": "Celebrity news", "likes": 150, "engagement": 30, "misinfo": True},
    {"post": "Sports update", "likes": 90, "engagement": 150, "misinfo": False},
    {"post": "Science breakthroughs", "likes": 130, "engagement": 80, "misinfo": False},
]
df = pd.DataFrame(sample_data)
df["polarization"] = np.round(np.random.uniform(-1, 1, len(df)), 2)  # Add polarization score

# ----- Bias Detection -----
def engagement_based_ranking(df):
    return df.sort_values(by='engagement', ascending=False)

def popularity_based_ranking(df):
    return df.sort_values(by='likes', ascending=False)

def polarization_based_ranking(df):
    return df.sort_values(by='polarization', key=abs, ascending=False)

def check_bias(df, engagement_threshold=100):
    flagged = df[df['engagement'] > engagement_threshold]
    return flagged['post'].tolist()

audit_notes = {
    'engagement': "⚠️ Engagement-based systems often amplify sensational or emotionally charged content, increasing polarization and misinformation.",
    'popularity': "⚠️ Popularity-based systems can reinforce inequality by favoring already well-known voices.",
    'polarization': "⚠️ Polarization-based systems may create echo chambers by surfacing extreme views over balanced content."
}

# ----- Dash App -----
app = dash.Dash(__name__)
app.title = "Algorithmic Bias Visualizer"

app.layout = html.Div([
    html.H1("🧠 Algorithmic Bias Visualizer"),
    html.P("Explore how different recommendation algorithms amplify content and contribute to bias."),
    
    html.Label("Choose Algorithm Type:"),
    dcc.Dropdown(
        id='algo-dropdown',
        options=[
            {'label': 'Engagement-Based', 'value': 'engagement'},
            {'label': 'Popularity-Based', 'value': 'popularity'},
            {'label': 'Polarization-Based', 'value': 'polarization'}
        ],
        value='engagement',
        clearable=False,
        style={'width': '50%'}
    ),

    html.Br(),

    html.Button("⬇ Export Rankings to CSV", id="export-button"),
    dcc.Download(id="download-dataframe-csv"),

    dcc.Graph(id='ranking-graph'),
    html.Div(id='bias-warning', style={'color': 'red', 'fontWeight': 'bold'}),
    html.Div(id='audit-panel', style={
        'marginTop': '20px',
        'padding': '10px',
        'border': '1px solid gray',
        'backgroundColor': '#f9f9f9'
    })
])

# ----- Callbacks -----
@app.callback(
    Output('ranking-graph', 'figure'),
    Output('bias-warning', 'children'),
    Output('audit-panel', 'children'),
    Input('algo-dropdown', 'value')
)
def update_output(selected_algo):
    if df.empty:
        return {}, "❌ No data available.", ""

    if selected_algo == 'engagement':
        ranked = engagement_based_ranking(df)
    elif selected_algo == 'popularity':
        ranked = popularity_based_ranking(df)
    else:
        ranked = polarization_based_ranking(df)

    fig = px.bar(
        ranked.head(20),
        x='post',
        y=['likes', 'engagement', 'polarization'],
        barmode='group',
        title=f"{selected_algo.capitalize()} Ranking (Sample Data)"
    )

    flagged = check_bias(ranked)
    warning = f"⚠️ High engagement bias detected in: {', '.join(flagged[:3])}..." if flagged else ""
    audit_text = audit_notes.get(selected_algo, "")
    return fig, warning, audit_text

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    prevent_initial_call=True,
)
def export_csv(n_clicks):
    return dcc.send_data_frame(df.to_csv, "ranked_content.csv")

# ----- Run Server -----
if __name__ == '__main__':
    app.run(debug=True)
