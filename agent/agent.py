from google.adk.agents  import ParallelAgent, LlmAgent

GEMINI_MODEL = "gemini-2.5-flash"

print("🚀 Initializing Stock Market Content Agents...")

# Market News Summary Agent
news_agent = LlmAgent(
    name="MarketNewsAgent",
    model=GEMINI_MODEL,
    instruction="""
You are a financial news analyst. Based on the user query, generate:
- A concise market headline
- Summary of the news (3–5 bullet points)
- Why this news matters for investors
- Potential risks or uncertainties
Keep the explanation simple and beginner-friendly.
""",
    output_key="market_news"
)

print("📰 Market News Agent ready.")

# Stock Analysis Agent
analysis_agent = LlmAgent(
    name="StockAnalysisAgent",
    model=GEMINI_MODEL,
    instruction="""
You are a stock research assistant. Based on the user query, provide:
1. Company or sector overview
2. Recent performance highlights
3. Key financial or growth indicators
4. Bullish vs Bearish perspective
Keep the output structured and easy to scan.
""",
    output_key="stock_analysis"
)

print("📊 Stock Analysis Agent ready.")

# Investment Insights Agent
insights_agent = LlmAgent(
    name="InvestmentInsightsAgent",
    model=GEMINI_MODEL,
    instruction="""
You are an investment strategist. Based on the user query, generate:
- Short-term outlook
- Long-term outlook
- Possible trading or investing strategies
- Risk management tips
Do not provide financial advice — only educational insights.
""",
    output_key="investment_insights"
)

print("💡 Investment Insights Agent ready.")

# Parallel Market Research Agent
market_research_agent = ParallelAgent(
    name="MarketResearchAgent",
    sub_agents=[news_agent, analysis_agent, insights_agent],
    description="Generates market news summaries, stock analysis, and investment insights in parallel."
)

print("⚡ Parallel Market Research Agent initialized.")

# Root agent (for ADK compatibility)
root_agent = market_research_agent

print("✅ Root agent is ready to process queries.")