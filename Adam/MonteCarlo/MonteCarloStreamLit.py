#Code to Incorportate in 'my_app.py'



# get_MC_input function creates a list of inputs to create a Monte Carlo class instance, where:
# Monte_Carlo_df: dataframe of prices;
# four_portfolios_df: dataframe of our selected portfolios - in the function it will be used to get weights input to Monte Carlo class;
# portfolio: we create an instance for each portfolio and also use portfolio tickers to select price data from Monte_Carlo_df
Monte_Carlo__list=[get_MC_input(api_call_df, four_portfolios_df, portfolio, initial_investment, time_horizon) for portfolio in four_portfolios]


#instantiating the class:
Capacity_MC=MCSimulation(Monte_Carlo__list[0][0], Monte_Carlo__list[0][2], Monte_Carlo__list[0][1], 300, int(Monte_Carlo__list[0][3]))

#Calling Monte Carlo Sim on Capacity Portfolio
Capacity_MC = MCSimulation(
    portfolio_data = Monte_Carlo__list[0][0],
    investment_amount = Monte_Carlo__list[0][2],
    weights = Monte_Carlo__list[0][1],
    num_simulation = 100, 
    years = int(Monte_Carlo__list[0][3]))

#Getting HvPlots and Returns on Capacity Sim
capacity_plot = Capacity_MC.plot_simulation()
capacity_dist = Capacity_MC.plot_distribution()
capacity_returns = Capacity_MC.return_amount()


#Calling Monte Carlo Sim on Tolerance Portfolio
Tolerance_MC = MCSimulation(
    portfolio_data = Monte_Carlo__list[1][0],
    investment_amount = Monte_Carlo__list[1][2],
    weights = Monte_Carlo__list[1][1],
    num_simulation = 100, 
    years = int(Monte_Carlo__list[1][3]))

#Getting HvPlots and Returns on Capacity Sim
tolerance_plot = Tolerance_MC.plot_simulation()
tolerance_dist = Tolerance_MC.plot_distribution()
tolerance_returns = Tolerance_MC.return_amount()


#Calling Monte Carlo Sim on Benchmark Portfolio
Benchmark_MC = MCSimulation(
    portfolio_data = Monte_Carlo__list[2][0],
    investment_amount = Monte_Carlo__list[2][2],
    weights = Monte_Carlo__list[2][1],
    num_simulation = 100, 
    years = int(Monte_Carlo__list[2][3]))

#Getting HvPlots and Returns on Benchmark Sim
benchmark_plot = Benchmark_MC.plot_simulation()
benchmark_dist = Benchmark_MC.plot_distribution()
benchmark_returns = Benchmark_MC.return_amount()

#Calling Monte Carlo Sim on Cryptomix Portfolio
Cryptomix_MC = MCSimulation(
    portfolio_data = Monte_Carlo__list[3][0],
    investment_amount = Monte_Carlo__list[3][2],
    weights = Monte_Carlo__list[3][1],
    num_simulation = 100, 
    years = int(Monte_Carlo__list[3][3]))

cryptomix_plot = Cryptomix_MC.plot_simulation()
cryptomix_dist = Cryptomix_MC.plot_distribution()
cryptomix_returns = Cryptomix_MC.return_amount()

with tab4:

    st.header("Future Predictions of Portfolios:")

    st.subheader("Monte Carlo Simulation Analysis:")

    st.write(f"With the utilization of a simulation known as 'Monte Carlo', your portfolios were analyzed for their estimated future returns using an intial invesment of **:blue[${initial_investment:.2f}]** over the span of **:blue[{time_horizon:.0f}]** years. The following were the outcomes...")

    st.markdown("_**Disclaimer:** These results are not guaranteed but rather an estimate based on the assumption of normal distribution, which quantifies risk and return by the mean for returns and standard deviation for risk._")

    st.header(f"{time_horizon:.0f} Year Portfolio Analysis:")

    column1, column2, column3, column4 = st.columns([1,2,2,1.5])
    
    with column1:

        st.subheader("_**Portfolio Type**_")

        st.markdown("**Capacity Portfolio:**")

        st.markdown("**Tolerance Portfolio:**")

        st.markdown("**Benchmark Portfolio:**")

        st.markdown("**Cryptomix Portfolio:**")

    with column2:

        st.subheader("_**Plot**_")

        st.bokeh_chart(hv.render(capacity_plot, backend='bokeh'))

        st.bokeh_chart(hv.render(tolerance_plot, backend='bokeh'))

        st.bokeh_chart(hv.render(benchmark_plot, backend='bokeh'))

        st.bokeh_chart(hv.render(cryptomix_plot, backend='bokeh'))

    with column3:

        st.subheader("**_Distribution_**")

        st.bokeh_chart(hv.render(capacity_dist, backend='bokeh'))

        st.bokeh_chart(hv.render(tolerance_dist, backend='bokeh'))

        st.bokeh_chart(hv.render(benchmark_dist, backend='bokeh'))

        st.bokeh_chart(hv.render(cryptomix_dist, backend='bokeh'))

    with column4:

        st.subheader("**_Estimated Returns_**")

        st.write(f'With a 95% confidence, your capacity portfolio will have an estimated outcome between **:blue[{capacity_returns[0]:.2f}]** and **:blue[{capacity_returns[1]:.2f}]** USD.')

        st.write(f'With a 95% confidence, your selected portfolio will have an estimated outcome between **:blue[{tolerance_returns[0]:.2f}]** and **:blue[{tolerance_returns[1]:.2f}]** USD.')

        st.write(f'With a 95% confidence, your selected portfolio will have an estimated outcome between **:blue[{benchmark_returns[0]:.2f}]** and **:blue[{benchmark_returns[1]:.2f}]** USD.')

        st.write(f'With a 95% confidence, your selected portfolio will have an estimated outcome between **:blue[{cryptomix_returns[0]:.2f}]** and **:blue[{cryptomix_returns[1]:.2f}]** USD.')