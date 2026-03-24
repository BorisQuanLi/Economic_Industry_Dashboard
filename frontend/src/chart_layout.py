# Dark theme compatible white and grey palette
COMMON_FONT_FAMILY = "Helvetica, Arial, sans-serif"
COMMON_FONT_COLOR = "#FFFFFF" # Pure White for dark themes
GRID_COLOR = "rgba(255,255,255,0.15)"
LINE_COLOR = "rgba(255,255,255,0.3)"

def apply_standard_chart_layout(fig, title, xaxis_title, yaxis_title, legend_title, font_size=12):
    # Determine if this is a percentage chart for formatting
    is_percentage = (yaxis_title == 'Percentage')
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=font_size + 6, color=COMMON_FONT_COLOR)
        ),
        xaxis_title=xaxis_title,
        yaxis_title="" if is_percentage else yaxis_title, # Remove redundant 'Percentage' label
        xaxis=dict(
            type='category',
            domain=[0.05, 0.82], # Slightly narrowed domain to give more room for larger legend text
            gridcolor=GRID_COLOR,
            showline=True,
            linecolor=LINE_COLOR,
            mirror=True,
            showspikes=True,
            spikemode='across',
            spikethickness=1,
            spikecolor=LINE_COLOR
        ),
        yaxis=dict(
            automargin=True,
            gridcolor=GRID_COLOR,
            showline=True,
            linecolor=LINE_COLOR,
            mirror=True,
            ticksuffix='% ' if is_percentage else '' # Add percentage sign and trailing space
        ),
        legend=dict(
            title=dict(text=f"<b>{legend_title}</b>", font=dict(size=18, color=COMMON_FONT_COLOR)),
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            borderwidth=0,
            x=0.84, # Moved closer to the new 82% domain end
            y=1,
            xanchor="left",
            yanchor="top",
            font=dict(size=16, color=COMMON_FONT_COLOR), # Large, consistent font size for all charts
            itemsizing='constant'
        ),
        margin=dict(l=50, r=30, t=100, b=80), 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        font=dict(
            family=COMMON_FONT_FAMILY,
            size=font_size,
            color=COMMON_FONT_COLOR,
        ),
        height=600,
    )
    
    # Also update Hovertemplate if it's a percentage chart
    if is_percentage:
        fig.update_traces(hovertemplate='%{y}% ')

    # Highlight points with high contrast markers
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
    return fig